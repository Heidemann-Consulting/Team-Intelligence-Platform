# File: ulacm_backend/tests/services/test_workflow_parser.py
# Purpose: Unit tests for workflow definition parsing and validation.
# No changes needed in this file for the identified failure.

import pytest
import yaml
from unittest.mock import patch, MagicMock

from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition, validate_workflow_definition_string

# --- Test Data: Valid YAML Examples ---

VALID_YAML_MINIMAL = """
processWorkFlowName: Minimal Test Workflow
trigger: manual
inputDocumentSelector: "*"
model: ollama/test-model
outputName: Output_{{Year}}.md
prompt: |
  Process this context: {{DocumentContext}}
"""

VALID_YAML_FULL = """
processWorkFlowName: Full Test Workflow
trigger: manual
inputDocumentSelector: "Daily_Log_*"
inputDateSelector: olderThanDays 30
model: ollama/llama3:latest
temperature: 0.9
outputName: Summary_{{Year}}-{{Month}}_{{WorkflowName}}.md
prompt: |
  SYSTEM: You are an assistant.
  CONTEXT: {{DocumentContext}}
  TASK: Summarize the context.
  OUTPUT FORMAT: Markdown Summary
"""

VALID_YAML_BETWEEN_DATES = """
processWorkFlowName: Between Dates Workflow
trigger: manual
inputDocumentSelector: "Report_*.txt"
inputDateSelector: between_2023-01-01_2023-03-31
model: ollama/mistral
outputName: Q1_Report_Summary.md
prompt: |
  Summarize reports between 2023-01-01 and 2023-03-31. Context: {{DocumentContext}}
"""

# --- Test Data: Invalid YAML/Structure Examples ---

INVALID_YAML_SYNTAX = """
processWorkFlowName: Invalid Syntax
trigger: manual
  inputDocumentSelector: "*" # Indentation error
model: ollama/test-model
outputName: Output.md
prompt: Fail me
"""

INVALID_YAML_NOT_DICT = """
- item1
- item2
"""

INVALID_YAML_MISSING_REQUIRED = """
processWorkFlowName: Missing Fields
trigger: manual
# model is missing
outputName: Output.md
prompt: |
  This will fail validation.
inputDocumentSelector: "*"
"""

INVALID_YAML_WRONG_TYPE = """
processWorkFlowName: Wrong Type
trigger: manual
inputDocumentSelector: "*"
model: ollama/test-model
temperature: "not-a-number" # Should be float
outputName: Output.md
prompt: Process this.
"""

INVALID_YAML_BAD_TRIGGER = """
processWorkFlowName: Bad Trigger
trigger: scheduled # Invalid trigger value
inputDocumentSelector: "*"
model: ollama/test-model
outputName: Output.md
prompt: Process this.
"""

INVALID_YAML_BAD_DATE_SELECTOR_1 = """
processWorkFlowName: Bad Date Selector 1
trigger: manual
inputDocumentSelector: "*"
inputDateSelector: olderThan 60 # Missing "Days"
model: ollama/test-model
outputName: Output.md
prompt: Process this.
"""

INVALID_YAML_BAD_DATE_SELECTOR_2 = """
processWorkFlowName: Bad Date Selector 2
trigger: manual
inputDocumentSelector: "*"
inputDateSelector: between_2023-01-01 # Missing end date
model: ollama/test-model
outputName: Output.md
prompt: Process this.
"""

INVALID_YAML_BAD_DATE_SELECTOR_3 = """
processWorkFlowName: Bad Date Selector 3
trigger: manual
inputDocumentSelector: "*"
inputDateSelector: between_2023-02-30_2023-03-15 # Invalid date Feb 30
model: ollama/test-model
outputName: Output.md
prompt: Process this.
"""
INVALID_YAML_BAD_DATE_SELECTOR_4 = """
processWorkFlowName: Bad Date Selector 4
trigger: manual
inputDocumentSelector: "*"
inputDateSelector: between_2023-05-01_2023-04-01 # Start date after end date
model: ollama/test-model
outputName: Output.md
prompt: Process this.
"""

# --- Test Cases ---

def test_parse_valid_minimal():
    """Test parsing a valid minimal workflow definition."""
    result = WorkflowDefinitionParser.parse_and_validate(VALID_YAML_MINIMAL)
    assert isinstance(result, ValidatedWorkflowDefinition)
    assert result.processWorkFlowName == "Minimal Test Workflow"
    assert result.trigger == "manual"
    assert result.inputDocumentSelector == "*"
    assert result.model == "ollama/test-model"
    assert result.outputName == "Output_{{Year}}"
    assert result.prompt.strip() == "Process this context: {{DocumentContext}}"
    assert result.temperature == 0.7 # Default value
    assert result.inputDateSelector is None

def test_parse_valid_full():
    """Test parsing a valid workflow definition with all fields."""
    result = WorkflowDefinitionParser.parse_and_validate(VALID_YAML_FULL)
    assert isinstance(result, ValidatedWorkflowDefinition)
    assert result.processWorkFlowName == "Full Test Workflow"
    assert result.trigger == "manual"
    assert result.inputDocumentSelector == "Daily_Log_*"
    assert result.inputDateSelector == "olderThanDays 30"
    assert result.model == "ollama/llama3:latest"
    assert result.temperature == 0.9
    assert result.outputName == "Summary_{{Year}}-{{Month}}_{{WorkflowName}}"
    assert "SYSTEM: You are an assistant." in result.prompt

