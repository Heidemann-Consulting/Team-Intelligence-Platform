// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.
// Updated for Option 3 (Admin System Team):
// - getItems parameters adjusted to support admin/team views of Templates/Workflows.
// - createItem needs to be called with context of who is creating.

import apiClient from './apiClient';
import {
  ContentItemBase,
  ContentItemDetail,
  ContentItemType,
  PaginatedResponse,
  SearchResultsResponseApi, // Assuming this is the raw backend response type for search
  ContentItemSearchResult,  // Frontend type for a search result item
  RunWorkflowResponse,
  ContentItemDuplicatePayload
} from '@/types/api';
import {
    ContentVersionDetails,
    SaveVersionResponse,
    ContentVersionListResponse
} from '@/types/content';
// import { Team } from '@/types/auth'; // To get currentTeam.team_id

export interface ContentItemCreatePayload {
  item_type: ContentItemType;
  name: string;
  template_id?: string; // For creating documents
  // For admin creating T/W, team_id is handled by backend based on admin role
}

export interface ContentItemMetaUpdatePayload {
  name?: string;
  is_globally_visible?: boolean;
}

export interface ContentVersionCreatePayload {
  markdown_content: string;
}

export interface SearchParams {
    query?: string;
    item_types?: string;
    created_after?: string;
    created_before?: string;
    offset?: number;
    limit?: number;
}

// Helper to determine if current user is admin
// In a real app, this might come from an auth context or a utility function
// For now, assuming admin actions are identified by lack of teamId or specific admin flag
// The backend uses a dedicated admin token.

const contentService = {
  // === Content Item Endpoints ===

  /**
   * Fetches content items.
   * For Admins:
   * - If item_type is TEMPLATE or WORKFLOW, lists items owned by ADMIN_SYSTEM_TEAM_ID.
   * - If item_type is DOCUMENT, lists all documents from all teams.
   * - If no item_type, lists all items (potentially very large).
   * For Teams:
   * - If item_type is DOCUMENT, lists documents owned by the team or globally visible non-admin documents.
   * - If item_type is TEMPLATE or WORKFLOW and `forUsage` is true, lists ADMIN_SYSTEM_TEAM_ID owned, globally visible items.
   * - Otherwise, for teams, listing TEMPLATE or WORKFLOW directly (not for_usage) should yield empty or be disallowed by UI.
   */
  getItems: async (params: {
    item_type?: ContentItemType;
    offset?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: string;
    // `for_usage` tells the backend that a team is requesting T/W for selection/execution
    // The backend `get_items_for_team_or_admin` uses `list_for_team_usage` based on this.
    for_usage?: boolean;
  }): Promise<PaginatedResponse<ContentItemBase>> => {
    // `for_usage` is now directly passed to the backend as a query param
    const response = await apiClient.get<PaginatedResponse<ContentItemBase>>('/items', { params });
    // Assuming backend PaginatedResponse matches frontend, otherwise map here
    return response.data;
  },

  createItem: async (itemData: ContentItemCreatePayload): Promise<ContentItemBase> => {
    // Backend determines ownership based on authenticated user (admin or team)
    const response = await apiClient.post<ContentItemBase>('/items', itemData);
    return response.data;
  },

  getItemDetails: async (itemId: string): Promise<ContentItemDetail> => {
    // Backend determines if user can access based on role and item ownership
    const response = await apiClient.get<ContentItemDetail>(`/items/${itemId}`);
    return response.data;
  },

  updateItemMeta: async (itemId: string, metaData: ContentItemMetaUpdatePayload): Promise<ContentItemBase> => {
    // Backend determines if user can update based on role and item ownership
    const response = await apiClient.put<ContentItemBase>(`/items/${itemId}/meta`, metaData);
    return response.data;
  },

  deleteItem: async (itemId: string): Promise<{ message: string }> => {
    // Backend determines if user can delete
    const response = await apiClient.delete<{ message: string }>(`/items/${itemId}`);
    return response.data;
  },

  duplicateItem: async (itemId: string, payload: ContentItemDuplicatePayload): Promise<ContentItemDetail> => {
    // Backend determines ownership of new item based on who is duplicating
    const response = await apiClient.post<ContentItemDetail>(`/items/${itemId}/duplicate`, payload);
    return response.data;
  },

  // === Content Version Endpoints ===
  // Access control is handled by backend based on user role and item ownership

  saveNewVersion: async (itemId: string, payload: ContentVersionCreatePayload): Promise<SaveVersionResponse> => {
    const response = await apiClient.post<SaveVersionResponse>(`/items/${itemId}/versions`, payload);
    return response.data;
  },

  listVersions: async (itemId: string, params?: { offset?: number; limit?: number; sort_order?: string }): Promise<ContentVersionListResponse> => {
    const response = await apiClient.get<ContentVersionListResponse>(`/items/${itemId}/versions`, { params });
    return response.data;
  },

  getVersionContent: async (itemId: string, versionId: string): Promise<ContentVersionDetails> => {
    const response = await apiClient.get<ContentVersionDetails>(`/items/${itemId}/versions/${versionId}`);
    return response.data;
  },

  // === Search Endpoint ===
  searchItems: async (params: SearchParams): Promise<PaginatedResponse<ContentItemSearchResult>> => {
     const response = await apiClient.get<SearchResultsResponseApi>('/search', { params });
     // Assuming SearchResultsResponseApi from backend needs mapping to PaginatedResponse<ContentItemSearchResult>
     return {
         total_count: response.data.total_count, // Ensure backend uses total_count or map if it's total_results
         offset: params.offset ?? 0,
         limit: params.limit ?? 20, // Default search limit
         items: response.data.items // Ensure backend results field is 'items' or map if it's 'results'
     };
  },

  // === Workflow Execution Endpoint ===
  runWorkflow: async (workflowItemId: string): Promise<RunWorkflowResponse> => {
    // This is a team-specific action. Backend ensures workflow is runnable by team.
    const response = await apiClient.post<RunWorkflowResponse>(`/workflows/${workflowItemId}/run`);
    return response.data;
  },
};

export default contentService;
