// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.

import apiClient from './apiClient';
import {
  ContentItemBase,
  ContentItemDetail,
  ContentItemType,
  PaginatedResponse,
  SearchResultsResponseApi,
  ContentItemSearchResult,
  RunWorkflowResponse,
  ContentItemDuplicatePayload,
  ContentItemListed, // Import the new type
} from '@/types/api';
import {
    ContentVersionDetails,
    SaveVersionResponse,
    ContentVersionListResponse
} from '@/types/content';

export interface ContentItemCreatePayload {
  item_type: ContentItemType;
  name: string;
  template_id?: string;
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
    item_types?: string; // Comma-separated
    created_after?: string; // YYYY-MM-DD
    created_before?: string; // YYYY-MM-DD
    offset?: number;
    limit?: number;
    sort_by?: string; // Added for search results sorting
    sort_order?: 'asc' | 'desc'; // Added for search results sorting
}

const contentService = {
  getItems: async (params: {
    item_type?: ContentItemType;
    offset?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc'; // Ensure this is part of the type
    for_usage?: boolean;
    // Add search query param for basic name filtering if needed,
    // otherwise SearchPage specific search API will be used for full-text
    name_query?: string; // Example: for simple name filtering
  }): Promise<PaginatedResponse<ContentItemListed>> => { // Use ContentItemListed
    const response = await apiClient.get<PaginatedResponse<ContentItemListed>>('/items', { params });
    return response.data;
  },

  createItem: async (itemData: ContentItemCreatePayload): Promise<ContentItemBase> => {
    const response = await apiClient.post<ContentItemBase>('/items', itemData);
    return response.data;
  },

  getItemDetails: async (itemId: string): Promise<ContentItemDetail> => {
    const response = await apiClient.get<ContentItemDetail>(`/items/${itemId}`);
    return response.data;
  },

  updateItemMeta: async (itemId: string, metaData: ContentItemMetaUpdatePayload): Promise<ContentItemBase> => {
    const response = await apiClient.put<ContentItemBase>(`/items/${itemId}/meta`, metaData);
    return response.data;
  },

  deleteItem: async (itemId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/items/${itemId}`);
    return response.data;
  },

  duplicateItem: async (itemId: string, payload: ContentItemDuplicatePayload): Promise<ContentItemDetail> => {
    const response = await apiClient.post<ContentItemDetail>(`/items/${itemId}/duplicate`, payload);
    return response.data;
  },

  saveNewVersion: async (itemId: string, payload: ContentVersionCreatePayload): Promise<SaveVersionResponse> => {
    const response = await apiClient.post<SaveVersionResponse>(`/items/${itemId}/versions`, payload);
    return response.data;
  },

  listVersions: async (itemId: string, params?: { offset?: number; limit?: number; sort_order?: 'asc' | 'desc' }): Promise<ContentVersionListResponse> => {
    const response = await apiClient.get<ContentVersionListResponse>(`/items/${itemId}/versions`, { params });
    return response.data;
  },

  getVersionContent: async (itemId: string, versionId: string): Promise<ContentVersionDetails> => {
    const response = await apiClient.get<ContentVersionDetails>(`/items/${itemId}/versions/${versionId}`);
    return response.data;
  },

  searchItems: async (params: SearchParams): Promise<PaginatedResponse<ContentItemSearchResult>> => {
     const response = await apiClient.get<SearchResultsResponseApi>('/search', { params });
     return {
         total_count: response.data.total_count,
         offset: params.offset ?? 0,
         limit: params.limit ?? 20, // Default limit for search in frontend was 20
         items: response.data.items
     };
  },

  runWorkflow: async (workflowItemId: string): Promise<RunWorkflowResponse> => {
    const response = await apiClient.post<RunWorkflowResponse>(`/workflows/${workflowItemId}/run`);
    return response.data;
  },
};

export default contentService;
