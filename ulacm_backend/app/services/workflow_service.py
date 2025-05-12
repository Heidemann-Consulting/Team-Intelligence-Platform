# File: ulacm_backend/app/services/workflow_service.py
# Purpose: Service for orchestrating Process Workflow execution.
# Updated: Modified _select_input_documents and execute_workflow to handle explicit_input_document_ids.
# Updated: Enhanced _construct_prompt and _generate_output_name to support additional placeholders
#          and basic string manipulations/arithmetic for outputName.

import logging
import datetime
import re
import fnmatch
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID as PyUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from sqlalchemy import or_, and_

from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition
from app.crud import crud_content_item
from app.crud import crud_content_version
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.schemas.content_version import ContentVersionCreate
from app.schemas.content_item import ContentItemCreate as ContentItemCreateSchema
from app.core.config import settings

log = logging.getLogger(__name__)
__all__ = ["execute_workflow", "OllamaServiceError", "WorkflowParsingError"]

MAX_UNIQUE_NAME_ATTEMPTS = 100

def _match_glob_pattern(name: str, pattern: str) -> bool:
    return fnmatch.fnmatch(name.lower(), pattern.lower())

def _filter_by_date_selector(
    item_date: datetime.datetime,
    date_selector_str: Optional[str],
    current_time: datetime.datetime
) -> bool:
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
                if start_date > end_date: raise ValueError("Start date must be before or equal to end date.")
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
    explicit_input_document_ids: Optional[List[PyUUID]] = None
) -> List[ContentItem]:
    log.debug(f"Selecting input documents for workflow '{workflow_item_name_for_log}' for team {executing_team_id}.")
    log.debug(f"Selectors: '{definition.inputDocumentSelectors}', Date filter: '{definition.inputDateSelector}', Explicit IDs: {explicit_input_document_ids}")

    selected_documents_map: Dict[PyUUID, ContentItem] = {}

    if explicit_input_document_ids:
        log.debug(f"Using explicitly provided document IDs: {explicit_input_document_ids}")
        if not explicit_input_document_ids:
             log.info(f"Workflow '{workflow_item_name_for_log}' will run with no explicit document inputs based on user choice.")
             return []

        stmt = (
            select(ContentItem)
            .where(ContentItem.item_id.in_(explicit_input_document_ids))
            .where(ContentItem.item_type == ContentItemTypeEnum.DOCUMENT)
            .options(
                joinedload(ContentItem.current_version).subqueryload(ContentVersion.saving_team),
                joinedload(ContentItem.owner_team)
            )
        )
        result = await db.execute(stmt)
        potential_docs = result.scalars().unique().all()

        for doc in potential_docs:
            is_accessible = (
                doc.team_id == executing_team_id or
                (doc.is_globally_visible and doc.team_id != settings.ADMIN_SYSTEM_TEAM_ID) or
                (doc.is_globally_visible and doc.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
            )
            if not is_accessible:
                log.warning(f"Document {doc.item_id} ('{doc.name}') was explicitly requested but is not accessible to team {executing_team_id}. Skipping.")
                continue
            if not doc.current_version:
                log.warning(f"Document {doc.item_id} ('{doc.name}') was explicitly requested but has no current version. Skipping.")
                continue
            selected_documents_map[doc.item_id] = doc
        log.info(f"Selected {len(selected_documents_map)} documents from explicitly provided IDs for workflow '{workflow_item_name_for_log}'.")

    else:
        log.debug(f"No explicit IDs provided. Using inputDocumentSelectors for workflow '{workflow_item_name_for_log}'.")
        stmt = (
            select(ContentItem)
            .where(ContentItem.item_type == ContentItemTypeEnum.DOCUMENT)
            .where(
                or_(
                    ContentItem.team_id == executing_team_id,
                    and_(
                        ContentItem.is_globally_visible == True,
                        ContentItem.team_id != settings.ADMIN_SYSTEM_TEAM_ID
                    )
                )
            )
            .options(
                joinedload(ContentItem.current_version).subqueryload(ContentVersion.saving_team),
                joinedload(ContentItem.owner_team)
            )
        )
        result = await db.execute(stmt)
        all_accessible_documents = result.scalars().unique().all()

        for selector_pattern in definition.inputDocumentSelectors:
            log.debug(f"Processing selector pattern: '{selector_pattern}' for workflow '{workflow_item_name_for_log}'")
            for doc in all_accessible_documents:
                if doc.item_id in selected_documents_map:
                    continue
                if not doc.current_version:
                    log.debug(f"Skipping document '{doc.name}' ({doc.item_id}): No current version for pattern '{selector_pattern}'.")
                    continue
                if not _match_glob_pattern(doc.name, selector_pattern):
                    log.debug(f"Skipping document '{doc.name}' ({doc.item_id}): Name does not match pattern '{selector_pattern}'.")
                    continue

                item_date_to_filter = doc.current_version.created_at
                if not _filter_by_date_selector(item_date_to_filter, definition.inputDateSelector, current_time):
                    log.debug(f"Skipping document '{doc.name}' ({doc.item_id}) for pattern '{selector_pattern}': Failed date filter '{definition.inputDateSelector}'. Version date: {item_date_to_filter}")
                    continue
                log.debug(f"Matched document '{doc.name}' ({doc.item_id}) with pattern '{selector_pattern}'.")
                selected_documents_map[doc.item_id] = doc
        log.info(f"Found {len(selected_documents_map)} unique input documents using selectors for workflow '{workflow_item_name_for_log}'.")

    selected_documents_list = sorted(list(selected_documents_map.values()), key=lambda d: d.name)
    if not selected_documents_list and definition.inputDocumentSelectors:
         log.info(f"No input documents matched the criteria for workflow '{workflow_item_name_for_log}' for team {executing_team_id}.")

    return selected_documents_list

def _construct_prompt(
    definition: ValidatedWorkflowDefinition,
    input_docs_content_list: List[str],
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str
) -> str:
    log.debug(f"Constructing prompt for workflow '{workflow_item_name_for_context}' with {len(input_doc_names_list)} inputs.")
    prompt_template = definition.prompt
    document_context_str = "\n\n---\n\n".join(
        f"[Document: {name}]\n\n{content}" for name, content in zip(input_doc_names_list, input_docs_content_list)
    ) if input_docs_content_list else "(No input documents found or provided for this execution)"

    first_input_name = input_doc_names_list[0] if input_doc_names_list else ""

    current_week_number = current_time.isocalendar()[1]
    current_month_name = current_time.strftime("%B")
    current_quarter_number = (current_time.month - 1) // 3 + 1

    replacements = {
        "{{DocumentContext}}": document_context_str,
        "{{CurrentDate}}": current_time.strftime("%Y-%m-%d"),
        "{{CurrentDate_YYYY-MM-DD}}": current_time.strftime("%Y-%m-%d"),
        "{{CurrentTime}}": current_time.strftime("%H:%M:%S"),
        "{{Year}}": current_time.strftime("%Y"),
        "{{Month}}": current_time.strftime("%m"),
        "{{Day}}": current_time.strftime("%d"),
        "{{InputFileNames}}": ", ".join(input_doc_names_list),
        "{{InputFileCount}}": str(len(input_doc_names_list)),
        "{{InputFileName}}": first_input_name,
        "{{WorkflowName}}": workflow_item_name_for_context,
        "{{CurrentWeekNumber}}": str(current_week_number),
        "{{CurrentMonthName}}": current_month_name,
        "{{CurrentQuarterNumber}}": str(current_quarter_number),
        "{{CurrentYear}}": current_time.strftime("%Y"),
    }
    final_prompt = prompt_template
    for placeholder, value in replacements.items():
        final_prompt = final_prompt.replace(placeholder, str(value))

    if "{{CurrentWeekNumber + 1}}" in final_prompt:
        final_prompt = final_prompt.replace("{{CurrentWeekNumber + 1}}", str(current_week_number + 1))

    log.debug(f"Constructed final prompt snippet: {(final_prompt[:200] + '...') if len(final_prompt) > 200 else final_prompt}")
    return final_prompt

def _apply_placeholder_filters(value_str: str, filters_str: str) -> str:
    current_value = value_str
    # Split filters by '|' but be careful not to split inside quotes if arguments have them.
    # For simplicity, assuming filter arguments don't contain '|'.
    filters = [f.strip() for f in filters_str.split('|')]
    for f_def in filters:
        filter_parts = f_def.split(":", 1)
        filter_name = filter_parts[0].strip()
        args_str = filter_parts[1] if len(filter_parts) > 1 else ""

        try:
            if filter_name == "replace":
                # Expects two arguments, separated by a comma. Handles simple quoted strings.
                # Example: replace: 'old_text', 'new_text'
                args = [arg.strip().strip("'").strip('"') for arg in args_str.split("','", 1)] # Split on quote-comma-quote
                if len(args) == 2:
                    current_value = current_value.replace(args[0], args[1])
                else:
                    # Fallback for simpler comma separation if quote-comma-quote fails
                    args = [arg.strip().strip("'").strip('"') for arg in args_str.split(",", 1)]
                    if len(args) == 2:
                         current_value = current_value.replace(args[0], args[1])
                    else:
                        log.warning(f"Replace filter expects 2 arguments, got: {args_str}")

            elif filter_name == "truncate":
                # Expects one integer argument.
                # Example: truncate: 30
                length = int(args_str.strip())
                current_value = current_value[:length]

            elif filter_name == "regex_replace":
                # Expects two arguments: pattern, replacement.
                # Example: regex_replace: 'pattern_string', 'replacement_string'
                args = [arg.strip().strip("'").strip('"') for arg in args_str.split("','", 1)] # Split on quote-comma-quote
                if len(args) == 2:
                    pattern, repl = args
                    current_value = re.sub(pattern, repl, current_value)
                else:
                    log.warning(f"Regex_replace filter expects 2 arguments, got: {args_str}")
            else:
                log.warning(f"Unsupported filter: {filter_name}")
        except Exception as e:
            log.warning(f"Could not apply filter '{f_def}' to value '{current_value}': {e}")
    return current_value


def _generate_output_name(
    definition: ValidatedWorkflowDefinition,
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str
) -> str:
    log.debug(f"Generating output name for workflow '{workflow_item_name_for_context}' using template '{definition.outputName}'")
    name_template = definition.outputName
    first_input_name_base = input_doc_names_list[0] if input_doc_names_list else ""

    current_week_number = current_time.isocalendar()[1]
    current_month_name = current_time.strftime("%B")
    current_quarter_number = (current_time.month - 1) // 3 + 1

    base_values = {
        "Year": current_time.strftime("%Y"),
        "Month": current_time.strftime("%m"),
        "Day": current_time.strftime("%d"),
        "InputFileName": first_input_name_base,
        "WorkflowName": workflow_item_name_for_context,
        "CurrentDate_YYYY-MM-DD": current_time.strftime("%Y-%m-%d"),
        "CurrentWeekNumber": str(current_week_number),
        "CurrentMonthName": current_month_name,
        "CurrentQuarterNumber": str(current_quarter_number),
        "CurrentYear": current_time.strftime("%Y"),
    }

    output_name = name_template

    def replace_advanced_placeholders(match):
        full_match_placeholder = match.group(0)
        expression = match.group(1).strip()

        if expression == "CurrentWeekNumber + 1":
            return str(current_week_number + 1)

        if '|' in expression:
            parts = expression.split('|', 1)
            var_name = parts[0].strip()
            filters_str = parts[1].strip()
            if var_name in base_values:
                val_to_filter = base_values[var_name]
                return _apply_placeholder_filters(val_to_filter, filters_str)
            else:
                log.warning(f"Variable '{var_name}' not found in base_values for outputName template filter.")
                return full_match_placeholder
        elif expression in base_values:
            return base_values[expression]
        else:
            log.warning(f"Placeholder '{{{{{expression}}}}}' not recognized in outputName template.")
            return full_match_placeholder

    output_name = re.sub(r"\{\{(.*?)\}\}", replace_advanced_placeholders, output_name)

    output_name = re.sub(r'[<>:"/\\|?*]', '_', output_name)
    output_name = re.sub(r'\s+', '_', output_name)
    output_name = re.sub(r'_+', '_', output_name)
    output_name = output_name.strip('_')

    log.debug(f"Generated output name: '{output_name}'")
    return output_name


async def _ensure_unique_output_name(db: AsyncSession, base_name: str, team_id: PyUUID) -> str:
    log.debug(f"Ensuring unique name for base '{base_name}' in team {team_id}")
    name_candidate = base_name
    counter = 0
    name_root, dot, name_ext = base_name.rpartition('.')
    if not dot:
        name_root = base_name
        name_ext = ""
    else:
        name_ext = dot + name_ext

    while True:
        is_unique = await crud_content_item.content_item.check_name_uniqueness(
            db, name=name_candidate, item_type=ContentItemTypeEnum.DOCUMENT, team_id=team_id
        )
        if is_unique:
            log.debug(f"Final unique name: '{name_candidate}'")
            return name_candidate
        counter += 1
        name_candidate = f"{name_root}_{counter}{name_ext}"
        if counter > MAX_UNIQUE_NAME_ATTEMPTS:
            log.error(f"Could not find unique name for base '{base_name}' after {MAX_UNIQUE_NAME_ATTEMPTS} attempts.")
            raise ValueError(f"Could not generate a unique output name for '{base_name}'. Max attempts reached.")

async def execute_workflow(
    db: AsyncSession,
    workflow_item: ContentItem,
    executing_team_id: PyUUID,
    explicit_input_document_ids: Optional[List[PyUUID]] = None
) -> Tuple[ContentItem, str]:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    actual_process_workflow_name = workflow_item.name
    log.info(f"Executing workflow '{actual_process_workflow_name}' (ID: {workflow_item.item_id}) for team {executing_team_id} at {current_time}")

    if not workflow_item.current_version:
        log.error(f"Workflow execution aborted: Item '{actual_process_workflow_name}' ({workflow_item.item_id}) has no current version.")
        raise ValueError("Workflow item has no current version to execute.")

    workflow_definition_str = workflow_item.current_version.markdown_content

    try:
        log.debug(f"Parsing workflow definition for '{actual_process_workflow_name}' ({workflow_item.item_id})")
        definition = WorkflowDefinitionParser.parse_and_validate(workflow_definition_str)
        if not definition.processWorkFlowName: # Ensure processWorkFlowName is set for placeholders
            definition.processWorkFlowName = actual_process_workflow_name


        selected_input_docs = await _select_input_documents(
            db=db,
            definition=definition,
            executing_team_id=executing_team_id,
            current_time=current_time,
            workflow_item_name_for_log=actual_process_workflow_name,
            explicit_input_document_ids=explicit_input_document_ids
        )
        input_docs_content_list = [doc.current_version.markdown_content for doc in selected_input_docs if doc.current_version]
        input_doc_names_list = [doc.name for doc in selected_input_docs]

        final_prompt = _construct_prompt(
            definition=definition,
            input_docs_content_list=input_docs_content_list,
            input_doc_names_list=input_doc_names_list,
            current_time=current_time,
            workflow_item_name_for_context=definition.processWorkFlowName # Use the (potentially set) name from definition
        )

        llm_response_text = ""
        try:
            log.info(f"Sending request to Ollama for workflow '{actual_process_workflow_name}' (Item ID: {workflow_item.item_id})")
            llm_response_text = await ollama_service_instance.generate(prompt=final_prompt)
            log.info(f"Received response from Ollama for workflow {workflow_item.item_id}")
        except OllamaServiceError as e:
            log.error(f"Ollama service error during workflow {workflow_item.item_id} ('{actual_process_workflow_name}') execution: {e}")
            raise

        raw_output_name = _generate_output_name(
            definition=definition,
            input_doc_names_list=input_doc_names_list,
            current_time=current_time,
            workflow_item_name_for_context=definition.processWorkFlowName # Use the name from definition
        )

        stmt_existing_output = select(ContentItem).where(
            ContentItem.name == raw_output_name,
            ContentItem.team_id == executing_team_id,
            ContentItem.item_type == ContentItemTypeEnum.DOCUMENT
        ).options(selectinload(ContentItem.current_version))
        result_existing_output = await db.execute(stmt_existing_output)
        existing_output_document_db = result_existing_output.scalar_one_or_none()

        output_document_db: ContentItem

        if existing_output_document_db:
            log.info(f"Workflow '{actual_process_workflow_name}' output document '{raw_output_name}' exists. Updating with new version.")
            output_document_db = existing_output_document_db
            output_version_payload = ContentVersionCreate(markdown_content=llm_response_text)
            await crud_content_version.content_version.create_new_version(
                db=db, item_id=output_document_db.item_id, version_in=output_version_payload,
                saved_by_team_id=executing_team_id, is_initial_version=False
            )
        else:
            unique_output_name = await _ensure_unique_output_name(db, raw_output_name, executing_team_id)
            output_item_create_payload = ContentItemCreateSchema(
                name=unique_output_name,
                item_type=ContentItemTypeEnum.DOCUMENT
            )
            output_document_db = await crud_content_item.content_item.create_item_for_team_or_admin(
                db=db,
                obj_in=output_item_create_payload,
                actor_team_id=executing_team_id,
                is_admin_actor=False
            )
            final_version_payload = ContentVersionCreate(markdown_content=llm_response_text)
            await crud_content_version.content_version.create_new_version(
                db=db,
                item_id=output_document_db.item_id,
                version_in=final_version_payload,
                saved_by_team_id=executing_team_id,
            )
            log.info(f"New output document '{unique_output_name}' (ID: {output_document_db.item_id}) created for workflow '{actual_process_workflow_name}'.")

        await db.refresh(output_document_db, attribute_names=['current_version_id', 'updated_at', 'current_version'])
        if output_document_db.current_version:
            stmt_load_version_team = (
                select(ContentVersion)
                .where(ContentVersion.version_id == output_document_db.current_version_id)
                .options(joinedload(ContentVersion.saving_team))
            )
            loaded_version_with_team = (await db.execute(stmt_load_version_team)).scalar_one_or_none()
            if loaded_version_with_team:
                output_document_db.current_version = loaded_version_with_team

        return output_document_db, llm_response_text

    except (WorkflowParsingError, OllamaServiceError, ValueError) as e:
        log.exception(f"Controlled error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        raise
    except Exception as e:
        log.exception(f"Unexpected error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        raise RuntimeError(f"An unexpected error occurred processing workflow '{actual_process_workflow_name}'.") from e
