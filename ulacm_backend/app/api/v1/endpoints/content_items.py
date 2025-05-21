# File: ulacm_backend/app/api/v1/endpoints/content_items.py
# Purpose: API endpoints for managing ContentItems.
# Updated: Relaxed template_id requirement check for DOCUMENT creation by Team Users.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union, Type
from uuid import UUID as PyUUID
from datetime import date as DateObject, datetime, timezone

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItemTypeEnum, ContentItem as ContentItemDBModel
from app.api.v1.deps import (
    get_current_team_user,
    get_current_user_or_admin_marker,
    get_requesting_user_is_admin,
)
from app.crud import crud_content_item
from app.schemas import (
    ContentItem,
    ContentItemCreate,
    ContentItemUpdateMeta,
    ContentItemWithCurrentVersion,
    ContentItemListResponse,
    ContentItemDuplicatePayload,
    ContentItemSearchResult,
    ContentItemListItem,
    Msg,
    TokenPayload
)
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError
from app.core.config import settings
from app.schemas.workflow_definition import WorkflowDefinition

log = logging.getLogger(__name__)
router = APIRouter()

def _get_parsed_workflow_definition(item_db: ContentItemDBModel) -> Optional[WorkflowDefinition]:
    parsed_def = None
    if item_db.item_type == ContentItemTypeEnum.WORKFLOW and \
       item_db.current_version and \
       item_db.current_version.markdown_content:
        try:
            parsed_def = WorkflowDefinitionParser.parse_and_validate(
                item_db.current_version.markdown_content
            )
        except WorkflowParsingError as e:
            log.warning(
                f"Endpoint Helper: Failed to parse workflow definition for item {item_db.item_id}: {e}"
            )
    return parsed_def

def _convert_orm_to_detail_schema(
    item_db: ContentItemDBModel,
    schema_class: Type[Union[ContentItemWithCurrentVersion, ContentItemSearchResult]]
) -> Union[ContentItemWithCurrentVersion, ContentItemSearchResult]:
    item_dict = {
        "item_id": item_db.item_id,
        "team_id": item_db.team_id,
        "item_type": item_db.item_type,
        "name": item_db.name,
        "is_globally_visible": item_db.is_globally_visible,
        "current_version_id": item_db.current_version_id,
        "created_at": item_db.created_at,
        "updated_at": item_db.updated_at,
        "current_version_for_computed_fields": item_db.current_version if hasattr(item_db, 'current_version') else None,
    }

    if schema_class == ContentItemSearchResult:
        item_dict["snippet"] = getattr(item_db, 'snippet', None)
        if item_db.current_version:
            item_dict["current_version_number"] = item_db.current_version.version_number

    item_dict['parsed_workflow_definition_internal'] = _get_parsed_workflow_definition(item_db)

    return schema_class.model_validate(item_dict)


@router.post(
    "",
    response_model=ContentItem,
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
    log_actor = "Admin" if is_admin_actor else f"Team {current_user_session.team_id if isinstance(current_user_session, TeamModel) else 'Unknown'}"

    if item_in.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
        if not is_admin_actor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can create Templates or Workflows.")
        if item_in.template_id: # Admins creating T/W should not provide a template_id for the T/W itself
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="template_id should not be provided when Admin is creating Templates or Workflows.")
        actor_team_id = None # For Admin creating T/W, actor_team_id is not used directly for ownership. CRUD assigns ADMIN_SYSTEM_TEAM_ID.
    elif item_in.item_type == ContentItemTypeEnum.DOCUMENT:
        if is_admin_actor: # Admins don't create team documents this way
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot create Documents for teams via this endpoint.")
        if not isinstance(current_user_session, TeamModel) or not current_user_session.team_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Team context required for creating documents.")
        actor_team_id = current_user_session.team_id
        # The check for template_id being required for team-user document creation
        # is now handled more flexibly in the CRUD layer.
        # If template_id is provided, it will be used. If not (e.g. AI generated doc), CRUD layer allows it.
        # The original strict check:
        # if not item_in.template_id and not is_admin_actor :
        #      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="template_id is required when a Team User is creating a Document.")
        # This line is now removed as CRUD handles it.
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type.")

    log.info(f"{log_actor} attempting to create {item_in.item_type.value}: Name='{item_in.name}'")

    try:
        new_item_db = await crud_content_item.content_item.create_item_for_team_or_admin(
            db=db, obj_in=item_in, actor_team_id=actor_team_id, is_admin_actor=is_admin_actor
        )
        log.info(f"Successfully created {new_item_db.item_type.value}: Name='{new_item_db.name}', ID='{new_item_db.item_id}', OwnerID='{new_item_db.team_id}'")
    except ValueError as ve:
        log.warning(f"Content item creation failed validation: {ve}")
        if "Invalid UUID format for template_id" in str(ve) or "Invalid template_id type" in str(ve):
             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
        if "Template (ID:" in str(ve) and "not found" in str(ve) : # Specific error from CRUD
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
        # Other ValueErrors from CRUD (like name uniqueness) become 409
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        log.exception(f"Error creating content item: Name='{item_in.name}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create content item.")

    response_item = ContentItem.model_validate(new_item_db)
    return response_item


