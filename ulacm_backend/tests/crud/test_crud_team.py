# File: ulacm_backend/tests/crud/test_crud_team.py
# Purpose: Unit tests for Team CRUD operations in app/crud/crud_team.py
# Changes:
# - Corrected mock setup for scalar_one_or_none to return values directly when awaited.
# - Added assertions to check that the mock methods were awaited.
# - Corrected mock setup for refresh in test_update_team_with_password.
# - Corrected UUID creation/passing in test_get_all_teams helper call.

import pytest
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from uuid import UUID as PyUUID, uuid4 # Import uuid4 function
from sqlalchemy.sql import Select, Update, Delete # Added Update/Delete
from datetime import datetime, timezone

# Import the CRUD object and schemas/models to test
from app.crud.crud_team import team as crud_team
from app.schemas.team import TeamCreate, TeamUpdate
from app.db.models.team import Team

# Use fixtures defined in conftest.py
pytestmark = pytest.mark.asyncio

# --- Helper Data ---
def create_test_team(
    team_id: PyUUID, # Accept UUID object directly
    team_name="Test Team Alpha",
    username="test_alpha_user",
    hashed_password="hashed_password_abc",
    is_active=True,
    created_at=None,
    updated_at=None,
) -> Team:
    """Helper function to create a Team ORM model instance for testing."""
    # The helper now accepts a PyUUID object directly
    return Team(
        team_id=team_id, # Use the passed UUID object
        team_name=team_name,
        username=username,
        hashed_password=hashed_password,
        is_active=is_active,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=updated_at or datetime.now(timezone.utc),
    )

# --- Test Cases ---

async def test_get_team_by_username(mock_db_session):
    """Test retrieving a team by username."""
    test_username = "test_user_1"
    expected_team = create_test_team(team_id=uuid4(), username=test_username) # Generate ID here
    # Correct Mock: Set return_value on the mocked method itself
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_team

    found_team = await crud_team.get_by_username(db=mock_db_session, username="Test_User_1")

    assert found_team == expected_team
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    assert "lower(teams.username)" in str(query.compile(compile_kwargs={"literal_binds": True}))
    assert f"lower('{test_username}')" in str(query.compile(compile_kwargs={"literal_binds": True}))

    # Test not found case
    mock_db_session.execute.reset_mock() # Reset execute mock calls
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock() # Reset scalar mock calls
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None # Re-mock return value
    not_found_team = await crud_team.get_by_username(db=mock_db_session, username="non_existent_user")
    assert not_found_team is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()


async def test_get_team_by_team_name(mock_db_session):
    """Test retrieving a team by team name."""
    test_team_name = "Awesome Project Team"
    expected_team = create_test_team(team_id=uuid4(), team_name=test_team_name)
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_team

    found_team = await crud_team.get_by_team_name(db=mock_db_session, team_name="awesome project team")

    assert found_team == expected_team
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    assert "lower(teams.team_name)" in str(query.compile(compile_kwargs={"literal_binds": True}))
    assert f"lower('{test_team_name}')" in str(query.compile(compile_kwargs={"literal_binds": True}))

    # Test not found case
    mock_db_session.execute.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    not_found_team = await crud_team.get_by_team_name(db=mock_db_session, team_name="Another Team")
    assert not_found_team is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()

async def test_get_team_by_id(mock_db_session):
    """Test retrieving a team by ID."""
    test_id = PyUUID("22222222-2222-2222-2222-222222222222")
    expected_team = create_test_team(team_id=test_id) # Pass UUID directly
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = expected_team

    found_team = await crud_team.get_by_id(db=mock_db_session, team_id=test_id)
    assert found_team == expected_team
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    call_args, _ = mock_db_session.execute.call_args
    query = call_args[0]
    assert isinstance(query, Select)
    assert f"teams.team_id = '{test_id}'" in str(query.compile(compile_kwargs={"literal_binds": True}))

    # Test not found case
    mock_db_session.execute.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.reset_mock()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    not_found_id = PyUUID("33333333-3333-3333-3333-333333333333")
    not_found_team = await crud_team.get_by_id(db=mock_db_session, team_id=not_found_id)
    assert not_found_team is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()

