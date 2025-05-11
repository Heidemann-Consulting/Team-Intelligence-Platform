// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.
// Updated: Modified GetItemsParams to include content_query.

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
  name_query?: string;
  content_query?: string; // New parameter for content search
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
}

const contentService = {
  getItems: async (params: GetItemsParams): Promise<PaginatedResponse<ContentItemListed>> => {
    const filteredParams: Record<string, any> = {};
    for (const key in params) {
        if (params[key as keyof GetItemsParams] !== undefined && params[key as keyof GetItemsParams] !== null && params[key as keyof GetItemsParams] !== '') {
            if (key === 'is_globally_visible' && typeof params[key as keyof GetItemsParams] === 'boolean') {
                 filteredParams[key] = params[key as keyof GetItemsParams];
            } else if (key !== 'is_globally_visible') {
                 filteredParams[key] = params[key as keyof GetItemsParams];
            }
        }
    }
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
    const response = await apiClient.post<RunWorkflowResponse>(`/workflows/${workflowItemId}/run`, payload);
    return response.data;
  },
};

export default contentService;
