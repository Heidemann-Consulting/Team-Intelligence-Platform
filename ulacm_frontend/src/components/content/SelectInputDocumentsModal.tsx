// File: ulacm_frontend/src/components/content/SelectInputDocumentsModal.tsx
// Purpose: Modal for selecting input documents for a workflow.

import React, { useState, useEffect, useCallback } from 'react';
// import toast from 'react-hot-toast';
import { X, CheckCircle, AlertTriangle, FileText, ChevronRight, ChevronLeft, Info } from 'lucide-react';
import { ContentItemListed, ContentItemType, PaginatedResponse } from '@/types/api';
import contentService from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface SelectInputDocumentsModalProps {
  isOpen: boolean;
  workflow: ContentItemListed; // The workflow for which inputs are being selected
  onClose: () => void;
  onConfirm: (selectedDocumentIds: string[]) => void; // Passes the selected document IDs
}

const SelectInputDocumentsModal: React.FC<SelectInputDocumentsModalProps> = ({
  isOpen,
  workflow,
  onClose,
  onConfirm,
}) => {
  const [availableDocuments, setAvailableDocuments] = useState<ContentItemListed[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docsPagination, setDocsPagination] = useState({
    offset: 0,
    limit: 10, // Adjust as needed
    total_count: 0,
  });

  const fetchApplicableDocuments = useCallback(async (offset = 0) => {
    if (!isOpen) return;
    setIsLoadingDocs(true);
    setError(null);
    try {
      const params = {
        item_type: ContentItemType.DOCUMENT, // Fetch only documents
        limit: docsPagination.limit,
        offset: offset,
        sort_by: 'name', // Alphabetical sort
        sort_order: 'asc' as 'asc',
        // Potentially add more filters here based on workflow.inputDocumentSelectors
        // This would require backend support for more complex filtering or frontend filtering.
        // For now, listing all team documents.
      };
      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);
      setAvailableDocuments(data.items);
      setDocsPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
      if (data.items.length === 0 && offset === 0) {
        // No documents found at all on the first page
      }
    } catch (err: any) {
      console.error("Failed to fetch applicable documents:", err);
      const errorMessage = err.message || 'Failed to load documents.';
      setError(errorMessage);
    } finally {
      setIsLoadingDocs(false);
    }
  }, [isOpen, docsPagination.limit]);

  useEffect(() => {
    if (isOpen) {
      fetchApplicableDocuments(0); // Fetch on open, reset to first page
      setSelectedDocumentIds([]); // Clear previous selections
    }
  }, [isOpen, fetchApplicableDocuments]);


  const handleDocumentSelection = (docId: string) => {
    setSelectedDocumentIds(prevSelected =>
      prevSelected.includes(docId)
        ? prevSelected.filter(id => id !== docId)
        : [...prevSelected, docId]
    );
  };

  const handleConfirmSelection = () => {
    if (availableDocuments.length === 0 && selectedDocumentIds.length === 0) {
      // This is the "run anyway" scenario if no documents were found.
      // Or, if user explicitly deselects all and confirms.
    }
    onConfirm(selectedDocumentIds);
  };

  const handlePageChange = (newOffset: number) => {
    if (newOffset >= 0 && newOffset < docsPagination.total_count) {
      fetchApplicableDocuments(newOffset);
    }
  };

  const totalPages = Math.ceil(docsPagination.total_count / docsPagination.limit);
  const currentPage = Math.floor(docsPagination.offset / docsPagination.limit) + 1;


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-auto transform transition-all max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-ulacm-gray-200 flex-shrink-0">
          <h3 className="text-xl font-semibold text-ulacm-gray-800">
            Select Input Documents for "{workflow.name}"
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Area */}
        <div className="px-6 py-5 flex-grow overflow-y-auto space-y-4">
          {isLoadingDocs && (
            <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
              <LoadingSpinner size="md" color="text-purple-600" />
              <p className="mt-3 text-ulacm-gray-600">Loading applicable documents...</p>
            </div>
          )}

          {!isLoadingDocs && error && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-6 w-6 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h4 className="text-md font-semibold text-red-800 mb-1">Error Loading Documents</h4>
                  <p className="text-sm text-red-700 break-words">{error}</p>
                </div>
              </div>
            </div>
          )}

          {!isLoadingDocs && !error && availableDocuments.length === 0 && (
            <div className="bg-yellow-50 border border-yellow-300 p-4 rounded-lg text-center">
              <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <h4 className="text-md font-semibold text-yellow-800 mb-1">No Applicable Documents Found</h4>
              <p className="text-sm text-yellow-700">
                There are no documents available for selection based on the current criteria.
                You can choose to run the workflow without input documents or cancel.
              </p>
            </div>
          )}

          {!isLoadingDocs && !error && availableDocuments.length > 0 && (
            <div className="space-y-3 max-h-96 overflow-y-auto border border-ulacm-gray-200 rounded-lg p-3 bg-ulacm-gray-50">
              <p className="text-sm text-ulacm-gray-600 mb-2">
                Select the documents to use as input for the workflow. Documents are sorted alphabetically.
              </p>
              {availableDocuments.map(doc => (
                <label
                  key={doc.item_id}
                  htmlFor={`doc-${doc.item_id}`}
                  className="flex items-center p-3 bg-white rounded-md border border-ulacm-gray-200 hover:border-ulacm-primary/50 hover:bg-ulacm-primary/5 cursor-pointer transition-colors"
                >
                  <input
                    type="checkbox"
                    id={`doc-${doc.item_id}`}
                    checked={selectedDocumentIds.includes(doc.item_id)}
                    onChange={() => handleDocumentSelection(doc.item_id)}
                    className="h-5 w-5 text-ulacm-primary rounded border-ulacm-gray-300 focus:ring-ulacm-primary/50 mr-3 shrink-0"
                  />
                  <FileText size={18} className="mr-2 text-ulacm-primary shrink-0" />
                  <span className="text-sm font-medium text-ulacm-gray-700 truncate" title={doc.name}>
                    {doc.name}
                  </span>
                  {/* Add more info like version or date if needed */}
                </label>
              ))}
               {/* Pagination for documents list */}
                {docsPagination.total_count > docsPagination.limit && (
                    <div className="mt-4 flex items-center justify-between text-xs text-ulacm-gray-500 pt-2 border-t border-ulacm-gray-200">
                    <div>
                        Showing {docsPagination.offset + 1}-{Math.min(docsPagination.offset + docsPagination.limit, docsPagination.total_count)} of {docsPagination.total_count}
                    </div>
                    <div className="flex items-center space-x-1">
                        <button
                        onClick={() => handlePageChange(docsPagination.offset - docsPagination.limit)}
                        disabled={currentPage === 1 || isLoadingDocs}
                        className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                        >
                        <ChevronLeft size={16} />
                        </button>
                        <span>Page {currentPage}/{totalPages}</span>
                        <button
                        onClick={() => handlePageChange(docsPagination.offset + docsPagination.limit)}
                        disabled={currentPage === totalPages || isLoadingDocs}
                        className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                        >
                        <ChevronRight size={16} />
                        </button>
                    </div>
                    </div>
                )}
            </div>
          )}

          {workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0 && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
                <p className="font-semibold text-blue-700 flex items-center"><Info size={16} className="mr-1.5"/> Workflow Input Expectation:</p>
                <p className="text-blue-600 text-xs mt-1">This workflow is configured to look for documents matching:
                    <code className="ml-1 bg-blue-100 px-1 py-0.5 rounded text-blue-700">
                        {workflow.workflow_input_document_selectors.join(', ')}
                    </code>
                </p>
            </div>
          )}

        </div>


        {/* Footer Actions */}
        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
          <button
            type="button"
            onClick={handleConfirmSelection}
            disabled={isLoadingDocs} // Disable if still loading initial docs. Enable even if no docs selected for "Run Anyway"
            className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-purple-600 hover:bg-purple-700 text-white focus:ring-purple-500 disabled:opacity-70"
          >
            <CheckCircle size={18} className="mr-1.5" />
            {availableDocuments.length === 0 ? 'Run Workflow Anyway' : (selectedDocumentIds.length === 0 ? 'Run Without Inputs' : `Run with ${selectedDocumentIds.length} Document(s)`)}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="mt-3 w-full sm:mt-0 sm:w-auto inline-flex justify-center rounded-lg border border-ulacm-gray-300 shadow-sm px-5 py-2.5 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light transition-colors duration-150"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default SelectInputDocumentsModal;
