# File: ulacm_backend/tests/services/test_workflow_service.py
# Purpose: Unit tests for workflow_service functions.
# Changes:
# - Corrected mock setup in test_select_input_documents.
# - Corrected patch targets in test_ensure_unique_output_name,
#   test_execute_workflow_success, and test_execute_workflow_output_creation_error.
# - Removed global pytestmark, added @pytest.mark.asyncio to async tests only.
# - Corrected UUID comparison in test_select_input_documents assertion.
# - Added rollback assertions to error tests.

import pytest
import datetime
from datetime import timezone, timedelta # Ensure timedelta is imported
from freezegun import freeze_time
from unittest.mock import patch, AsyncMock, MagicMock, call
from uuid import UUID as PyUUID, uuid4 # Import uuid4 function

# Import the functions/classes/exceptions to test
from app.services import workflow_service # Keep this? Or import specifics? Let's import specifics.
from app.services.workflow_service import (
    _filter_by_date_selector,
    _match_glob_pattern,
    _select_input_documents,
    _construct_prompt,
    _generate_output_name,
    _ensure_unique_output_name,
    execute_workflow,
    MAX_UNIQUE_NAME_ATTEMPTS # Import constant
)
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition
from app.services.ollama_service import OllamaServiceError
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.db.models.team import Team
from app.schemas.content_version import ContentVersionCreate

# Use fixtures defined in conftest.py if needed
# pytestmark = pytest.mark.asyncio # <-- REMOVED global marker


# Use freeze_time to make tests deterministic regardless of when they run
FROZEN_TIME_STR = "2025-05-08 12:00:00+00:00" # Thursday, May 8, 2025 12:00 UTC
FROZEN_TIME_DT = datetime.datetime.fromisoformat(FROZEN_TIME_STR)


# --- Helper Data & Fixtures ---
def create_test_content_version(
    version_id_str="cccccccc-1111-1111-1111-111111111111",
    item_id_str="aaaaaaaa-1111-1111-1111-111111111111",
    markdown_content="# Test Content V1",
    version_number=1,
    saved_by_team_id_str="11111111-1111-1111-1111-111111111111",
    created_at=None
) -> ContentVersion:
    """Helper function to create a ContentVersion ORM model instance."""
    return ContentVersion(
        version_id=PyUUID(version_id_str),
        item_id=PyUUID(item_id_str),
        markdown_content=markdown_content,
        version_number=version_number,
        saved_by_team_id=PyUUID(saved_by_team_id_str),
        created_at=created_at or datetime.datetime.now(timezone.utc)
    )

def create_test_content_item(
    item_id_str="aaaaaaaa-1111-1111-1111-111111111111",
    team_id_str="11111111-1111-1111-1111-111111111111",
    item_type=ContentItemTypeEnum.DOCUMENT,
    name="Test Document",
    is_globally_visible=False,
    current_version=None,
    created_at=None,
    updated_at=None
) -> ContentItem:
    """Helper function to create a ContentItem ORM model instance."""
    current_version_id = current_version.version_id if current_version else None
    item = ContentItem(
        item_id=PyUUID(item_id_str),
        team_id=PyUUID(team_id_str),
        item_type=item_type,
        name=name,
        is_globally_visible=is_globally_visible,
        current_version_id=current_version_id,
        current_version=current_version,
        created_at=created_at or datetime.datetime.now(timezone.utc),
        updated_at=updated_at or datetime.datetime.now(timezone.utc)
    )
    return item

@pytest.fixture
def sample_workflow_item() -> ContentItem:
    """Fixture for a sample workflow ContentItem with a version."""
    workflow_def_content = """
processWorkFlowName: Test Workflow
trigger: manual
inputDocumentSelector: "Input_Doc_*"
inputDateSelector: newerThanDays 7
model: ollama/test-model
temperature: 0.6
outputName: Output_{{Year}}-{{Month}}-{{Day}}.md
prompt: |
  Process context: {{DocumentContext}}
  Input names: {{InputFileNames}}
  Input count: {{InputFileCount}}
"""
    version = create_test_content_version(markdown_content=workflow_def_content)
    workflow = create_test_content_item(
        item_type=ContentItemTypeEnum.WORKFLOW,
        name="Sample Workflow Item",
        current_version=version
    )
    return workflow