@patch('app.crud.crud_team.get_password_hash', return_value="hashed_new_password")
async def test_create_team(mock_get_password_hash, mock_db_session):
    """Test creating a new team."""
    team_data = TeamCreate(
        team_name="New Unique Team",
        username="new_unique_user",
        password="new_password_123"
    )
    # Mock commit and add for create
    mock_db_session.commit = AsyncMock()
    mock_db_session.add = MagicMock()

    # Simulate refresh adding attributes to the passed object
    async def mock_refresh(obj, attribute_names=None):
        obj.team_id = PyUUID("44444444-4444-4444-4444-444444444444")
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        obj.is_active = True # Default

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh) # Make refresh mock awaitable

    created_team = await crud_team.create(db=mock_db_session, obj_in=team_data)

    # Check password hashing was called
    mock_get_password_hash.assert_called_once_with(team_data.password)

    # Check database operations
    mock_db_session.add.assert_called_once()
    added_obj = mock_db_session.add.call_args[0][0]
    assert isinstance(added_obj, Team)
    assert added_obj.team_name == team_data.team_name
    assert added_obj.username == team_data.username
    assert added_obj.hashed_password == "hashed_new_password"

    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(added_obj) # Check refresh was awaited

    # Check returned object
    assert created_team is added_obj
    assert created_team.team_name == team_data.team_name
    assert created_team.hashed_password == "hashed_new_password"
    assert hasattr(created_team, 'team_id')

@patch('app.crud.crud_team.get_password_hash', return_value="hashed_updated_password")
async def test_update_team_with_password(mock_get_password_hash, mock_db_session):
    """Test updating a team, including the password."""
    existing_team_id = uuid4()
    existing_team = create_test_team(team_id=existing_team_id)
    update_data = TeamUpdate(
        team_name="Updated Test Team Alpha",
        password="updated_password_456"
    )

    # *** FIX: Use AsyncMock for refresh to allow assert_awaited_once_with ***
    mock_db_session.refresh = AsyncMock()
    mock_db_session.add = MagicMock() # if using add
    mock_db_session.commit = AsyncMock() # Mock commit needed for base update

    # Mock the base class update method directly
    with patch('app.crud.base.CRUDBase.update', new_callable=AsyncMock) as mock_base_update:
        # Simulate base update modifying the object and returning it
        async def side_effect_update(db, db_obj, obj_in):
            obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            for field, value in obj_data.items():
                 setattr(db_obj, field, value)
            db_obj.updated_at = datetime.now(timezone.utc)
            # Simulate the commit and refresh that base class does
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        mock_base_update.side_effect = side_effect_update

        updated_team = await crud_team.update(db=mock_db_session, db_obj=existing_team, obj_in=update_data)

        # Check password hashing was called
        mock_get_password_hash.assert_called_once_with(update_data.password)

        # Check base update call (which includes hashing logic internally for Team)
        mock_base_update.assert_awaited_once()
        # Check the arguments passed to the base update
        base_call_args, base_call_kwargs = mock_base_update.call_args
        assert base_call_kwargs['db'] == mock_db_session
        assert base_call_kwargs['db_obj'] == existing_team
        assert base_call_kwargs['obj_in']['team_name'] == update_data.team_name
        assert base_call_kwargs['obj_in']['hashed_password'] == "hashed_updated_password" # Hashed pw passed to base
        assert "password" not in base_call_kwargs['obj_in'] # Plain password removed


    # Check object attributes were updated (by the mocked side_effect)
    assert updated_team.team_name == update_data.team_name
    assert updated_team.hashed_password == "hashed_updated_password"
    assert updated_team.username == "test_alpha_user" # Ensure username wasn't touched

    # Assertions on session handled by base class mock's simulated behavior
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(existing_team)

    assert updated_team is existing_team

@patch('app.crud.crud_team.get_password_hash')
async def test_update_team_without_password(mock_get_password_hash, mock_db_session):
    """Test updating a team without changing the password."""
    original_hashed_password = "original_hashed_pw"
    existing_team_id = uuid4()
    existing_team = create_test_team(team_id=existing_team_id, hashed_password=original_hashed_password)
    update_data = TeamUpdate(
        team_name="Only Name Changed"
    )

    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock() # Make refresh awaitable

    # Mock the base class update method directly
    with patch('app.crud.base.CRUDBase.update', new_callable=AsyncMock) as mock_base_update:
        async def side_effect_update(db, db_obj, obj_in):
            obj_data = obj_in.model_dump(exclude_unset=True)
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            db_obj.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        mock_base_update.side_effect = side_effect_update

        updated_team = await crud_team.update(db=mock_db_session, db_obj=existing_team, obj_in=update_data)

        mock_get_password_hash.assert_not_called() # Check password hashing was NOT called
        mock_base_update.assert_awaited_once()
        base_call_args, base_call_kwargs = mock_base_update.call_args
        assert base_call_kwargs['obj_in']['team_name'] == update_data.team_name
        assert "password" not in base_call_kwargs['obj_in']
        assert "hashed_password" not in base_call_kwargs['obj_in']


    assert updated_team.team_name == update_data.team_name
    assert updated_team.hashed_password == original_hashed_password # Password unchanged
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(existing_team)
    assert updated_team is existing_team