@router.get(
    "",
    response_model=ContentItemListResponse,
    summary="List Content Items with Filtering"
)
async def list_content_items_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
    item_type: Optional[ContentItemTypeEnum] = Query(None, description="Filter by item type (DOCUMENT, TEMPLATE, WORKFLOW)"),
    name_query: Optional[str] = Query(None, description="Filter by item name (case-insensitive, partial match)"),
    content_query: Optional[str] = Query(None, description="Filter by item content (full-text search, case-insensitive)"),
    name_globs: Optional[str] = Query(None, description="Comma-separated list of glob patterns for item name filtering (e.g., 'FY23_*,Report_Q?')"),
    created_after: Optional[DateObject] = Query(None, description="Filter by creation date (YYYY-MM-DD format, inclusive start)"),
    created_before: Optional[DateObject] = Query(None, description="Filter by creation date (YYYY-MM-DD format, inclusive end)"),
    is_globally_visible_filter: Optional[bool] = Query(None, alias="is_globally_visible", description="Filter by global visibility status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(15, ge=1, le=100),
    sort_by: str = Query("updated_at", enum=["name", "created_at", "updated_at", "item_type", "rank"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker),
    is_admin_actor: bool = Depends(get_requesting_user_is_admin),
    for_usage: bool = Query(False, description="True if a team is listing Templates/Workflows to use (not manage)")
):
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_actor_team_id = current_user_session.team_id if isinstance(current_user_session, TeamModel) else None
    log_actor = "Admin" if is_admin_actor else f"Team {requesting_actor_team_id}"

    name_glob_patterns_list: Optional[List[str]] = None
    if name_globs:
        name_glob_patterns_list = [pattern.strip() for pattern in name_globs.split(',') if pattern.strip()]

    log.info(
        f"{log_actor} listing items: Type={item_type}, NameQuery='{name_query}', ContentQuery='{content_query}', NameGlobs='{name_glob_patterns_list}', "
        f"CreatedAfter={created_after}, CreatedBefore={created_before}, "
        f"GlobalFilter={is_globally_visible_filter}, ForUsage={for_usage}, "
        f"Offset={offset}, Limit={limit}, SortBy={sort_by}, SortOrder={sort_order}"
    )

    created_after_dt: Optional[datetime] = None
    if created_after:
        created_after_dt = datetime.combine(created_after, datetime.min.time(), tzinfo=timezone.utc)

    created_before_dt: Optional[datetime] = None
    if created_before:
        created_before_dt = datetime.combine(created_before, datetime.max.time(), tzinfo=timezone.utc)


    items_db_orm_list, total_count = await crud_content_item.content_item.get_items_for_team_or_admin(
        db=db,
        requesting_actor_team_id=requesting_actor_team_id,
        is_admin_actor=is_admin_actor,
        item_type_filter=item_type,
        name_query=name_query,
        content_query=content_query,
        name_glob_patterns=name_glob_patterns_list,
        created_after=created_after_dt,
        created_before=created_before_dt,
        is_globally_visible_filter=is_globally_visible_filter,
        list_for_team_usage=for_usage if not is_admin_actor else False,
        skip=offset, limit=limit, sort_by=sort_by, sort_order=sort_order
    )

    response_items_schemas: List[ContentItemListItem] = []
    for item_db_obj in items_db_orm_list:
        list_item_data = {
            "item_id": item_db_obj.item_id,
            "team_id": item_db_obj.team_id,
            "item_type": item_db_obj.item_type,
            "name": item_db_obj.name,
            "is_globally_visible": item_db_obj.is_globally_visible,
            "current_version_id": item_db_obj.current_version_id,
            "created_at": item_db_obj.created_at,
            "updated_at": item_db_obj.updated_at,
            "current_version_number": item_db_obj.current_version.version_number if item_db_obj.current_version else None,
            "workflow_input_document_selectors": None,
            "workflow_output_name_template": None,
        }

        if item_db_obj.item_type == ContentItemTypeEnum.WORKFLOW:
            parsed_workflow_def = _get_parsed_workflow_definition(item_db_obj)
            if parsed_workflow_def:
                list_item_data["workflow_input_document_selectors"] = parsed_workflow_def.inputDocumentSelectors
                list_item_data["workflow_output_name_template"] = parsed_workflow_def.outputName

        schema_item = ContentItemListItem.model_validate(list_item_data)
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

    item_db = await crud_content_item.content_item.get_by_id_for_team_or_admin_usage(
        db, item_id=item_id, requesting_team_id=requesting_team_id, is_admin_request=is_admin_actor
    )

    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found or not accessible.")

    response_data = _convert_orm_to_detail_schema(item_db, ContentItemWithCurrentVersion)
    return response_data


@router.put(
    "/{item_id}/meta",
    response_model=ContentItem,
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
    log.info(f"{log_actor} attempting to update metadata for item ID: {item_id} with data: {item_in.model_dump(exclude_unset=True)}")

    try:
        updated_item_db = await crud_content_item.content_item.update_item_meta_for_owner_or_admin(
            db=db, item_id=item_id, item_in=item_in,
            requesting_actor_team_id=requesting_actor_team_id, is_admin_actor=is_admin_actor
        )
    except ValueError as ve:
        log.warning(f"Update metadata for item {item_id} failed validation: {ve}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        log.exception(f"Error updating metadata for item {item_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update item metadata.")

    if not updated_item_db:
        item_exists = await crud_content_item.content_item.get_by_id(db, item_id=item_id)
        if not item_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
        else:
            # This path means can_update was false in CRUD, implying permission issue
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item's metadata.")

    log.info(f"Successfully updated metadata for item: '{updated_item_db.name}' ({item_id})")
    response_item = ContentItem.model_validate(updated_item_db)
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

    if not deleted_item: # This means it was not found OR not authorized by CRUD logic
        item_exists = await crud_content_item.content_item.get_by_id(db, item_id=item_id) # Check if it exists at all
        if not item_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found.")
        else:
            # Existed, but CRUD didn't allow deletion (permission issue)
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
        final_duplicated_item_orm = await crud_content_item.content_item.duplicate_item_logic(
            db=db,
            source_item_id=item_id,
            payload=payload,
            requesting_actor_team_id=duplicating_team_id,
            is_admin_actor=is_admin_actor
        )
        log.info(f"{log_actor} successfully duplicated item {item_id} into new item {final_duplicated_item_orm.item_id} ('{final_duplicated_item_orm.name}')")

    except ValueError as ve:
        log.warning(f"Content item duplication for {item_id} failed validation or permission: {ve}")
        if "not found" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
        elif "not authorized" in str(ve).lower() or "cannot duplicate" in str(ve).lower() or "not permitted" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ve))
        elif "already exists" in str(ve).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        log.exception(f"Error duplicating item {item_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to duplicate content item.")

    response_data = _convert_orm_to_detail_schema(final_duplicated_item_orm, ContentItemWithCurrentVersion)
    return response_data
