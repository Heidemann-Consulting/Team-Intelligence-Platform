# File: ulacm_backend/app/crud/crud_search.py
# Purpose: CRUD operations for searching content items using PostgreSQL FTS.

from typing import List, Optional, Tuple
from uuid import UUID as PyUUID
from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, desc, false as sql_false # Import false
from sqlalchemy.dialects.postgresql import TSQUERY, TSVECTOR

from app.db.models.content_item import ContentItem, ContentItemTypeEnum # Correct Enum import
from app.db.models.content_version import ContentVersion
from sqlalchemy.orm import aliased, joinedload, contains_eager
from app.core.config import settings

FTS_CONFIG = 'english'

# Use single quotes for HTML attributes to avoid issues with nested double quotes
FTS_START_SEL = "<mark class='search-highlight'>"
FTS_STOP_SEL = "</mark>"
FTS_MAX_WORDS = 35
FTS_MIN_WORDS = 15
FTS_SHORT_WORD = 3
FTS_HIGHLIGHT_ALL = "TRUE" # PostgreSQL ts_headline option is boolean but passed as string 'TRUE' or 'FALSE'

async def search_content_items_complex(
    db: AsyncSession,
    *,
    team_id: PyUUID,
    search_query_text: Optional[str] = None,
    item_types_filter: Optional[List[ContentItemTypeEnum]] = None,
    created_after_filter: Optional[date] = None,
    created_before_filter: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc"
) -> Tuple[List[Tuple[ContentItem, Optional[str]]], int]:
    """
    Performs a complex search across content items using PostgreSQL Full-Text Search.
    Includes snippet generation using ts_headline.
    """

    CurrentVersion = aliased(ContentVersion)

    # Base query structure
    base_select_entities = [ContentItem]
    # Initial base_query setup
    # The select entities will be re-defined later if FTS is active
    current_base_query = (
        select(*base_select_entities)
        .join(CurrentVersion, ContentItem.current_version_id == CurrentVersion.version_id)
        .options(
            contains_eager(ContentItem.current_version.of_type(CurrentVersion))
            .joinedload(CurrentVersion.saving_team),
            joinedload(ContentItem.owner_team)
        )
    )

    # Initial count_query setup
    current_count_query = (
        select(func.count(ContentItem.item_id))
        .select_from(ContentItem)
        .join(CurrentVersion, ContentItem.current_version_id == CurrentVersion.version_id)
    )

    final_conditions = []

    team_documents_condition = and_(
        ContentItem.item_type == ContentItemTypeEnum.DOCUMENT, # Corrected here
        ContentItem.team_id == team_id
    )
    global_documents_condition = and_(
        ContentItem.item_type == ContentItemTypeEnum.DOCUMENT, # Corrected here
        ContentItem.is_globally_visible == True,
        ContentItem.team_id != settings.ADMIN_SYSTEM_TEAM_ID
    )
    admin_templates_condition = and_(
        ContentItem.item_type == ContentItemTypeEnum.TEMPLATE, # Corrected here
        ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID,
        ContentItem.is_globally_visible == True
    )
    admin_workflows_condition = and_(
        ContentItem.item_type == ContentItemTypeEnum.WORKFLOW, # Corrected here
        ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID,
        ContentItem.is_globally_visible == True
    )

    if item_types_filter:
        type_specific_or_conditions = []
        if ContentItemTypeEnum.DOCUMENT in item_types_filter: # Corrected here
            type_specific_or_conditions.append(team_documents_condition)
            type_specific_or_conditions.append(global_documents_condition)
        if ContentItemTypeEnum.TEMPLATE in item_types_filter: # Corrected here
            type_specific_or_conditions.append(admin_templates_condition)
        if ContentItemTypeEnum.WORKFLOW in item_types_filter: # Corrected here
            type_specific_or_conditions.append(admin_workflows_condition)

        if type_specific_or_conditions:
            final_conditions.append(or_(*type_specific_or_conditions))
        else:
            final_conditions.append(sql_false())
    else:
        final_conditions.append(or_(
            team_documents_condition,
            global_documents_condition,
            admin_templates_condition,
            admin_workflows_condition
        ))

    if final_conditions:
        merged_conditions = and_(*final_conditions)
        current_base_query = current_base_query.where(merged_conditions)
        current_count_query = current_count_query.where(merged_conditions)
    else:
        current_base_query = current_base_query.where(sql_false())
        current_count_query = current_count_query.where(sql_false())

    if created_after_filter:
        start_dt = datetime.combine(created_after_filter, datetime.min.time())
        current_base_query = current_base_query.where(ContentItem.created_at >= start_dt)
        current_count_query = current_count_query.where(ContentItem.created_at >= start_dt)

    if created_before_filter:
        end_dt = datetime.combine(created_before_filter + timedelta(days=1), datetime.min.time())
        current_base_query = current_base_query.where(ContentItem.created_at < end_dt)
        current_count_query = current_count_query.where(ContentItem.created_at < end_dt)

    fts_rank_column = None
    snippet_column = None
    ts_query_obj = None

    if search_query_text and search_query_text.strip():
        ts_query_obj = func.plainto_tsquery(FTS_CONFIG, search_query_text)

        match_condition = or_(
            func.to_tsvector(FTS_CONFIG, ContentItem.name).op('@@')(ts_query_obj),
            CurrentVersion.content_tsv.op('@@')(ts_query_obj)
        )

        fts_rank_column = (
            func.ts_rank_cd(CurrentVersion.content_tsv, ts_query_obj) * 0.8 +
            func.ts_rank_cd(func.to_tsvector(FTS_CONFIG, ContentItem.name), ts_query_obj) * 0.2
        ).label("rank")

        options_str_for_pg = (
            f'StartSel="{FTS_START_SEL}", StopSel="{FTS_STOP_SEL}", '
            f'MaxWords={FTS_MAX_WORDS}, MinWords={FTS_MIN_WORDS}, ShortWord={FTS_SHORT_WORD}, HighlightAll={FTS_HIGHLIGHT_ALL}'
        )

        snippet_column = func.ts_headline(
            FTS_CONFIG,
            CurrentVersion.markdown_content,
            ts_query_obj,
            options_str_for_pg
        ).label("snippet")

        # Reconstruct select to include ContentItem entity and the new FTS columns
        # Start from the FROM clause of the current_base_query to keep joins
        # and apply existing WHERE clauses before the match_condition for FTS
        select_from_target = current_base_query.froms[0]

        # Get existing WHERE clause from current_base_query
        existing_where_clause = current_base_query._whereclause # Accessing internal attribute, might need adjustment if API changes

        reconstructed_query = select(ContentItem, fts_rank_column, snippet_column).select_from(select_from_target)

        # Re-apply options
        reconstructed_query = reconstructed_query.options(
            contains_eager(ContentItem.current_version.of_type(CurrentVersion))
            .joinedload(CurrentVersion.saving_team),
            joinedload(ContentItem.owner_team)
        )

        if existing_where_clause is not None:
            reconstructed_query = reconstructed_query.where(existing_where_clause)

        current_base_query = reconstructed_query.where(match_condition) # Add FTS match condition
        current_count_query = current_count_query.where(match_condition)


    sort_field = None
    if sort_by == "rank" and fts_rank_column is not None:
        sort_field = fts_rank_column
    elif sort_by == "name":
        sort_field = ContentItem.name
    else:
        sort_field = ContentItem.updated_at

    order_expression = sort_field.asc() if sort_order.lower() == "asc" else sort_field.desc()
    current_base_query = current_base_query.order_by(order_expression)

    total_count_result = await db.execute(current_count_query)
    total_count = total_count_result.scalar_one()

    current_base_query = current_base_query.offset(skip).limit(limit)
    items_result = await db.execute(current_base_query)

    items_with_snippets: List[Tuple[ContentItem, Optional[str]]] = []
    if fts_rank_column is not None and snippet_column is not None:
        for row_tuple in items_result.all():
            item_entity = row_tuple[0]
            snippet_text = row_tuple[2]
            items_with_snippets.append((item_entity, snippet_text))
    else:
        for item_entity in items_result.scalars().all():
            items_with_snippets.append((item_entity, None))

    return items_with_snippets, total_count
