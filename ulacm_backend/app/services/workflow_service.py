# File: ulacm_backend/app/services/workflow_service.py
# Purpose: Service for orchestrating Process Workflow execution.
# Updated: Uses workflow_item.name for processWorkFlowName.

import logging
import datetime
import re
import fnmatch
from typing import List, Tuple, Optional, Dict, Any
from uuid import UUID as PyUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import or_

from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition
from app.crud import content_item, content_version
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.schemas.content_version import ContentVersionCreate

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
    # processWorkFlowName is now taken from workflow_item.name directly where this function is called
    db: AsyncSession,
    definition: ValidatedWorkflowDefinition,
    executing_team_id: PyUUID,
    current_time: datetime.datetime,
    workflow_item_name_for_log: str # Added for logging context
) -> List[ContentItem]:
    log.debug(f"Selecting input documents for workflow '{workflow_item_name_for_log}' with pattern '{definition.inputDocumentSelector}' and date filter '{definition.inputDateSelector}' for team {executing_team_id}")
    stmt = (
        select(ContentItem)
        .where(ContentItem.item_type == ContentItemTypeEnum.DOCUMENT)
        .where(or_(ContentItem.team_id == executing_team_id, ContentItem.is_globally_visible == True))
        .options(joinedload(ContentItem.current_version))
    )
    result = await db.execute(stmt)
    all_accessible_documents = result.scalars().unique().all()
    selected_documents: List[ContentItem] = []
    for doc in all_accessible_documents:
        if not doc.current_version:
            log.debug(f"Skipping document '{doc.name}' ({doc.item_id}): No current version.")
            continue
        if not _match_glob_pattern(doc.name, definition.inputDocumentSelector):
            log.debug(f"Skipping document '{doc.name}' ({doc.item_id}): Name does not match pattern '{definition.inputDocumentSelector}'.")
            continue
        item_date_to_filter = doc.current_version.created_at
        if not _filter_by_date_selector(item_date_to_filter, definition.inputDateSelector, current_time):
            log.debug(f"Skipping document '{doc.name}' ({doc.item_id}): Failed date filter '{definition.inputDateSelector}'. Version date: {item_date_to_filter}")
            continue
        selected_documents.append(doc)
    selected_documents.sort(key=lambda d: d.name)
    log.info(f"Found {len(selected_documents)} input documents for workflow '{workflow_item_name_for_log}'")
    return selected_documents

def _construct_prompt(
    # processWorkFlowName is now taken from workflow_item.name directly where this function is called
    definition: ValidatedWorkflowDefinition,
    input_docs_content_list: List[str],
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str # Added for {{WorkflowName}} placeholder
) -> str:
    log.debug(f"Constructing prompt for workflow '{workflow_item_name_for_context}' with {len(input_doc_names_list)} inputs.")
    prompt_template = definition.prompt
    document_context_str = "\n\n---\n\n".join(
        f"[Document: {name}]\n\n{content}" for name, content in zip(input_doc_names_list, input_docs_content_list)
    ) if input_docs_content_list else "(No input documents found)"
    first_input_name = input_doc_names_list[0] if input_doc_names_list else ""
    replacements = {
        "{{DocumentContext}}": document_context_str,
        "{{CurrentDate}}": current_time.strftime("%Y-%m-%d"),
        "{{CurrentTime}}": current_time.strftime("%H:%M:%S"),
        "{{Year}}": current_time.strftime("%Y"),
        "{{Month}}": current_time.strftime("%m"),
        "{{Day}}": current_time.strftime("%d"),
        "{{InputFileNames}}": ", ".join(input_doc_names_list),
        "{{InputFileCount}}": str(len(input_doc_names_list)),
        "{{InputFileName}}": first_input_name,
        "{{WorkflowName}}": workflow_item_name_for_context, # Use the passed item name
    }
    final_prompt = prompt_template
    for placeholder, value in replacements.items():
        final_prompt = final_prompt.replace(placeholder, str(value))
    log.debug(f"Constructed final prompt snippet: {(final_prompt[:200] + '...') if len(final_prompt) > 200 else final_prompt}")
    return final_prompt

