# File: ulacm_backend/tests/crud/test_crud_search.py
# Purpose: Unit tests for search operations in app/crud/crud_search.py
# Changes:
# - Corrected UUID comparison in test_search_no_query_or_filters assertion (hyphenless).
# - Avoided literal_binds=True when checking FTS functions in test_search_with_query_text.
# - Corrected enum casing comparison in test_search_with_filters assertion.

import pytest
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from uuid import UUID as PyUUID, uuid4 # Import uuid4
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timezone, timedelta

# Import the function and models to test
from app.crud.crud_search import search_content_items_complex, FTS_CONFIG, FTS_START_SEL, FTS_STOP_SEL
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.db.models.team import Team

# Use fixtures defined in conftest.py
pytestmark = pytest.mark.asyncio

# --- Helper Data ---
def create_test_content_version(
    version_id="cccccccc-1111-1111-1111-111111111111",
    item_id="aaaaaaaa-1111-1111-1111-111111111111",
    markdown_content="# Test Content V1",
    version_number=1,
    saved_by_team_id="11111111-1111-1111-1111-111111111111"
) -> ContentVersion:
    """Helper function to create a ContentVersion ORM model instance."""
    return ContentVersion(
        version_id=PyUUID(version_id),
        item_id=PyUUID(item_id),
        markdown_content=markdown_content,
        version_number=version_number,
        saved_by_team_id=PyUUID(saved_by_team_id),
        created_at=datetime.now(timezone.utc),
    )

