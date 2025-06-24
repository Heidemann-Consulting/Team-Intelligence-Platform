# File: ulacm_backend/tests/crud/test_crud_content_version.py
# Purpose: Unit tests for ContentVersion CRUD operations in app/crud/crud_content_version.py
# Changes:
# - Corrected mock setup for scalar_one_or_none/scalar_one to return values directly when awaited.
# - Corrected assertions for UPDATE statement in create_new_version tests.
# - Corrected assertions for UUID format in WHERE clauses.

import pytest
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from uuid import UUID as PyUUID, uuid4  # Import uuid4 function
from sqlalchemy.sql import Select, Update, text
from datetime import datetime, timezone

# Import the CRUD object and schemas/models to test
from app.crud.crud_content_version import content_version as crud_content_version
from app.schemas.content_version import ContentVersionCreate
from app.db.models.content_version import ContentVersion
from app.db.models.content_item import ContentItem  # Needed for FK reference
from app.db.models.team import Team  # Added for helper

# Use fixtures defined in conftest.py
pytestmark = pytest.mark.asyncio


# --- Helper Data ---
def create_test_content_version(
    version_id="cccccccc-1111-1111-1111-111111111111",
    item_id="aaaaaaaa-1111-1111-1111-111111111111",
    markdown_content="# Test Content V1",
    version_number=1,
    saved_by_team_id="11111111-1111-1111-1111-111111111111",
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


# --- Test Cases ---


async def test_get_by_id(mock_db_session):
    """Test retrieving a content version by its ID."""
    test_id = PyUUID("cccccccc-1111-1111-1111-111111111111")
    expected_version = create_test_content_version(version_id=str(test_id))
    # Correct Mock: Set return_value on the mocked method itself
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = (
        expected_version
    )

    # Call the function under test (which should now await the mock's result)
    found_version = await crud_content_version.get_by_id(
        db=mock_db_session, version_id=test_id
    )

    # Assertions
    assert found_version == expected_version
    mock_db_session.execute.assert_awaited_once()  # Verify the execute was awaited
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()  # Verify the method was called
    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    assert f"content_versions.version_id = '{test_id}'" in str(
        query.compile(compile_kwargs={"literal_binds": True})
    )

    # Test not found case
    mock_db_session.execute.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    not_found_version = await crud_content_version.get_by_id(
        db=mock_db_session, version_id=PyUUID(uuid4().hex)
    )
    assert not_found_version is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()


async def test_create_new_version_first(mock_db_session):
    """Test creating the first version for a content item."""
    item_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    item_id_str_no_hyphen = str(item_id).replace("-", "")  # For WHERE clause check
    team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    version_data = ContentVersionCreate(markdown_content="# Initial Content")
    new_version_id = PyUUID("dddddddd-1111-1111-1111-111111111111")

    # Simulate refresh adding attributes
    async def mock_refresh(obj, attribute_names=None):
        # Simulate ID generation after add/flush
        if isinstance(obj, ContentVersion) and "version_id" in attribute_names:
            obj.version_id = new_version_id
        elif isinstance(obj, ContentVersion):  # General refresh after commit
            obj.version_id = new_version_id  # Ensure ID persists if needed
            # Optionally simulate relationship loading if needed by assertions
            # obj.item = MagicMock(spec=ContentItem)
            # obj.saving_team = MagicMock(spec=Team)

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.flush = AsyncMock()
    mock_db_session.add = MagicMock()

    # Simulate execute for the UPDATE statement returning success (rowcount > 0)
    # The execute call happens *within* create_new_version
    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1  # Assume update succeeded
    # Configure execute to return the mock result when called
    mock_db_session.execute = AsyncMock(return_value=mock_update_result)

    with patch(
        "app.services.embedding_service.generate_embedding", return_value=[0.1, 0.2]
    ):
        created_version = await crud_content_version.create_new_version(
            db=mock_db_session,
            item_id=item_id,
            version_in=version_data,
            saved_by_team_id=team_id,
            is_initial_version=True,
        )

    # Check DB add call
    mock_db_session.add.assert_called_once()
    added_obj = mock_db_session.add.call_args[0][0]
    assert isinstance(added_obj, ContentVersion)
    assert added_obj.item_id == item_id
    assert added_obj.saved_by_team_id == team_id
    assert added_obj.markdown_content == version_data.markdown_content
    assert added_obj.version_number == 1  # Should be 1 for initial version
    assert added_obj.content_vector == [0.1, 0.2]

    # Check DB flush call (to get version_id before update)
    mock_db_session.flush.assert_awaited_once()

    # Check DB execute call for the UPDATE statement
    mock_db_session.execute.assert_awaited_once()
    update_call_args, _ = mock_db_session.execute.call_args
    update_stmt = update_call_args[0]
    assert isinstance(update_stmt, Update)  # Check it's an update statement
    compiled_update_str = str(
        update_stmt.compile(compile_kwargs={"literal_binds": True})
    )

    # *** FIX: Check SET and WHERE clauses correctly ***
    assert f"SET current_version_id = '{new_version_id}'" in compiled_update_str
    assert f"updated_at = now()" in compiled_update_str
    assert (
        f"WHERE content_items.item_id = '{item_id_str_no_hyphen}'"
        in compiled_update_str
    )

    # Check DB refresh call (after flush and update logic)
    # Refresh is called on the new_version object after flushing and after potential commit by caller
    # The exact number of calls depends on how refresh is used after commit in the caller
    assert mock_db_session.refresh.await_count >= 1

    # Check returned object
    assert created_version == added_obj
    assert (
        created_version.version_id == new_version_id
    )  # Ensure ID was set by refresh mock
    assert created_version.version_number == 1


async def test_create_new_version_subsequent(mock_db_session):
    """Test creating a subsequent version for a content item."""
    item_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    item_id_str_no_hyphen = str(item_id).replace("-", "")  # For WHERE clause check
    team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    version_data = ContentVersionCreate(markdown_content="# Updated Content V3")
    current_max_version = 2
    new_version_id = PyUUID("eeeeeeee-1111-1111-1111-111111111111")

    # Simulate finding the current max version number
    mock_max_version_result = MagicMock()
    mock_max_version_result.scalar_one.return_value = current_max_version

    # Simulate execute for the UPDATE statement
    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1

    # Set side effect for execute: first call returns max version, second returns update result
    mock_db_session.execute = AsyncMock(
        side_effect=[mock_max_version_result, mock_update_result]
    )

    # Simulate refresh adding attributes
    async def mock_refresh(obj, attribute_names=None):
        if isinstance(obj, ContentVersion) and "version_id" in attribute_names:
            obj.version_id = new_version_id
        elif isinstance(obj, ContentVersion):
            obj.version_id = new_version_id

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db_session.flush = AsyncMock()
    mock_db_session.add = MagicMock()

    with patch(
        "app.services.embedding_service.generate_embedding", return_value=[0.3, 0.4]
    ):
        created_version = await crud_content_version.create_new_version(
            db=mock_db_session,
            item_id=item_id,
            version_in=version_data,
            saved_by_team_id=team_id,
            is_initial_version=False,  # Not the initial version
        )

    # Check DB add call
    mock_db_session.add.assert_called_once()
    added_obj = mock_db_session.add.call_args[0][0]
    assert isinstance(added_obj, ContentVersion)
    assert added_obj.version_number == current_max_version + 1  # Should be incremented
    assert added_obj.content_vector == [0.3, 0.4]

    # Check DB flush call
    mock_db_session.flush.assert_awaited_once()

    # Check DB execute calls (max version query + update)
    assert mock_db_session.execute.await_count == 2

    # Check the max version query structure
    max_version_query = mock_db_session.execute.await_args_list[0].args[0]
    assert isinstance(max_version_query, Select)
    max_version_query_str = str(
        max_version_query.compile(compile_kwargs={"literal_binds": True})
    )
    assert "max(content_versions.version_number)" in max_version_query_str.lower()
    # *** FIX: Check WHERE clause with hyphenless UUID ***
    assert (
        f"WHERE content_versions.item_id = '{item_id_str_no_hyphen}'"
        in max_version_query_str
    )

    # Check the update query structure (similar to previous test)
    update_stmt = mock_db_session.execute.await_args_list[1].args[0]
    assert isinstance(update_stmt, Update)
    compiled_update_str = str(
        update_stmt.compile(compile_kwargs={"literal_binds": True})
    )
    # *** FIX: Check SET and WHERE clauses correctly ***
    assert f"SET current_version_id = '{new_version_id}'" in compiled_update_str
    assert f"updated_at = now()" in compiled_update_str
    assert (
        f"WHERE content_items.item_id = '{item_id_str_no_hyphen}'"
        in compiled_update_str
    )

    # Check DB refresh call
    assert mock_db_session.refresh.await_count >= 1

    # Check returned object
    assert created_version == added_obj
    assert created_version.version_id == new_version_id
    assert created_version.version_number == current_max_version + 1


async def test_get_versions_for_item(mock_db_session):
    """Test retrieving versions for an item with pagination and sorting."""
    test_item_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    test_item_id_str_no_hyphen = str(test_item_id).replace(
        "-", ""
    )  # For WHERE clause check
    version1 = create_test_content_version(
        version_number=1, version_id="cccccccc-1111-1111-1111-000000000001"
    )
    version2 = create_test_content_version(
        version_number=2, version_id="cccccccc-1111-1111-1111-000000000002"
    )
    expected_versions = [version2, version1]  # Assuming default desc sort
    total_count = 5

    # Mock the db calls
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = total_count  # Sync
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = expected_versions  # Sync

    # Setup execute to return count result first, then items result
    mock_db_session.execute = AsyncMock(
        side_effect=[mock_count_result, mock_items_result]
    )

    result_versions, result_count = await crud_content_version.get_versions_for_item(
        db=mock_db_session,
        item_id=test_item_id,
        skip=0,
        limit=10,
        sort_order="desc",  # Default
    )

    assert result_count == total_count
    assert result_versions == expected_versions
    assert mock_db_session.execute.await_count == 2

    # Inspect the queries passed to execute
    count_query_str = str(
        mock_db_session.execute.await_args_list[0]
        .args[0]
        .compile(compile_kwargs={"literal_binds": True})
    )
    items_query_str = str(
        mock_db_session.execute.await_args_list[1]
        .args[0]
        .compile(compile_kwargs={"literal_binds": True})
    )

    # *** FIX: Check filters with hyphenless UUID ***
    assert (
        f"WHERE content_versions.item_id = '{test_item_id_str_no_hyphen}'"
        in count_query_str
    )
    assert (
        f"WHERE content_versions.item_id = '{test_item_id_str_no_hyphen}'"
        in items_query_str
    )
    # Check sorting
    assert "ORDER BY content_versions.version_number DESC" in items_query_str
    # Check pagination
    assert "LIMIT 10" in items_query_str
    assert "OFFSET 0" in items_query_str


async def test_get_specific_version_by_number(mock_db_session):
    """Test retrieving a specific version by item ID and version number."""
    test_item_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    version_number_to_find = 3
    expected_version = create_test_content_version(
        item_id=str(test_item_id), version_number=version_number_to_find
    )

    # Correct Mock: Set return_value on the mocked method itself
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = (
        expected_version
    )

    found_version = await crud_content_version.get_specific_version_by_number(
        db=mock_db_session, item_id=test_item_id, version_number=version_number_to_find
    )

    assert found_version == expected_version
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    query_str = str(query.compile(compile_kwargs={"literal_binds": True}))
    assert f"content_versions.item_id = '{test_item_id}'" in query_str
    assert f"content_versions.version_number = {version_number_to_find}" in query_str

    # Test not found case
    mock_db_session.execute.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    not_found_version = await crud_content_version.get_specific_version_by_number(
        db=mock_db_session, item_id=test_item_id, version_number=99
    )
    assert not_found_version is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
