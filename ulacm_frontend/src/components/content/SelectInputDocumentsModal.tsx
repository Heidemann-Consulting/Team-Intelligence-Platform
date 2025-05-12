// File: ulacm_frontend/src/components/content/SelectInputDocumentsModal.tsx
// Purpose: Modal for selecting input documents for a workflow.
// Updated for Option 3:
// - Passes workflow.inputDocumentSelectors as name_globs to backend for server-side pre-filtering.
// - Removes client-side filtering by workflow selectors.
// - FTS content_query is applied by backend in conjunction with name_globs.

import React, { useState, useEffect, useCallback } from 'react';
import { X, CheckCircle, AlertTriangle, FileText, ChevronRight, ChevronLeft, ListFilter, Search as SearchIcon, Loader } from 'lucide-react';
import { ContentItemListed, ContentItemType, PaginatedResponse } from '@/types/api';
import contentService, { GetItemsParams } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface SelectInputDocumentsModalProps {
  isOpen: boolean;
  workflow: ContentItemListed;
  onClose: () => void;
  onConfirm: (selectedDocumentIds: string[], additionalAiInput?: string) => void;
}

const SelectInputDocumentsModal: React.FC<SelectInputDocumentsModalProps> = ({
  isOpen,
  workflow,
  onClose,
  onConfirm,
}) => {
  // documentsFromApi now stores results pre-filtered by backend (FTS + name_globs)
  const [documentsFromApi, setDocumentsFromApi] = useState<ContentItemListed[]>([]);
  const [displayedDocuments, setDisplayedDocuments] = useState<ContentItemListed[]>([]);

  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  // selectedDocumentsDetails still needed to keep selected items visible across FTS/pagination changes
  const [selectedDocumentsDetails, setSelectedDocumentsDetails] = useState<ContentItemListed[]>([]);

  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [docSearchQuery, setDocSearchQuery] = useState(''); // FTS query by user
  const [debouncedDocSearchQuery, setDebouncedDocSearchQuery] = useState('');
  const [isDocSearchTyping, setIsDocSearchTyping] = useState(false);
  const [additionalAiInput, setAdditionalAiInput] = useState('');

  const [docsPagination, setDocsPagination] = useState({
    offset: 0,
    limit: 10,
    total_count: 0, // This will now be total from API (FTS + name_globs filtered)
  });

  useEffect(() => {
    setIsDocSearchTyping(true);
    const handler = setTimeout(() => {
      setDebouncedDocSearchQuery(docSearchQuery);
      setDocsPagination(p => ({ ...p, offset: 0 }));
      setIsDocSearchTyping(false);
    }, 500);
    return () => clearTimeout(handler);
  }, [docSearchQuery]);

  const fetchDocumentsForSelection = useCallback(async (fetchOffset = 0) => {
    if (!isOpen) return;
    setIsLoadingDocs(true);
    setError(null);

    try {
      const nameGlobsPayload = workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0
        ? workflow.workflow_input_document_selectors.join(',')
        : undefined;

      const params: GetItemsParams = {
        item_type: ContentItemType.DOCUMENT,
        limit: docsPagination.limit,
        offset: fetchOffset,
        sort_by: debouncedDocSearchQuery.trim() ? 'rank' : 'name',
        sort_order: debouncedDocSearchQuery.trim() ? 'desc' : 'asc',
        content_query: debouncedDocSearchQuery.trim() || undefined,
        name_globs: nameGlobsPayload, // Pass workflow selectors to backend
      };
      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);

      setDocumentsFromApi(data.items);
      setDocsPagination(prev => ({ ...prev, total_count: data.total_count, offset: fetchOffset }));

    } catch (err: any) {
      console.error("Failed to fetch documents for selection:", err);
      const errorMessage = err.message || 'Failed to load documents.';
      setError(errorMessage);
      setDocumentsFromApi([]);
      setDocsPagination(prev => ({ ...prev, total_count: 0, offset: fetchOffset }));
    } finally {
      setIsLoadingDocs(false);
    }
  }, [isOpen, docsPagination.limit, debouncedDocSearchQuery, workflow.workflow_input_document_selectors]);

  useEffect(() => {
    if (isOpen) {
      setDocSearchQuery('');
      setDebouncedDocSearchQuery('');
      setAdditionalAiInput('');
      setSelectedDocumentIds([]);
      setSelectedDocumentsDetails([]);
      setDocumentsFromApi([]);
      fetchDocumentsForSelection(0);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  useEffect(()=>{
    if(isOpen && !isDocSearchTyping){
        fetchDocumentsForSelection(docsPagination.offset)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[debouncedDocSearchQuery, docsPagination.offset, isOpen, isDocSearchTyping])

  // Combine API results with persistently selected items for display
  useEffect(() => {
    const currentDisplayMap = new Map<string, ContentItemListed>();

    // Add documents from the current API page (already FTS and workflow-selector filtered by backend)
    documentsFromApi.forEach(doc => currentDisplayMap.set(doc.item_id, doc));

    // Add persistently selected documents.
    // Since backend pre-filters by workflow.inputDocumentSelectors, selected items should already match them.
    // This ensures they stay visible if they fall off current FTS page.
    selectedDocumentsDetails.forEach(selectedDoc => {
      if (!currentDisplayMap.has(selectedDoc.item_id)) {
        currentDisplayMap.set(selectedDoc.item_id, selectedDoc);
      }
    });

    const finalDisplayList = Array.from(currentDisplayMap.values());

    finalDisplayList.sort((a, b) => {
        const aIsSelected = selectedDocumentIds.includes(a.item_id);
        const bIsSelected = selectedDocumentIds.includes(b.item_id);
        if (aIsSelected && !bIsSelected) return -1;
        if (!aIsSelected && bIsSelected) return 1;
        // For non-selected items, or items with same selection status,
        // ideally maintain the order from `documentsFromApi` (which could be by rank or name)
        // This simple sort might not perfectly preserve API order for non-selected items if selected items are interspersed.
        // A more complex sort could preserve original index for non-selected if needed.
        return 0;
    });
    setDisplayedDocuments(finalDisplayList);
  }, [documentsFromApi, selectedDocumentsDetails, selectedDocumentIds]);


  const handleDocumentSelection = (doc: ContentItemListed) => {
    const docId = doc.item_id;
    setSelectedDocumentIds(prevSelected => {
      const newSelectedIds = prevSelected.includes(docId)
        ? prevSelected.filter(id => id !== docId)
        : [...prevSelected, docId];

      if (newSelectedIds.includes(docId)) {
        setSelectedDocumentsDetails(prevDetails => {
          if (!prevDetails.find(d => d.item_id === docId)) {
            return [...prevDetails, doc];
          }
          return prevDetails;
        });
      } else {
        setSelectedDocumentsDetails(prevDetails => prevDetails.filter(d => d.item_id !== docId));
      }
      return newSelectedIds;
    });
  };

  const handleConfirmSelection = () => {
    // Backend will re-verify against selectors, so just pass current selection
    onConfirm(selectedDocumentIds, additionalAiInput.trim());
  };

  const handlePageChange = (newOffset: number) => {
    if (newOffset >= 0 && (newOffset < docsPagination.total_count || docsPagination.total_count === 0)) {
      setDocsPagination(prev => ({ ...prev, offset: newOffset }));
    }
  };

  const totalDisplayPages = Math.max(1, Math.ceil(docsPagination.total_count / docsPagination.limit));
  const currentDisplayPage = Math.floor(docsPagination.offset / docsPagination.limit) + 1;

  if (!isOpen) return null;

  const noDocsMatchFilters = displayedDocuments.length === 0 && (debouncedDocSearchQuery || (workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0)) && !isLoadingDocs;
  const noDocsAvailableAtAll = displayedDocuments.length === 0 && !debouncedDocSearchQuery && !(workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0) && docsPagination.total_count === 0 && !isLoadingDocs;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl mx-auto transform transition-all max-h-[90vh] flex flex-col">
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

        <div className="px-6 py-5 flex-grow overflow-y-auto space-y-4">
          <div className="relative">
            <input
              type="search"
              value={docSearchQuery}
              onChange={(e) => setDocSearchQuery(e.target.value)}
              placeholder="Search documents by name or content..."
              className="w-full pl-10 pr-4 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out text-sm"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ulacm-gray-400 pointer-events-none">
              {isDocSearchTyping || (isLoadingDocs && debouncedDocSearchQuery) ? <Loader size={18} className="animate-spin"/> : <SearchIcon size={18} />}
            </div>
          </div>

          {workflow.workflow_input_document_selectors && workflow.workflow_input_document_selectors.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
              <p className="font-semibold text-blue-700 flex items-center"><ListFilter size={16} className="mr-1.5"/> Workflow Input Filter Active:</p>
              <p className="text-blue-600 text-xs mt-1">
                The backend is filtering documents to match:
                <code className="ml-1 bg-blue-100 px-1 py-0.5 rounded text-blue-700 font-mono">
                  {workflow.workflow_input_document_selectors.join(' OR ')}
                </code>.
                 Your search will apply within these results.
              </p>
            </div>
          )}

          {isLoadingDocs && displayedDocuments.length === 0 &&  (
            <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
              <LoadingSpinner size="md" color="text-purple-600" />
              <p className="mt-3 text-ulacm-gray-600">Loading documents...</p>
            </div>
          )}

          {!isLoadingDocs && error && (
             <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow">
              <div className="flex">
                <div className="flex-shrink-0"><AlertTriangle className="h-5 w-5 text-red-400" /></div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error Loading Documents</h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {!isLoadingDocs && !error && (noDocsMatchFilters || noDocsAvailableAtAll) && (
             <div className="bg-yellow-50 border border-yellow-300 p-4 rounded-lg text-center min-h-[150px] flex flex-col justify-center">
              <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <h4 className="text-md font-semibold text-yellow-800 mb-1">
                {noDocsAvailableAtAll ? "No Documents Available" : "No Documents Match Filters"}
              </h4>
              <p className="text-sm text-yellow-700">
                {noDocsAvailableAtAll ? "Your team currently has no documents." :
                 (debouncedDocSearchQuery ? `Your search for "${debouncedDocSearchQuery}" did not yield results matching the workflow's input criteria.` : "No documents match the workflow's input criteria.")
                }
              </p>
            </div>
          )}

          {!isLoadingDocs && !error && displayedDocuments.length > 0 && (
            <div className="space-y-3 max-h-60 overflow-y-auto border border-ulacm-gray-200 rounded-lg p-3 bg-ulacm-gray-50">
              <p className="text-sm text-ulacm-gray-600 mb-2">
                {`Select documents. Displaying ${displayedDocuments.length} document(s).`}
                {debouncedDocSearchQuery && ` Total backend matches for FTS & selectors: ${docsPagination.total_count}.`}
              </p>
              {displayedDocuments.map(doc => (
                <label
                  key={doc.item_id}
                  htmlFor={`doc-select-${doc.item_id}`}
                  className={`flex items-center p-3 bg-white rounded-md border hover:bg-ulacm-primary/5 cursor-pointer transition-colors
                    ${selectedDocumentIds.includes(doc.item_id) ? 'border-ulacm-primary ring-2 ring-ulacm-primary/50' : 'border-ulacm-gray-200 hover:border-ulacm-primary/50'}
                  `}
                >
                  <input
                    type="checkbox"
                    id={`doc-select-${doc.item_id}`}
                    checked={selectedDocumentIds.includes(doc.item_id)}
                    onChange={() => handleDocumentSelection(doc)}
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

          {!isLoadingDocs && !error && docsPagination.total_count > docsPagination.limit && displayedDocuments.length > 0 && (
             <div className="mt-4 flex items-center justify-between text-xs text-ulacm-gray-500 pt-2 border-t border-ulacm-gray-200">
                <div>
                    {`Showing page ${currentDisplayPage} of ${totalDisplayPages} (Total matches: ${docsPagination.total_count})`}
                </div>
                <div className="flex items-center space-x-1">
                    <button
                        onClick={() => handlePageChange(docsPagination.offset - docsPagination.limit)}
                        disabled={currentDisplayPage === 1 || isLoadingDocs}
                        className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                    >
                        <ChevronLeft size={16} />
                    </button>
                    <span>Page {currentDisplayPage}/{totalDisplayPages}</span>
                    <button
                        onClick={() => handlePageChange(docsPagination.offset + docsPagination.limit)}
                        disabled={currentDisplayPage === totalDisplayPages || isLoadingDocs}
                        className="p-1 rounded hover:bg-ulacm-gray-200 disabled:opacity-50"
                    >
                        <ChevronRight size={16} />
                    </button>
                </div>
            </div>
          )}

          <div className="pt-3">
            <label htmlFor="additionalAiInput" className="block text-sm font-medium text-ulacm-gray-700 mb-1">
              Additional input for the AI (Optional):
            </label>
            <textarea
              id="additionalAiInput"
              value={additionalAiInput}
              onChange={(e) => setAdditionalAiInput(e.target.value)}
              rows={3}
              placeholder="Type any additional text, instructions, or context to provide directly to the AI for this workflow execution..."
              className="w-full px-3.5 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition-colors text-sm"
            />
             <p className="mt-1 text-xs text-ulacm-gray-500">This text will be appended to the prompt as if it were an added document.</p>
          </div>
        </div>

        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
          <button
            type="button"
            onClick={handleConfirmSelection}
            disabled={isLoadingDocs}
            className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-purple-600 hover:bg-purple-700 text-white focus:ring-purple-500 disabled:opacity-70"
          >
            <CheckCircle size={18} className="mr-1.5" />
            {selectedDocumentIds.length === 0 ? 'Run Workflow (No Documents Selected)' : `Run with ${selectedDocumentIds.length} Document(s)`}
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
