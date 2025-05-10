# File: ulacm_backend/app/schemas/workflow_definition.py
# Purpose: Pydantic schemas for Process Workflow definitions and execution.
# Updated: Made processWorkFlowName optional in the schema.

from pydantic import (
    BaseModel, UUID4, constr, Field, field_validator, ValidationInfo
)
from typing import Optional, List, Dict, Any
import datetime

from app.schemas.content_item import ContentItem

class WorkflowDefinition(BaseModel):
    processWorkFlowName: Optional[constr(min_length=1, max_length=255)] = None # Now optional
    trigger: constr(pattern=r"^manual$") = "manual"
    inputDocumentSelector: constr(min_length=1, max_length=255)
    inputDateSelector: Optional[constr(min_length=1, max_length=100)] = None
    outputName: constr(min_length=1, max_length=255)
    prompt: str

    @field_validator('inputDateSelector')
    @classmethod
    def validate_date_selector_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        parts = v.split(" ")
        if parts[0].lower() in ["olderthandays", "newerthandays"]:
            if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) >= 0:
                return v
            else:
                raise ValueError("Invalid format for olderThanDays/newerThanDays. Use 'olderThanDays N' or 'newerThanDays N' where N is a non-negative integer.")
        elif parts[0].lower().startswith("between_"):
            if len(parts) == 1:
                date_parts = parts[0].split("_")[1:]
                if len(date_parts) == 2:
                    start_date_str, end_date_str = date_parts[0], date_parts[1]
                    try:
                        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                        if start_date > end_date:
                            raise ValueError("Start date must be before or equal to end date in 'between' selector.")
                        return v
                    except ValueError as e:
                        raise ValueError(f"Invalid date format or range in 'between' selector: {e}")
                else:
                    raise ValueError("Invalid format for between. Use 'between_YYYY-MM-DD_YYYY-MM-DD'.")
            else:
                 raise ValueError("Invalid format. No spaces allowed after 'between_...' keyword.")
        else:
            raise ValueError(f"Unrecognized date selector format: '{parts[0]}'. Allowed: olderThanDays, newerThanDays, between_YYYY-MM-DD_YYYY-MM-DD")

class WorkflowExecutionInputDocument(BaseModel):
    item_id: UUID4
    name: str
    content: str

class WorkflowExecutionOutputDocument(ContentItem):
    markdown_content: str
    current_version_number: int = 1
    model_config = { "from_attributes": True }

class RunWorkflowResponse(BaseModel):
    message: str
    output_document: WorkflowExecutionOutputDocument
    llm_raw_response: Optional[str] = None