def _generate_output_name(
    # processWorkFlowName is now taken from workflow_item.name directly where this function is called
    definition: ValidatedWorkflowDefinition,
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str # Added for {{WorkflowName}} placeholder
) -> str:
    log.debug(f"Generating output name for workflow '{workflow_item_name_for_context}' using template '{definition.outputName}'")
    name_template = definition.outputName
    first_input_name_base = input_doc_names_list[0] if input_doc_names_list else ""
    replacements = {
        "{{Year}}": current_time.strftime("%Y"),
        "{{Month}}": current_time.strftime("%m"),
        "{{Day}}": current_time.strftime("%d"),
        "{{InputFileName}}": first_input_name_base,
        "{{WorkflowName}}": workflow_item_name_for_context, # Use the passed item name
    }
    output_name = name_template
    for placeholder, value in replacements.items():
        output_name = output_name.replace(placeholder, str(value))
    output_name = re.sub(r'[<>:"/\\|?*]', '_', output_name)
    output_name = re.sub(r'_+', '_', output_name)
    log.debug(f"Generated raw output name: '{output_name}'")
    return output_name

async def _ensure_unique_output_name(db: AsyncSession, base_name: str, team_id: PyUUID) -> str:
    # (This function remains unchanged as its logic is independent of processWorkFlowName source)
    log.debug(f"Ensuring unique name for base '{base_name}' in team {team_id}")
    name_candidate = base_name
    counter = 0
    name_parts = base_name.rsplit('.', 1)
    name_root = name_parts[0]
    name_ext = f".{name_parts[1]}" if len(name_parts) > 1 else ""
    while True:
        is_unique = await content_item.check_name_uniqueness(
            db, name=name_candidate, item_type=ContentItemTypeEnum.DOCUMENT, team_id=team_id
        )
        if is_unique:
            log.debug(f"Final unique name: '{name_candidate}'")
            return name_candidate
        counter += 1
        name_candidate = f"{name_root}_{counter}{name_ext}"
        if counter > MAX_UNIQUE_NAME_ATTEMPTS:
             log.error(f"Could not find unique name for base '{base_name}' after {MAX_UNIQUE_NAME_ATTEMPTS} attempts.")
             raise ValueError(f"Could not generate a unique output name for '{base_name}'.")