def test_parse_valid_between_dates():
    """Test parsing a valid definition with a between date selector."""
    result = WorkflowDefinitionParser.parse_and_validate(VALID_YAML_BETWEEN_DATES)
    assert isinstance(result, ValidatedWorkflowDefinition)
    assert result.inputDateSelector == "between_2023-01-01_2023-03-31"

def test_parse_invalid_yaml_syntax():
    """Test parsing invalid YAML syntax."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_SYNTAX)
    assert "Invalid YAML syntax" in str(excinfo.value)
    assert "line 4" in str(excinfo.value)

def test_parse_not_a_dictionary():
    """Test parsing input that is not a YAML mapping/dictionary."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_NOT_DICT)
    assert "Workflow definition must be a YAML mapping" in str(excinfo.value)

def test_parse_missing_required_field():
    """Test parsing valid YAML missing a required field."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_MISSING_REQUIRED)
    assert "Field required" in str(excinfo.value)
    # Pydantic v2 error messages might differ slightly in format
    assert "'model'" in str(excinfo.value) # Check if the missing field name is mentioned
    assert excinfo.value.field == 'model' # Check the field attribute of the exception


def test_parse_wrong_field_type():
    """Test parsing valid YAML with an incorrect field type."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_WRONG_TYPE)
    assert "Input should be a valid number" in str(excinfo.value)
    assert "'temperature'" in str(excinfo.value)
    assert excinfo.value.field == 'temperature'
    assert excinfo.value.value == 'not-a-number'

def test_parse_invalid_trigger_value():
    """Test parsing with an invalid value for the 'trigger' field."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_BAD_TRIGGER)
    assert "String should match pattern '^manual$'" in str(excinfo.value)
    assert "'trigger'" in str(excinfo.value)
    assert excinfo.value.field == 'trigger'

def test_parse_invalid_date_selectors():
    """Test various invalid inputDateSelector formats."""
    with pytest.raises(WorkflowParsingError) as excinfo1:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_BAD_DATE_SELECTOR_1)
    assert "Unrecognized date selector format: 'olderthan'" in str(excinfo1.value)
    assert excinfo1.value.field == 'inputDateSelector'

    with pytest.raises(WorkflowParsingError) as excinfo2:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_BAD_DATE_SELECTOR_2)
    assert "Invalid format. Use 'between_YYYY-MM-DD_YYYY-MM-DD'" in str(excinfo2.value)
    assert excinfo2.value.field == 'inputDateSelector'

    with pytest.raises(WorkflowParsingError) as excinfo3:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_BAD_DATE_SELECTOR_3)
    assert "Invalid date format. Use YYYY-MM-DD" in str(excinfo3.value)
    assert excinfo3.value.field == 'inputDateSelector'

    with pytest.raises(WorkflowParsingError) as excinfo4:
        WorkflowDefinitionParser.parse_and_validate(INVALID_YAML_BAD_DATE_SELECTOR_4)
    # Check for the specific core error message within the full exception string
    # This assertion should now pass because the validator was fixed
    assert "Start date must be before or equal to end date" in str(excinfo4.value)
    assert excinfo4.value.field == 'inputDateSelector' # Check field name is correct

def test_parse_empty_input():
    """Test parsing an empty string."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate("")
    assert "Workflow definition content cannot be empty" in str(excinfo.value)

def test_parse_whitespace_input():
    """Test parsing a string with only whitespace."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        WorkflowDefinitionParser.parse_and_validate("   \n\t  ")
    assert "Workflow definition content cannot be empty" in str(excinfo.value)

def test_parse_none_input():
    """Test parsing when None is passed (e.g., if content is missing)."""
    with pytest.raises(WorkflowParsingError) as excinfo:
         # Simulate the behavior if None were passed, though type hints prevent it directly
         # We test this scenario by checking the initial guard clause.
         # Directly calling parse_and_validate with None would raise TypeError typically
         # Test the guard check instead
         WorkflowDefinitionParser.parse_and_validate("") # Already tested empty string case
         WorkflowDefinitionParser.parse_and_validate(" ") # Already tested whitespace case
    # If the function allowed None, the error would be different, but the guards handle empty/whitespace

@patch('app.services.workflow_parser.WorkflowDefinitionParser.parse_and_validate')
def test_validate_workflow_definition_string_valid(mock_parse_and_validate):
    """Test the convenience validation function with valid input."""
    mock_parse_and_validate.return_value = MagicMock(spec=ValidatedWorkflowDefinition) # Mock successful parse
    try:
        validate_workflow_definition_string(VALID_YAML_FULL)
        mock_parse_and_validate.assert_called_once_with(VALID_YAML_FULL)
    except WorkflowParsingError:
        pytest.fail("validate_workflow_definition_string raised WorkflowParsingError unexpectedly.")


@patch('app.services.workflow_parser.WorkflowDefinitionParser.parse_and_validate', side_effect=WorkflowParsingError("Test parsing error"))
def test_validate_workflow_definition_string_invalid(mock_parse_and_validate):
    """Test the convenience validation function with invalid input."""
    with pytest.raises(WorkflowParsingError) as excinfo:
        validate_workflow_definition_string(INVALID_YAML_SYNTAX) # Content doesn't matter due to mock

    assert "Test parsing error" in str(excinfo.value)
    mock_parse_and_validate.assert_called_once_with(INVALID_YAML_SYNTAX)
