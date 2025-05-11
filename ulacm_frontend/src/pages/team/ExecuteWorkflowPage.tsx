// File: ulacm_frontend/src/pages/team/ExecuteWorkflowPage.tsx
// Purpose: Page for Teams to list and execute available (Admin-created) Workflows.
// Updated: Displays input document selectors and output name template.
// Replaced InfoSquare with Info icon.

import React, { useState, useEffect, useCallback } from 'react';
import { FolderGit2, Play, AlertCircle, RefreshCw, ChevronLeft, ChevronRight, Search as SearchIcon, Info, FileInput, FileOutput } from 'lucide-react'; // Changed InfoSquare to Info
import toast from 'react-hot-toast';

import { ContentItemListed, ContentItemType, PaginatedResponse, RunWorkflowResponse } from '@/types/api';
import contentService from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import RunWorkflowModal from '@/components/content/RunWorkflowModal';
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
  const [selectedWorkflow, setSelectedWorkflow] = useState<ContentItemListed | null>(null);
  const [showRunModal, setShowRunModal] = useState(false);
  const [runWorkflowOutput, setRunWorkflowOutput] = useState<RunWorkflowResponse | { error: string } | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const navigate = useNavigate();

  const fetchWorkflows = useCallback(async (offset = 0) => {
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
      };
      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);
      setWorkflows(data.items);
      setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
    } catch (err: any) {
      console.error("Failed to fetch workflows:", err);
      const errorMessage = err.message || 'Failed to load available workflows.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.limit]);

  useEffect(() => {
    fetchWorkflows(pagination.offset);
  }, [fetchWorkflows, pagination.offset]);

  const handleExecuteWorkflow = (workflow: ContentItemListed) => {
    setSelectedWorkflow(workflow);
    setRunWorkflowOutput(null);
    setIsRunning(true);
    setShowRunModal(true);
    contentService.runWorkflow(workflow.item_id)
      .then(result => {
        setRunWorkflowOutput(result);
        toast.success(`Workflow "${workflow.name}" executed successfully.`);
      })
      .catch(err => {
        const msg = err.message || 'Workflow execution failed.';
        setRunWorkflowOutput({ error: msg });
        toast.error(msg);
      })
      .finally(() => {
        setIsRunning(false);
      });
  };

  const handleCloseRunModal = () => {
    setShowRunModal(false);
    setSelectedWorkflow(null);
    setRunWorkflowOutput(null);
  };

  const handleViewOutputDocument = (outputItemId: string) => {
    handleCloseRunModal();
    navigate(`/app/documents/${outputItemId}`);
  };

  const handlePageChange = (newOffset: number) => {
    if (newOffset >= 0 && newOffset < pagination.total_count) {
      setPagination(prev => ({ ...prev, offset: newOffset }));
    }
  };

  const totalPages = Math.ceil(pagination.total_count / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  const filteredWorkflows = workflows.filter(wf =>
    wf.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter workflows by name..."
              className="w-full md:w-64 pl-10 pr-4 py-2 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out text-sm"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ulacm-gray-400 pointer-events-none">
              <SearchIcon size={18} />
            </div>
          </div>
          <button
            onClick={() => fetchWorkflows(pagination.offset)}
            disabled={isLoading}
            className="p-2.5 text-ulacm-gray-500 hover:text-ulacm-primary hover:bg-ulacm-gray-100 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50"
            title="Refresh Workflows List"
          >
            <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {isLoading && workflows.length === 0 && (
        <div className="flex justify-center items-center py-20 bg-white rounded-xl shadow-md border border-ulacm-gray-100">
          <LoadingSpinner size="lg" color="text-purple-600" />
          <p className="ml-3 text-ulacm-gray-600">Loading available workflows...</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Failed to Load Workflows</h3>
              <div className="mt-2 text-sm text-red-700"><p>{error}</p></div>
              <div className="mt-4">
                <button onClick={() => fetchWorkflows(0)} className="text-sm font-medium text-red-800 hover:text-red-600 underline">
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {!isLoading && !error && (
        <>
          {filteredWorkflows.length === 0 && searchTerm && (
            <div className="text-center py-12 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                <SearchIcon size={48} className="mx-auto text-ulacm-gray-300"/>
                <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No workflows match "{searchTerm}"</h3>
                <p className="mt-1 text-sm text-ulacm-gray-500">Try a different search term or clear the filter.</p>
            </div>
          )}
          {filteredWorkflows.length === 0 && !searchTerm && workflows.length === 0 && (
             <div className="text-center py-12 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                <FolderGit2 size={48} className="mx-auto text-ulacm-gray-300"/>
                <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No Workflows Available</h3>
                <p className="mt-1 text-sm text-ulacm-gray-500">Administrators need to create and share workflows for execution.</p>
            </div>
          )}

          {filteredWorkflows.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredWorkflows.map((wf) => (
                <div key={wf.item_id} className="bg-white p-5 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-200 border border-ulacm-gray-100 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center mb-3">
                      <FolderGit2 className="h-7 w-7 mr-2.5 text-purple-600 flex-shrink-0" />
                      <h2 className="text-xl font-semibold text-ulacm-gray-800 truncate" title={wf.name}>
                        {wf.name}
                      </h2>
                    </div>

                    {/* Display Input Document Selectors */}
                    {wf.workflow_input_document_selectors && wf.workflow_input_document_selectors.length > 0 && (
                      <div className="mb-3">
                        <h4 className="text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider mb-1.5 flex items-center">
                          <FileInput size={14} className="mr-1.5 text-ulacm-gray-400"/> Input Document Selectors
                        </h4>
                        <ul className="list-none pl-0 space-y-0.5">
                          {wf.workflow_input_document_selectors.map((selector, index) => (
                            <li key={index} className="text-sm text-ulacm-gray-700 bg-ulacm-gray-50 px-2 py-1 rounded-md border border-ulacm-gray-200">
                              <code className="text-purple-700">{selector}</code>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Display Output Name Template */}
                    {wf.workflow_output_name_template && (
                      <div className="mb-4">
                        <h4 className="text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider mb-1.5 flex items-center">
                           <FileOutput size={14} className="mr-1.5 text-ulacm-gray-400"/> Output Document Name Template
                        </h4>
                        <p className="text-sm text-ulacm-gray-700 bg-ulacm-gray-50 px-2 py-1 rounded-md border border-ulacm-gray-200">
                          <code className="text-blue-700">{wf.workflow_output_name_template}</code>
                        </p>
                         <p className="mt-1 text-xs text-ulacm-gray-500 italic flex items-center">
                            <Info size={12} className="mr-1 text-ulacm-gray-400 flex-shrink-0"/> Placeholders like `{"{{InputFileName}}"}`, `{"{{WorkflowName}}"}`, `{"{{Year}}"}` will be replaced on execution.
                        </p>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleExecuteWorkflow(wf)}
                    disabled={isRunning && selectedWorkflow?.item_id === wf.item_id}
                    className="w-full mt-4 flex items-center justify-center bg-purple-600 hover:bg-purple-700 focus:bg-purple-700 text-white font-semibold py-2.5 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {isRunning && selectedWorkflow?.item_id === wf.item_id ? (
                      <LoadingSpinner size="sm" color="text-white" className="mr-2" />
                    ) : (
                      <Play size={18} className="mr-1.5" />
                    )}
                    {isRunning && selectedWorkflow?.item_id === wf.item_id ? 'Executing...' : 'Run Workflow'}
                  </button>
                </div>
              ))}
            </div>
          )}

          {pagination.total_count > pagination.limit && filteredWorkflows.length > 0 && (
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

      {selectedWorkflow && showRunModal && (
        <RunWorkflowModal
          isOpen={showRunModal}
          workflowName={selectedWorkflow.name}
          isLoading={isRunning}
          output={runWorkflowOutput}
          onClose={handleCloseRunModal}
          onViewOutput={handleViewOutputDocument}
        />
      )}
    </div>
  );
};

export default ExecuteWorkflowPage;
