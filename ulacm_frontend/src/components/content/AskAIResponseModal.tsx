// File: ulacm_frontend/src/components/content/AskAIResponseModal.tsx
// Purpose: Modal to display AI responses and allow saving as a new document.
// Improved auto-scrolling and UI update logic.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { X, Save, AlertTriangle, Brain, Copy as CopyIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { format } from 'date-fns';
import { AskAIRequestPayload, AskAIResponseData } from '@/types/api';
import contentService from '@/services/contentService';

const removeThinkTags = (text: string): string => {
  if (!text) return "";
  return text.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
};

interface AskAIResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveAsNewDocument: (documentName: string, content: string) => Promise<void>;
  currentDocumentName?: string;
  askAiQuery: string;
  currentEditorContent: string;
}

const AskAIResponseModal: React.FC<AskAIResponseModalProps> = ({
  isOpen,
  onClose,
  onSaveAsNewDocument,
  currentDocumentName,
  askAiQuery,
  currentEditorContent,
}) => {
  const [newDocumentName, setNewDocumentName] = useState('');
  const [isSavingAsNew, setIsSavingAsNew] = useState(false);

  const [accumulatedStreamedContent, setAccumulatedStreamedContent] = useState<string>("");
  const [processedContent, setProcessedContent] = useState<string>("");
  const [finalResponseData, setFinalResponseData] = useState<AskAIResponseData | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const accumulatedStreamedContentRef = useRef(accumulatedStreamedContent);
  const streamDisplayRef = useRef<HTMLDivElement>(null); // Changed ref to HTMLDivElement

  useEffect(() => {
    accumulatedStreamedContentRef.current = accumulatedStreamedContent;
    if (streamDisplayRef.current && isStreaming) {
      requestAnimationFrame(() => {
        if (streamDisplayRef.current) {
          streamDisplayRef.current.scrollTop = streamDisplayRef.current.scrollHeight;
        }
      });
    }
  }, [accumulatedStreamedContent, isStreaming]);

  const handleStreamChunk = useCallback((chunk: string) => {
    setAccumulatedStreamedContent(prev => prev + chunk);
  }, []);

  const handleStreamComplete = useCallback((data: AskAIResponseData) => {
    setFinalResponseData(data);
    setIsStreaming(false);
    setProcessedContent(removeThinkTags(accumulatedStreamedContentRef.current));
  }, []);

  const handleStreamError = useCallback((error: Error) => {
    const errorMessage = error.message || "An error occurred while streaming AI response.";
    setStreamError(errorMessage);
    setIsStreaming(false);
    setProcessedContent(removeThinkTags(accumulatedStreamedContentRef.current));
    toast.error(errorMessage);
  }, []);

  useEffect(() => {
    if (isOpen) {
      setAccumulatedStreamedContent("");
      accumulatedStreamedContentRef.current = "";
      setProcessedContent("");
      setFinalResponseData(null);
      setStreamError(null);
      setIsSavingAsNew(false);

      const baseName = currentDocumentName ? `AI_Response_to_${currentDocumentName.replace(/\s+/g, '_')}` : 'AI_Generated_Document';
      const dateSuffix = format(new Date(), 'yyyy-MM-dd');
      setNewDocumentName(`${baseName}_${dateSuffix}`);

      if (askAiQuery) {
        setIsStreaming(true);
        const payload: AskAIRequestPayload = {
            current_document_content: currentEditorContent,
            user_query: askAiQuery,
            document_name: currentDocumentName || "Untitled Document"
        };
        contentService.askAI(
            payload,
            handleStreamChunk,
            handleStreamComplete,
            handleStreamError
        ).catch(setupError => {
            console.error("Error initiating AskAI stream:", setupError);
            handleStreamError(new Error(setupError.message || "Failed to initiate AI stream."));
        });
      } else {
        setStreamError("No query provided to ask AI.");
        setIsStreaming(false);
      }
    }
  }, [isOpen, askAiQuery, currentEditorContent, currentDocumentName, handleStreamChunk, handleStreamComplete, handleStreamError]);


  if (!isOpen) return null;

  const handleSave = async () => {
    if (!newDocumentName.trim()) {
      toast.error("Please enter a name for the new document.");
      return;
    }
    const contentToSave = processedContent || removeThinkTags(accumulatedStreamedContentRef.current);
    if (!contentToSave) {
      toast.error("No AI content available to save.");
      return;
    }

    setIsSavingAsNew(true);
    try {
      await onSaveAsNewDocument(newDocumentName.trim(), contentToSave);
    } catch (e) {
      console.error("Error during save from modal:", e);
    } finally {
      setIsSavingAsNew(false);
    }
  };

  const copyToClipboard = (text: string | undefined | null) => {
    const contentToCopy = text ? removeThinkTags(text) : "";
    if (!contentToCopy && !isStreaming) {
        toast.error("No content to copy.");
        return;
    }
    if (contentToCopy){
        navigator.clipboard.writeText(contentToCopy)
        .then(() => toast.success("AI response copied to clipboard!"))
        .catch(err => {
            console.error("Failed to copy AI response: ", err);
            toast.error("Failed to copy AI response.");
        });
    }
  };

  const hasError = !!streamError;
  const contentForDisplay = isStreaming ? accumulatedStreamedContent : processedContent;
  const canSave = !!(processedContent || accumulatedStreamedContentRef.current) && !isStreaming && !streamError;


  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-auto transform transition-all max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-ulacm-gray-200 flex-shrink-0">
          <h3 className="text-xl font-semibold text-ulacm-gray-800 flex items-center">
            <Brain size={20} className="mr-2 text-ulacm-secondary" /> AI Response
          </h3>
          <button
            onClick={onClose}
            disabled={isStreaming || isSavingAsNew}
            className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-secondary/50"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Area */}
        <div className="px-6 py-5 flex-grow overflow-y-auto space-y-4">
          {isStreaming && !accumulatedStreamedContent && !streamError && (
            <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
              <LoadingSpinner size="lg" color="text-ulacm-secondary" />
              <p className="mt-4 text-lg font-medium text-ulacm-gray-700">AI is thinking...</p>
              <p className="text-sm text-ulacm-gray-500">Please wait for the response to stream.</p>
            </div>
          )}

          { ( (isStreaming && accumulatedStreamedContent) || (!isStreaming && (processedContent || streamError)) ) ? (
            <div className="space-y-3">
                {isStreaming && accumulatedStreamedContent && (
                    <div className="flex items-center text-ulacm-secondary">
                        <LoadingSpinner size="sm" color="text-ulacm-secondary" className="mr-2"/>
                        <span>AI is generating response...</span>
                    </div>
                )}
                <div className="flex justify-end">
                      <button
                          onClick={() => copyToClipboard(contentForDisplay)}
                          className="text-xs flex items-center text-ulacm-gray-500 hover:text-ulacm-secondary p-1 rounded hover:bg-ulacm-gray-100 transition-colors"
                          title="Copy AI response to clipboard"
                      >
                          <CopyIcon size={14} className="mr-1"/> Copy Response
                      </button>
                </div>
              <div ref={streamDisplayRef} className="bg-ulacm-gray-50 p-4 rounded-lg border border-ulacm-gray-200 text-sm text-ulacm-gray-800 max-h-[40vh] overflow-y-auto prose prose-sm max-w-none">
                <pre className="whitespace-pre-wrap break-words font-sans">
                    {contentForDisplay || (isStreaming ? "Waiting for stream..." : (streamError ? "Error during stream." : "No response yet."))}
                </pre>
              </div>
            </div>
          ) : null }


          {!isStreaming && hasError && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg mt-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-6 w-6 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h4 className="text-md font-semibold text-red-800 mb-1">Error from AI</h4>
                  <p className="text-sm text-red-700 bg-red-100 p-3 rounded break-words">
                    {streamError}
                  </p>
                </div>
              </div>
            </div>
          )}

          {!isStreaming && canSave && (
              <div className="pt-3 space-y-2">
                {finalResponseData?.model_used && (
                    <p className="text-xs text-ulacm-gray-500">Model used: {finalResponseData.model_used}</p>
                )}
                <label htmlFor="newDocNameInput" className="block text-sm font-medium text-ulacm-gray-700">
                  Save as new document with name:
                </label>
                <input
                  id="newDocNameInput"
                  type="text"
                  value={newDocumentName}
                  onChange={(e) => setNewDocumentName(e.target.value)}
                  placeholder="Enter name for the new document"
                  className="w-full px-3.5 py-2 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition-colors"
                  disabled={isSavingAsNew}
                />
              </div>
          )}
           {!isStreaming && !hasError && !accumulatedStreamedContent && !finalResponseData && !canSave && (
              <div className="text-center py-10 text-ulacm-gray-500 italic">
                AI response not available or stream not started.
              </div>
           )}
        </div>

        {/* Footer Actions */}
        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
          {canSave && (
            <button
              type="button"
              onClick={handleSave}
              disabled={isSavingAsNew || !newDocumentName.trim()}
              className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-ulacm-primary hover:bg-ulacm-primary-dark text-white focus:ring-ulacm-primary disabled:opacity-70"
            >
              {isSavingAsNew ? <LoadingSpinner size="sm" color="text-white" className="mr-2"/> : <Save size={18} className="mr-1.5"/>}
              {isSavingAsNew ? 'Saving...' : 'Save as New Document'}
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            disabled={isStreaming || isSavingAsNew}
            className="mt-3 w-full sm:mt-0 sm:w-auto inline-flex justify-center rounded-lg border border-ulacm-gray-300 shadow-sm px-5 py-2.5 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light transition-colors duration-150 disabled:opacity-70"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
export default AskAIResponseModal;
