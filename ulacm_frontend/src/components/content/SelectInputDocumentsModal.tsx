// File: ulacm_frontend/src/components/content/SelectInputDocumentsModal.tsx
// Purpose: Modal for selecting input documents for a workflow.
// Updated: Added client-side filtering based on workflow.inputDocumentSelectors.

// import React, { useState, useEffect, useCallback, useMemo } from 'react';
import React, { useState, useEffect, useCallback } from 'react';
// import toast from 'react-hot-toast';
// import { X, CheckCircle, AlertTriangle, FileText, ChevronRight, ChevronLeft, Info, ListFilter } from 'lucide-react';
import { X, CheckCircle, AlertTriangle, FileText, ChevronRight, ChevronLeft, ListFilter } from 'lucide-react';
import { ContentItemListed, ContentItemType, PaginatedResponse } from '@/types/api';
import contentService from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface SelectInputDocumentsModalProps {
  isOpen: boolean;
  workflow: ContentItemListed; // The workflow for which inputs are being selected
  onClose: () => void;
  onConfirm: (selectedDocumentIds: string[]) => void; // Passes the selected document IDs
}

// Helper function to convert simple glob patterns to RegExp
function globToRegex(glob: string): RegExp {
  const regexString = glob
    .replace(/[.+^${}()|[\]\\]/g, '\\$&') // Escape regex special chars
    .replace(/\*/g, '.*') // Convert * to .*
    .replace(/\?/g, '.'); // Convert ? to .
  return new RegExp(`^${regexString}$`, 'i'); // Case-insensitive match for the whole string
}

