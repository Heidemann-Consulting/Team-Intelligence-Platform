# File: ulacm_backend/app/api/v1/endpoints/content_items.py
# Purpose: API endpoints for managing ContentItems.
# Updated for Option 3 (Admin System Team):
# - Admins create Templates/Workflows owned by ADMIN_SYSTEM_TEAM_ID.
# - Teams create Documents owned by their team, using Admin System Templates.
# - Access control based on admin status and item ownership.
# Fixed: Ensure 'for_usage' items include item_id by using ContentItemSchema.
# Updated: Use ContentItemWithCurrentVersion for list items to include current_version_number.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from uuid import UUID as PyUUID

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItemTypeEnum, ContentItem as ContentItemDBModel
from app.api.v1.deps import (
    get_current_team_user,
    get_current_admin_user,
    get_current_user_or_admin_marker,
    get_requesting_user_is_admin,
    ensure_admin_user
)
from app.crud import crud_content_item
from app.schemas import (
    ContentItemSchema,
    ContentItemCreate,
    ContentItemUpdateMeta,
    ContentItemWithCurrentVersion, # Import this for use in the list
    ContentItemListResponse,
    ContentItemDuplicatePayload,
    Msg,
    TokenPayload
)
from app.schemas.content_item import ContentItemBase
from app.core.config import settings

log = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "",
    response_model=ContentItemSchema, # Response for create is the full ContentItemSchema
    status_code=status.HTTP_201_CREATED,
    summary="Create New Content Item (Document by Team, Template/Workflow by Admin)"
)
async def create_content_item_endpoint(
    request: Request,
    *,
    db: AsyncSession = Depends(get_db),
    item_in: ContentItemCreate,
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    actor_team_id: Optional[PyUUID] = None
    effective_owner_id: PyUUID

    log_actor = "Admin" if is_admin_actor else f"Team {current_user_session.team_id if isinstance(current_user_session, TeamModel) else 'Unknown'}"

    if item_in.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
        if not is_admin_actor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can create Templates or Workflows.")
        if item_in.template_id: # Should not be provided for T/W creation
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="template_id should not be provided for Templates or Workflows.")
        effective_owner_id = settings.ADMIN_SYSTEM_TEAM_ID
        actor_team_id = None # Admin acts as system
    elif item_in.item_type == ContentItemTypeEnum.DOCUMENT:
        if is_admin_actor: # Admins don't create team documents via this generic endpoint
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot create Documents for teams via this endpoint.")
        if not isinstance(current_user_session, TeamModel) or not current_user_session.team_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Team context required for creating documents.")
        actor_team_id = current_user_session.team_id
        effective_owner_id = actor_team_id
        if not item_in.template_id: # template_id is mandatory for Document creation by team
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="template_id is required when creating a Document.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type.")

    log.info(f"{log_actor} attempting to create {item_in.item_type.value}: Name='{item_in.name}' to be owned by {effective_owner_id}")

    try:
        new_item_db = await crud_content_item.content_item.create_item_for_team_or_admin(
            db=db, obj_in=item_in, actor_team_id=actor_team_id, is_admin_actor=is_admin_actor
        )
        log.info(f"Successfully created {new_item_db.item_type.value}: Name='{new_item_db.name}', ID='{new_item_db.item_id}', OwnerID='{new_item_db.team_id}'")
    except ValueError as ve:
        log.warning(f"Content item creation failed validation: {ve}")
        if "Invalid UUID format for template_id" in str(ve):
             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        log.exception(f"Error creating content item: Name='{item_in.name}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create content item.")

    response_item = ContentItemSchema.model_validate(new_item_db)
    return response_item


