# File: ulacm_backend/app/api/v1/endpoints/workflows_exec.py
# Purpose: API endpoint for executing Process Workflows.
# Updated: Endpoint now accepts optional input_document_ids in the request body.
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from uuid import UUID as PyUUID
from typing import Union, List, Optional # Added List, Optional

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItem as ContentItemModel, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.api.v1.deps import get_current_team_user # Specific dep for this team-only endpoint
from app.crud import crud_content_item
from app.services import workflow_service, OllamaServiceError, WorkflowParsingError
from app.schemas.workflow_definition import RunWorkflowResponse, RunWorkflowPayload # Added RunWorkflowPayload
from app.schemas.content_item import ContentItemWithCurrentVersion
from app.core.config import settings

log = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/{workflow_item_id}/run",
    response_model=RunWorkflowResponse,
    summary="Run Process Workflow (Team User Endpoint)"
)
async def run_process_workflow(
    request: Request,
    workflow_item_id: PyUUID = Path(..., description="The ID of the Process Workflow to execute"),
    payload: Optional[RunWorkflowPayload] = None, # Changed to accept optional payload
    db: AsyncSession = Depends(get_db),
    current_team: TeamModel = Depends(get_current_team_user)
):
    requesting_team_id_for_log = current_team.team_id
    log.info(f"Team ID {requesting_team_id_for_log} requesting execution for workflow ID: {workflow_item_id}")
    if payload and payload.input_document_ids:
        log.info(f"With explicit input document IDs: {payload.input_document_ids}")


    workflow_item_db_obj = await crud_content_item.content_item.get_by_id(db, item_id=workflow_item_id)

    if not workflow_item_db_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found.")

    if not (
        workflow_item_db_obj.item_type == ContentItemTypeEnum.WORKFLOW and
        workflow_item_db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID and
        workflow_item_db_obj.is_globally_visible is True
    ):
        log.warning(f"Team {requesting_team_id_for_log} attempted to run workflow {workflow_item_id} which is not a valid Admin-owned, globally visible workflow.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to run this workflow, or it's not a valid runnable workflow.")

    if not workflow_item_db_obj.current_version_id or not workflow_item_db_obj.current_version:
        log.warning(f"Workflow run failed for team {requesting_team_id_for_log}: Workflow {workflow_item_id} ('{workflow_item_db_obj.name}') has no content (no current version).")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Workflow has no content to execute.")

    try:
        log.info(f"Starting workflow execution for: '{workflow_item_db_obj.name}' ({workflow_item_id}) by team {requesting_team_id_for_log}")

        explicit_input_ids: Optional[List[PyUUID]] = None
        if payload and payload.input_document_ids:
            explicit_input_ids = payload.input_document_ids

        output_document_db, llm_response_text = await workflow_service.execute_workflow(
            db=db,
            workflow_item=workflow_item_db_obj,
            executing_team_id=requesting_team_id_for_log,
            explicit_input_document_ids=explicit_input_ids # Pass the IDs
        )
        await db.commit()
        await db.refresh(output_document_db, attribute_names=['current_version', 'owner_team'])
        if output_document_db.current_version:
            stmt = (
                select(ContentVersion)
                .options(joinedload(ContentVersion.saving_team)) # type: ignore
                .where(ContentVersion.version_id == output_document_db.current_version.version_id) # type: ignore
            )
            result = await db.execute(stmt)
            fully_loaded_current_version = result.scalar_one_or_none()
            if fully_loaded_current_version:
                output_document_db.current_version = fully_loaded_current_version # type: ignore
            else:
                log.warning(f"Could not fully reload current_version with 'saving_team' for output document {output_document_db.item_id}")

        log.info(f"Workflow '{workflow_item_db_obj.name}' ({workflow_item_id}) executed successfully by team {requesting_team_id_for_log}. Output document ID: {output_document_db.item_id}")

        output_doc_response_schema = ContentItemWithCurrentVersion.model_validate(output_document_db)

        return RunWorkflowResponse(
            message="Workflow executed successfully.",
            output_document=output_doc_response_schema,
            llm_raw_response=llm_response_text
        )
    except WorkflowParsingError as wpe:
        await db.rollback()
        log.warning(f"Workflow execution for {workflow_item_id} by team {requesting_team_id_for_log} failed due to parsing error: {wpe}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Workflow definition error: {str(wpe)}")
    except ValueError as ve:
        await db.rollback()
        log.warning(f"Workflow execution for {workflow_item_id} by team {requesting_team_id_for_log} failed due to value error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Workflow execution error: {str(ve)}")
    except OllamaServiceError as ose:
        await db.rollback()
        log.error(f"Ollama service error during workflow execution for {workflow_item_id} by team {requesting_team_id_for_log}: {ose}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Ollama service error: {str(ose)}")
    except Exception as e:
        await db.rollback()
        log.exception(f"Unexpected error during workflow execution for {workflow_item_id} by team {requesting_team_id_for_log}: {type(e).__name__} - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during workflow execution.")
