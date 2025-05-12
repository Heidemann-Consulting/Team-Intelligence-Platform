// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.
// Updated: GetItemsParams to include name_globs for server-side filtering by workflow selectors.

import apiClient from './apiClient';
import {
  ContentItemBaseCore,
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

export interface GetItemsParams {
  item_type?: ContentItemType;
  offset?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  for_usage?: boolean;
  name_query?: string; // For simple substring name search
  content_query?: string;
  name_globs?: string; // Comma-separated list of glob patterns for name
  created_after?: string;
  created_before?: string;
  is_globally_visible?: boolean;
}

export interface SearchParams {
    query?: string;
    item_types?: string;
    created_after?: string;
    created_before?: string;
    offset?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
}

export interface RunWorkflowPayload {
  input_document_ids?: string[];
  additional_ai_input?: string;
}

const contentService = {
  getItems: async (params: GetItemsParams): Promise<PaginatedResponse<ContentItemListed>> => {
    const filteredParams: Record<string, any> = {};
    // Build params carefully, excluding undefined/null/empty strings
    (Object.keys(params) as Array<keyof GetItemsParams>).forEach(key => {
        const value = params[key];
        if (value !== undefined && value !== null) {
            if (typeof value === 'string' && value.trim() === '') {
                // Skip empty strings
            } else {
                 filteredParams[key] = value;
            }
        }
    });
    const response = await apiClient.get<PaginatedResponse<ContentItemListed>>('/items', { params: filteredParams });
    return response.data;
  },

  createItem: async (itemData: ContentItemCreatePayload): Promise<ContentItemBaseCore> => {
    const response = await apiClient.post<ContentItemBaseCore>('/items', itemData);
    return response.data;
  },

  getItemDetails: async (itemId: string): Promise<ContentItemDetail> => {
    const response = await apiClient.get<ContentItemDetail>(`/items/${itemId}`);
    return response.data;
  },

  updateItemMeta: async (itemId: string, metaData: ContentItemMetaUpdatePayload): Promise<ContentItemBaseCore> => {
    const response = await apiClient.put<ContentItemBaseCore>(`/items/${itemId}/meta`, metaData);
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

  runWorkflow: async (workflowItemId: string, payload?: RunWorkflowPayload): Promise<RunWorkflowResponse> => {
    const requestPayload = payload && Object.keys(payload).length > 0 ? payload : {};
    const response = await apiClient.post<RunWorkflowResponse>(`/workflows/${workflowItemId}/run`, requestPayload);
    return response.data;
  },
};

export default contentService;
