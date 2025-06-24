# File: ulacm_backend/app/services/workflow_service.py
# Purpose: Service for orchestrating Process Workflow execution.
# Fixed: Remove <think> tags from LLM response before saving to document.

import logging
import datetime
import re
import fnmatch
import json
from typing import List, Tuple, Optional, Dict, Any, AsyncIterator
from uuid import UUID as PyUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import or_, and_, update as sqlalchemy_update
from pydantic.json import pydantic_encoder

from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition
from app.crud import crud_content_item
from app.crud import crud_content_version
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.schemas.content_version import ContentVersionCreate
from app.schemas.content_item import ContentItemCreate as ContentItemCreateSchema
from app.schemas.workflow_definition import WorkflowExecutionOutputDocument
from app.core.config import settings

log = logging.getLogger(__name__)
__all__ = ["execute_workflow_streaming", "OllamaServiceError", "WorkflowParsingError"]

MAX_UNIQUE_NAME_ATTEMPTS = 100
ULACM_STREAM_END_TOKEN = "ULACM_STREAM_END_TOKEN:"

def _remove_think_tags(text: str) -> str:
    """Removes <think>...</think> tags from a string."""
    if not text:
        return ""
    # Regex to match <think>...</think> tags, including multi-line content (re.DOTALL equivalent)
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def _match_glob_pattern(name: str, pattern: str) -> bool:
    # Helper function to match a name against a glob pattern, case-insensitively.
    return fnmatch.fnmatch(name.lower(), pattern.lower())

def _filter_by_date_selector(
    item_date: datetime.datetime,
    date_selector_str: Optional[str],
    current_time: datetime.datetime
) -> bool:
    # Helper function to filter an item based on a date selector string.
    if not date_selector_str:
        return True
    v_lower = date_selector_str.lower().strip()
    parts = v_lower.split()
    selector_type = parts[0]

    item_date_aware = item_date
    current_time_aware = current_time
    if current_time.tzinfo is None and item_date.tzinfo is not None:
        current_time_aware = current_time.replace(tzinfo=datetime.timezone.utc)
    elif current_time.tzinfo is not None and item_date.tzinfo is None:
        item_date_aware = item_date.replace(tzinfo=datetime.timezone.utc)

    try:
        if selector_type == "olderthandays" and len(parts) == 2 and parts[1].isdigit():
            days = int(parts[1])
            if days < 0: raise ValueError("Days must be non-negative")
            threshold = current_time_aware - datetime.timedelta(days=days)
            return item_date_aware < threshold
        elif selector_type == "newerthandays" and len(parts) == 2 and parts[1].isdigit():
            days = int(parts[1])
            if days < 0: raise ValueError("Days must be non-negative")
            threshold = current_time_aware - datetime.timedelta(days=days)
            return item_date_aware > threshold
        elif selector_type.startswith("between_") and len(parts) == 1:
            date_strings = selector_type.split("_")[1:]
            if len(date_strings) == 2:
                start_date_str, end_date_str = date_strings[0], date_strings[1]
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if start_date > end_date:
                    raise ValueError("Start date must be before or equal to end date.")
                start_dt = datetime.datetime.combine(start_date, datetime.time.min)
                end_dt = datetime.datetime.combine(end_date, datetime.time.max)
                if item_date_aware.tzinfo is not None:
                    start_dt = start_dt.replace(tzinfo=item_date_aware.tzinfo)
                    end_dt = end_dt.replace(tzinfo=item_date_aware.tzinfo)
                return start_dt <= item_date_aware <= end_dt
            else: raise ValueError("Invalid between format. Use between_YYYY-MM-DD_YYYY-MM-DD")
        else: raise ValueError(f"Unrecognized date selector format: '{selector_type}'")
    except ValueError as e:
        log.warning(f"Invalid date format or value in selector '{date_selector_str}': {e}")
        return False

