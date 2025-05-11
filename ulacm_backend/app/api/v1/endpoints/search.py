# File: ulacm_backend/app/api/v1/endpoints/search.py
# Purpose: API endpoint for searching content items.
# Updated with logging.
# Updated: Admins can now use the search endpoint.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union # Added Union
from datetime import date
from uuid import UUID as PyUUID

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItemTypeEnum
from app.api.v1.deps import (
    get_current_team_user,
    get_current_user_or_admin_marker, # Added
    get_requesting_user_is_admin # Added
)
from app.crud import crud_search
from app.schemas import ContentItemSearchResult, SearchResultsResponse, TokenPayload # Using specific search response type

log = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "",
    response_model=SearchResultsResponse, # Use specific SearchResultsResponse
    summary="Search Content Items"
)
async def search_content_items(
    request: Request, # Added for logging
    db: AsyncSession = Depends(get_db),
    current_user_session: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker), # Changed
    is_admin_actor: bool = Depends(get_requesting_user_is_admin), # Added
    query: Optional[str] = Query(None, description="Search term for item name or full-text content. (FR-SRCH-002)"),
    item_types: Optional[str] = Query(None, description="Comma-separated list of item types (Document,Template,Workflow). (FR-SRCH-002)"),
    created_after: Optional[date] = Query(None, description="Filter by creation date (YYYY-MM-DD format). (FR-SRCH-002)"),
    created_before: Optional[date] = Query(None, description="Filter by creation date (YYYY-MM-DD format). (FR-SRCH-002)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, max=100)
):
    """
    Perform a search across Documents, Templates, and Workflows. (FR-SRCH-001)
    Results are filtered by team ownership or global visibility for team users.
    Admins can search across all content items. (FR-SRCH-003)
    Corresponds to SRS 8.6.1.
    """
    if not current_user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    requesting_team_id: Optional[PyUUID] = None
    log_actor_type = "Admin"
    if not is_admin_actor and isinstance(current_user_session, TeamModel):
        requesting_team_id = current_user_session.team_id
        log_actor_type = f"Team {requesting_team_id}"
    elif not is_admin_actor: # Should not happen if current_user_session is None and not admin
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user session for search.")


    log.info(f"{log_actor_type} performing search: Query='{query}', Types='{item_types}', "
             f"CreatedAfter='{created_after}', CreatedBefore='{created_before}', Offset={offset}, Limit={limit}")

    parsed_item_types: Optional[List[ContentItemTypeEnum]] = None
    if item_types:
        try:
            types_list = [it.strip().capitalize() for it in item_types.split(",")] # Capitalize for enum matching
            parsed_item_types = [ContentItemTypeEnum(it) for it in types_list if it in ContentItemTypeEnum.__members__]
            if len(parsed_item_types) != len(types_list):
                log.warning(f"Invalid item types provided by {log_actor_type}: '{item_types}'")
                # Optionally raise error or just ignore invalid types
        except ValueError:
            log.warning(f"Error parsing item_types '{item_types}' for {log_actor_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid item_types provided. Valid types are Document, Template, Workflow."
            )

    try:
        items_with_snippets, total_count = await crud_search.search_content_items_complex(
            db,
            requesting_team_id=requesting_team_id, # Pass team_id or None for admin
            is_admin_actor=is_admin_actor,        # Pass is_admin flag
            search_query_text=query,
            item_types_filter=parsed_item_types,
            created_after_filter=created_after,
            created_before_filter=created_before,
            skip=offset,
            limit=limit
        )
        log.info(f"Search by {log_actor_type} found {total_count} results, returning {len(items_with_snippets)}.")
    except Exception as e:
        log.exception(f"Error during search execution for {log_actor_type}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed.")

    # Map DB models and snippets to ContentItemSearchResult schemas
    search_results_schemas = []
    for item_db, snippet_str in items_with_snippets:
        schema_item = ContentItemSearchResult.model_validate(item_db)
        if item_db.current_version:
            schema_item.current_version_number = item_db.current_version.version_number
        else:
            schema_item.current_version_number = 0
        schema_item.snippet = snippet_str
        search_results_schemas.append(schema_item)

    return SearchResultsResponse(
        total_count=total_count,
        offset=offset,
        limit=limit,
        items=search_results_schemas
    )
