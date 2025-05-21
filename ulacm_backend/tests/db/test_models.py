# File: ulacm_backend/tests/db/test_models.py
# Purpose: Unit tests for SQLAlchemy database models.
# Changes:
# - Imported the `uuid` module.
# - Changed `UUID4()` to `uuid.uuid4()` for generating a new UUID.
# - Ensured consistent UUID object usage for IDs.
# - Corrected relationship assignment test to set FKs explicitly.

import pytest
from datetime import datetime, timezone
from uuid import UUID as PyUUID, uuid4 # Import uuid4 function as well
import uuid # <-- Import the uuid module

# Import models to test
from app.db.models.team import Team
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.db.base_class import Base # Import base if testing its functionality

# --- Constants for IDs (Using PyUUID directly) ---
TEST_TEAM_ID = PyUUID("11111111-1111-1111-1111-111111111111")
TEST_ITEM_ID = PyUUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
TEST_VERSION_ID = PyUUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
TEST_SAVER_TEAM_ID = PyUUID("22222222-2222-2222-2222-222222222222")

# --- Test Cases ---

def test_team_model_creation():
    """Test creating an instance of the Team model."""
    now = datetime.now(timezone.utc)
    team = Team(
        team_id=TEST_TEAM_ID,
        team_name="Test Team",
        username="testuser",
        hashed_password="hashed_pw",
        is_active=True,
        created_at=now,
        updated_at=now
    )
    assert team.team_id == TEST_TEAM_ID
    assert team.team_name == "Test Team"
    assert team.username == "testuser"
    assert team.hashed_password == "hashed_pw"
    assert team.is_active is True
    assert team.created_at == now
    assert team.updated_at == now
    # Check relationship attributes exist (will be None or empty lists initially)
    assert hasattr(team, 'owned_content_items')
    assert hasattr(team, 'saved_versions')
    assert team.owned_content_items == [] # Default for InstrumentedList
    assert team.saved_versions == []

def test_content_item_model_creation():
    """Test creating instances of the ContentItem model for different types."""
    now = datetime.now(timezone.utc)

    # Document type
    doc = ContentItem(
        item_id=TEST_ITEM_ID,
        team_id=TEST_TEAM_ID,
        item_type=ContentItemTypeEnum.DOCUMENT,
        name="Test Document",
        is_globally_visible=False,
        current_version_id=None,
        created_at=now,
        updated_at=now
    )
    assert doc.item_id == TEST_ITEM_ID
    assert doc.team_id == TEST_TEAM_ID
    assert doc.item_type == ContentItemTypeEnum.DOCUMENT
    assert doc.name == "Test Document"
    assert doc.is_globally_visible is False
    assert doc.current_version_id is None
    assert hasattr(doc, 'owner_team')
    assert hasattr(doc, 'versions')
    assert hasattr(doc, 'current_version')

    # Template type
    template = ContentItem(
        # item_id should ideally be set by DB or assigned manually after init for tests
        team_id=TEST_TEAM_ID,
        item_type=ContentItemTypeEnum.TEMPLATE,
        name="Test Template",
        is_globally_visible=True,
        current_version_id=TEST_VERSION_ID, # Keep this if testing FK assignment
        created_at=now,
        updated_at=now
    )
    # Fix: Assign a generated UUID using uuid.uuid4()
    template.item_id = uuid.uuid4()
    assert isinstance(template.item_id, PyUUID) # Check it's a UUID object
    assert template.item_type == ContentItemTypeEnum.TEMPLATE
    assert template.is_globally_visible is True
    assert template.current_version_id == TEST_VERSION_ID

    # Workflow type
    workflow = ContentItem(
        team_id=TEST_TEAM_ID,
        item_type=ContentItemTypeEnum.WORKFLOW,
        name="Test Workflow"
        # No need for created_at/updated_at if using DB defaults, but ok for unit test
    )
    workflow.item_id = uuid.uuid4() # Example: Assign after if needed
    assert workflow.item_type == ContentItemTypeEnum.WORKFLOW
    assert isinstance(workflow.item_id, PyUUID)