async def _select_input_documents(
    db: AsyncSession,
    definition: ValidatedWorkflowDefinition,
    executing_team_id: PyUUID,
    current_time: datetime.datetime,
    workflow_item_name_for_log: str,
    explicit_input_document_ids: Optional[List[PyUUID]] = None,
    additional_ai_input: Optional[str] = None,
) -> List[str]:
    """Retrieve relevant text snippets for a workflow using the retrieval service."""
    log.debug(
        f"Retrieving snippets for workflow '{workflow_item_name_for_log}' for team {executing_team_id}."
    )

    query_text = definition.prompt
    if additional_ai_input:
        query_text += f"\n{additional_ai_input}"

    try:
        snippets = await get_relevant_snippets(db, query_text, top_k=5)
        log.info(
            f"Retrieved {len(snippets)} snippets for workflow '{workflow_item_name_for_log}'."
        )
        return snippets
    except Exception as exc:  # pragma: no cover - retrieval errors are logged
        log.error(
            f"Error retrieving snippets for workflow '{workflow_item_name_for_log}': {exc}"
        )
        return []

def _construct_prompt(
    definition: ValidatedWorkflowDefinition,
    input_docs_content_list: List[str],
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str,
    additional_ai_input: Optional[str] = None,
    explicit_current_document_content: Optional[str] = None
) -> str:
    # Constructs the final prompt string.
    log.debug(f"Constructing prompt for workflow '{workflow_item_name_for_context}' with {len(input_doc_names_list)} documents, additional input length {len(additional_ai_input or '')}, and explicit content length {len(explicit_current_document_content or '')}.")
    prompt_template = definition.prompt
    document_context_parts = []

    if explicit_current_document_content is not None:
        document_context_parts.append(f"[Current Document Context]\n\n{explicit_current_document_content}")
        log.debug("Using explicit_current_document_content as the primary document context.")
    elif input_docs_content_list:
        for name, content in zip(input_doc_names_list, input_docs_content_list):
            document_context_parts.append(f"[Document: {name}]\n\n{content}")
        log.debug(f"Using content from {len(input_doc_names_list)} selected documents.")

    if additional_ai_input and additional_ai_input.strip():
        log.debug(f"Appending additional AI input (length: {len(additional_ai_input)}) to prompt context.")
        document_context_parts.append(f"[Additional AI Input]\n\n{additional_ai_input.strip()}")

    document_context_str = "\n\n---\n\n".join(document_context_parts) if document_context_parts else "(No input documents or additional AI input provided for this execution)"
    first_input_name = input_doc_names_list[0] if input_doc_names_list else ("Current Document" if explicit_current_document_content is not None else "")
    current_week_number = current_time.isocalendar()[1]
    current_month_name = current_time.strftime("%B")
    current_quarter_number = (current_time.month - 1) // 3 + 1

    replacements = {
        "{{DocumentContext}}": document_context_str, "{{CurrentDate}}": current_time.strftime("%Y-%m-%d"),
        "{{CurrentDate_YYYY-MM-DD}}": current_time.strftime("%Y-%m-%d"), "{{CurrentTime}}": current_time.strftime("%H:%M:%S"),
        "{{Year}}": current_time.strftime("%Y"), "{{Month}}": current_time.strftime("%m"), "{{Day}}": current_time.strftime("%d"),
        "{{InputFileNames}}": ", ".join(input_doc_names_list) if not explicit_current_document_content else first_input_name,
        "{{InputFileCount}}": str(len(input_docs_content_list)) if not explicit_current_document_content else "1",
        "{{InputFileName}}": first_input_name, "{{WorkflowName}}": workflow_item_name_for_context,
        "{{CurrentWeekNumber}}": str(current_week_number), "{{CurrentMonthName}}": current_month_name,
        "{{CurrentQuarterNumber}}": str(current_quarter_number), "{{CurrentYear}}": current_time.strftime("%Y"),
    }
    final_prompt = prompt_template
    for placeholder, value in replacements.items():
        final_prompt = final_prompt.replace(placeholder, str(value))
    if "{{CurrentWeekNumber + 1}}" in final_prompt:
        final_prompt = final_prompt.replace("{{CurrentWeekNumber + 1}}", str(current_week_number + 1))
    log.debug(f"Constructed final prompt snippet: {(final_prompt[:200] + '...') if len(final_prompt) > 200 else final_prompt}")
    return final_prompt

