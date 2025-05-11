// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.
// Updated: Changed ContentItemBase to ContentItemBaseCore for createItem return type.

import apiClient from './apiClient';
import {
  ContentItemBaseCore, // Changed from ContentItemBase
  ContentItemDetail,
  ContentItemType,
  PaginatedResponse,
  SearchResultsResponseApi,
  ContentItemSearchResult,
  RunWorkflowResponse,
  ContentItemDuplicatePayload,
  ContentItemListed,
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
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
}

const contentService = {
  getItems: async (params: {
    item_type?: ContentItemType;
    offset?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    for_usage?: boolean;
    name_query?: string;
  }): Promise<PaginatedResponse<ContentItemListed>> => {
    const response = await apiClient.get<PaginatedResponse<ContentItemListed>>('/items', { params });
    return response.data;
  },

  createItem: async (itemData: ContentItemCreatePayload): Promise<ContentItemBaseCore> => { // Changed return type
    const response = await apiClient.post<ContentItemBaseCore>('/items', itemData); // Changed expected response type
    return response.data;
  },

  getItemDetails: async (itemId: string): Promise<ContentItemDetail> => {
    const response = await apiClient.get<ContentItemDetail>(`/items/${itemId}`);
    return response.data;
  },

  updateItemMeta: async (itemId: string, metaData: ContentItemMetaUpdatePayload): Promise<ContentItemBaseCore> => { // Changed return type
    const response = await apiClient.put<ContentItemBaseCore>(`/items/${itemId}/meta`, metaData); // Changed expected response type
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
         limit: params.limit ?? 20,
         items: response.data.items
     };
  },

  runWorkflow: async (workflowItemId: string): Promise<RunWorkflowResponse> => {
    const response = await apiClient.post<RunWorkflowResponse>(`/workflows/${workflowItemId}/run`);
    return response.data;
  },
};
export default contentService;
