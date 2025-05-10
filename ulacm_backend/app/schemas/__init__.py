# File: ulacm_backend/app/schemas/__init__.py
# Purpose: Makes Pydantic schemas available for easier import.
# Corrected: Import 'ContentItem' and then alias it.

from .token import Token, TokenPayload
from .team import TeamBase, TeamCreate, TeamUpdate, TeamInDB, Team as TeamSchema, TeamListResponse
from .content_item import (
    ContentItemBase, ContentItemCreate, ContentItemUpdateMeta, ContentItemInDBBase,
    ContentItem, # <--- Import the original name 'ContentItem'
    ContentItemWithCurrentVersion, ContentItemTypeEnum,
    ContentItemDuplicatePayload, ContentItemSearchResult, ContentItemListResponse,
    SearchResultsResponse
)
from .content_version import (
    ContentVersionBase, ContentVersionCreate, ContentVersionInDBBase,
    ContentVersion as ContentVersionSchema, # Alias for ContentVersion
    ContentVersionDetails, ContentVersionListResponse,
    SaveVersionResponse,
    VersionMeta
)
from .workflow_definition import (
    WorkflowDefinition, WorkflowExecutionInputDocument, WorkflowExecutionOutputDocument,
    RunWorkflowResponse
)
from .msg import Msg # For simple message responses

# --- Apply Aliases After Import (Optional but good practice if used elsewhere) ---
# Although direct use of the imported name 'ContentItem' might be simpler,
# if you standardized on 'ContentItemSchema' elsewhere, keep the alias consistent.
# If you previously changed endpoints etc. to use 'ContentItemSchema', keep this alias logic.
# If not, you could remove the alias and just use 'ContentItem'.
# Assuming you intended to use the alias 'ContentItemSchema' widely:
ContentItemSchema = ContentItem # <-- Define the alias here

# Ensure VersionMeta is also exported if needed directly from schemas package
# (Already added in previous step)