def _apply_placeholder_filters(value_str: str, filters_str: str) -> str:
    # Applies filters to placeholder values.
    current_value = value_str
    filters = [f.strip() for f in filters_str.split('|')]
    for f_def in filters:
        filter_parts = f_def.split(":", 1)
        filter_name = filter_parts[0].strip()
        args_str = filter_parts[1] if len(filter_parts) > 1 else ""
        try:
            if filter_name == "replace":
                args = [arg.strip().strip("'").strip('"') for arg in args_str.split("','", 1)]
                if len(args) == 2: current_value = current_value.replace(args[0], args[1])
                else:
                    args = [arg.strip().strip("'").strip('"') for arg in args_str.split(",", 1)]
                    if len(args) == 2: current_value = current_value.replace(args[0], args[1])
                    else: log.warning(f"Replace filter expects 2 arguments, got: {args_str}")
            elif filter_name == "truncate": current_value = current_value[:int(args_str.strip())]
            elif filter_name == "regex_replace":
                args = [arg.strip().strip("'").strip('"') for arg in args_str.split("','", 1)]
                if len(args) == 2: current_value = re.sub(args[0], args[1], current_value)
                else: log.warning(f"Regex_replace filter expects 2 arguments, got: {args_str}")
            else: log.warning(f"Unsupported filter: {filter_name}")
        except Exception as e: log.warning(f"Could not apply filter '{f_def}' to value '{current_value}': {e}")
    return current_value

def _generate_output_name(
    definition: ValidatedWorkflowDefinition, input_doc_names_list: List[str], current_time: datetime.datetime,
    workflow_item_name_for_context: str, explicit_current_document_name_seed: Optional[str] = None
) -> str:
    # Generates the output document name.
    log.debug(f"Generating output name for workflow '{workflow_item_name_for_context}' using template '{definition.outputName}'")
    name_template = definition.outputName
    first_input_name_base = explicit_current_document_name_seed if explicit_current_document_name_seed else (input_doc_names_list[0] if input_doc_names_list else "")
    current_week_number = current_time.isocalendar()[1]
    current_month_name = current_time.strftime("%B")
    current_quarter_number = (current_time.month - 1) // 3 + 1
    base_values = {
        "Year": current_time.strftime("%Y"), "Month": current_time.strftime("%m"), "Day": current_time.strftime("%d"),
        "InputFileName": first_input_name_base, "WorkflowName": workflow_item_name_for_context,
        "CurrentDate_YYYY-MM-DD": current_time.strftime("%Y-%m-%d"), "CurrentWeekNumber": str(current_week_number),
        "CurrentMonthName": current_month_name, "CurrentQuarterNumber": str(current_quarter_number),
        "CurrentYear": current_time.strftime("%Y"),
    }
    output_name = name_template
    def replace_advanced_placeholders(match):
        full_match_placeholder, expression = match.group(0), match.group(1).strip()
        if expression == "CurrentWeekNumber + 1": return str(current_week_number + 1)
        if '|' in expression:
            var_name, filters_str = [p.strip() for p in expression.split('|', 1)]
            if var_name in base_values: return _apply_placeholder_filters(base_values[var_name], filters_str)
            log.warning(f"Variable '{var_name}' not found for outputName filter."); return full_match_placeholder
        if expression in base_values: return base_values[expression]
        log.warning(f"Placeholder '{{{{{expression}}}}}' not recognized."); return full_match_placeholder
    output_name = re.sub(r"\{\{(.*?)\}\}", replace_advanced_placeholders, output_name)
    output_name = re.sub(r'[<>:"/\\|?*]', '_', output_name)
    output_name = re.sub(r'\s+', '_', output_name)
    output_name = re.sub(r'_+', '_', output_name).strip('_')
    log.debug(f"Generated output name: '{output_name}'")
    return output_name