async def execute_workflow(
    db: AsyncSession,
    workflow_item: ContentItem, # This is the ContentItem ORM model for the workflow
    executing_team_id: PyUUID
) -> Tuple[ContentItem, str]:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    # Use workflow_item.name as the authoritative processWorkFlowName
    actual_process_workflow_name = workflow_item.name
    log.info(f"Executing workflow '{actual_process_workflow_name}' (ID: {workflow_item.item_id}) for team {executing_team_id} at {current_time}")

    if not workflow_item.current_version:
        log.error(f"Workflow execution aborted: Item '{actual_process_workflow_name}' ({workflow_item.item_id}) has no current version.")
        raise ValueError("Workflow item has no current version to execute.")

    workflow_definition_str = workflow_item.current_version.markdown_content

    try:
        log.debug(f"Parsing workflow definition for '{actual_process_workflow_name}' ({workflow_item.item_id})")
        definition = WorkflowDefinitionParser.parse_and_validate(workflow_definition_str)

        # If processWorkFlowName was in the YAML, it's in definition.processWorkFlowName.
        # If not, definition.processWorkFlowName is None (because it's Optional in schema).
        # We will consistently use workflow_item.name for logging and placeholder replacement.
        if definition.processWorkFlowName and definition.processWorkFlowName != actual_process_workflow_name:
            log.warning(f"Workflow definition for item '{actual_process_workflow_name}' contains a 'processWorkFlowName' ('{definition.processWorkFlowName}'). This field is now ignored; using the item's name instead.")

        # Override or set it for clarity within the definition object if needed,
        # though helper functions will receive workflow_item.name directly.
        definition.processWorkFlowName = actual_process_workflow_name


        selected_input_docs = await _select_input_documents(
            db=db,
            definition=definition,
            executing_team_id=executing_team_id,
            current_time=current_time,
            workflow_item_name_for_log=actual_process_workflow_name # Pass for logging
        )
        input_docs_content_list = [doc.current_version.markdown_content for doc in selected_input_docs if doc.current_version]
        input_doc_names_list = [doc.name for doc in selected_input_docs]

        final_prompt = _construct_prompt(
            definition=definition,
            input_docs_content_list=input_docs_content_list,
            input_doc_names_list=input_doc_names_list,
            current_time=current_time,
            workflow_item_name_for_context=actual_process_workflow_name # Pass for {{WorkflowName}}
        )

        llm_response_text = ""
        try:
            log.info(f"Sending request to Ollama for workflow '{actual_process_workflow_name}' (Item ID: {workflow_item.item_id})")
            llm_response_text = await ollama_service_instance.generate(prompt=final_prompt)
            log.info(f"Received response from Ollama for workflow {workflow_item.item_id}")
        except OllamaServiceError as e:
            log.error(f"Ollama service error during workflow {workflow_item.item_id} ('{actual_process_workflow_name}') execution: {e}")
            raise # Re-raise to be caught by the outer try-except

        raw_output_name = _generate_output_name(
            definition=definition,
            input_doc_names_list=input_doc_names_list,
            current_time=current_time,
            workflow_item_name_for_context=actual_process_workflow_name # Pass for {{WorkflowName}}
        )

        stmt = select(ContentItem).where(
            ContentItem.name == raw_output_name,
            ContentItem.team_id == executing_team_id,
            ContentItem.item_type == ContentItemTypeEnum.DOCUMENT
        ).options(selectinload(ContentItem.current_version))
        result = await db.execute(stmt)
        existing_output_document_db = result.scalar_one_or_none()

        output_document_db: ContentItem
        if existing_output_document_db:
            log.info(f"Workflow '{actual_process_workflow_name}' output document '{raw_output_name}' exists. Updating with new version.")
            output_document_db = existing_output_document_db
            output_version_payload = ContentVersionCreate(markdown_content=llm_response_text)
            await content_version.create_new_version(
                db=db, item_id=output_document_db.item_id, version_in=output_version_payload,
                saved_by_team_id=executing_team_id, is_initial_version=False
            )
        else:
            unique_output_name = await _ensure_unique_output_name(db, raw_output_name, executing_team_id)
            output_document_db = ContentItem(
                name=unique_output_name, item_type=ContentItemTypeEnum.DOCUMENT,
                team_id=executing_team_id, is_globally_visible=False
            )
            db.add(output_document_db)
            await db.flush()
            output_version_payload = ContentVersionCreate(markdown_content=llm_response_text)
            await content_version.create_new_version(
                db=db, item_id=output_document_db.item_id, version_in=output_version_payload,
                saved_by_team_id=executing_team_id, is_initial_version=True
            )
            log.info(f"New output document '{unique_output_name}' (ID: {output_document_db.item_id}) created for workflow '{actual_process_workflow_name}'.")

        await db.refresh(output_document_db, attribute_names=['current_version_id', 'updated_at', 'current_version'])
        if output_document_db.current_version:
             await db.refresh(output_document_db.current_version, attribute_names=['saving_team'])
        return output_document_db, llm_response_text

    except (WorkflowParsingError, OllamaServiceError, ValueError) as e:
        log.exception(f"Error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        await db.rollback()
        raise
    except Exception as e: # Catch any other unexpected errors
        log.exception(f"Unexpected error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        await db.rollback()
        # Raise a more generic error or re-raise if appropriate
        raise RuntimeError(f"An unexpected error occurred processing workflow '{actual_process_workflow_name}'.") from e