@pytest.fixture
def sample_validated_definition(sample_workflow_item) -> ValidatedWorkflowDefinition:
    """Fixture providing a parsed and validated workflow definition."""
    return WorkflowDefinitionParser.parse_and_validate(sample_workflow_item.current_version.markdown_content)

@pytest.fixture
def sample_input_doc() -> ContentItem:
    """Fixture for a sample input document."""
    version = create_test_content_version(
        item_id_str="bbbbbbbb-1111-1111-1111-111111111111",
        markdown_content="This is the content of input doc 1.",
        created_at=FROZEN_TIME_DT - timedelta(days=3) # Within newerThanDays 7
    )
    doc = create_test_content_item(
        item_id_str="bbbbbbbb-1111-1111-1111-111111111111",
        name="Input_Doc_1",
        item_type=ContentItemTypeEnum.DOCUMENT,
        current_version=version,
        created_at=FROZEN_TIME_DT - timedelta(days=3) # Use version creation time for filter usually
    )
    return doc

# --- Tests for _filter_by_date_selector ---
# (Keep existing tests from previous file version)
now = FROZEN_TIME_DT
yesterday = now - timedelta(days=1)
last_week = now - timedelta(days=7)
last_month = now - timedelta(days=30)
two_months_ago = now - timedelta(days=60)
tomorrow = now + timedelta(days=1)

# Test cases: (item_date, date_selector_str, current_time, expected_result, description)
filter_test_data = [
    # --- olderThanDays ---
    (yesterday, "olderThanDays 0", now, True, "olderThanDays 0: Yesterday IS older than now"),
    (last_week, "olderThanDays 6", now, True, "olderThanDays 6: Last week is older"),
    (last_week, "olderThanDays 7", now, False, "olderThanDays 7: Last week is not older (exactly 7 days ago)"),
    (last_month, "olderThanDays 29", now, True, "olderThanDays 29: Last month is older"),
    (two_months_ago, "olderThanDays 60", now, False, "olderThanDays 60: Exactly 60 days ago is not older"),
    (two_months_ago, "olderThanDays 59", now, True, "olderThanDays 59: 60 days ago is older"),
    (now, "olderThanDays 0", now, False, "olderThanDays 0: Now is not older than now"),
    (tomorrow, "olderThanDays 0", now, False, "olderThanDays 0: Tomorrow is not older"),
    (last_week, "olderThanDays -1", now, False, "olderThanDays: Negative days is invalid (returns False)"),

    # --- newerThanDays ---
    (yesterday, "newerThanDays 0", now, False, "newerThanDays 0: Yesterday IS NOT newer than now"),
    (yesterday, "newerThanDays 1", now, False, "newerThanDays 1: Yesterday is not newer (exactly 1 day ago)"),
    (last_week, "newerThanDays 8", now, True, "newerThanDays 8: Last week IS newer than 8 days ago"),
    (last_week, "newerThanDays 6", now, False, "newerThanDays 6: Last week IS NOT newer than 6 days ago"),
    (now, "newerThanDays 0", now, False, "newerThanDays 0: Now is not newer than now"),
    (tomorrow, "newerThanDays 0", now, True, "newerThanDays 0: Tomorrow is newer"),
    (two_months_ago, "newerThanDays 59", now, False,"newerThanDays 59: 60 days ago IS NOT newer than 59 days ago"),
    (two_months_ago, "newerThanDays 60", now, False, "newerThanDays 60: Exactly 60 days ago is not newer"),
    (last_week, "newerThanDays -1", now, False, "newerThanDays: Negative days is invalid (returns False)"),

    # --- between_YYYY-MM-DD_YYYY-MM-DD ---
    (now, "between_2025-05-01_2025-05-31", now, True, "between: Today is within May"),
    (yesterday, "between_2025-05-01_2025-05-07", now, True, "between: Yesterday is within range"),
    (last_week, "between_2025-05-01_2025-05-07", now, True, "between: Last week (May 1st) is start boundary"),
    (last_week, "between_2025-05-02_2025-05-08", now, False, "between: Last week (May 1st) is before range"),
    (now, "between_2025-05-08_2025-05-08", now, True, "between: Single day range including today"),
    (yesterday, "between_2025-05-08_2025-05-08", now, False, "between: Single day range excluding yesterday"),
    (two_months_ago, "between_2025-03-01_2025-03-31", now, True, "between: Two months ago within March"),
    (now, "between_2025-06-01_2025-06-30", now, False, "between: Today is before June range"),
    (now, "between_2025-05-10_2025-05-01", now, False, "between: Invalid range (start > end)"),
    (now, "between_2025-05-08_2025-05-08", now.replace(tzinfo=None), True, "between: Aware item_date vs naive current_time handled"),
    (now.replace(tzinfo=None), "between_2025-05-08_2025-05-08", now, True, "between: Naive item_date vs aware current_time handled"),


    # --- None or Invalid Selectors ---
    (now, None, now, True, "None selector always matches"),
    (yesterday, "", now, True, "Empty selector always matches"),
    (now, "invalid_selector", now, False, "Invalid selector format returns False"),
    (now, "olderThanDays", now, False, "Incomplete olderThanDays returns False"),
    (now, "newerThanDays", now, False, "Incomplete newerThanDays returns False"),
    (now, "between_2025-05-01", now, False, "Incomplete between returns False"),
    (now, "between_2025-05_2025-06", now, False, "Invalid date format in between returns False"),
    (now, "olderThanDays abc", now, False, "Invalid number in olderThanDays returns False"),
]

