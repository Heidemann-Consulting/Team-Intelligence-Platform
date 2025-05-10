// File: ulacm_frontend/src/types/api.ts
// Purpose: TypeScript types for API request/response structures.
// No changes needed here from previous version if backend aligns to these.
// team_id on ContentItemBase remains string, backend handles its value (actual team or ADMIN_SYSTEM_TEAM_ID).

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

export interface ContentItemBase {
  item_id: string;
  team_id: string; // Owning team or ADMIN_SYSTEM_TEAM_ID for admin T/W
  item_type: ContentItemType;
  name: string;
  is_globally_visible: boolean;
  current_version_id?: string | null;
  current_version_number?: number;
  created_at: string;
  updated_at: string;
}

export interface ContentItemDetail extends ContentItemBase {
  markdown_content?: string | null;
  version_created_at?: string | null;
  version_saved_by_team_id?: string | null; // ID of the team that saved this version (could be ADMIN_SYSTEM_TEAM_ID)
}

// Used for what team gets when listing templates/workflows for usage
// May not be strictly needed if ContentItemBase is used and frontend just doesn't show some fields
export interface ContentItemForUsage extends Omit<ContentItemBase, 'team_id' | 'is_globally_visible'> {
  // team_id and is_globally_visible might be irrelevant if only admin items are shown
  description?: string; // Optional: if backend can provide descriptions for listed T/W
}


export interface ContentItemDuplicatePayload {
  new_name: string;
  source_version_id?: string;
}

export interface ContentItemSearchResult extends ContentItemBase {
    snippet?: string | null;
}

// Assumed backend response for search
export interface SearchResultsResponseApi extends PaginatedResponse<ContentItemSearchResult> {}


export interface WorkflowExecutionOutputDocument extends ContentItemDetail {
    markdown_content: string;
    current_version_number: 1;
}

export interface RunWorkflowResponse {
    message: string;
    output_document: WorkflowExecutionOutputDocument;
    llm_raw_response?: string | null;
}
