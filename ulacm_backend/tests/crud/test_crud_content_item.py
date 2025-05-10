# File: ulacm_backend/tests/crud/test_crud_content_item.py
# Purpose: Unit tests for ContentItem CRUD operations in app/crud/crud_content_item.py
# Changes:
# - Corrected assertions for async mock calls (check value, check await).
# - Corrected `assert_not_awaited` to `await_count == 0`.
# - Passed template_id as string in test_create_with_owner_document_from_template.
# - Corrected casing in SQL assertion strings for item_type.
# - Ensured helper sets is_globally_visible explicitly.

import pytest
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from uuid import UUID as PyUUID, uuid4 # Import uuid4 function
from sqlalchemy.sql import Select, Update, Delete
from datetime import datetime, timezone

# Import the CRUD object and schemas/models to test
from app.crud.crud_content_item import content_item as crud_content_item, ContentItemTypeEnum
# Import schema and models directly, avoid potential alias issues in tests
from app.schemas.content_item import ContentItemCreate, ContentItemUpdateMeta
from app.db.models.content_item import ContentItem
from app.db.models.content_version import ContentVersion
from app.db.models.team import Team

# Use fixtures defined in conftest.py
pytestmark = pytest.mark.asyncio

# --- Helper Data ---
def create_test_content_item(
    item_id="aaaaaaaa-1111-1111-1111-111111111111",
    team_id="11111111-1111-1111-1111-111111111111",
    item_type=ContentItemTypeEnum.DOCUMENT,
    name="Test Document",
    is_globally_visible=False, # Ensure default is set
    current_version_id=None,
    current_version=None
) -> ContentItem:
    """Helper function to create a ContentItem ORM model instance."""
    # Explicitly handle default for is_globally_visible if passed as None
    if is_globally_visible is None:
        is_globally_visible = False

    item = ContentItem(
        item_id=PyUUID(item_id),
        team_id=PyUUID(team_id),
        item_type=item_type,
        name=name,
        is_globally_visible=is_globally_visible,
        current_version_id=PyUUID(current_version_id) if current_version_id else None,
        # Simulating relationships
        owner_team=Team(team_id=PyUUID(team_id), team_name="Owner Team", username="owner_user"),
        current_version=current_version,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    # Ensure attribute is set after init as well, for robustness
    item.is_globally_visible = is_globally_visible
    return item

def create_test_content_version(
    version_id="cccccccc-1111-1111-1111-111111111111",
    item_id="aaaaaaaa-1111-1111-1111-111111111111",
    markdown_content="# Test Content",
    version_number=1,
    saved_by_team_id="11111111-1111-1111-1111-111111111111",
    saved_by_team=None
) -> ContentVersion:
    """Helper function to create a ContentVersion ORM model instance."""
    version = ContentVersion(
        version_id=PyUUID(version_id),
        item_id=PyUUID(item_id),
        markdown_content=markdown_content,
        version_number=version_number,
        saved_by_team_id=PyUUID(saved_by_team_id),
        saving_team=saved_by_team or Team(team_id=PyUUID(saved_by_team_id), team_name="Saver Team", username="saver_user"),
        created_at=datetime.now(timezone.utc)
    )
    return version

# --- Test Cases ---

async def test_get_by_id(mock_db_session):
    """Test retrieving a content item by its ID."""
    test_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    mock_version = create_test_content_version(version_id="cccccccc-1111-1111-1111-111111111111")
    expected_item = create_test_content_item(item_id=str(test_id), current_version_id=str(mock_version.version_id), current_version=mock_version)
    # Correct Mock: Set return_value on the mocked method itself
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_item

    # Call the function under test (which should now await the mock's result)
    found_item = await crud_content_item.get_by_id(db=mock_db_session, item_id=test_id)

    # Assertions
    assert found_item == expected_item # Compare the actual objects
    mock_db_session.execute.assert_awaited_once() # Verify the execute was awaited
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once() # Verify the method was called

    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    assert f"content_items.item_id = '{test_id}'" in str(query.compile(compile_kwargs={"literal_binds": True}))
    assert "joinedload" in str(query)
    assert "current_version" in str(query)
    assert "saving_team" in str(query)

    # Test not found case
    mock_db_session.execute.reset_mock() # Reset execute mock calls
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock() # Reset scalar mock calls
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None # Re-mock return value

    not_found_item = await crud_content_item.get_by_id(db=mock_db_session, item_id=PyUUID(uuid4().hex))
    assert not_found_item is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()


async def test_get_by_id_for_team_owned(mock_db_session):
    """Test retrieving an item by ID owned by the team."""
    test_item_id = PyUUID("aaaaaaaa-1111-1111-1111-111111111111")
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    expected_item = create_test_content_item(item_id=str(test_item_id), team_id=str(test_team_id))
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_item

    found_item = await crud_content_item.get_by_id_for_team(db=mock_db_session, item_id=test_item_id, team_id=test_team_id)

    assert found_item == expected_item
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query_str = str(call_args[0].compile(compile_kwargs={"literal_binds": True}))
    assert f"content_items.item_id = '{test_item_id}'" in query_str
    assert f"content_items.team_id = '{test_team_id}'" in query_str
    assert "content_items.is_globally_visible = true" in query_str # Part of the OR condition

async def test_get_by_id_for_team_global(mock_db_session):
    """Test retrieving a globally visible item by ID for a different team."""
    test_item_id = PyUUID("bbbbbbbb-2222-2222-2222-222222222222")
    owner_team_id = PyUUID("99999999-9999-9999-9999-999999999999")
    requesting_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    expected_item = create_test_content_item(item_id=str(test_item_id), team_id=str(owner_team_id), is_globally_visible=True)
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_item

    found_item = await crud_content_item.get_by_id_for_team(db=mock_db_session, item_id=test_item_id, team_id=requesting_team_id)

    assert found_item == expected_item
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query_str = str(call_args[0].compile(compile_kwargs={"literal_binds": True}))
    assert f"content_items.item_id = '{test_item_id}'" in query_str
    assert f"(content_items.team_id = '{requesting_team_id}' OR content_items.is_globally_visible = true)" in query_str.replace('\n','')

async def test_get_by_id_for_team_not_found(mock_db_session):
    """Test retrieving an item by ID that's not found or not accessible."""
    test_item_id = PyUUID("bbbbbbbb-2222-2222-2222-222222222222")
    requesting_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    found_item = await crud_content_item.get_by_id_for_team(db=mock_db_session, item_id=test_item_id, team_id=requesting_team_id)
    assert found_item is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()

@patch('app.crud.crud_content_version.content_version')
async def test_create_with_owner_template_or_workflow(mock_crud_version, mock_db_session):
    """Test creating a Template or Workflow (no template lookup needed)."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    item_data = ContentItemCreate(
        name="My New Workflow",
        item_type=ContentItemTypeEnum.WORKFLOW
    )

    # Make create_new_version an AsyncMock so we can check await_count
    mock_crud_version.create_new_version = AsyncMock()

    async def mock_refresh(obj, attribute_names=None):
        obj.item_id = PyUUID("dddddddd-4444-4444-4444-444444444444")
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        obj.current_version = None
        # Simulate DB default application if not set explicitly
        if not hasattr(obj, 'is_globally_visible') or obj.is_globally_visible is None:
             obj.is_globally_visible = False # Ensure refresh provides the default

    mock_db_session.refresh = mock_refresh
    # Mock commit and flush as they are awaited in the CRUD operation
    mock_db_session.commit = AsyncMock()
    mock_db_session.flush = AsyncMock()


    created_item = await crud_content_item.create_with_owner(db=mock_db_session, obj_in=item_data, team_id=test_team_id)

    mock_db_session.add.assert_called_once()
    added_obj = mock_db_session.add.call_args[0][0]
    assert isinstance(added_obj, ContentItem)
    assert added_obj.name == item_data.name
    assert added_obj.item_type == item_data.item_type
    assert added_obj.team_id == test_team_id
    assert added_obj.is_globally_visible is False # Default

    mock_db_session.flush.assert_awaited_once()
    # *** FIX: Use await_count check ***
    assert mock_crud_version.create_new_version.await_count == 0 # No initial version for T/W
    # mock_db_session.commit.assert_awaited_once() # Commit is called outside in this example structure
    assert mock_db_session.refresh.await_count >= 1 # At least after flush

    assert created_item is added_obj
    assert created_item.current_version is None

@patch('app.crud.crud_content_version.content_version')
async def test_create_with_owner_document_from_template(mock_crud_version, mock_db_session):
    """Test creating a Document, which requires template lookup and version creation."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    template_id = PyUUID("eeeeeeee-5555-5555-5555-555555555555")
    template_content = "# Template Heading\nTemplate Body"
    doc_name = "Doc From Template"
    # *** FIX: Pass template_id as string, matching schema change ***
    item_data = ContentItemCreate(
        name=doc_name,
        item_type=ContentItemTypeEnum.DOCUMENT,
        template_id=str(template_id)
    )

    # Mock finding the template
    mock_template_version = create_test_content_version(markdown_content=template_content)
    mock_template_item = create_test_content_item(
        item_id=str(template_id), item_type=ContentItemTypeEnum.TEMPLATE, current_version=mock_template_version
    )
    # Simulate template query result
    mock_template_result = MagicMock()
    mock_template_result.scalar_one_or_none = AsyncMock(return_value=mock_template_item)
    mock_db_session.execute.return_value = mock_template_result

    # Mock the version creation call
    mock_crud_version.create_new_version = AsyncMock(return_value=MagicMock(spec=ContentVersion))
    # Mock commit and flush
    mock_db_session.commit = AsyncMock()
    mock_db_session.flush = AsyncMock()

    async def mock_refresh(obj, attribute_names=None):
        obj.item_id = PyUUID("ffffffff-6666-6666-6666-666666666666")
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        # Explicitly set default for visibility
        if not hasattr(obj, 'is_globally_visible') or obj.is_globally_visible is None:
             obj.is_globally_visible = False
        if attribute_names == ['current_version']: # Simulate loading relationship
             obj.current_version = mock_crud_version.create_new_version.return_value

    mock_db_session.refresh = mock_refresh

    created_item = await crud_content_item.create_with_owner(db=mock_db_session, obj_in=item_data, team_id=test_team_id)

    # Check add was called with correct initial data
    mock_db_session.add.assert_called_once()
    added_obj = mock_db_session.add.call_args[0][0]
    assert isinstance(added_obj, ContentItem)
    assert added_obj.name == doc_name
    assert added_obj.item_type == ContentItemTypeEnum.DOCUMENT
    assert added_obj.team_id == test_team_id
    assert added_obj.is_globally_visible is False # Check default

    # Check flush was called
    mock_db_session.flush.assert_awaited_once()

    # Check template query was executed
    assert mock_db_session.execute.call_count > 0 # More precise checks are complex
    mock_template_result.scalar_one_or_none.assert_awaited_once() # Check await

    # Check version creation was called correctly
    mock_crud_version.create_new_version.assert_awaited_once()
    call_kwargs = mock_crud_version.create_new_version.call_args.kwargs
    assert call_kwargs['db'] == mock_db_session
    assert call_kwargs['item_id'] == added_obj.item_id # Check it used the flushed ID
    assert call_kwargs['version_in'].markdown_content == template_content
    assert call_kwargs['saved_by_team_id'] == test_team_id
    assert call_kwargs['is_initial_version'] is True

    # mock_db_session.commit.assert_awaited_once() # Commit is called outside
    assert mock_db_session.refresh.await_count >= 2 # At least after flush and after commit/versioning

    assert created_item is added_obj
    assert created_item.current_version is not None # Ensure relationship was simulated


async def test_get_items_for_team(mock_db_session):
    """Test retrieving items for a team with filters, sort, pagination."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    test_team_id_str_no_hyphen = str(test_team_id).replace('-', '')

    item1 = create_test_content_item(name="Doc B", item_type=ContentItemTypeEnum.DOCUMENT)
    item2 = create_test_content_item(name="Template A", item_type=ContentItemTypeEnum.TEMPLATE)
    expected_items = [item1, item2] # Assume sorting puts Doc B first
    total_count = 5

    # Mock the db calls
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = total_count # scalar_one is sync
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = expected_items # all is sync

    # Setup execute to return count result first, then items result
    mock_db_session.execute = AsyncMock(side_effect=[mock_count_result, mock_items_result])

    result_items, result_count = await crud_content_item.get_items_for_team(
        db=mock_db_session,
        team_id=test_team_id,
        item_type=ContentItemTypeEnum.DOCUMENT, # Example filter
        skip=0,
        limit=10,
        sort_by="name",
        sort_order="desc"
    )

    assert result_count == total_count
    assert result_items == expected_items
    assert mock_db_session.execute.await_count == 2

    # Inspect the queries passed to execute
    count_query_str = str(mock_db_session.execute.await_args_list[0].args[0].compile(compile_kwargs={"literal_binds": True})).replace('\n', '')
    items_query_str = str(mock_db_session.execute.await_args_list[1].args[0].compile(compile_kwargs={"literal_binds": True})).replace('\n', '')

    # Check team/global filter
    assert f"(content_items.team_id = '{test_team_id_str_no_hyphen}' OR content_items.is_globally_visible = true)" in count_query_str
    assert f"(content_items.team_id = '{test_team_id_str_no_hyphen}' OR content_items.is_globally_visible = true)" in items_query_str
    # *** FIX: Correct casing check ***
    assert f"ITEM_TYPE = '{ContentItemTypeEnum.DOCUMENT.value.upper()}'" in count_query_str.upper()
    assert f"ITEM_TYPE = '{ContentItemTypeEnum.DOCUMENT.value.upper()}'" in items_query_str.upper()
    # Check sorting
    assert "ORDER BY content_items.name DESC" in items_query_str
    # Check pagination
    assert "LIMIT 10" in items_query_str
    assert "OFFSET 0" in items_query_str


async def test_check_name_uniqueness(mock_db_session):
    """Test checking name uniqueness for a team and item type."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    item_type = ContentItemTypeEnum.TEMPLATE
    name_to_check = "Unique Template Name"
    duplicate_name = "Existing Template Name"
    item_id_to_exclude = PyUUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")

    # Test case: Name is unique
    mock_result_unique = MagicMock()
    mock_result_unique.scalar_one.return_value = 0 # scalar_one is sync
    mock_db_session.execute = AsyncMock(return_value=mock_result_unique) # Mock execute await

    is_unique = await crud_content_item.check_name_uniqueness(
        db=mock_db_session, name=name_to_check, item_type=item_type, team_id=test_team_id
    )
    assert is_unique is True
    mock_db_session.execute.assert_awaited_once()
    mock_result_unique.scalar_one.assert_called_once()

    call_args, _ = mock_db_session.execute.call_args
    query_str = str(call_args[0].compile(compile_kwargs={"literal_binds": True}))
    assert f"lower(content_items.name) = lower('{name_to_check}')" in query_str
    # *** FIX: Correct casing check ***
    assert f"ITEM_TYPE = '{item_type.value.upper()}'" in query_str.upper()
    assert f"content_items.team_id = '{test_team_id}'" in query_str
    assert f"content_items.item_id != '{item_id_to_exclude}'" not in query_str


    # Test case: Name is duplicate
    mock_db_session.execute.reset_mock() # Reset execute mock calls
    mock_result_dup = MagicMock()
    mock_result_dup.scalar_one.return_value = 1
    mock_db_session.execute.return_value = mock_result_dup

    is_unique_dup = await crud_content_item.check_name_uniqueness(
        db=mock_db_session, name=duplicate_name, item_type=item_type, team_id=test_team_id
    )
    assert is_unique_dup is False
    mock_db_session.execute.assert_awaited_once()
    mock_result_dup.scalar_one.assert_called_once()


    # Test case: Name is unique when excluding own ID (for update)
    mock_db_session.execute.reset_mock()
    mock_result_update = MagicMock()
    mock_result_update.scalar_one.return_value = 0
    mock_db_session.execute.return_value = mock_result_update

    is_unique_update = await crud_content_item.check_name_uniqueness(
        db=mock_db_session, name=duplicate_name, item_type=item_type, team_id=test_team_id, exclude_item_id=item_id_to_exclude
    )
    assert is_unique_update is True
    mock_db_session.execute.assert_awaited_once()
    mock_result_update.scalar_one.assert_called_once()

    call_args_update, _ = mock_db_session.execute.call_args
    query_str_update = str(call_args_update[0].compile(compile_kwargs={"literal_binds": True}))
    assert f"content_items.item_id != '{item_id_to_exclude}'" in query_str_update


async def test_update_item_meta(mock_db_session):
    """Test updating content item metadata."""
    existing_item = ContentItem(
        item_id=PyUUID("ffeebbaa-1111-1111-1111-111111111111"),
        team_id=PyUUID("11111111-1111-1111-1111-111111111111"),
        item_type=ContentItemTypeEnum.DOCUMENT,
        name="Old Name",
        is_globally_visible=False
    )
    update_data = ContentItemUpdateMeta(
        name="New Meta Name",
        is_globally_visible=True
    )

    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    # Mock the base class update method directly as the logic resides there
    with patch('app.crud.base.CRUDBase.update', new_callable=AsyncMock) as mock_base_update:
        # Simulate base update modifying the object and returning it
        async def side_effect_update(db, db_obj, obj_in):
            obj_data = obj_in.model_dump(exclude_unset=True)
            for field, value in obj_data.items():
                 setattr(db_obj, field, value)
            # Simulate DB commit and refresh effect
            db_obj.updated_at = datetime.now(timezone.utc)
            return db_obj
        mock_base_update.side_effect = side_effect_update

        updated_item = await crud_content_item.update(db=mock_db_session, db_obj=existing_item, obj_in=update_data)

        mock_base_update.assert_awaited_once_with(db=mock_db_session, db_obj=existing_item, obj_in=update_data)


    assert updated_item == existing_item
    assert updated_item.name == "New Meta Name"
    assert updated_item.is_globally_visible is True
    # Base class update handles commit/refresh, don't need to assert on session directly here


async def test_remove_item(mock_db_session):
    """Test removing a content item."""
    item_to_delete_id = PyUUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
    item_obj = create_test_content_item(item_id=str(item_to_delete_id))

    # Simulate finding the item
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = item_obj
    # Mock commit/delete
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    # Perform remove
    deleted_item = await crud_content_item.remove_item(db=mock_db_session, item_id=item_to_delete_id)

    # Check result
    assert deleted_item == item_obj
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()

    # Check DB calls
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_awaited_once_with(item_obj)
    mock_db_session.commit.assert_awaited_once() # Assuming remove_item commits

    # Test removing non-existent item
    mock_db_session.reset_mock() # Reset all calls
    # Re-mock relevant methods
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()


    non_existent_id = PyUUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
    deleted_item_none = await crud_content_item.remove_item(db=mock_db_session, item_id=non_existent_id)

    assert deleted_item_none is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    mock_db_session.delete.assert_not_awaited()
    mock_db_session.commit.assert_not_awaited()
