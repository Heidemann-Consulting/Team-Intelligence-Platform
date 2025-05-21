# File: ulacm_backend/app/schemas/workflow_definition.py
# Purpose: Pydantic schemas for Process Workflow definitions and execution.
# Updated: Ensured WorkflowExecutionOutputDocument always provides a 'markdown_content' string.

from pydantic import (
    BaseModel, UUID4, constr, Field, field_validator, ValidationInfo, computed_field
)
from typing import Optional, List, Dict, Any
import datetime

from app.schemas.content_item import ContentItem # This is effectively ContentItemInDBBase
from app.schemas.content_version import ContentVersionDetails # For typing current_version_data

class WorkflowDefinition(BaseModel):
    processWorkFlowName: Optional[constr(min_length=1, max_length=255)] = None
    trigger: constr(pattern=r"^manual$") = "manual"
    inputDocumentSelectors: List[constr(min_length=1, max_length=255)] = Field(..., min_length=1)
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

class WorkflowExecutionOutputDocument(ContentItem): # Inherits fields from ContentItem (ContentItemInDBBase)
    """
    Pydantic schema for the output_document part of the RunWorkflowResponse.
    It ensures 'markdown_content' and 'current_version_number' are correctly populated
    from the ContentItem ORM model's 'current_version' relationship.
    """

    # This field is used internally by the computed properties below.
    # Pydantic, with from_attributes=True and populate_by_name=True, will look for an attribute
    # named 'current_version' on the ORM model and validate its data using ContentVersionDetails.
    # We exclude it from the final dumped JSON as its data will be flattened into this model.
    current_version_data: Optional[ContentVersionDetails] = Field(default=None, alias="current_version", exclude=True)

    @computed_field
    @property
    def markdown_content(self) -> str:
        """
        Ensures markdown_content is always a string.
        Defaults to an empty string if current_version or its markdown_content is None.
        The database schema for content_versions.markdown_content is NOT NULL,
        so current_version_data.markdown_content should ideally always be a string.
        """
        if self.current_version_data and self.current_version_data.markdown_content is not None:
            return self.current_version_data.markdown_content
        # This case (current_version_data or its markdown_content being None) should be rare for a successfully
        # created workflow output, as the content comes from the LLM response which should be non-null.
        # Defaulting to empty string ensures the frontend type contract (markdown_content: string) is met.
        log = logging.getLogger(__name__) # Local import for logging within property
        log.warning(f"WorkflowExecutionOutputDocument: markdown_content was None for item_id {self.item_id if hasattr(self, 'item_id') else 'Unknown'}, defaulting to empty string. Current_version_data: {self.current_version_data}")
        return ""

    @computed_field
    @property
    def current_version_number(self) -> int:
        """
        Provides the version number, defaulting to 1 if not available from current_version_data.
        """
        if self.current_version_data:
            return self.current_version_data.version_number
        # For a newly created workflow output document, it should always have version 1.
        # If current_version_data is None here, it might indicate an issue in populating
        # the ORM object before Pydantic validation.
        log = logging.getLogger(__name__) # Local import for logging within property
        log.warning(f"WorkflowExecutionOutputDocument: current_version_number was not available for item_id {self.item_id if hasattr(self, 'item_id') else 'Unknown'}, defaulting to 1. Current_version_data: {self.current_version_data}")
        return 1

    model_config = {
        "from_attributes": True, # Allows Pydantic to read from ORM attributes
        "populate_by_name": True, # Allows use of alias "current_version" for current_version_data
    }

class RunWorkflowPayload(BaseModel):
    input_document_ids: Optional[List[UUID4]] = Field(None, description="Optional list of specific document IDs to use as input.")
    additional_ai_input: Optional[str] = Field(None, description="Optional additional text input for the AI.")
    current_document_content: Optional[str] = Field(None, description="Optional raw content of the current document, for 'Ask AI' like features.")

class RunWorkflowResponse(BaseModel):
    message: str
    output_document: WorkflowExecutionOutputDocument
    llm_raw_response: Optional[str] = None # This is the full raw response, which client reconstructs from stream