# *** FIX: Removed global pytestmark, added mark only to async tests ***
@pytest.mark.parametrize("item_date, date_selector_str, current_time, expected_result, description", filter_test_data)
@freeze_time(FROZEN_TIME_STR)
def test_filter_by_date_selector_parametrized(item_date, date_selector_str, current_time, expected_result, description):
    """ Tests the _filter_by_date_selector function with various inputs. """
    assert _filter_by_date_selector(item_date, date_selector_str, FROZEN_TIME_DT) == expected_result, description

# --- Tests for Other Helpers ---

@pytest.mark.parametrize("name, pattern, expected", [
    ("Report_2023", "*", True),
    ("Report_2023.txt", "*", False),
    ("KW10_Analysis", "KW*_Analysis", True),
    ("KW10_Summary", "KW*_Analysis", False),
    ("Daily_Log_2023-10-25", "Daily_Log_????-??-??", True),
    ("Daily_Log_2023-10-25X", "Daily_Log_????-??-??", False),
    ("meeting_notes", "meeting*", True),
    ("meeting_notes", "meeting", False), # Glob requires '*' for partial match
    ("CaseSensitiveDoc", "*", True), # Test case insensitivity
])
def test_match_glob_pattern(name, pattern, expected):
    """Test the glob pattern matching helper."""
    assert _match_glob_pattern(name, pattern) == expected

