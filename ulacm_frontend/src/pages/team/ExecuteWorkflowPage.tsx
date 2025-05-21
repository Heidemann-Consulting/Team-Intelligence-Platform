// File: ulacm_frontend/src/pages/team/ExecuteWorkflowPage.tsx
// Purpose: Page for Teams to list and execute available (Admin-created) Workflows.
// Updated to use the refactored RunWorkflowModal for streaming.
// Fixed: Decoupled main workflow list fetching from individual prompt preview fetching to improve stability.
// Fixed: Adjusted prompt preview container CSS to ensure proper scrolling from the top in all browsers.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { FolderGit2, Play, AlertTriangle, RefreshCw, ChevronLeft, ChevronRight, Search as SearchIcon, Info, ListTree, TextCursorInput, Eye } from 'lucide-react';
import { ContentItemListed, ContentItemType, PaginatedResponse, ContentItemDetail } from '@/types/api';
import contentService from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import RunWorkflowModal from '@/components/content/RunWorkflowModal';
import SelectInputDocumentsModal from '@/components/content/SelectInputDocumentsModal';
import { useNavigate } from 'react-router-dom';

type GetItemsParams = Parameters<typeof contentService.getItems>[0];

const ExecuteWorkflowPage: React.FC = () => {
  const [workflows, setWorkflows] = useState<ContentItemListed[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 15,
    total_count: 0,
  });
  const [workflowToGetInputsFor, setWorkflowToGetInputsFor] = useState<ContentItemListed | null>(null);
  const [showSelectInputsModal, setShowSelectInputsModal] = useState(false);

  const [selectedWorkflowForRun, setSelectedWorkflowForRun] = useState<ContentItemListed | null>(null);
  const [initialPayloadForRun, setInitialPayloadForRun] = useState<Parameters<typeof contentService.runWorkflow>[4]>(undefined);
  const [showRunModal, setShowRunModal] = useState(false);

  const [contentQueryInput, setContentQueryInput] = useState('');
  const [debouncedContentQuery, setDebouncedContentQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const navigate = useNavigate();

  const [workflowPromptPreviews, setWorkflowPromptPreviews] = useState<Record<string, string | null>>({});
  const [loadingPreviewFor, setLoadingPreviewFor] = useState<string | null>(null);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);


  useEffect(() => {
    setIsTyping(true);
    const handler = setTimeout(() => {
      if (isMounted.current) {
        setDebouncedContentQuery(contentQueryInput);
        setPagination(p => ({ ...p, offset: 0 }));
        setIsTyping(false);
      }
    }, 500);
    return () => clearTimeout(handler);
  }, [contentQueryInput]);

  const fetchWorkflowPrompt = useCallback(async (workflowId: string) => {
    if (!isMounted.current) return;
    setLoadingPreviewFor(workflowId);
    try {
      const details: ContentItemDetail = await contentService.getItemDetails(workflowId);
      let promptContent = "Prompt not found in details.";
      if (details.markdown_content) {
        const match = details.markdown_content.match(/prompt:\s*\|?\s*([\s\S]*)/i);
        if (match && match[1]) {
          promptContent = match[1].trim();
        } else {
          promptContent = details.markdown_content;
        }
      }
      if (isMounted.current) {
        setWorkflowPromptPreviews(prev => ({ ...prev, [workflowId]: promptContent }));
      }
    } catch (err) {
      console.error(`Failed to fetch details for workflow ${workflowId} for prompt preview:`, err);
      if (isMounted.current) {
        setWorkflowPromptPreviews(prev => ({ ...prev, [workflowId]: "Could not load prompt preview." }));
      }
    } finally {
      if (isMounted.current) {
        setLoadingPreviewFor(null);
      }
    }
  }, []);

  const stableFetchWorkflows = useCallback(async (offset = 0) => {
    if (!isMounted.current) return;
    setIsLoading(true);
    setError(null);
    try {
      const params: GetItemsParams = {
        item_type: ContentItemType.WORKFLOW,
        offset,
        limit: pagination.limit,
        sort_by: 'name',
        sort_order: 'asc',
        for_usage: true,
        content_query: debouncedContentQuery.trim() || undefined,
      };
      if (params.content_query) {
        params.sort_by = 'rank';
        params.sort_order = 'desc';
      }

      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);
      if (isMounted.current) {
        setWorkflows(data.items);
        setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
      }
    } catch (err: any) {
      console.error("Failed to fetch workflows:", err);
      if (isMounted.current) {
        const errorMessage = err.message || 'Failed to load available workflows.';
        setError(errorMessage);
      }
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  }, [pagination.limit, debouncedContentQuery]);

  useEffect(() => {
    if (isMounted.current) {
        stableFetchWorkflows(pagination.offset);
    }
  }, [stableFetchWorkflows, pagination.offset]);

  useEffect(() => {
    if (isMounted.current && workflows.length > 0) {
      workflows.forEach(wf => {
        if (!workflowPromptPreviews[wf.item_id]) {
          fetchWorkflowPrompt(wf.item_id);
        }
      });
    }
  }, [workflows, fetchWorkflowPrompt, workflowPromptPreviews]);


  const handleInitiateWorkflowRun = (workflow: ContentItemListed) => {
    setWorkflowToGetInputsFor(workflow);
    setShowSelectInputsModal(true);
  };

  const handleConfirmInputDocumentSelection = (selectedDocumentIds: string[], additionalAiInput?: string) => {
    setShowSelectInputsModal(false);
    if (workflowToGetInputsFor) {
      setSelectedWorkflowForRun(workflowToGetInputsFor);
      setInitialPayloadForRun({
        input_document_ids: selectedDocumentIds.length > 0 ? selectedDocumentIds : undefined,
        additional_ai_input: additionalAiInput?.trim() || undefined,
      });
      setShowRunModal(true);
    }
    setWorkflowToGetInputsFor(null);
  };

  const handleCloseRunModal = () => {
    setShowRunModal(false);
    setSelectedWorkflowForRun(null);
    setInitialPayloadForRun(undefined);
  };

  const handleViewOutputDocument = (outputItemId: string) => {
    handleCloseRunModal();
    navigate(`/app/documents/${outputItemId}`);
  };

  const handlePageChange = (newOffset: number) => {
    if (newOffset >= 0 && (newOffset < pagination.total_count || pagination.total_count === 0)) {
      setPagination(prev => ({ ...prev, offset: newOffset }));
    }
  };

  const totalPages = Math.ceil(pagination.total_count / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const displayableWorkflows = workflows;

  const renderPromptPreviewHTML = (promptText: string | null): { __html: string } => {
    if (!promptText) return { __html: "<p class='text-ulacm-gray-400 italic text-xs text-center p-2'>No prompt preview available.</p>" };
    try {
      return { __html: `<pre class="whitespace-pre-wrap text-xs">${promptText.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>` };
    } catch (parseError) {
      console.error("Error rendering prompt preview:", parseError);
      return { __html: "<p class='text-red-500 font-semibold text-xs'>Error rendering prompt preview.</p>" };
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row justify-between md:items-center">
        <h1 className="text-3xl font-bold text-ulacm-gray-800 flex items-center">
          <FolderGit2 size={30} className="mr-3 text-purple-600" /> Execute Workflow
        </h1>
        <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
          <div className="relative">
            <input
              type="search"
              value={contentQueryInput}
              onChange={(e) => setContentQueryInput(e.target.value)}
              placeholder="Search workflow name/content..."
              className="w-full md:w-64 pl-10 pr-4 py-2 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out text-sm"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ulacm-gray-400 pointer-events-none">
              {isTyping || (isLoading && debouncedContentQuery) ? <LoadingSpinner size="sm" color="text-ulacm-gray-400"/> : <SearchIcon size={18} />}
            </div>
          </div>
          <button
            onClick={() => stableFetchWorkflows(pagination.offset)}
            disabled={isLoading}
            className="p-2.5 text-ulacm-gray-500 hover:text-ulacm-primary hover:bg-ulacm-gray-100 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50"
            title="Refresh Workflows List"
          >
            <RefreshCw size={18} className={isLoading && !isTyping ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {isLoading && displayableWorkflows.length === 0 && (
        <div className="flex justify-center items-center py-20 bg-white rounded-xl shadow-md border border-ulacm-gray-100">
          <LoadingSpinner size="lg" color="text-purple-600" />
          <p className="ml-3 text-ulacm-gray-600">Loading available workflows...</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-red-400" aria-hidden="true" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Failed to Load Workflows</h3>
              <div className="mt-2 text-sm text-red-700"><p>{error}</p></div>
              <div className="mt-4">
                <button onClick={() => stableFetchWorkflows(0)} className="text-sm font-medium text-red-800 hover:text-red-600 underline">
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {!isLoading && !error && (
        <>
          {displayableWorkflows.length === 0 && debouncedContentQuery && pagination.total_count === 0 &&(
            <div className="text-center py-12 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                 <SearchIcon size={48} className="mx-auto text-ulacm-gray-300"/>
                <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No workflows match "{debouncedContentQuery}"</h3>
                <p className="mt-1 text-sm text-ulacm-gray-500">Try a different search term.</p>
            </div>
          )}
          {displayableWorkflows.length === 0 && !debouncedContentQuery && pagination.total_count === 0 && (
             <div className="text-center py-12 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                <FolderGit2 size={48} className="mx-auto text-ulacm-gray-300"/>
                <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No Workflows Available</h3>
                <p className="mt-1 text-sm text-ulacm-gray-500">Administrators need to create and share workflows for execution.</p>
             </div>
          )}

          {displayableWorkflows.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayableWorkflows.map((wf) => (
                <div key={wf.item_id} className="bg-white p-5 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-200 border border-ulacm-gray-100 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center mb-3">
                      <FolderGit2 className="h-7 w-7 mr-2.5 text-purple-600 flex-shrink-0" />
                      <h2 className="text-xl font-semibold text-ulacm-gray-800 truncate" title={wf.name}>
                        {wf.name}
                      </h2>
                    </div>

                    {wf.workflow_input_document_selectors && wf.workflow_input_document_selectors.length > 0 && (
                      <div className="mb-3">
                        <h4 className="text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider mb-1.5 flex items-center">
                          <ListTree size={14} className="mr-1.5 text-ulacm-gray-400"/> Input Document Selectors
                        </h4>
                        <ul className="list-none pl-0 space-y-1 max-h-20 overflow-y-auto scrollbar-thin scrollbar-thumb-ulacm-gray-200 scrollbar-track-ulacm-gray-100">
                          {wf.workflow_input_document_selectors.map((selector, index) => (
                            <li key={index} className="text-sm text-ulacm-gray-700 bg-ulacm-gray-50 px-2.5 py-1 rounded-md border border-ulacm-gray-200 shadow-sm">
                              <code className="text-purple-700 font-mono text-xs">{selector}</code>
                            </li>
                          ))}
                        </ul>
                         <p className="mt-1.5 text-xs text-ulacm-gray-500 italic flex items-start">
                            <Info size={14} className="mr-1 text-ulacm-gray-400 flex-shrink-0 mt-px"/> This workflow can use documents matching these patterns.
                        </p>
                      </div>
                    )}
                     {!(wf.workflow_input_document_selectors && wf.workflow_input_document_selectors.length > 0) && (
                        <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-md">
                            <p className="text-xs text-blue-700 flex items-center">
                                <Info size={14} className="mr-1.5 shrink-0"/> This workflow does not specify input document selectors.
                            </p>
                        </div>
                    )}

                    <div className="mb-3">
                         <h4 className="text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider mb-1.5 flex items-center">
                          <Eye size={14} className="mr-1.5 text-ulacm-gray-400"/> Workflow Prompt Preview
                        </h4>
                        {/* Adjusted container: removed flex-col and justify-center to allow natural top alignment for scrolling */}
                        <div className="text-sm text-ulacm-gray-700 bg-ulacm-gray-50 p-2.5 rounded-md border border-ulacm-gray-200 shadow-sm max-h-32 min-h-[4.5rem] overflow-y-auto scrollbar-thin scrollbar-thumb-ulacm-gray-300 scrollbar-track-ulacm-gray-100">
                          {loadingPreviewFor === wf.item_id ? (
                            <div className="flex items-center justify-center text-xs text-ulacm-gray-500 h-full"> {/* h-full to fill min-height for centering */}
                               <LoadingSpinner size="sm" className="mr-1.5" /> Loading preview...
                            </div>
                          ) : (
                            // No inner div with h-full needed here, let <pre> dictate its content height
                            <div dangerouslySetInnerHTML={renderPromptPreviewHTML(workflowPromptPreviews[wf.item_id] || "Prompt preview not available or too short.")} />
                          )}
                        </div>
                    </div>


                     {wf.workflow_output_name_template && (
                       <div className="mb-4">
                        <h4 className="text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider mb-1.5 flex items-center">
                          <TextCursorInput size={14} className="mr-1.5 text-ulacm-gray-400"/> Output Name Template
                        </h4>
                        <p className="text-sm text-ulacm-gray-700 bg-ulacm-gray-50 px-2.5 py-1 rounded-md border border-ulacm-gray-200 shadow-sm">
                          <code className="text-blue-700 font-mono text-xs">{wf.workflow_output_name_template}</code>
                        </p>
                         <p className="mt-1.5 text-xs text-ulacm-gray-500 italic flex items-start">
                            <Info size={14} className="mr-1 text-ulacm-gray-400 flex-shrink-0 mt-px"/> Placeholders will be replaced on execution.
                        </p>
                       </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleInitiateWorkflowRun(wf)}
                    className="w-full mt-4 flex items-center justify-center bg-purple-600 hover:bg-purple-700 focus:bg-purple-700 text-white font-semibold py-2.5 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    <Play size={18} className="mr-1.5" /> Run Workflow
                  </button>
                </div>
              ))}
            </div>
          )}

          {pagination.total_count > pagination.limit && displayableWorkflows.length > 0 && (
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-sm text-ulacm-gray-600">
              <div>
                Showing <span className="font-semibold">{pagination.offset + 1}</span> to <span className="font-semibold">{Math.min(pagination.offset + pagination.limit, pagination.total_count)}</span> of <span className="font-semibold">{pagination.total_count}</span> workflows
              </div>
              <div className="flex items-center space-x-2 mt-3 sm:mt-0">
                <button
                   onClick={() => handlePageChange(pagination.offset - pagination.limit)}
                  disabled={currentPage === 1 || isLoading}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-ulacm-gray-600 bg-white border border-ulacm-gray-300 rounded-md hover:bg-ulacm-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                   <ChevronLeft size={16} className="mr-1" /> Previous
                </button>
                <span>Page {currentPage} of {totalPages}</span>
                <button
                  onClick={() => handlePageChange(pagination.offset + pagination.limit)}
                  disabled={currentPage === totalPages || isLoading}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-ulacm-gray-600 bg-white border border-ulacm-gray-300 rounded-md hover:bg-ulacm-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next <ChevronRight size={16} className="ml-1" />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {workflowToGetInputsFor && showSelectInputsModal && (
        <SelectInputDocumentsModal
            isOpen={showSelectInputsModal}
            workflow={workflowToGetInputsFor}
            onClose={() => { setShowSelectInputsModal(false); setWorkflowToGetInputsFor(null); }}
            onConfirm={handleConfirmInputDocumentSelection}
        />
      )}

      {selectedWorkflowForRun && showRunModal && (
        <RunWorkflowModal
          isOpen={showRunModal}
          workflowToExecute={selectedWorkflowForRun}
          initialPayload={initialPayloadForRun}
          onClose={handleCloseRunModal}
          onViewOutput={handleViewOutputDocument}
        />
      )}
    </div>
  );
};

export default ExecuteWorkflowPage;