async def _ensure_unique_output_name(db: AsyncSession, base_name: str, team_id: PyUUID) -> str:
    # Ensures the output document name is unique.
    log.debug(f"Ensuring unique name for base '{base_name}' in team {team_id}")
    name_candidate, counter = base_name, 0
    name_root, dot, name_ext = base_name.rpartition('.')
    if not dot: name_root, name_ext = base_name, ""
    else: name_ext = dot + name_ext
    while True:
        if await crud_content_item.content_item.check_name_uniqueness(db, name=name_candidate, item_type=ContentItemTypeEnum.DOCUMENT, team_id=team_id):
            log.debug(f"Final unique name: '{name_candidate}'"); return name_candidate
        counter += 1; name_candidate = f"{name_root}_{counter}{name_ext}"
        if counter > MAX_UNIQUE_NAME_ATTEMPTS:
            log.error(f"Could not find unique name for base '{base_name}' after {MAX_UNIQUE_NAME_ATTEMPTS} attempts.")
            raise ValueError(f"Could not generate a unique output name for '{base_name}'. Max attempts reached.")

async def execute_workflow_streaming(
    db: AsyncSession, workflow_item: ContentItem, executing_team_id: PyUUID,
    explicit_input_document_ids: Optional[List[PyUUID]] = None,
    explicit_additional_ai_input: Optional[str] = None,
    explicit_current_document_content: Optional[str] = None,
    explicit_current_document_name_seed: Optional[str] = "CurrentDocument"
) -> AsyncIterator[str]:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    actual_process_workflow_name = workflow_item.name
    log.info(f"Executing workflow '{actual_process_workflow_name}' (ID: {workflow_item.item_id}) for team {executing_team_id} at {current_time}")

    if not workflow_item.current_version:
        log.error(f"Workflow execution aborted: Item '{actual_process_workflow_name}' ({workflow_item.item_id}) has no current version.")
        yield f"{ULACM_STREAM_END_TOKEN}{json.dumps({'error': 'Workflow item has no current version to execute.'}, default=pydantic_encoder)}"
        return

    workflow_definition_str = workflow_item.current_version.markdown_content
    accumulated_llm_chunks: List[str] = []

    try:
        log.debug(f"Parsing workflow definition for '{actual_process_workflow_name}' ({workflow_item.item_id})")
        definition = WorkflowDefinitionParser.parse_and_validate(workflow_definition_str)
        if not definition.processWorkFlowName: definition.processWorkFlowName = actual_process_workflow_name

        retrieved_snippets: List[str] = []
        if explicit_current_document_content is None:
            retrieved_snippets = await _select_input_documents(
                db=db,
                definition=definition,
                executing_team_id=executing_team_id,
                current_time=current_time,
                workflow_item_name_for_log=actual_process_workflow_name,
                explicit_input_document_ids=explicit_input_document_ids,
                additional_ai_input=explicit_additional_ai_input,
            )

        input_docs_content_list = retrieved_snippets
        input_doc_names_list = [f"Snippet_{i+1}" for i in range(len(retrieved_snippets))]

        final_prompt = _construct_prompt(
            definition, input_docs_content_list, input_doc_names_list, current_time,
            definition.processWorkFlowName, explicit_additional_ai_input, explicit_current_document_content
        )

        log.info(f"Streaming request to Ollama for workflow '{actual_process_workflow_name}' (Item ID: {workflow_item.item_id})")
        async for llm_chunk in ollama_service_instance.generate_stream(prompt=final_prompt):
            accumulated_llm_chunks.append(llm_chunk)
            yield llm_chunk

        raw_llm_response = "".join(accumulated_llm_chunks)
        # Remove <think> tags from the full response before saving
        cleaned_llm_response = _remove_think_tags(raw_llm_response)
        log.info(f"Finished streaming from Ollama for workflow {workflow_item.item_id}. Raw length: {len(raw_llm_response)}, Cleaned length: {len(cleaned_llm_response)}")

        raw_output_name = _generate_output_name(
            definition, input_doc_names_list, current_time, definition.processWorkFlowName,
            explicit_current_document_name_seed if explicit_current_document_content is not None else None
        )

        stmt_existing_output = select(ContentItem).where(
            ContentItem.name == raw_output_name, ContentItem.team_id == executing_team_id, ContentItem.item_type == ContentItemTypeEnum.DOCUMENT
        ).options(selectinload(ContentItem.current_version))
        existing_output_document_db = (await db.execute(stmt_existing_output)).scalar_one_or_none()
        output_document_db: ContentItem

        if existing_output_document_db:
            log.info(f"Workflow '{actual_process_workflow_name}' output document '{raw_output_name}' exists. Appending new version with cleaned content.")
            output_document_db = existing_output_document_db
            output_version_payload = ContentVersionCreate(markdown_content=cleaned_llm_response) # Use cleaned response
            await crud_content_version.content_version.create_new_version(
                 db=db,
                 item_id=output_document_db.item_id,
                 version_in=output_version_payload,
                 saved_by_team_id=executing_team_id,
                 is_initial_version=False
            )
            await db.refresh(output_document_db, attribute_names=["current_version_id", "updated_at", "current_version"])
        else:
            unique_output_name = await _ensure_unique_output_name(db, raw_output_name, executing_team_id)
            output_item_create_payload = ContentItemCreateSchema(name=unique_output_name, item_type=ContentItemTypeEnum.DOCUMENT)
            temp_output_document_db_after_create = await crud_content_item.content_item.create_item_for_team_or_admin(
                db=db,
                obj_in=output_item_create_payload,
                actor_team_id=executing_team_id,
                is_admin_actor=False
            )
            output_document_db = await crud_content_item.content_item.get_by_id(db, item_id=temp_output_document_db_after_create.item_id)
            if not output_document_db:
                 log.error(f"Critical: Failed to re-fetch newly created output document {temp_output_document_db_after_create.item_id} for workflow '{actual_process_workflow_name}'.")
                 raise ValueError("Failed to retrieve newly created output document for version update.")
            if output_document_db.current_version_id and output_document_db.current_version:
                log.info(f"Updating initial version {output_document_db.current_version.version_id} for new output document {output_document_db.item_id} ('{unique_output_name}') with cleaned LLM content.")
                stmt_update_version = (
                    sqlalchemy_update(ContentVersion)
                    .where(ContentVersion.version_id == output_document_db.current_version_id)
                    .values(markdown_content=cleaned_llm_response, saved_by_team_id=executing_team_id) # Use cleaned response
                    .execution_options(synchronize_session=False)
                )
                await db.execute(stmt_update_version)
                await db.refresh(output_document_db.current_version, attribute_names=["markdown_content", "saved_by_team_id"])
            else:
                log.error(f"Newly created output document {output_document_db.item_id} ('{unique_output_name}') does not have current_version_id or current_version. Cannot save LLM content.")
                raise ValueError("Failed to establish initial version details for output document.")
            log.info(f"New output document '{unique_output_name}' (ID: {output_document_db.item_id}) created for workflow '{actual_process_workflow_name}'.")

        await db.commit()

        await db.refresh(output_document_db, attribute_names=['current_version', 'owner_team'])
        if output_document_db.current_version:
             stmt_load_saving_team = select(ContentVersion).options(joinedload(ContentVersion.saving_team)).where(ContentVersion.version_id == output_document_db.current_version.version_id)
             loaded_version = (await db.execute(stmt_load_saving_team)).scalar_one_or_none()
             if loaded_version: output_document_db.current_version = loaded_version

        # The output_document in the final JSON payload should reflect the cleaned content
        # that was actually saved.
        if output_document_db.current_version:
            output_document_db.current_version.markdown_content = cleaned_llm_response

        output_doc_response_schema = WorkflowExecutionOutputDocument.model_validate(output_document_db)
        final_data_payload = {
            "message": "Workflow executed successfully.",
            "output_document": output_doc_response_schema.model_dump(exclude_none=True),
        }
        yield f"{ULACM_STREAM_END_TOKEN}{json.dumps(final_data_payload, default=pydantic_encoder)}"

    except (WorkflowParsingError, OllamaServiceError, ValueError) as e:
        log.exception(f"Controlled error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        await db.rollback()
        yield f"{ULACM_STREAM_END_TOKEN}{json.dumps({'error': str(e)}, default=pydantic_encoder)}"
    except Exception as e:
        log.exception(f"Unexpected error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        await db.rollback()
        yield f"{ULACM_STREAM_END_TOKEN}{json.dumps({'error': f'An unexpected error occurred: {str(e)}'}, default=pydantic_encoder)}"
