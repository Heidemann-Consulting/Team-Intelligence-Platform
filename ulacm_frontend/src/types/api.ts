// File: ulacm_frontend/src/types/api.ts
// Purpose: TypeScript types for API request/response structures.
// Updated: Adjusted ContentItemListed to match backend's lightweight ContentItemListItem.

import { Team } from './auth';

export interface TeamListResponse {
  total_count: number;
  offset: number;
  limit: number;
  teams: Team[];
}

export interface PaginatedResponse<T> {
  total_count: number;
  offset: number;
  limit: number;
  items: T[];
}

export enum ContentItemType {
  DOCUMENT = "DOCUMENT",
  TEMPLATE = "TEMPLATE",
  WORKFLOW = "WORKFLOW",
}

// Base properties common to all content items when listed or detailed
export interface ContentItemBaseCore {
  item_id: string;
  team_id: string; // Owning team's ID
  item_type: ContentItemType;
  name: string;
  is_globally_visible: boolean;
  current_version_id?: string | null;
  current_version_number?: number; // Current version number of the item
  created_at: string; // Item creation date
  updated_at: string; // Item last updated date (includes new versions, meta changes)
}

// Lightweight representation for list views.
// Corresponds to backend's ContentItemListItem.
export interface ContentItemListed extends ContentItemBaseCore {
  // Inherits item_id, team_id, item_type, name, is_globally_visible,
  // current_version_id, current_version_number, created_at, updated_at.

  // Workflow-specific fields, populated if item_type is WORKFLOW.
  // These are directly on the ContentItemListItem if it's a workflow.
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}


// Detailed representation, used for editor view or single item retrieval.
// Corresponds to backend's ContentItemWithCurrentVersion.
export interface ContentItemDetail extends ContentItemBaseCore {
  // Fields from ContentItemBaseCore are inherited.

  // Fields from the current version, typically included in detail views.
  markdown_content: string | null; // Current version's markdown content.
  version_created_at?: string | null; // Current version's creation date (save time).
  version_saved_by_team_id?: string | null; // Team ID of who saved the current version.

  // Workflow-specific fields, populated if item_type is WORKFLOW.
  // These are derived from the current_version's content.
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}


export interface ContentItemForUsage extends Omit<ContentItemBaseCore, 'team_id' | 'is_globally_visible'> {
  description?: string;
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}

export interface ContentItemDuplicatePayload {
  new_name: string;
  source_version_id?: string;
  target_owner_team_id?: string;
}

// Schema for items returned in search results.
// Corresponds to backend's ContentItemSearchResult.
export interface ContentItemSearchResult extends ContentItemBaseCore {
  // Inherits item_id, team_id, item_type, name, is_globally_visible,
  // current_version_id, current_version_number, created_at, updated_at.
  snippet?: string | null;

  // Workflow-specific fields, populated if item_type is WORKFLOW and search result includes them.
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}

// This type might be specific to the backend's direct response for search
export interface SearchResultsResponseApi extends PaginatedResponse<ContentItemSearchResult> {}


export interface WorkflowExecutionOutputDocument extends ContentItemDetail {
    markdown_content: string;
    current_version_number: number;
}

export interface RunWorkflowResponse {
    message: string;
    output_document: WorkflowExecutionOutputDocument;
    llm_raw_response?: string | null;
}
