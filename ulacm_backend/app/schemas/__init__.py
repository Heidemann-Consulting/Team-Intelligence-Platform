# File: ulacm_backend/app/schemas/__init__.py
# Purpose: Makes Pydantic schemas available for easier import.
# Updated: Added ContentItemListItem to exports.

from .token import Token, TokenPayload
from .team import TeamBase, TeamCreate, TeamUpdate, TeamInDB, Team as TeamSchema, TeamListResponse
from .content_item import (
    ContentItemBase, ContentItemCreate, ContentItemUpdateMeta, ContentItemInDBBase,
    ContentItem, # Schema for basic item representation
    ContentItemWithCurrentVersion, # Schema for detailed item with full current version
    ContentItemListItem, # Lightweight schema for list views
    ContentItemTypeEnum,
    ContentItemDuplicatePayload, ContentItemSearchResult, ContentItemListResponse,
    SearchResultsResponse
)
from .content_version import (
    ContentVersionBase, ContentVersionCreate, ContentVersionInDBBase,
    ContentVersion as ContentVersionSchema, # Schema for version details
    ContentVersionDetails, ContentVersionListResponse,
    SaveVersionResponse,
    VersionMeta
)
from .workflow_definition import (
    WorkflowDefinition, WorkflowExecutionInputDocument, WorkflowExecutionOutputDocument,
    RunWorkflowResponse, RunWorkflowPayload # Added RunWorkflowPayload
)
from .msg import Msg

# It's good practice to also make specific schemas available directly if they were aliased before.
# For example, if ContentItemSchema was an alias for ContentItem, ensure ContentItem is exported.
# In this case, ContentItem is already part of the bulk import from .content_item.

# No specific alias for ContentItemSchema was used here that needs re-exporting.
# The previous ContentItemSchema = ContentItem was just for local aliasing if needed,
# but direct import of ContentItem is clearer.
