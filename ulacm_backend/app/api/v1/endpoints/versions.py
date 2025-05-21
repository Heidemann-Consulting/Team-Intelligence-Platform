# File: ulacm_backend/app/api/v1/endpoints/versions.py
# Purpose: API endpoints for managing ContentVersions.
# Updated for Option 3 (Admin System Team):
# - Versions of Admin-owned Templates/Workflows are saved by ADMIN_SYSTEM_TEAM_ID.
# - Access control to versioning endpoints based on item type and user role.
# Modification: Ensure SaveVersionResponse returns the newest version data.
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from uuid import UUID as PyUUID
from datetime import datetime, timezone

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItem as ContentItemModel, ContentItemTypeEnum
from app.api.v1.deps import (
    get_current_user_or_admin_marker,
    get_requesting_user_is_admin,
    # ensure_admin_user # Not directly used in this specific version of file, but good for other admin-only routes
)
from app.crud import crud_content_item, crud_content_version
from app.schemas import (
    ContentVersionDetails,
    ContentVersionListResponse,
    VersionMeta,
    ContentVersionCreate as ContentVersionCreateSchema,
    SaveVersionResponse,
    TokenPayload # For type checking admin user
)
# from app.schemas.content_version import ContentVersionCreate # Ensure this specific schema is available if used
from app.core.config import settings # For ADMIN_SYSTEM_TEAM_ID

log = logging.getLogger(__name__)
router = APIRouter()

async def get_item_and_check_versioning_permission(
    item_id: PyUUID,
    db: AsyncSession,
    current_user_session: Union[TeamModel, TokenPayload, None],
    is_admin_actor: bool,
    write_access_needed: bool # True if saving a new version
) -> ContentItemModel:
    """
    Helper to fetch an item and check if the current actor (admin or team)
    has permission to perform versioning operations (read or write) on it.
    """
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    item = await crud_content_item.content_item.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")

    actor_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    action = "manage versions for" if write_access_needed else "view versions of"

    can_perform_action = False
    if is_admin_actor:
        # Admins can version their own T/W (owned by ADMIN_SYSTEM_TEAM_ID)
        if item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and item.team_id == settings.ADMIN_SYSTEM_TEAM_ID:
            can_perform_action = True
        # Admins can version any Document (versions saved under doc owner's team_id or ADMIN_SYSTEM_TEAM_ID if admin is the one editing)
        # For simplicity and current model: if admin saves a doc version, it's attributed to ADMIN_SYSTEM_TEAM_ID.
        elif item.item_type == ContentItemTypeEnum.DOCUMENT:
             can_perform_action = True # Admin can view/save versions of any document
    elif actor_team_id: # Team user
        if item.item_type == ContentItemTypeEnum.DOCUMENT and item.team_id == actor_team_id:
            can_perform_action = True # Teams can version their own documents
        # Teams cannot directly version Templates/Workflows via these endpoints.
    if not can_perform_action:
        log.warning(f"User (Admin: {is_admin_actor}, TeamID: {actor_team_id}) cannot {action} item {item_id} (Type: {item.item_type}, Owner: {item.team_id})")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to {action} this item.")

    return item