def create_test_content_item(
    item_id="aaaaaaaa-1111-1111-1111-111111111111",
    team_id="11111111-1111-1111-1111-111111111111",
    item_type=ContentItemTypeEnum.DOCUMENT,
    name="Test Document",
    is_globally_visible=False,
    current_version_id=None,
    current_version=None
) -> ContentItem:
    """Helper function to create a ContentItem ORM model instance."""
    if current_version and not current_version_id:
        current_version_id = str(current_version.version_id)
    item = ContentItem(
        item_id=PyUUID(item_id),
        team_id=PyUUID(team_id),
        item_type=item_type,
        name=name,
        is_globally_visible=is_globally_visible,
        current_version_id=PyUUID(current_version_id) if current_version_id else None,
        current_version=current_version,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return item

# --- Test Setup ---
@pytest.fixture
def mock_db_execute(mock_db_session: AsyncMock):
    """Fixture to provide mock results for db.execute calls."""
    def _setup_results(count_result_val=0, items_result_val=[]):
        mock_count_result = MagicMock()
        mock_count_result.scalar_one.return_value = count_result_val

        mock_items_result = MagicMock()
        # Determine structure of items_result_val to mock correctly
        if items_result_val and isinstance(items_result_val[0], tuple):
             # Simulate results like (item, rank, snippet) or (item, snippet)
             mock_items_result.unique.return_value.all.return_value = items_result_val
             mock_items_result.scalars.return_value.unique.return_value.all = MagicMock(side_effect=AttributeError("Use .all() directly for tuples"))
        elif items_result_val:
             # Simulate results of only ContentItem objects
             mock_items_result.scalars.return_value.unique.return_value.all.return_value = items_result_val
             mock_items_result.unique.return_value.all = MagicMock(side_effect=AttributeError("Use .scalars().unique().all() for ORM objects"))
        else:
             # Handle empty list for both cases
             mock_items_result.scalars.return_value.unique.return_value.all.return_value = []
             mock_items_result.unique.return_value.all.return_value = []

        mock_db_session.execute = AsyncMock(side_effect=[mock_count_result, mock_items_result])
        return mock_db_session
    return _setup_results


# --- Test Cases ---

async def test_search_no_query_or_filters(mock_db_execute):
    """Test search with no specific query or filters (should return all accessible items)."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    test_team_id_str_no_hyphen = str(test_team_id).replace('-', '') # For WHERE clause check
    mock_version = create_test_content_version()
    item1 = create_test_content_item(name="Doc 1", current_version=mock_version)
    item2 = create_test_content_item(name="Template 1", item_type=ContentItemTypeEnum.TEMPLATE, current_version=mock_version)
    db = mock_db_execute(count_result_val=2, items_result_val=[item1, item2])

    results, total_count = await search_content_items_complex(
        db=db,
        team_id=test_team_id,
        skip=0,
        limit=10
    )

    assert total_count == 2
    assert len(results) == 2
    assert results[0][0] == item1 # Results are tuples (item, snippet)
    assert results[0][1] is None # Snippet should be None when no query text
    assert results[1][0] == item2
    assert results[1][1] is None

    # Check queries passed to execute
    assert db.execute.await_count == 2
    count_query = db.execute.await_args_list[0].args[0]
    items_query = db.execute.await_args_list[1].args[0]

    # Verify basic structure and visibility filter
    assert isinstance(count_query, Select)
    assert isinstance(items_query, Select)
    # Compile without literal binds first to check structure if needed
    count_query_str_compiled = str(count_query.compile())
    items_query_str_compiled = str(items_query.compile())
    # Compile with literal binds for value checking
    count_query_str_literal = str(count_query.compile(compile_kwargs={"literal_binds": True})).replace('\n', '')
    items_query_str_literal = str(items_query.compile(compile_kwargs={"literal_binds": True})).replace('\n', '')

    # *** FIX: Corrected UUID comparison (hyphenless) ***
    assert f"(content_items.team_id = '{test_team_id_str_no_hyphen}' OR content_items.is_globally_visible = true)" in count_query_str_literal
    assert f"(content_items.team_id = '{test_team_id_str_no_hyphen}' OR content_items.is_globally_visible = true)" in items_query_str_literal
    # Ensure no FTS functions are present
    assert "plainto_tsquery" not in items_query_str_compiled
    assert "ts_rank_cd" not in items_query_str_compiled
    assert "ts_headline" not in items_query_str_compiled
    assert "ORDER BY content_items.updated_at DESC" in items_query_str_literal # Default sort

async def test_search_with_query_text(mock_db_execute):
    """Test search using FTS query text."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    search_term = "important keyword"
    mock_version = create_test_content_version()
    item1 = create_test_content_item(name="Relevant Doc", current_version=mock_version)
    # Simulate result including rank and snippet (item, rank, snippet)
    mock_result_row = (item1, 0.8, f"{FTS_START_SEL}keyword{FTS_STOP_SEL} context")
    # Pass the tuple structure to the mock setup
    db = mock_db_execute(count_result_val=1, items_result_val=[mock_result_row])

    results, total_count = await search_content_items_complex(
        db=db,
        team_id=test_team_id,
        search_query_text=search_term,
        skip=0,
        limit=10
    )

    assert total_count == 1
    assert len(results) == 1
    assert results[0][0] == item1
    assert results[0][1] == f"{FTS_START_SEL}keyword{FTS_STOP_SEL} context" # Snippet included

    assert db.execute.await_count == 2
    # Check that FTS functions are in the items query
    items_query = db.execute.await_args_list[1].args[0]
    # *** FIX: Compile without literal_binds for checking function calls ***
    items_query_str_compiled = str(items_query.compile(compile_kwargs={}))

    assert "plainto_tsquery" in items_query_str_compiled # Check function name presence
    assert "ts_rank_cd" in items_query_str_compiled
    assert "ts_headline" in items_query_str_compiled
    assert "@@" in items_query_str_compiled # Check for FTS operator

    # Check ordering clause (can use literal binds here if not checking FTS params directly)
    items_query_str_literal = str(items_query.compile(compile_kwargs={"literal_binds": True}))
    assert "ORDER BY rank DESC" in items_query_str_literal # Check ordering clause

async def test_search_with_filters(mock_db_execute):
    """Test search with item type and date filters."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    item_type_filter = [ContentItemTypeEnum.TEMPLATE]
    created_after_filter = date(2023, 1, 1)
    created_before_filter = date(2023, 12, 31)
    db = mock_db_execute(count_result_val=0, items_result_val=[]) # Assume no results for simplicity

    await search_content_items_complex(
        db=db,
        team_id=test_team_id,
        item_types_filter=item_type_filter,
        created_after_filter=created_after_filter,
        created_before_filter=created_before_filter,
        skip=0, limit=10
    )

    assert db.execute.await_count == 2
    count_query = db.execute.await_args_list[0].args[0]
    items_query = db.execute.await_args_list[1].args[0]
    count_query_str = str(count_query.compile(compile_kwargs={"literal_binds": True}))
    items_query_str = str(items_query.compile(compile_kwargs={"literal_binds": True}))

    # *** FIX: Correct casing check ***
    assert f"ITEM_TYPE IN ('{ContentItemTypeEnum.TEMPLATE.value.upper()}')" in count_query_str.upper()
    assert f"ITEM_TYPE IN ('{ContentItemTypeEnum.TEMPLATE.value.upper()}')" in items_query_str.upper()
    # Check date filters (convert date to expected datetime format for check)
    start_dt_str = datetime.combine(created_after_filter, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
    # Before filter should be exclusive of the end date, so add 1 day
    end_dt_str = datetime.combine(created_before_filter + timedelta(days=1), datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
    assert f"content_items.created_at >= '{start_dt_str}'" in count_query_str
    assert f"content_items.created_at >= '{start_dt_str}'" in items_query_str
    assert f"content_items.created_at < '{end_dt_str}'" in count_query_str
    assert f"content_items.created_at < '{end_dt_str}'" in items_query_str


async def test_search_pagination(mock_db_execute):
    """Test pagination parameters are applied."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    skip_val = 20
    limit_val = 5
    db = mock_db_execute(count_result_val=50, items_result_val=[]) # Assume 50 total

    _, total_count = await search_content_items_complex(
        db=db,
        team_id=test_team_id,
        skip=skip_val,
        limit=limit_val
    )

    assert total_count == 50
    assert db.execute.await_count == 2

    items_query = db.execute.await_args_list[1].args[0]
    items_query_str = str(items_query.compile(compile_kwargs={"literal_binds": True}))

    assert f"LIMIT {limit_val}" in items_query_str
    assert f"OFFSET {skip_val}" in items_query_str