async def test_get_all_teams(mock_db_session):
    """Test retrieving multiple teams with pagination."""
    # *** FIX: Pass generated UUIDs directly ***
    team1 = create_test_team(team_id=uuid4(), username="user1")
    team2 = create_test_team(team_id=uuid4(), username="user2")
    expected_teams = [team1, team2]
    total_count = 25

    # Mock the db calls for the base class method get_multi_with_total_count
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = total_count # scalar_one is sync
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = expected_teams # all is sync

    mock_db_session.execute = AsyncMock(side_effect=[mock_count_result, mock_items_result])

    result_teams, result_count = await crud_team.get_all_teams(db=mock_db_session, skip=10, limit=5)

    assert result_count == total_count
    assert result_teams == expected_teams
    assert mock_db_session.execute.await_count == 2

    # Optionally check query details for count and items select
    count_call_args = mock_db_session.execute.await_args_list[0].args[0]
    items_call_args = mock_db_session.execute.await_args_list[1].args[0]
    assert "count(" in str(count_call_args.compile(compile_kwargs={"literal_binds": True})).lower()
    assert "LIMIT 5" in str(items_call_args.compile(compile_kwargs={"literal_binds": True}))
    assert "OFFSET 10" in str(items_call_args.compile(compile_kwargs={"literal_binds": True}))

async def test_activate_deactivate_team(mock_db_session):
    """Test activating and deactivating a team."""
    team_obj = create_test_team(team_id=uuid4(), is_active=True)
    mock_db_session.refresh = AsyncMock() # Mock refresh needed
    mock_db_session.commit = AsyncMock() # Mock commit needed
    mock_db_session.add = MagicMock() # Mock add

    # Deactivate
    updated_team_inactive = await crud_team.activate_deactivate_team(db=mock_db_session, team=team_obj, is_active=False)
    assert updated_team_inactive.is_active is False
    assert mock_db_session.add.call_count == 1
    assert mock_db_session.commit.await_count == 1
    assert mock_db_session.refresh.await_count == 1
    mock_db_session.refresh.assert_awaited_with(team_obj)
    # Reset mocks for next call
    mock_db_session.reset_mock()
    mock_db_session.refresh = AsyncMock() # Re-mock refresh
    mock_db_session.commit = AsyncMock() # Re-mock commit
    mock_db_session.add = MagicMock() # Re-mock add


    # Activate
    updated_team_active = await crud_team.activate_deactivate_team(db=mock_db_session, team=team_obj, is_active=True)
    assert updated_team_active.is_active is True
    assert mock_db_session.add.call_count == 1
    assert mock_db_session.commit.await_count == 1
    assert mock_db_session.refresh.await_count == 1
    mock_db_session.refresh.assert_awaited_with(team_obj)

    assert updated_team_inactive is team_obj
    assert updated_team_active is team_obj


async def test_remove_team(mock_db_session):
    """Test removing a team."""
    team_to_delete_id = PyUUID("55555555-5555-5555-5555-555555555555")
    team_obj = create_test_team(team_id=team_to_delete_id) # Pass UUID directly

    # Simulate finding the team
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = team_obj
    # Mock commit/delete
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    # Perform remove
    deleted_team = await crud_team.remove_team(db=mock_db_session, team_id=team_to_delete_id)

    # Check result
    assert deleted_team == team_obj
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()

    # Check DB calls
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.delete.assert_awaited_once_with(team_obj)
    mock_db_session.commit.assert_awaited_once() # Assuming remove_team commits

    # Test removing non-existent team
    mock_db_session.reset_mock() # Reset all calls
    # Re-mock relevant methods
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    mock_db_session.delete = AsyncMock()
    mock_db_session.commit = AsyncMock()

    non_existent_id = PyUUID("66666666-6666-6666-6666-666666666666")
    deleted_team_none = await crud_team.remove_team(db=mock_db_session, team_id=non_existent_id)

    assert deleted_team_none is None
    mock_db_session.execute.return_value.scalar_one_or_none.assert_called_once()
    mock_db_session.delete.assert_not_awaited()
    mock_db_session.commit.assert_not_awaited()
