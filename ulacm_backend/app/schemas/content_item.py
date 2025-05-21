# File: ulacm_backend/app/schemas/content_item.py
# Purpose: Pydantic schemas for ContentItem data (Documents, Templates, Workflows).
# Updated: Relaxed template_id validation for DOCUMENT type to support programmatic creation.
# Updated: Refined ContentItemListItem for lightweight list responses.
# Fixed: ContentItemListItem now inherits from ContentItemInDBBase to include created_at.

from pydantic import (
    BaseModel,
    UUID4,
    constr,
    Field,
    field_validator,
    model_validator,
    ValidationInfo,
    computed_field,
)
from typing import Optional, List, Union, Any
import datetime
import uuid
import logging

from app.db.models.content_item import ContentItemTypeEnum
from .content_version import ContentVersionDetails # Used by ContentItemWithCurrentVersion
# Forward reference will be used for WorkflowDefinition

log = logging.getLogger(__name__)

class ContentItemBase(BaseModel):
    name: constr(min_length=1, max_length=255)
    item_type: ContentItemTypeEnum

    model_config = {"from_attributes": True}


class ContentItemCreate(ContentItemBase):
    template_id: Optional[Union[UUID4, str]] = Field(
        None,
        description="For Documents created by users: the template to use. For Admin T/W creation or programmatic document creation (e.g., workflow output): not used or optional.",
    )

    @field_validator("template_id")
    @classmethod
    def check_template_id_format(
        cls, v: Optional[Union[UUID4, str]]
    ) -> Optional[Union[UUID4, str]]:
        if isinstance(v, str):
            try:
                return uuid.UUID(v, version=4)
            except ValueError:
                raise ValueError(f"Invalid UUID format for template_id: '{v}'")
        return v

    @model_validator(mode="after")
    def check_document_and_template_logic(self) -> "ContentItemCreate":
        if self.item_type != ContentItemTypeEnum.DOCUMENT and self.template_id:
            raise ValueError(
                "template_id should only be provided when item_type is 'Document'."
            )
        return self


class ContentItemUpdateMeta(BaseModel):
    name: Optional[constr(min_length=1, max_length=255)] = None
    is_globally_visible: Optional[bool] = None


class ContentItemInDBBase(ContentItemBase):
    item_id: UUID4
    team_id: UUID4
    is_globally_visible: bool
    current_version_id: Optional[UUID4] = None
    created_at: datetime.datetime # Item's creation timestamp
    updated_at: datetime.datetime # Item's last update timestamp

    model_config = {"from_attributes": True}


class ContentItem(ContentItemInDBBase):
    """Basic representation of a content item, often used for metadata updates or simple returns."""
    pass


class ContentItemWithCurrentVersion(ContentItem):
    """Detailed representation of a content item, including its current version's details.
    Used when full content is needed, e.g., for the editor view or single item retrieval."""
    current_version_for_computed_fields: Optional[ContentVersionDetails] = Field(
        default=None, alias="current_version", exclude=True
    )

    # Absolute path string literal for forward reference
    parsed_workflow_definition_internal: Optional['app.schemas.workflow_definition.WorkflowDefinition'] = Field(default=None, exclude=True)

    @computed_field
    @property
    def current_version_number(self) -> Optional[int]:
        if self.current_version_for_computed_fields:
            return self.current_version_for_computed_fields.version_number
        return None

    @computed_field
    @property
    def markdown_content(self) -> Optional[str]:
        if self.current_version_for_computed_fields:
            return self.current_version_for_computed_fields.markdown_content
        return None

    @computed_field
    @property
    def version_created_at(self) -> Optional[datetime.datetime]:
        if self.current_version_for_computed_fields:
            return self.current_version_for_computed_fields.created_at
        return None

    @computed_field
    @property
    def version_saved_by_team_id(self) -> Optional[UUID4]:
        if self.current_version_for_computed_fields:
            return self.current_version_for_computed_fields.saved_by_team_id
        return None

    @computed_field
    @property
    def workflow_input_document_selectors(self) -> Optional[List[str]]:
        if self.item_type == ContentItemTypeEnum.WORKFLOW and self.parsed_workflow_definition_internal:
            if self.parsed_workflow_definition_internal:
                 return self.parsed_workflow_definition_internal.inputDocumentSelectors
        return None

    @computed_field
    @property
    def workflow_output_name_template(self) -> Optional[str]:
        if self.item_type == ContentItemTypeEnum.WORKFLOW and self.parsed_workflow_definition_internal:
            if self.parsed_workflow_definition_internal:
                return self.parsed_workflow_definition_internal.outputName
        return None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class ContentItemListItem(ContentItemInDBBase): # Changed inheritance from ContentItemBase
    """
    Lightweight representation of a content item for list views.
    Inherits item_id, team_id, item_type, name, is_globally_visible,
    current_version_id, created_at, updated_at from ContentItemInDBBase.
    Omits full markdown_content. Includes essential fields for display in lists.
    Workflow-specific fields are populated if the item is a workflow.
    """
    current_version_number: Optional[int] = None # Explicitly defined here

    # For workflows, these are populated by the endpoint/conversion logic if applicable
    workflow_input_document_selectors: Optional[List[str]] = None
    workflow_output_name_template: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }


class ContentItemDuplicatePayload(BaseModel):
    new_name: constr(min_length=1, max_length=255)
    source_version_id: Optional[UUID4] = None
    target_owner_team_id: Optional[UUID4] = Field(
        None,
        description="For Admin use: Assigns ownership of the duplicate to this team_id.",
    )


class ContentItemSearchResult(ContentItemBase): # Search result can also be lightweight
    """Schema for items returned in search results. Includes a snippet."""
    item_id: UUID4
    team_id: UUID4
    is_globally_visible: bool
    current_version_id: Optional[UUID4] = None
    created_at: datetime.datetime # Ensure created_at is here for search results too
    updated_at: datetime.datetime
    current_version_number: Optional[int] = None
    snippet: Optional[str] = None

    parsed_workflow_definition_internal: Optional['app.schemas.workflow_definition.WorkflowDefinition'] = Field(default=None, exclude=True)

    @computed_field
    @property
    def workflow_input_document_selectors(self) -> Optional[List[str]]:
        if self.item_type == ContentItemTypeEnum.WORKFLOW and self.parsed_workflow_definition_internal:
            if self.parsed_workflow_definition_internal:
                return self.parsed_workflow_definition_internal.inputDocumentSelectors
        return None

    @computed_field
    @property
    def workflow_output_name_template(self) -> Optional[str]:
        if self.item_type == ContentItemTypeEnum.WORKFLOW and self.parsed_workflow_definition_internal:
            if self.parsed_workflow_definition_internal:
                return self.parsed_workflow_definition_internal.outputName
        return None

    model_config = {"from_attributes": True}


class ContentItemListResponse(BaseModel):
    total_count: int
    offset: int
    limit: int
    items: List[ContentItemListItem]


class SearchResultsResponse(BaseModel):
    total_count: int
    offset: int
    limit: int
    items: List[ContentItemSearchResult]