# *** FIX: Added asyncio mark ***
@pytest.mark.asyncio
@freeze_time(FROZEN_TIME_STR)
async def test_select_input_documents(mock_db_session, sample_validated_definition, sample_input_doc):
    """Test selecting input documents based on definition criteria."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    test_team_id_str_no_hyphen = str(test_team_id).replace('-', '') # For WHERE clause check
    # Create another doc that matches pattern but fails date filter
    old_version = create_test_content_version(
        item_id_str="cccccccc-2222-2222-2222-222222222222",
        created_at=FROZEN_TIME_DT - timedelta(days=10) # Older than 7 days
    )
    old_doc = create_test_content_item(
        item_id_str="cccccccc-2222-2222-2222-222222222222",
        name="Input_Doc_Old", current_version=old_version
    )
    # Create a doc that doesn't match name pattern
    wrong_name_doc = create_test_content_item(name="Wrong_Name")
    # Create a doc owned by another team but globally visible (should be included)
    global_version = create_test_content_version(item_id_str="dddddddd-3333-3333-3333-333333333333", created_at=FROZEN_TIME_DT - timedelta(days=1))
    global_doc = create_test_content_item(
        item_id_str="dddddddd-3333-3333-3333-333333333333",
        team_id_str="99999999-9999-9999-9999-999999999999",
        name="Input_Doc_Global", is_globally_visible=True, current_version=global_version
    )


    # Mock DB execute to return all potential docs
    all_docs = [sample_input_doc, old_doc, wrong_name_doc, global_doc]
    # Correct Mock: Execute returns a mock result obj, and sync methods work on it
    mock_result = MagicMock()
    mock_result.scalars.return_value.unique.return_value.all.return_value = all_docs
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    selected_docs = await _select_input_documents(
        db=mock_db_session,
        definition=sample_validated_definition,
        executing_team_id=test_team_id,
        current_time=FROZEN_TIME_DT
    )

    # Assert only sample_input_doc and global_doc are selected
    assert len(selected_docs) == 2
    selected_ids = {doc.item_id for doc in selected_docs}
    assert sample_input_doc.item_id in selected_ids
    assert global_doc.item_id in selected_ids
    assert old_doc.item_id not in selected_ids # Failed date filter
    assert wrong_name_doc.item_id not in selected_ids # Failed name filter

    # Check the DB query filters correctly (visibility)
    mock_db_session.execute.assert_awaited_once() # Ensure execute was awaited
    call_args, _ = mock_db_session.execute.call_args
    query_str = str(call_args[0].compile(compile_kwargs={"literal_binds": True}))
    # *** FIX: Correct UUID comparison (hyphenless) ***
    assert f"(content_items.team_id = '{test_team_id_str_no_hyphen}' OR content_items.is_globally_visible = true)" in query_str.replace('\n','')
    assert "content_items.item_type = 'Document'" in query_str

# *** FIX: Removed asyncio mark (decorator) ***
@freeze_time(FROZEN_TIME_STR)
def test_construct_prompt(sample_validated_definition):
    """Test placeholder replacement in the prompt."""
    input_contents = ["Content of Doc 1.", "Content of Doc 2."]
    input_names = ["Input_Doc_1", "Input_Doc_2"]

    expected_context = "[Document: Input_Doc_1.md]\n\nContent of Doc 1.\n\n---\n\n[Document: Input_Doc_2.md]\n\nContent of Doc 2."

    final_prompt = _construct_prompt(
        definition=sample_validated_definition,
        input_docs_content_list=input_contents,
        input_doc_names_list=input_names,
        current_time=FROZEN_TIME_DT
    )

    assert f"Process context: {expected_context}" in final_prompt
    assert "Input names: Input_Doc_1.md, Input_Doc_2" in final_prompt
    assert "Input count: 2" in final_prompt
    assert "{{CurrentDate}}" not in final_prompt

    # Test with no input documents
    final_prompt_no_input = _construct_prompt(
        definition=sample_validated_definition,
        input_docs_content_list=[],
        input_doc_names_list=[],
        current_time=FROZEN_TIME_DT
    )
    assert "Process context: (No input documents found)" in final_prompt_no_input
    assert "Input names: " in final_prompt_no_input
    assert "Input count: 0" in final_prompt_no_input

# *** FIX: Removed asyncio mark (decorator) ***
@freeze_time(FROZEN_TIME_STR)
def test_generate_output_name(sample_validated_definition):
    """Test placeholder replacement in the output name template."""
    input_names = ["Input_Doc_1"]
    expected_name = f"Output_{FROZEN_TIME_DT.strftime('%Y-%m-%d')}"

    generated_name = _generate_output_name(
        definition=sample_validated_definition,
        input_doc_names_list=input_names,
        current_time=FROZEN_TIME_DT
    )
    assert generated_name == expected_name

    # Test template using other placeholders
    definition_alt_name = sample_validated_definition.model_copy(update={
        "outputName": "{{WorkflowName}}_{{InputFileName}}"
    })
    expected_name_alt = f"{sample_validated_definition.processWorkFlowName}_Input_Doc_1"
    generated_name_alt = _generate_output_name(
        definition=definition_alt_name,
        input_doc_names_list=input_names,
        current_time=FROZEN_TIME_DT
    )
    assert generated_name_alt == expected_name_alt

    # Test sanitization
    definition_bad_chars = sample_validated_definition.model_copy(update={
        "outputName": "Output_<>/\\:?*"
    })
    expected_name_sanitized = "Output________"
    generated_name_sanitized = _generate_output_name(
        definition=definition_bad_chars,
        input_doc_names_list=[],
        current_time=FROZEN_TIME_DT
    )
    assert generated_name_sanitized == expected_name_sanitized

# *** FIX: Corrected patch target ***
# *** FIX: Added asyncio mark ***
@patch('app.crud.content_item.check_name_uniqueness') # Now patching the correct module path if service imports module
@pytest.mark.asyncio
async def test_ensure_unique_output_name(mock_check_unique, mock_db_session):
    """Test finding a unique output name."""
    test_team_id = PyUUID("11111111-1111-1111-1111-111111111111")
    base_name = "Generated_Output"
    base_name_root = "Generated_Output"

    # Scenario 1: Base name is already unique
    mock_check_unique.return_value = True
    # Use the actual imported object in the service if available
    # If workflow_service imports `content_item` instance, use that
    # If it imports `crud_content_item` module, need to mock differently
    # Assuming service imports `content_item` instance from `app.crud` now:
    with patch('app.services.workflow_service.content_item.check_name_uniqueness', new=AsyncMock(return_value=True)) as patched_check_unique:
        unique_name = await _ensure_unique_output_name(mock_db_session, base_name, test_team_id)
        assert unique_name == base_name
        patched_check_unique.assert_awaited_once_with(db=mock_db_session, name=base_name, item_type=ContentItemTypeEnum.DOCUMENT, team_id=test_team_id)


    # Scenario 2: Base name conflicts, _1 is unique
    mock_check_unique_sfx = AsyncMock(side_effect = [False, True])
    with patch('app.services.workflow_service.content_item.check_name_uniqueness', new=mock_check_unique_sfx):
        unique_name_suffixed = await _ensure_unique_output_name(mock_db_session, base_name, test_team_id)
        assert unique_name_suffixed == f"{base_name_root}_1"
        assert mock_check_unique_sfx.await_count == 2
        mock_check_unique_sfx.assert_has_awaits([
            call(db=mock_db_session, name=base_name, item_type=ContentItemTypeEnum.DOCUMENT, team_id=test_team_id),
            call(db=mock_db_session, name=f"{base_name_root}_1", item_type=ContentItemTypeEnum.DOCUMENT, team_id=test_team_id)
        ])

    # Scenario 3: Fails after too many attempts
    mock_check_unique_fail = AsyncMock(return_value=False)
    with patch('app.services.workflow_service.content_item.check_name_uniqueness', new=mock_check_unique_fail):
        with pytest.raises(ValueError, match="Could not generate a unique output name"):
            # Patch the loop limit directly in the service module for testing
            with patch.object(workflow_service, 'MAX_UNIQUE_NAME_ATTEMPTS', 2):
                await _ensure_unique_output_name(mock_db_session, base_name, test_team_id)
    assert mock_check_unique_fail.await_count == 3 # Base name + attempts 1 and 2

# --- Test execute_workflow ---

# *** FIX: Corrected patch targets ***
# *** FIX: Added asyncio mark ***
@patch('app.services.workflow_service.WorkflowDefinitionParser.parse_and_validate')
@patch('app.services.workflow_service._select_input_documents')
@patch('app.services.workflow_service.ollama_service_instance.generate')
@patch('app.services.workflow_service._ensure_unique_output_name')
@patch('app.crud.content_version.content_version.create_new_version') # Target instance method
@freeze_time(FROZEN_TIME_STR)
@pytest.mark.asyncio
async def test_execute_workflow_success(
    mock_create_version, mock_ensure_unique, mock_ollama_generate,
    mock_select_inputs, mock_parse, mock_db_session,
    sample_workflow_item, sample_validated_definition, sample_input_doc
):
    """Test the successful execution path of a workflow."""
    test_team_id = sample_workflow_item.team_id
    llm_response = "## Generated Document Content"
    expected_output_name = f"Output_{FROZEN_TIME_DT.strftime('%Y-%m-%d')}"

    # Configure mocks
    mock_parse.return_value = sample_validated_definition
    mock_select_inputs.return_value = [sample_input_doc]
    mock_ollama_generate.return_value = llm_response
    mock_ensure_unique.return_value = expected_output_name
    # Mock version creation to return a mock version object
    mock_new_output_version = create_test_content_version(markdown_content=llm_response)
    mock_create_version.return_value = mock_new_output_version

    # Mock commit and flush
    mock_db_session.commit = AsyncMock()
    mock_db_session.flush = AsyncMock()

    # Simulate refresh loading the relationship
    async def mock_refresh(obj, attribute_names=None):
        if isinstance(obj, ContentItem) and 'current_version' in (attribute_names or []):
            obj.current_version = mock_new_output_version
        elif isinstance(obj, ContentItem): # Handle general refresh calls
             pass

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

    # Execute the workflow
    output_doc, raw_llm_response = await execute_workflow(
        db=mock_db_session,
        workflow_item=sample_workflow_item,
        executing_team_id=test_team_id
    )

    # Assertions
    mock_parse.assert_called_once_with(sample_workflow_item.current_version.markdown_content)
    mock_select_inputs.assert_awaited_once_with(mock_db_session, sample_validated_definition, test_team_id, FROZEN_TIME_DT)
    mock_ollama_generate.assert_awaited_once()
    generate_kwargs = mock_ollama_generate.call_args.kwargs
    assert generate_kwargs['model'] == sample_validated_definition.model
    assert sample_input_doc.current_version.markdown_content in generate_kwargs['prompt']
    assert sample_input_doc.name in generate_kwargs['prompt']
    assert generate_kwargs['temperature'] == sample_validated_definition.temperature

    expected_raw_name = _generate_output_name(sample_validated_definition, [sample_input_doc.name], FROZEN_TIME_DT)
    mock_ensure_unique.assert_awaited_once_with(mock_db_session, expected_raw_name, test_team_id)

    mock_db_session.add.assert_called_once()
    added_item = mock_db_session.add.call_args[0][0]
    assert isinstance(added_item, ContentItem)
    assert added_item.name == expected_output_name
    assert added_item.item_type == ContentItemTypeEnum.DOCUMENT
    assert added_item.team_id == test_team_id

    mock_create_version.assert_awaited_once()
    version_call_kwargs = mock_create_version.call_args.kwargs
    assert version_call_kwargs['db'] == mock_db_session
    assert version_call_kwargs['item_id'] == added_item.item_id
    assert version_call_kwargs['version_in'].markdown_content == llm_response
    assert version_call_kwargs['saved_by_team_id'] == test_team_id
    assert version_call_kwargs['is_initial_version'] is True

    mock_db_session.commit.assert_awaited_once() # Commit should be called by endpoint, not service
    mock_db_session.refresh.assert_awaited_once_with(added_item, attribute_names=['current_version_id', 'updated_at', 'current_version'])


    assert output_doc == added_item
    assert raw_llm_response == llm_response
    # assert output_doc.current_version == mock_new_output_version # Check relationship load simulated by refresh mock


# *** FIX: Added asyncio mark ***
@pytest.mark.asyncio
async def test_execute_workflow_no_current_version(mock_db_session):
    """Test workflow execution when the workflow item has no version."""
    workflow_item_no_version = create_test_content_item(item_type=ContentItemTypeEnum.WORKFLOW, current_version=None)
    test_team_id = workflow_item_no_version.team_id

    with pytest.raises(ValueError, match="Workflow item has no current version"):
        await execute_workflow(mock_db_session, workflow_item_no_version, test_team_id)

# *** FIX: Added asyncio mark ***
@patch('app.services.workflow_service.WorkflowDefinitionParser.parse_and_validate', side_effect=WorkflowParsingError("Bad format"))
@pytest.mark.asyncio
async def test_execute_workflow_parsing_error(mock_parse, mock_db_session, sample_workflow_item):
    """Test workflow execution when parsing fails."""
    test_team_id = sample_workflow_item.team_id
    mock_db_session.rollback = AsyncMock() # Mock rollback

    with pytest.raises(WorkflowParsingError, match="Bad format"):
        await execute_workflow(mock_db_session, sample_workflow_item, test_team_id)
    mock_parse.assert_called_once()
    # *** FIX: Check rollback was awaited ***
    mock_db_session.rollback.assert_awaited_once()

# *** FIX: Added asyncio mark ***
@patch('app.services.workflow_service.WorkflowDefinitionParser.parse_and_validate')
@patch('app.services.workflow_service._select_input_documents')
@patch('app.services.workflow_service.ollama_service_instance.generate', side_effect=OllamaServiceError("Ollama down"))
@pytest.mark.asyncio
async def test_execute_workflow_ollama_error(
    mock_ollama_generate, mock_select_inputs, mock_parse, mock_db_session,
    sample_workflow_item, sample_validated_definition
):
    """Test workflow execution when Ollama call fails."""
    test_team_id = sample_workflow_item.team_id
    mock_parse.return_value = sample_validated_definition
    mock_select_inputs.return_value = [] # No inputs needed for this test
    mock_db_session.rollback = AsyncMock() # Mock rollback

    with pytest.raises(OllamaServiceError, match="Ollama down"):
        await execute_workflow(mock_db_session, sample_workflow_item, test_team_id)

    mock_parse.assert_called_once()
    mock_select_inputs.assert_awaited_once()
    mock_ollama_generate.assert_awaited_once() # Ensure it was called
    # *** FIX: Check rollback was awaited ***
    mock_db_session.rollback.assert_awaited_once()

# *** FIX: Corrected patch targets ***
# *** FIX: Added asyncio mark ***
@patch('app.services.workflow_service.WorkflowDefinitionParser.parse_and_validate')
@patch('app.services.workflow_service._select_input_documents')
@patch('app.services.workflow_service.ollama_service_instance.generate')
@patch('app.services.workflow_service._ensure_unique_output_name')
@patch('app.crud.content_version.content_version.create_new_version', side_effect=Exception("DB error saving version")) # Target instance method
@pytest.mark.asyncio
async def test_execute_workflow_output_creation_error(
    mock_create_version, mock_ensure_unique, mock_ollama_generate,
    mock_select_inputs, mock_parse, mock_db_session,
    sample_workflow_item, sample_validated_definition
):
    """Test workflow execution when saving the output document fails."""
    test_team_id = sample_workflow_item.team_id
    llm_response = "Some output"
    expected_output_name = "Output_Name"

    mock_parse.return_value = sample_validated_definition
    mock_select_inputs.return_value = []
    mock_ollama_generate.return_value = llm_response
    mock_ensure_unique.return_value = expected_output_name
    mock_db_session.flush = AsyncMock() # Mock flush
    mock_db_session.rollback = AsyncMock() # Mock rollback

    with pytest.raises(ValueError, match="Failed to create or save the output document"):
        await execute_workflow(mock_db_session, sample_workflow_item, test_team_id)

    # Ensure steps leading up to version creation were called
    mock_parse.assert_called_once()
    mock_select_inputs.assert_awaited_once()
    mock_ollama_generate.assert_awaited_once()
    mock_ensure_unique.assert_awaited_once()
    mock_db_session.add.assert_called_once() # Item added
    mock_db_session.flush.assert_awaited_once() # Flushed before version creation
    # *** FIX: Check version creation was awaited ***
    mock_create_version.assert_awaited_once()
    # *** FIX: Check rollback was awaited ***
    mock_db_session.rollback.assert_awaited_once()
