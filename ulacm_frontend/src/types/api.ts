// File: ulacm_frontend/src/types/api.ts
// Purpose: TypeScript types for API request/response structures.
// Updated: Added workflow_input_document_selectors and workflow_output_name_template to relevant types.

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
  current_version_number?: number;
  created_at: string; // Item creation date
  updated_at: string; // Item last updated date (includes new versions, meta changes)
}

// This is the primary type used in ContentListPage and ExecuteWorkflowPage for listed items.
// It includes fields from ContentItemWithCurrentVersion (backend) that are relevant for listing.
export interface ContentItemListed extends ContentItemBaseCore {
  // Fields derived from the current version
  markdown_content?: string | null; // Current version's markdown (might be too heavy for general lists, often on detail)
  version_created_at?: string | null; // Current version's creation date (save time of current version)
  version_saved_by_team_id?: string | null; // Current version's saver

  // Workflow-specific fields, populated if item_type is WORKFLOW
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}


export interface ContentItemDetail extends ContentItemListed {
  // ContentItemListed already includes most necessary fields.
  // markdown_content is definitely needed for detail view.
  markdown_content: string | null; // Ensure it's present, even if null

  // version_created_at and version_saved_by_team_id are already in ContentItemListed
  // workflow_input_document_selectors and workflow_output_name_template are also in ContentItemListed
}


export interface ContentItemForUsage extends Omit<ContentItemBaseCore, 'team_id' | 'is_globally_visible'> {
  description?: string; // Example of a field specific to this usage context
  // May also need workflow_input_document_selectors and workflow_output_name_template if used for workflows
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}

export interface ContentItemDuplicatePayload {
  new_name: string;
  source_version_id?: string;
  target_owner_team_id?: string; // Optional: For admin to assign duplicate to a different team
}

export interface ContentItemSearchResult extends ContentItemListed {
    snippet?: string | null;
    // Inherits workflow_input_document_selectors and workflow_output_name_template from ContentItemListed
    // if search results are to include this data (would require backend search to parse workflow content)
}

// This type might be specific to the backend's direct response for search
export interface SearchResultsResponseApi extends PaginatedResponse<ContentItemSearchResult> {}


export interface WorkflowExecutionOutputDocument extends ContentItemDetail {
    // ContentItemDetail now includes workflow_input_document_selectors and workflow_output_name_template
    // if the output document itself is a workflow (which is not typical).
    // For a Document output, these workflow-specific fields would be null/undefined.
    markdown_content: string; // Ensure this is always present for the output document's content
    current_version_number: number;
}

export interface RunWorkflowResponse {
    message: string;
    output_document: WorkflowExecutionOutputDocument;
    llm_raw_response?: string | null;
}
