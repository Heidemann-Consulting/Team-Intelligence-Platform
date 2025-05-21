# File: ulacm_backend/app/api/v1/endpoints/workflows_exec.py
# Purpose: API endpoint for executing Process Workflows.
# Updated: Payload now includes current_document_content for "Ask AI" feature.
# Modified to use StreamingResponse for the /run endpoint.

import logging
import json # For parsing the final JSON payload from the stream
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from fastapi.responses import StreamingResponse # Added for streaming
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID as PyUUID
from typing import Union, List, Optional, AsyncIterator # Added AsyncIterator

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItem as ContentItemModel, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.api.v1.deps import get_current_team_user # Specific dep for this team-only endpoint

from app.crud import crud_content_item
from app.services import workflow_service, OllamaServiceError, WorkflowParsingError # workflow_service will provide the streaming function
from app.schemas.workflow_definition import RunWorkflowResponse, RunWorkflowPayload # RunWorkflowPayload is now updated
from app.schemas.content_item import ContentItemWithCurrentVersion
from app.core.config import settings

log = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/{workflow_item_id}/run",
    # response_model is tricky for StreamingResponse that yields text then JSON.
    # OpenAPI docs might not perfectly represent this. Client needs to handle mixed stream.
    # response_model=RunWorkflowResponse, # Commenting out as direct model won't match stream
    summary="Run Process Workflow (Team User Endpoint) - Streams Response",
    status_code=status.HTTP_200_OK # The stream itself is OK, errors handled within stream or as final part
)
async def run_process_workflow_streaming( # Renamed for clarity
    request: Request,
    workflow_item_id: PyUUID = Path(..., description="The ID of the Process Workflow to execute"),
    payload: Optional[RunWorkflowPayload] = None, # This will now include current_document_content
    db: AsyncSession = Depends(get_db),
    current_team: TeamModel = Depends(get_current_team_user)
):
    requesting_team_id_for_log = current_team.team_id
    log.info(f"Team ID {requesting_team_id_for_log} requesting streaming execution for workflow ID: {workflow_item_id}")

    explicit_input_ids: Optional[List[PyUUID]] = None
    additional_input_text: Optional[str] = None
    current_doc_content_input: Optional[str] = None
    current_doc_name_seed_input: Optional[str] = "CurrentDocument"

    if payload:
        if payload.input_document_ids:
            explicit_input_ids = payload.input_document_ids
            log.info(f"With explicit input document IDs: {explicit_input_ids}")
        if payload.additional_ai_input:
            additional_input_text = payload.additional_ai_input
            log.info(f"With additional AI input text provided (length: {len(additional_input_text)}).")
        if payload.current_document_content: # Handle new field
            current_doc_content_input = payload.current_document_content
            log.info(f"With explicit current document content provided (length: {len(current_doc_content_input)}).")
            # Use the name of the document being "asked about" as a seed for the output name
            # Assuming the frontend might send this in the payload if applicable.
            # For now, `explicit_current_document_name_seed` defaults to "CurrentDocument"
            # and can be overridden if frontend provides a more specific name in a future payload enhancement.
            # Example: if payload included `current_document_name`, we could use it here.
            # current_doc_name_seed_input = payload.current_document_name or "CurrentDocument"
    else:
        log.info("No payload provided (no explicit document IDs, additional AI input, or current document content).")


    workflow_item_db_obj = await crud_content_item.content_item.get_by_id(db, item_id=workflow_item_id)

    if not workflow_item_db_obj:
        # For non-streaming, we'd raise HTTPException.
        # For streaming, we need to ensure the stream itself communicates this.
        # The service layer's generator should handle this by yielding an error token.
        # Or, we check upfront and return an HTTP error *before* attempting to stream.
        # The latter is cleaner for distinct HTTP errors vs. errors *during* stream.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    if not (
        workflow_item_db_obj.item_type == ContentItemTypeEnum.WORKFLOW and
        workflow_item_db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID and # Or it could be a special system workflow not tied to admin "ownership" in the usual sense
        workflow_item_db_obj.is_globally_visible is True
    ):
        log.warning(f"Team {requesting_team_id_for_log} attempted to run workflow {workflow_item_id} which is not a valid Admin-owned, globally visible workflow.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to run this workflow, or it's not a valid runnable workflow.")

    if not workflow_item_db_obj.current_version_id or not workflow_item_db_obj.current_version:
        log.warning(f"Workflow run failed for team {requesting_team_id_for_log}: Workflow {workflow_item_id} ('{workflow_item_db_obj.name}') has no content (no current version).")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow has no content to execute.")

    async def stream_generator():
        try:
            log.info(f"Starting workflow execution stream for: '{workflow_item_db_obj.name}' ({workflow_item_id}) by team {requesting_team_id_for_log}")
            async for chunk in workflow_service.execute_workflow_streaming( # Use the new streaming service method
                db=db,
                workflow_item=workflow_item_db_obj,
                executing_team_id=requesting_team_id_for_log,
                explicit_input_document_ids=explicit_input_ids,
                explicit_additional_ai_input=additional_input_text,
                explicit_current_document_content=current_doc_content_input, # New arg
                explicit_current_document_name_seed=current_doc_name_seed_input
            ):
                yield chunk # Stream raw text chunks or the final JSON payload
        except WorkflowParsingError as wpe:
            log.warning(f"Workflow execution stream for {workflow_item_id} by team {requesting_team_id_for_log} failed due to parsing error: {wpe}")
            # Yield a final error message in the stream
            yield f"{workflow_service.ULACM_STREAM_END_TOKEN}{json.dumps({'error': f'Workflow definition error: {str(wpe)}'})}"
        except ValueError as ve:
            log.warning(f"Workflow execution stream for {workflow_item_id} by team {requesting_team_id_for_log} failed due to value error: {ve}")
            yield f"{workflow_service.ULACM_STREAM_END_TOKEN}{json.dumps({'error': f'Workflow execution error: {str(ve)}'})}"
        except OllamaServiceError as ose:
            log.error(f"Ollama service error during workflow execution stream for {workflow_item_id} by team {requesting_team_id_for_log}: {ose}")
            yield f"{workflow_service.ULACM_STREAM_END_TOKEN}{json.dumps({'error': f'Ollama service error: {str(ose)}'})}"
        except Exception as e:
            log.exception(f"Unexpected error during workflow execution stream for {workflow_item_id} by team {requesting_team_id_for_log}: {type(e).__name__} - {e}")
            yield f"{workflow_service.ULACM_STREAM_END_TOKEN}{json.dumps({'error': 'An unexpected error occurred during workflow execution.'})}"
            # Do not raise HTTPException from within the stream generator as it won't be handled correctly.
            # The error is communicated as the last part of the stream.

    return StreamingResponse(stream_generator(), media_type="text/plain") # Media type can be text/event-stream for SSE
