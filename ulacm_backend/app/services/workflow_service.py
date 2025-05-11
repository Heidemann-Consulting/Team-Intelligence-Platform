# File: ulacm_backend/app/services/workflow_service.py
# Purpose: Service for orchestrating Process Workflow execution.
# Updated: Uses workflow_item.name for processWorkFlowName.
# Updated: Handles a list of inputDocumentSelectors.
# Updated: Changed CRUD imports to break circular dependency.

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
# Changed CRUD imports
from app.crud import crud_content_item # Import the module
from app.crud import crud_content_version # Import the module
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.schemas.content_version import ContentVersionCreate
from app.schemas.content_item import ContentItemCreate as ContentItemCreateSchema

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
    workflow_item_name_for_log: str
) -> List[ContentItem]:
    log.debug(f"Selecting input documents for workflow '{workflow_item_name_for_log}' with selectors '{definition.inputDocumentSelectors}' and date filter '{definition.inputDateSelector}' for team {executing_team_id}")
    stmt = (
        select(ContentItem)
        .where(ContentItem.item_type == ContentItemTypeEnum.DOCUMENT)
        .where(or_(ContentItem.team_id == executing_team_id, ContentItem.is_globally_visible == True))
        .options(joinedload(ContentItem.current_version))
    )
    result = await db.execute(stmt)
    all_accessible_documents = result.scalars().unique().all()

    selected_documents_map: Dict[PyUUID, ContentItem] = {}

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

    selected_documents_list = sorted(list(selected_documents_map.values()), key=lambda d: d.name)
    log.info(f"Found {len(selected_documents_list)} unique input documents for workflow '{workflow_item_name_for_log}' across all selectors.")
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
        "{{WorkflowName}}": workflow_item_name_for_context,
    }
    final_prompt = prompt_template
    for placeholder, value in replacements.items():
        final_prompt = final_prompt.replace(placeholder, str(value))
    log.debug(f"Constructed final prompt snippet: {(final_prompt[:200] + '...') if len(final_prompt) > 200 else final_prompt}")
    return final_prompt

def _generate_output_name(
    definition: ValidatedWorkflowDefinition,
    input_doc_names_list: List[str],
    current_time: datetime.datetime,
    workflow_item_name_for_context: str
) -> str:
    log.debug(f"Generating output name for workflow '{workflow_item_name_for_context}' using template '{definition.outputName}'")
    name_template = definition.outputName
    first_input_name_base = input_doc_names_list[0] if input_doc_names_list else ""

    replacements = {
        "{{Year}}": current_time.strftime("%Y"),
        "{{Month}}": current_time.strftime("%m"),
        "{{Day}}": current_time.strftime("%d"),
        "{{InputFileName}}": first_input_name_base,
        "{{WorkflowName}}": workflow_item_name_for_context,
    }
    output_name = name_template
    for placeholder, value in replacements.items():
        output_name = output_name.replace(placeholder, str(value))

    output_name = re.sub(r'[<>:"/\\|?*]', '_', output_name)
    output_name = re.sub(r'\s+', '_', output_name)
    output_name = re.sub(r'_+', '_', output_name)
    output_name = output_name.strip('_')

    log.debug(f"Generated raw output name: '{output_name}'")
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
        # Use the imported module to access the instance
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
    executing_team_id: PyUUID
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
        definition.processWorkFlowName = actual_process_workflow_name

        selected_input_docs = await _select_input_documents(
            db=db,
            definition=definition,
            executing_team_id=executing_team_id,
            current_time=current_time,
            workflow_item_name_for_log=actual_process_workflow_name
        )
        input_docs_content_list = [doc.current_version.markdown_content for doc in selected_input_docs if doc.current_version]
        input_doc_names_list = [doc.name for doc in selected_input_docs]

        final_prompt = _construct_prompt(
            definition=definition,
            input_docs_content_list=input_docs_content_list,
            input_doc_names_list=input_doc_names_list,
            current_time=current_time,
            workflow_item_name_for_context=actual_process_workflow_name
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
            workflow_item_name_for_context=actual_process_workflow_name
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
            # Use the imported module to access the instance
            await crud_content_version.content_version.create_new_version(
                db=db, item_id=output_document_db.item_id, version_in=output_version_payload,
                saved_by_team_id=executing_team_id, is_initial_version=False
            )
        else:
            unique_output_name = await _ensure_unique_output_name(db, raw_output_name, executing_team_id)

            output_document_db = ContentItem(
                name=unique_output_name,
                item_type=ContentItemTypeEnum.DOCUMENT,
                team_id=executing_team_id,
                is_globally_visible=False
            )
            db.add(output_document_db)
            await db.flush()

            output_version_payload = ContentVersionCreate(markdown_content=llm_response_text)
            # Use the imported module to access the instance
            await crud_content_version.content_version.create_new_version(
                db=db, item_id=output_document_db.item_id, version_in=output_version_payload,
                saved_by_team_id=executing_team_id, is_initial_version=True
            )
            log.info(f"New output document '{unique_output_name}' (ID: {output_document_db.item_id}) created for workflow '{actual_process_workflow_name}'.")

        await db.refresh(output_document_db, attribute_names=['current_version_id', 'updated_at', 'current_version'])
        if output_document_db.current_version:
            await db.refresh(output_document_db.current_version, attribute_names=['saving_team'])

        return output_document_db, llm_response_text

    except (WorkflowParsingError, OllamaServiceError, ValueError) as e:
        log.exception(f"Controlled error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        raise
    except Exception as e:
        log.exception(f"Unexpected error during workflow execution for '{actual_process_workflow_name}' ({workflow_item.item_id}): {e}")
        raise RuntimeError(f"An unexpected error occurred processing workflow '{actual_process_workflow_name}'.") from e