const SelectInputDocumentsModal: React.FC<SelectInputDocumentsModalProps> = ({
  isOpen,
  workflow,
  onClose,
  onConfirm,
}) => {
  const [allFetchedDocuments, setAllFetchedDocuments] = useState<ContentItemListed[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<ContentItemListed[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docsPagination, setDocsPagination] = useState({
    offset: 0,
    limit: 100, // Fetch a larger set for client-side filtering, or implement server-side pagination for filtered list
    total_count: 0, // This will be total of initially fetched, not filtered
  });
   // Pagination for the displayed (filtered) list
   const [displayPagination, setDisplayPagination] = useState({
    currentPage: 1,
    itemsPerPage: 10,
  });


  const applyClientSideFilters = useCallback((documents: ContentItemListed[]): ContentItemListed[] => {
    if (!workflow.workflow_input_document_selectors || workflow.workflow_input_document_selectors.length === 0) {
      return documents; // No selectors, return all documents
    }
    const selectorsRegex = workflow.workflow_input_document_selectors.map(globToRegex);
    return documents.filter(doc => selectorsRegex.some(regex => regex.test(doc.name)));
  }, [workflow.workflow_input_document_selectors]);


  const fetchApplicableDocuments = useCallback(async () => {
    if (!isOpen) return;
    setIsLoadingDocs(true);
    setError(null);
    try {
      // Fetch all team documents first
      const params = {
        item_type: ContentItemType.DOCUMENT,
        limit: docsPagination.limit, // Fetch a large number for client filtering
        offset: 0, // Always fetch from start for client filtering context
        sort_by: 'name',
        sort_order: 'asc' as 'asc',
      };
      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);
      setAllFetchedDocuments(data.items); // Store all fetched for potential re-filter

      const currentFiltered = applyClientSideFilters(data.items);
      setFilteredDocuments(currentFiltered);
      // Update total_count for display pagination based on the filtered list
      setDocsPagination(prev => ({ ...prev, total_count: data.items.length, offset:0 })); // total_count of all docs of team
      setDisplayPagination(prev => ({ ...prev, currentPage: 1 }));


      if (data.items.length === 0) {
        // No documents owned by team at all
      } else if (currentFiltered.length === 0 && workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0) {
        // Documents exist, but none match selectors
      }

    } catch (err: any) {
      console.error("Failed to fetch applicable documents:", err);
      const errorMessage = err.message || 'Failed to load documents.';
      setError(errorMessage);
    } finally {
      setIsLoadingDocs(false);
    }
  }, [isOpen, docsPagination.limit, applyClientSideFilters, workflow.workflow_input_document_selectors]);

  useEffect(() => {
    if (isOpen) {
      fetchApplicableDocuments();
      setSelectedDocumentIds([]);
    }
  }, [isOpen, fetchApplicableDocuments]); // fetchApplicableDocuments dependency ensures it re-runs if selectors change (though workflow prop is stable per modal instance)


  const handleDocumentSelection = (docId: string) => {
    setSelectedDocumentIds(prevSelected =>
      prevSelected.includes(docId)
        ? prevSelected.filter(id => id !== docId)
        : [...prevSelected, docId]
    );
  };

  const handleConfirmSelection = () => {
    onConfirm(selectedDocumentIds);
  };

  // Calculate documents for the current display page
  const indexOfLastDoc = displayPagination.currentPage * displayPagination.itemsPerPage;
  const indexOfFirstDoc = indexOfLastDoc - displayPagination.itemsPerPage;
  const currentDisplayDocuments = filteredDocuments.slice(indexOfFirstDoc, indexOfLastDoc);
  const totalDisplayPages = Math.ceil(filteredDocuments.length / displayPagination.itemsPerPage);

  const handleDisplayPageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalDisplayPages) {
      setDisplayPagination(prev => ({ ...prev, currentPage: newPage }));
    }
  };


  if (!isOpen) return null;

  const noDocumentsMatchSelectors = filteredDocuments.length === 0 && allFetchedDocuments.length > 0 &&  workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0;
  const noDocumentsAtAll = filteredDocuments.length === 0 && allFetchedDocuments.length === 0;


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

          {workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
                <p className="font-semibold text-blue-700 flex items-center"><ListFilter size={16} className="mr-1.5"/> Document Filter Applied:</p>
                <p className="text-blue-600 text-xs mt-1">
                    This workflow is configured to use documents matching:
                    <code className="ml-1 bg-blue-100 px-1 py-0.5 rounded text-blue-700 font-mono">
                        {workflow.workflow_input_document_selectors.join(', ')}
                    </code>
                </p>
            </div>
          )}


          {!isLoadingDocs && !error && (noDocumentsMatchSelectors || noDocumentsAtAll) && (
            <div className="bg-yellow-50 border border-yellow-300 p-4 rounded-lg text-center">
              <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <h4 className="text-md font-semibold text-yellow-800 mb-1">
                {noDocumentsAtAll ? "No Documents Available" : "No Documents Match Workflow Filters"}
              </h4>
              <p className="text-sm text-yellow-700">
                {noDocumentsAtAll ? "Your team currently has no documents to select from." : "No documents were found matching the workflow's input criteria."}
                <br/>You can still choose to run the workflow without specific input documents or cancel.
              </p>
            </div>
          )}

          {!isLoadingDocs && !error && currentDisplayDocuments.length > 0 && (
            <div className="space-y-3 max-h-80 overflow-y-auto border border-ulacm-gray-200 rounded-lg p-3 bg-ulacm-gray-50">
              <p className="text-sm text-ulacm-gray-600 mb-2">
                Select the documents to use as input. Documents are sorted alphabetically. Showing {currentDisplayDocuments.length} of {filteredDocuments.length} matching documents.
              </p>
              {currentDisplayDocuments.map(doc => (
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
                </label>
              ))}
            </div>
          )}
          {!isLoadingDocs && !error && filteredDocuments.length > displayPagination.itemsPerPage && (
             <div className="mt-4 flex items-center justify-between text-xs text-ulacm-gray-500 pt-2 border-t border-ulacm-gray-200">
                <div>
                    Showing {indexOfFirstDoc + 1}-{Math.min(indexOfLastDoc, filteredDocuments.length)} of {filteredDocuments.length} matching documents
                </div>
                <div className="flex items-center space-x-1">
                    <button
                    onClick={() => handleDisplayPageChange(displayPagination.currentPage - 1)}
                    disabled={displayPagination.currentPage === 1 || isLoadingDocs}
                    className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                    >
                    <ChevronLeft size={16} />
                    </button>
                    <span>Page {displayPagination.currentPage}/{totalDisplayPages}</span>
                    <button
                    onClick={() => handleDisplayPageChange(displayPagination.currentPage + 1)}
                    disabled={displayPagination.currentPage === totalDisplayPages || isLoadingDocs}
                    className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                    >
                    <ChevronRight size={16} />
                    </button>
                </div>
                </div>
          )}


        </div>


        {/* Footer Actions */}
        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
          <button
            type="button"
            onClick={handleConfirmSelection}
            disabled={isLoadingDocs}
            className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-purple-600 hover:bg-purple-700 text-white focus:ring-purple-500 disabled:opacity-70"
          >
            <CheckCircle size={18} className="mr-1.5" />
            {(noDocumentsMatchSelectors || noDocumentsAtAll) ? 'Run Workflow Anyway' : (selectedDocumentIds.length === 0 ? 'Run Without Selected Inputs' : `Run with ${selectedDocumentIds.length} Document(s)`)}
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
