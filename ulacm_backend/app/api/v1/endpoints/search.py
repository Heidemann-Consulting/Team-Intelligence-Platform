# File: ulacm_backend/app/api/v1/endpoints/search.py
# Purpose: API endpoint for searching content items.
# Updated with logging.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from uuid import UUID as PyUUID

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.db.models.content_item import ContentItemTypeEnum
from app.api.v1.deps import get_current_team_user
from app.crud import crud_search
from app.schemas import ContentItemSearchResult, SearchResultsResponse # Using specific search response type

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
    current_team: TeamModel = Depends(get_current_team_user),
    query: Optional[str] = Query(None, description="Search term for item name or full-text content. (FR-SRCH-002)"),
    item_types: Optional[str] = Query(None, description="Comma-separated list of item types (Document,Template,Workflow). (FR-SRCH-002)"),
    created_after: Optional[date] = Query(None, description="Filter by creation date (YYYY-MM-DD format). (FR-SRCH-002)"),
    created_before: Optional[date] = Query(None, description="Filter by creation date (YYYY-MM-DD format). (FR-SRCH-002)"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, max=100)
):
    """
    Perform a search across Documents, Templates, and Workflows. (FR-SRCH-001)
    Results are filtered by team ownership or global visibility. (FR-SRCH-003)
    Corresponds to SRS 8.6.1.
    """
    log.info(f"Team ID {current_team.team_id} performing search: Query='{query}', Types='{item_types}', "
             f"CreatedAfter='{created_after}', CreatedBefore='{created_before}', Offset={offset}, Limit={limit}")

    parsed_item_types: Optional[List[ContentItemTypeEnum]] = None
    if item_types:
        try:
            types_list = [it.strip().capitalize() for it in item_types.split(",")] # Capitalize for enum matching
            parsed_item_types = [ContentItemTypeEnum(it) for it in types_list if it in ContentItemTypeEnum.__members__]
            if len(parsed_item_types) != len(types_list):
                log.warning(f"Invalid item types provided by team {current_team.team_id}: '{item_types}'")
                # Optionally raise error or just ignore invalid types
        except ValueError:
            log.warning(f"Error parsing item_types '{item_types}' for team {current_team.team_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid item_types provided. Valid types are Document, Template, Workflow."
            )

    try:
        items_with_snippets, total_count = await crud_search.search_content_items_complex(
            db,
            team_id=current_team.team_id,
            search_query_text=query,
            item_types_filter=parsed_item_types,
            created_after_filter=created_after,
            created_before_filter=created_before,
            skip=offset,
            limit=limit
        )
        log.info(f"Search by team {current_team.team_id} found {total_count} results, returning {len(items_with_snippets)}.")
    except Exception as e:
        log.exception(f"Error during search execution for team {current_team.team_id}")
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
