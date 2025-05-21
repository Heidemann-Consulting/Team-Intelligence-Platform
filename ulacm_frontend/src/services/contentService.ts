// File: ulacm_frontend/src/services/contentService.ts
// Purpose: Service for API calls related to content items, versions, and workflow execution.
// Updated: Improved stream end handling in runWorkflow and askAI.

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
  AskAIRequestPayload,
  AskAIResponseData,
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
  content_query?: string;
  name_globs?: string;
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
  current_document_content?: string;
}

const ULACM_STREAM_END_TOKEN = "ULACM_STREAM_END_TOKEN:";


const contentService = {
  getItems: async (params: GetItemsParams): Promise<PaginatedResponse<ContentItemListed>> => {
    const filteredParams: Record<string, any> = {};
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

  runWorkflow: async (
    workflowItemId: string,
    onChunk: (chunk: string) => void,
    onComplete: (data: RunWorkflowResponse) => void,
    onError: (error: Error) => void,
    payload?: RunWorkflowPayload
  ): Promise<void> => {
    const serviceName = "Workflow"; // For logging
    const requestPayload = payload && Object.keys(payload).length > 0 ? payload : {};
    const apiUrl = `/api/v1/workflows/${workflowItemId}/run`;

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify(requestPayload),
        credentials: 'include',
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try { const errorData = await response.json(); errorDetail = errorData.detail || errorDetail; } catch (e) { /* ignore */ }
        throw new Error(errorDetail);
      }

      const reader = response.body?.getReader();
      if (!reader) { throw new Error('Failed to get response reader for streaming.'); }
      const decoder = new TextDecoder();
      let buffer = '';
      let streamEndedCleanly = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (!streamEndedCleanly) { // If loop finished without processing END_TOKEN
            if (buffer.length > 0 && buffer.includes(ULACM_STREAM_END_TOKEN)) {
              // Attempt to process final part if token is there but wasn't fully parsed
               const endTokenIndex = buffer.indexOf(ULACM_STREAM_END_TOKEN);
               const textPart = buffer.substring(0, endTokenIndex);
               if(textPart.length > 0) onChunk(textPart);
               const potentialJsonPayload = buffer.substring(endTokenIndex + ULACM_STREAM_END_TOKEN.length);
               try {
                   const jsonData = JSON.parse(potentialJsonPayload);
                   if (jsonData.error) onError(new Error(jsonData.error));
                   else onComplete(jsonData as RunWorkflowResponse);
                   streamEndedCleanly = true;
               } catch (e) {
                   onError(new Error(`${serviceName} stream ended with token but incomplete/invalid JSON payload.`));
               }
            } else if (buffer.length > 0) {
                onChunk(buffer); // Process remaining buffer as a chunk
                onError(new Error(`${serviceName} stream ended prematurely without a completion signal.`));
            } else {
                 onError(new Error(`${serviceName} stream ended unexpectedly without data or completion signal.`));
            }
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        let endTokenIndex = buffer.indexOf(ULACM_STREAM_END_TOKEN);

        while(endTokenIndex !== -1) {
            const textPart = buffer.substring(0, endTokenIndex);
            if(textPart.length > 0) {
                onChunk(textPart);
            }
            const remainingAfterToken = buffer.substring(endTokenIndex);

            if (remainingAfterToken.startsWith(ULACM_STREAM_END_TOKEN)) {
                const potentialJsonPayload = remainingAfterToken.substring(ULACM_STREAM_END_TOKEN.length);
                try {
                    const jsonData = JSON.parse(potentialJsonPayload);
                    if (jsonData.error) { onError(new Error(jsonData.error));
                    } else { onComplete(jsonData as RunWorkflowResponse); }
                    streamEndedCleanly = true;
                    buffer = "";
                    return;
                } catch (e) {
                    // JSON not complete yet, keep it in buffer for next read
                    buffer = remainingAfterToken;
                    break; // Break inner while to get more data
                }
            }
            // If not starting with token, it means token was found mid-buffer but json part is not there yet or malformed.
            // This case is tricky. Let's assume for now if token is found, the JSON follows quickly.
            // The current logic will keep 'buffer = remainingAfterToken' and try to parse in next outer loop iteration.
        }

        if (buffer.indexOf(ULACM_STREAM_END_TOKEN) === -1) { // No token found yet in current buffer
            if (buffer.length > 0) {
                onChunk(buffer);
            }
            buffer = '';
        }
      }
    } catch (error: any) {
      console.error(`${serviceName} execution streaming error:`, error);
      onError(error);
    }
  },

  askAI: async (
    payload: AskAIRequestPayload,
    onChunk: (chunk: string) => void,
    onComplete: (data: AskAIResponseData) => void,
    onError: (error: Error) => void
  ): Promise<void> => {
    const serviceName = "AskAI"; // For logging
    const apiUrl = '/api/v1/ai/ask';
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify(payload),
        credentials: 'include',
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status}`;
        try { const errorData = await response.json(); errorDetail = errorData.detail || errorDetail;} catch (e) { /* ignore */ }
        throw new Error(errorDetail);
      }

      const reader = response.body?.getReader();
      if (!reader) { throw new Error('Failed to get response reader for AskAI streaming.');}
      const decoder = new TextDecoder();
      let buffer = '';
      let streamEndedCleanly = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (!streamEndedCleanly) {
            if (buffer.length > 0 && buffer.includes(ULACM_STREAM_END_TOKEN)) {
               const endTokenIndex = buffer.indexOf(ULACM_STREAM_END_TOKEN);
               const textPart = buffer.substring(0, endTokenIndex);
               if(textPart.length > 0) onChunk(textPart);
               const potentialJsonPayload = buffer.substring(endTokenIndex + ULACM_STREAM_END_TOKEN.length);
               try {
                   const jsonData = JSON.parse(potentialJsonPayload);
                   if (jsonData.error) onError(new Error(jsonData.error));
                   else onComplete({ model_used: jsonData.model_used, ai_response: "" } as AskAIResponseData);
                   streamEndedCleanly = true;
               } catch (e) {
                   onError(new Error(`${serviceName} stream ended with token but incomplete/invalid JSON payload.`));
               }
            } else if (buffer.length > 0) {
                onChunk(buffer);
                onError(new Error(`${serviceName} stream ended prematurely without a completion signal.`));
            } else {
                onError(new Error(`${serviceName} stream ended unexpectedly without data or completion signal.`));
            }
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        let endTokenIndex = buffer.indexOf(ULACM_STREAM_END_TOKEN);

        while(endTokenIndex !== -1) {
            const textPart = buffer.substring(0, endTokenIndex);
            if(textPart.length > 0) {
                onChunk(textPart);
            }
            const remainingAfterToken = buffer.substring(endTokenIndex);

            if (remainingAfterToken.startsWith(ULACM_STREAM_END_TOKEN)) {
                const potentialJsonPayload = remainingAfterToken.substring(ULACM_STREAM_END_TOKEN.length);
                try {
                    const jsonData = JSON.parse(potentialJsonPayload);
                    if (jsonData.error) { onError(new Error(jsonData.error));
                    } else { onComplete({ model_used: jsonData.model_used, ai_response: "" } as AskAIResponseData); }
                    streamEndedCleanly = true;
                    buffer = "";
                    return;
                } catch (e) {
                    buffer = remainingAfterToken;
                    break;
                }
            }
        }

        if (buffer.indexOf(ULACM_STREAM_END_TOKEN) === -1) {
            if (buffer.length > 0) {
                onChunk(buffer);
            }
            buffer = '';
        }
      }
    } catch (error: any) {
      console.error(`${serviceName} streaming error:`, error);
      onError(error);
    }
  },
};

export default contentService;