def test_content_version_model_creation():
    """Test creating an instance of the ContentVersion model."""
    now = datetime.now(timezone.utc)
    version = ContentVersion(
        version_id=TEST_VERSION_ID,
        item_id=TEST_ITEM_ID,
        markdown_content="# Title\nContent here.",
        version_number=5,
        saved_by_team_id=TEST_SAVER_TEAM_ID,
        created_at=now
    )
    assert version.version_id == TEST_VERSION_ID
    assert version.item_id == TEST_ITEM_ID
    assert version.markdown_content == "# Title\nContent here."
    assert version.version_number == 5
    assert version.saved_by_team_id == TEST_SAVER_TEAM_ID
    assert version.created_at == now
    assert hasattr(version, 'item')
    assert hasattr(version, 'saving_team')

def test_relationships_assignment():
    """Test assigning related objects to relationship attributes."""
    team_owner = Team(team_id=TEST_TEAM_ID, team_name="Owner")
    team_saver = Team(team_id=TEST_SAVER_TEAM_ID, team_name="Saver")
    item = ContentItem(item_id=TEST_ITEM_ID, team_id=TEST_TEAM_ID)
    version = ContentVersion(
        version_id=TEST_VERSION_ID,
        item_id=TEST_ITEM_ID, # Ensure FK matches item's PK
        saved_by_team_id=TEST_SAVER_TEAM_ID, # Ensure FK matches saver's PK
        version_number=1,
        markdown_content="V1"
    )

    # Assign relationships
    item.owner_team = team_owner
    item.versions.append(version) # Append to list-based relationship
    item.current_version = version
    # Explicitly set the foreign key ID when setting the relationship object
    item.current_version_id = version.version_id
    version.item = item
    version.saving_team = team_saver

    # Check assignments (doesn't check DB loading)
    assert item.owner_team == team_owner
    assert item.team_id == team_owner.team_id # FK should ideally match
    assert len(item.versions) == 1
    assert item.versions[0] == version
    assert item.current_version == version
    assert item.current_version_id == version.version_id # FK should match

    assert version.item == item
    assert version.item_id == item.item_id # FK should match
    assert version.saving_team == team_saver
    assert version.saved_by_team_id == team_saver.team_id # FK should match

    # Check back-populates (if applicable and correctly simulated)
    # These depend on SQLAlchemy session state normally
    # assert item in team_owner.owned_content_items # This won't work without a session usually
    # assert version in team_saver.saved_versions

def test_base_asdict_method():
    """Test the _asdict helper method from the Base class."""
    now = datetime.now(timezone.utc)
    team = Team(
        team_id=TEST_TEAM_ID,
        team_name="Dict Team",
        username="dictuser",
        hashed_password="pw",
        is_active=False,
        created_at=now,
        updated_at=now
    )
    # Simulate being bound to a session state for inspect() to work fully
    # This is a simplified check for the method's existence and basic functionality
    # A more robust test would involve an actual session or mocking inspect()
    team_dict = team._asdict()

    expected_keys = {'team_id', 'team_name', 'username', 'hashed_password', 'is_active', 'created_at', 'updated_at'}
    # Filter out internal SQLAlchemy state attributes if they appear
    actual_keys = {k for k in team_dict.keys() if not k.startswith('_sa_')}

    assert actual_keys.issuperset(expected_keys) # Check if expected keys are present
    assert team_dict['team_id'] == TEST_TEAM_ID
    assert team_dict['team_name'] == "Dict Team"
    assert team_dict['username'] == "dictuser"
    assert team_dict['hashed_password'] == "pw"
    assert team_dict['is_active'] is False
    assert team_dict['created_at'] == now
    assert team_dict['updated_at'] == now

def test_tablename_generation():
    """Test automatic table name generation from the Base class."""
    assert Team.__tablename__ == "teams"
    assert ContentItem.__tablename__ == "content_items"
    assert ContentVersion.__tablename__ == "content_versions"