@router.get(
    "",
    response_model=ContentItemListResponse,
    summary="List Content Items"
)
async def list_content_items_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
    item_type: Optional[ContentItemTypeEnum] = Query(None, description="Filter by item type"),
    offset: int = Query(0, ge=0),
    limit: int = Query(15, ge=1, le=100),
    sort_by: str = Query("updated_at", enum=["name", "created_at", "updated_at"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin),
    for_usage: bool = Query(False, description="True if a team is listing Templates/Workflows to use (not manage)")
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_actor_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {requesting_actor_team_id}"
    log.info(f"{log_actor} listing items: Type={item_type}, ForUsage={for_usage}, Offset={offset}, Limit={limit}")

    items_db, total_count = await crud_content_item.content_item.get_items_for_team_or_admin(
        db=db,
        requesting_actor_team_id=requesting_actor_team_id,
        is_admin_actor=is_admin_actor,
        item_type_filter=item_type,
        list_for_team_usage=for_usage if not is_admin_actor else False,
        skip=offset, limit=limit, sort_by=sort_by, sort_order=sort_order
    )

    # Use ContentItemWithCurrentVersion to ensure current_version_number is populated
    response_items_schemas: List[ContentItemWithCurrentVersion] = []
    for item_db_obj in items_db:
        schema_item = ContentItemWithCurrentVersion.model_validate(item_db_obj)
        response_items_schemas.append(schema_item)


    return ContentItemListResponse(
        total_count=total_count, offset=offset, limit=limit, items=response_items_schemas
    )


@router.get(
    "/{item_id}",
    response_model=ContentItemWithCurrentVersion,
    summary="Get Content Item Details (includes current version content)"
)
async def get_content_item_details_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to retrieve"),
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {requesting_team_id}"
    log.info(f"{log_actor} requesting details for item ID: {item_id}")

    item_db = await crud_content_item.content_item.get_by_id(db, item_id=item_id)
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")

    can_access_full_details = False
    if is_admin_actor:
        can_access_full_details = True
    elif requesting_team_id:
        if item_db.item_type == ContentItemTypeEnum.DOCUMENT and (item_db.team_id == requesting_team_id or item_db.is_globally_visible):
            can_access_full_details = True
        elif item_db.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and \
             item_db.team_id == settings.ADMIN_SYSTEM_TEAM_ID and item_db.is_globally_visible:
            can_access_full_details = True


    if not can_access_full_details:
        log.warning(f"{log_actor} access denied for full details of item {item_id} (type: {item_db.item_type}, owner: {item_db.team_id}).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access full details of this item.")

    response_data = ContentItemWithCurrentVersion.model_validate(item_db)
    return response_data


@router.put(
    "/{item_id}/meta",
    response_model=ContentItemSchema,
    summary="Update Content Item Metadata (Name, Visibility)"
)
async def update_content_item_metadata_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to update metadata for"),
    item_in: ContentItemUpdateMeta = ...,
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_actor_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {requesting_actor_team_id}"
    log.info(f"{log_actor} attempting to update metadata for item ID: {item_id}")

    try:
        updated_item_db = await crud_content_item.content_item.update_item_meta_for_owner_or_admin(
            db=db, item_id=item_id, item_in=item_in,
            requesting_actor_team_id=requesting_actor_team_id, is_admin_actor=is_admin_actor
        )
    except ValueError as ve:
        log.warning(f"Update metadata for item {item_id} failed validation: {ve}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        log.exception(f"Error updating metadata for item {item_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update item metadata.")

    if not updated_item_db:
        item_exists = await crud_content_item.content_item.get_by_id(db, item_id=item_id)
        if not item_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item's metadata.")

    log.info(f"Successfully updated metadata for item: '{updated_item_db.name}' ({item_id})")
    response_item = ContentItemSchema.model_validate(updated_item_db)
    return response_item


@router.delete(
    "/{item_id}",
    response_model=Msg,
    status_code=status.HTTP_200_OK,
    summary="Delete Content Item"
)
async def delete_content_item_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to delete"),
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_actor_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {requesting_actor_team_id}"
    log.info(f"{log_actor} attempting to delete item ID: {item_id}")

    deleted_item = await crud_content_item.content_item.remove_item_for_owner_or_admin(
        db=db, item_id=item_id, requesting_actor_team_id=requesting_actor_team_id, is_admin_actor=is_admin_actor
    )

    if not deleted_item:
        item_exists = await crud_content_item.content_item.get_by_id(db, item_id=item_id)
        if not item_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item.")

    log.info(f"Successfully deleted item: '{deleted_item.name}' ({item_id})")
    return Msg(message=f"Content item '{deleted_item.name}' (ID: {item_id}) and all its versions deleted successfully.")


@router.post(
    "/{item_id}/duplicate",
    response_model=ContentItemWithCurrentVersion,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate Content Item"
)
async def duplicate_content_item_endpoint(
    request: Request,
    item_id: PyUUID = Path(..., description="The ID of the content item to duplicate"),
    payload: ContentItemDuplicatePayload = ...,
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin)
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    duplicating_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {duplicating_team_id}"
    log.info(f"{log_actor} attempting to duplicate item ID: {item_id} as '{payload.new_name}'")

    try:
        final_duplicated_item = await crud_content_item.content_item.duplicate_item_logic(
            db=db,
            source_item_id=item_id,
            payload=payload,
            requesting_actor_team_id=duplicating_team_id,
            is_admin_actor=is_admin_actor
        )
        log.info(f"{log_actor} successfully duplicated item {item_id} into new item {final_duplicated_item.item_id} ('{final_duplicated_item.name}')")

    except ValueError as ve:
        log.warning(f"Content item duplication for {item_id} failed validation or permission: {ve}")
        if "not found" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
        elif "not authorized" in str(ve).lower() or "cannot duplicate" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ve))
        elif "already exists" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        log.exception(f"Error duplicating item {item_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to duplicate content item.")

    response_data = ContentItemWithCurrentVersion.model_validate(final_duplicated_item)
    return response_data
