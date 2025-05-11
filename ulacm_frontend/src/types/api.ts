// File: ulacm_frontend/src/types/api.ts
// Purpose: TypeScript types for API request/response structures.

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

// This will be the primary type used in ContentListPage
export interface ContentItemListed extends ContentItemBase {
  // Fields from ContentItemBase are inherited
  // Fields from ContentItemWithCurrentVersion (backend) that are relevant for listing:
  markdown_content?: string | null; // Current version's markdown (might be too heavy for list)
  version_created_at?: string | null; // Current version's creation date
  version_saved_by_team_id?: string | null; // Current version's saver
}


export interface ContentItemBase {
  item_id: string;
  team_id: string; // Owning team's ID
  item_type: ContentItemType;
  name: string;
  is_globally_visible: boolean;
  current_version_id?: string | null;
  current_version_number?: number;
  created_at: string; // Item creation date
  updated_at: string; // Item last updated date (includes new versions, meta changes)
  // Added to hold the creation date of the current version specifically
  version_created_at?: string | null;
}

export interface ContentItemDetail extends ContentItemBase {
  markdown_content?: string | null;
  // version_created_at is already in ContentItemBase now
  version_saved_by_team_id?: string | null;
}

export interface ContentItemForUsage extends Omit<ContentItemBase, 'team_id' | 'is_globally_visible'> {
  description?: string;
}

export interface ContentItemDuplicatePayload {
  new_name: string;
  source_version_id?: string;
}

export interface ContentItemSearchResult extends ContentItemBase {
    snippet?: string | null;
    // version_created_at is inherited from ContentItemBase
}

export interface SearchResultsResponseApi extends PaginatedResponse<ContentItemSearchResult> {}

export interface WorkflowExecutionOutputDocument extends ContentItemDetail {
    markdown_content: string; // Ensure this is always present
    current_version_number: number; // Defaulted to 1 in backend, should be accurate
}

export interface RunWorkflowResponse {
    message: string;
    output_document: WorkflowExecutionOutputDocument;
    llm_raw_response?: string | null;
}
