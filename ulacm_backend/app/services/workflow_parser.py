# File: ulacm_backend/app/services/workflow_parser.py
# Purpose: Parses and validates Process Workflow definitions more robustly.
# Updated: inputDocumentSelector changed to inputDocumentSelectors (list)

import yaml
import datetime
from pydantic import (
    ValidationError, field_validator, model_validator, Field, constr,
    ValidationInfo
)
from typing import Optional, Any, List

from app.schemas.workflow_definition import WorkflowDefinition

class WorkflowParsingError(ValueError):
    """Custom exception for workflow definition parsing and validation errors."""
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.field = field
        self.value = value
        detail = f"Field '{field}': {message}" if field else message
        if value is not None:
            detail += f" (value: {repr(value)})"
        super().__init__(detail)

class ValidatedWorkflowDefinition(WorkflowDefinition):
    """
    Extends the base WorkflowDefinition schema with stricter validation rules.
    processWorkFlowName will be populated from the ContentItem's name if not present in YAML.
    """

    @model_validator(mode='before')
    @classmethod
    def check_required_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise ValueError('Workflow definition must be a dictionary-like object.')

        # processWorkFlowName is now optional in the YAML content itself.
        # It will be derived from the workflow item's name if not provided.
        required_fields_in_yaml = ['inputDocumentSelectors', 'outputName', 'prompt']

        missing_fields = [field for field in required_fields_in_yaml if field not in data or not data[field]]
        if missing_fields:
            raise ValueError(f"Missing required fields in workflow definition content: {', '.join(missing_fields)}")

        if 'inputDocumentSelectors' in data:
            if not isinstance(data['inputDocumentSelectors'], list):
                raise ValueError("Field 'inputDocumentSelectors': Must be a list of strings.")
            if not data['inputDocumentSelectors']: # Ensure list is not empty
                raise ValueError("Field 'inputDocumentSelectors': List cannot be empty.")
            for selector in data['inputDocumentSelectors']:
                if not isinstance(selector, str) or not selector.strip():
                    raise ValueError("Field 'inputDocumentSelectors': Each selector in the list must be a non-empty string.")


        if 'trigger' in data and data['trigger'] != "manual":
            raise ValueError("Field 'trigger': Only 'manual' is currently supported.")

        return data

class WorkflowDefinitionParser:
    @staticmethod
    def parse_and_validate(workflow_content_str: str) -> ValidatedWorkflowDefinition:
        if not workflow_content_str or workflow_content_str.isspace():
            raise WorkflowParsingError("Workflow definition content cannot be empty.")
        try:
            parsed_yaml = yaml.safe_load(workflow_content_str)
            if parsed_yaml is None:
                raise WorkflowParsingError("Workflow definition content is empty after parsing.")
            if not isinstance(parsed_yaml, dict):
                raise WorkflowParsingError("Workflow definition must be a YAML mapping (key-value pairs).")
        except yaml.YAMLError as e:
            line = e.problem_mark.line + 1 if e.problem_mark else 'N/A'
            column = e.problem_mark.column + 1 if e.problem_mark else 'N/A'
            raise WorkflowParsingError(f"Invalid YAML syntax near line {line}, column {column}: {e.problem}")

        try:
            # processWorkFlowName is now Optional in the schema, so it won't fail here if missing.
            # It will be set programmatically in the workflow_service if not in YAML.
            workflow_def = ValidatedWorkflowDefinition(**parsed_yaml)
            return workflow_def
        except ValidationError as e:
            error_messages = []
            first_error_field = None
            first_error_value = None
            for error in e.errors():
                field_path = " -> ".join(map(str, error["loc"]))
                if not first_error_field:
                    first_error_field = field_path
                    try:
                        value = parsed_yaml
                        for key in error["loc"]: value = value[key]
                        first_error_value = value
                    except (KeyError, TypeError): first_error_value = 'N/A'
                msg = error['msg']
                error_messages.append(f"Field '{field_path}': {msg}")
            raise WorkflowParsingError(
                f"Invalid workflow definition structure: {'; '.join(error_messages)}",
                field=first_error_field, value=first_error_value
            )
        except Exception as e:
            raise WorkflowParsingError(f"An unexpected error occurred during validation: {str(e)}")

def validate_workflow_definition_string(workflow_content_str: str):
    WorkflowDefinitionParser.parse_and_validate(workflow_content_str)
