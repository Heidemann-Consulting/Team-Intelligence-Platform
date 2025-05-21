// File: ulacm_frontend/src/types/api.ts
// Purpose: TypeScript types for API request/response structures.
// Updated: Added AskAIRequest and AskAIResponse types for the new AI endpoint.

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

export interface ContentItemBaseCore {
  item_id: string;
  team_id: string;
  item_type: ContentItemType;
  name: string;
  is_globally_visible: boolean;
  current_version_id?: string | null;
  current_version_number?: number;
  created_at: string;
  updated_at: string;
}

export interface ContentItemListed extends ContentItemBaseCore {
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}

export interface ContentItemDetail extends ContentItemBaseCore {
  markdown_content: string | null;
  version_created_at?: string | null;
  version_saved_by_team_id?: string | null;
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

export interface ContentItemSearchResult extends ContentItemBaseCore {
  snippet?: string | null;
  workflow_input_document_selectors?: string[] | null;
  workflow_output_name_template?: string | null;
}

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

// New Types for "Ask AI" feature
export interface AskAIRequestPayload {
    current_document_content: string;
    user_query: string;
    document_name?: string;
}

export interface AskAIResponseData {
    ai_response: string;
    model_used?: string;
}
