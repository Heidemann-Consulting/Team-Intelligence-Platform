# File: ulacm_backend/app/crud/crud_search.py
# Purpose: CRUD operations for searching content items using PostgreSQL FTS.
# Updated to include ts_headline for snippet generation.

from typing import List, Optional, Tuple
from uuid import UUID as PyUUID
from datetime import date, datetime, timedelta # <-- Import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, text, desc, cast, TEXT # Import FTS functions and desc
from sqlalchemy.dialects.postgresql import TSQUERY, TSVECTOR # Import specific PG types

from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from sqlalchemy.orm import aliased, joinedload, contains_eager

# Define the text search configuration (e.g., 'english')
FTS_CONFIG = 'english'
# Define highlight markers for ts_headline
FTS_START_SEL = '<mark class="search-highlight">' # Start highlight HTML tag
FTS_STOP_SEL = '</mark>' # End highlight HTML tag

async def search_content_items_complex(
    db: AsyncSession,
    *,
    team_id: PyUUID,
    search_query_text: Optional[str] = None,
    item_types_filter: Optional[List[ContentItemTypeEnum]] = None,
    created_after_filter: Optional[date] = None,
    created_before_filter: Optional[date] = None,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Tuple[ContentItem, Optional[str]]], int]: # Return type changed to include snippet string
    """
    Performs a complex search across content items using PostgreSQL Full-Text Search.
    Includes snippet generation using ts_headline. FR-SRCH-004.

    Args:
        db: The SQLAlchemy async session.
        team_id: The ID of the team performing the search (for visibility).
        search_query_text: Text to search in item name or full-text content.
        item_types_filter: List of item types to filter by.
        created_after_filter: Filter items created after this date.
        created_before_filter: Filter items created before this date.
        skip: Pagination offset.
        limit: Pagination limit.

    Returns:
        A tuple containing a list of tuples (ContentItem object, Optional[snippet string])
        and the total count of matching items.
    """
    # Alias ContentVersion for joining to current version's content
    CurrentVersion = aliased(ContentVersion)

    # Base query joining ContentItem with its current version
    # Selecting the ContentItem model directly
    base_query = (
        select(ContentItem) # Select the main model
        .join(CurrentVersion, ContentItem.current_version_id == CurrentVersion.version_id)
        .options(contains_eager(ContentItem.current_version.of_type(CurrentVersion))) # Eager load current version data efficiently
        .where(
            or_( # Visibility filter
                ContentItem.team_id == team_id,
                ContentItem.is_globally_visible == True
            )
        )
    )

    # Base query for counting results
    count_query = (
        select(func.count(ContentItem.item_id))
        .select_from(ContentItem)
        .join(CurrentVersion, ContentItem.current_version_id == CurrentVersion.version_id) # Join needed for FTS filter
        .where(
            or_( # Visibility filter
                ContentItem.team_id == team_id,
                ContentItem.is_globally_visible == True
            )
        )
    )

    # Apply standard filters
    if item_types_filter:
        base_query = base_query.where(ContentItem.item_type.in_(item_types_filter))
        count_query = count_query.where(ContentItem.item_type.in_(item_types_filter))

    if created_after_filter:
        # Start of the day
        start_dt = datetime.combine(created_after_filter, datetime.min.time())
        base_query = base_query.where(ContentItem.created_at >= start_dt)
        count_query = count_query.where(ContentItem.created_at >= start_dt)

    if created_before_filter:
        # End of the day (exclusive)
        # Use timedelta directly
        end_dt = datetime.combine(created_before_filter + timedelta(days=1), datetime.min.time())
        base_query = base_query.where(ContentItem.created_at < end_dt)
        count_query = count_query.where(ContentItem.created_at < end_dt)

    # --- Full-Text Search Logic ---
    fts_rank_column = None
    snippet_column = None
    ts_query = None

    if search_query_text and search_query_text.strip():
        # Use plainto_tsquery for safer handling of user input
        ts_query = func.plainto_tsquery(FTS_CONFIG, search_query_text)

        # Use pre-calculated tsvector column if available (Recommended)
        if hasattr(CurrentVersion, 'content_tsv'):
            match_condition = or_(
                func.to_tsvector(FTS_CONFIG, ContentItem.name).op('@@')(ts_query), # FTS on name
                CurrentVersion.content_tsv.op('@@')(ts_query) # FTS on pre-calculated content vector
            )
            # Calculate rank based on content and name vectors
            fts_rank_column = (
                func.ts_rank_cd(CurrentVersion.content_tsv, ts_query) * 0.8 +
                func.ts_rank_cd(func.to_tsvector(FTS_CONFIG, ContentItem.name), ts_query) * 0.2
            ).label("rank")
            # Define snippet generation using ts_headline on the original content column
            snippet_column = func.ts_headline(
                FTS_CONFIG, # Configuration
                CurrentVersion.markdown_content, # Original content column
                ts_query, # The query
                f'StartSel="{FTS_START_SEL}", StopSel="{FTS_STOP_SEL}", MaxWords=35, MinWords=15, ShortWord=3, HighlightAll=TRUE' # Options
            ).label("snippet")
        else:
            # Fallback: Calculate tsvector on-the-fly (Less performant)
            print("Warning: Pre-calculated 'content_tsv' column not found. Using on-the-fly tsvector calculation for content search.") # Replace with logger
            ts_vector_content = func.to_tsvector(FTS_CONFIG, CurrentVersion.markdown_content)
            ts_vector_name = func.to_tsvector(FTS_CONFIG, ContentItem.name)
            match_condition = or_(
                ts_vector_name.op('@@')(ts_query),
                ts_vector_content.op('@@')(ts_query)
            )
            # Calculate rank
            fts_rank_column = (
                func.ts_rank_cd(ts_vector_content, ts_query) * 0.8 +
                func.ts_rank_cd(ts_vector_name, ts_query) * 0.2
            ).label("rank")
            # Define snippet generation
            snippet_column = func.ts_headline(
                FTS_CONFIG,
                CurrentVersion.markdown_content,
                ts_query,
                f'StartSel="{FTS_START_SEL}", StopSel="{FTS_STOP_SEL}", MaxWords=35, MinWords=15, ShortWord=3, HighlightAll=TRUE'
            ).label("snippet")

        # Add the snippet and rank columns to the select query
        base_query = base_query.add_columns(fts_rank_column, snippet_column)
        # Add the FTS match condition to WHERE clause
        base_query = base_query.where(match_condition)
        count_query = count_query.where(match_condition)

    # --- Ordering ---
    if fts_rank_column is not None:
        # Order primarily by rank, then by update timestamp as a tie-breaker
        base_query = base_query.order_by(desc(fts_rank_column), desc(ContentItem.updated_at))
    else:
        # Default sort if no search query is provided
        base_query = base_query.order_by(desc(ContentItem.updated_at))

    # --- Count Execution ---
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar_one()

    # --- Main Query Execution with Pagination ---
    base_query = base_query.offset(skip).limit(limit)
    items_result = await db.execute(base_query)

    # Process results
    items_with_snippets: List[Tuple[ContentItem, Optional[str]]] = []
    if snippet_column is not None:
        # Results contain tuples of (ContentItem, rank, snippet)
        # Need to handle potential duplicates due to join if not using .unique() properly
        # Using unique() on the results processor
        processed_results = items_result.unique().all()
        for item, rank, snippet_text in processed_results:
            items_with_snippets.append((item, snippet_text))
    else:
        # Results contain only ContentItem objects
        processed_results = items_result.scalars().unique().all()
        for item in processed_results:
            items_with_snippets.append((item, None)) # No snippet generated

    return items_with_snippets, total_count