@router.post(
    "/{item_id}/versions",
    response_model=SaveVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save New Version of Content Item"
)
async def save_new_version_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to save a new version for"),
    version_in: ContentVersionCreateSchema = ...,
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    item = await get_item_and_check_versioning_permission(item_id, db, current_user_session, is_admin_actor, write_access_needed=True)

    actor_team_id_for_save: PyUUID
    if is_admin_actor:
        actor_team_id_for_save = settings.ADMIN_SYSTEM_TEAM_ID
    elif isinstance(current_user_session, TeamModel) and item.item_type == ContentItemTypeEnum.DOCUMENT and item.team_id == current_user_session.team_id:
        actor_team_id_for_save = current_user_session.team_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Version saving not permitted for this user/item type.")

    log_actor = "Admin (as System)" if is_admin_actor else f"Team {actor_team_id_for_save}"
    log.info(f"{log_actor} saving new version for item ID: {item_id} (Type: {item.item_type})")

    if item.item_type == ContentItemTypeEnum.WORKFLOW:
        from app.services.workflow_parser import validate_workflow_definition_string, WorkflowParsingError
        try:
            validate_workflow_definition_string(version_in.markdown_content)
        except WorkflowParsingError as e:
            log.warning(f"Save version failed for workflow item {item_id} due to invalid definition: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Process Workflow definition: {str(e)}")

    try:
        new_version_db = await crud_content_version.content_version.create_new_version(
            db=db, item_id=item.item_id, version_in=version_in, saved_by_team_id=actor_team_id_for_save
        )
        await db.commit()

        # Fetch the item again to get its latest updated_at timestamp and other potentially changed direct attributes.
        # The primary goal here is to get the correct item_updated_at.
        # We will use new_version_db directly for the new_version details to ensure accuracy.
        updated_item_meta = await crud_content_item.content_item.get_by_id(db, item_id=item.item_id)

        final_item_id_for_response = item.item_id
        final_item_name_for_log = item.name # Original name for logging context
        final_item_updated_at_for_response = datetime.now(timezone.utc) # Default if fetch fails

        if updated_item_meta:
            final_item_id_for_response = updated_item_meta.item_id
            final_item_name_for_log = updated_item_meta.name
            final_item_updated_at_for_response = updated_item_meta.updated_at
        else:
            # This case should be rare if the item existed to begin with.
            log.warning(
                f"Could not re-fetch ContentItem {item.item_id} metadata after version save. "
                f"Using original item ID and name for logging, and new version's creation time for item_updated_at."
            )
            # Use new_version_db.created_at as it's the most relevant timestamp for the "update"
            final_item_updated_at_for_response = new_version_db.created_at


        log.info(
            f"Successfully saved version {new_version_db.version_number} (ID: {new_version_db.version_id}) "
            f"for item {final_item_id_for_response} ('{final_item_name_for_log}')"
        )

        # Construct the response using the new_version_db directly for the 'new_version' field.
        # This ensures the frontend receives the content and details of the version that was just saved.
        return SaveVersionResponse(
            item_id=final_item_id_for_response,
            new_version=ContentVersionDetails.model_validate(new_version_db),
            item_updated_at=final_item_updated_at_for_response
        )

    except ValueError as ve: # From create_new_version if item not found or other validation
        await db.rollback()
        log.warning(f"Error saving new version for item {item_id}: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        await db.rollback()
        log.exception(f"Unexpected error saving new version for item {item_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save new version.")


@router.get(
    "/{item_id}/versions",
    response_model=ContentVersionListResponse,
    summary="List Versions of a Content Item"
)
async def list_item_versions_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to list versions for"),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_order: str = Query("desc", enum=["asc", "desc"], description="Sort order for version_number ('asc' or 'desc')"),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    item = await get_item_and_check_versioning_permission(item_id, db, current_user_session, is_admin_actor, write_access_needed=False)

    log_actor = "Admin" if is_admin_actor else f"Team {current_user_session.team_id if isinstance(current_user_session, TeamModel) else None}" # type: ignore
    log.info(f"{log_actor} requesting version history for item ID: {item_id}")

    versions_db, total_count = await crud_content_version.content_version.get_versions_for_item(
        db, item_id=item.item_id, skip=offset, limit=limit, sort_order=sort_order # type: ignore
    )
    log.info(f"Returning {len(versions_db)} versions out of {total_count} for item {item_id} ('{item.name}')") # type: ignore
    version_metas = [VersionMeta.model_validate(v_db) for v_db in versions_db]
    return ContentVersionListResponse(
        total_count=total_count, item_id=item.item_id, offset=offset, limit=limit, versions=version_metas # type: ignore
    )


@router.get(
    "/{item_id}/versions/{version_id}",
    response_model=ContentVersionDetails,
    summary="Get Specific Version Content"
)
async def get_specific_version_content_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item"),
    version_id: PyUUID = Path(..., description="The ID of the version to retrieve"),
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    item = await get_item_and_check_versioning_permission(item_id, db, current_user_session, is_admin_actor, write_access_needed=False)
    log_actor = "Admin" if is_admin_actor else f"Team {current_user_session.team_id if isinstance(current_user_session, TeamModel) else None}" # type: ignore
    log.info(f"{log_actor} requesting content for item ID: {item_id}, version ID: {version_id}")

    version = await crud_content_version.content_version.get_by_id(db, version_id=version_id)
    if not version or version.item_id != item_id: # type: ignore
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found for this item.")

    log.info(f"Returning content for item '{item.name}' ({item_id}), version {version.version_number} ({version_id})") # type: ignore
    return ContentVersionDetails.model_validate(version)
