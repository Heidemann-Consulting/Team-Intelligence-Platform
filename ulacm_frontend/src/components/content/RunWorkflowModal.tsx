// File: ulacm_frontend/src/components/content/RunWorkflowModal.tsx
// Purpose: Modal to display workflow execution status and results, handling streaming.
// Improved auto-scrolling and UI update logic.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { X, CheckCircle, AlertTriangle, Copy as CopyIcon, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import { RunWorkflowResponse, ContentItemListed } from '@/types/api';
import contentService, { RunWorkflowPayload } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';

const removeThinkTags = (text: string): string => {
  if (!text) return "";
  return text.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
};

interface RunWorkflowModalProps {
  isOpen: boolean;
  workflowToExecute: ContentItemListed | null;
  initialPayload?: RunWorkflowPayload;
  onClose: () => void;
  onViewOutput: (itemId: string) => void;
}

const RunWorkflowModal: React.FC<RunWorkflowModalProps> = ({
  isOpen,
  workflowToExecute,
  initialPayload,
  onClose,
  onViewOutput,
}) => {
  const [accumulatedStreamedContent, setAccumulatedStreamedContent] = useState<string>("");
  const [processedContent, setProcessedContent] = useState<string>("");
  const [finalOutput, setFinalOutput] = useState<RunWorkflowResponse | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);

  const streamDisplayRef = useRef<HTMLDivElement>(null); // Changed ref to HTMLDivElement

  const accumulatedStreamedContentRef = useRef(accumulatedStreamedContent);
  useEffect(() => {
    accumulatedStreamedContentRef.current = accumulatedStreamedContent;
  }, [accumulatedStreamedContent]);


  useEffect(() => {
    if (isStreaming && streamDisplayRef.current) {
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

  const handleStreamComplete = useCallback((data: RunWorkflowResponse) => {
    setIsStreaming(false);
    setFinalOutput(data);
    const cleanContent = removeThinkTags(accumulatedStreamedContentRef.current);
    setProcessedContent(cleanContent);

    if (data.output_document) {
        setFinalOutput(prev => prev ? {
            ...prev,
            output_document: {
                ...prev.output_document!,
                markdown_content: cleanContent
            }
        } : null);
    }
    if (data.message) {
        toast.success(data.message || `Workflow "${workflowToExecute?.name || 'Workflow'}" processing complete.`);
    }
  }, [workflowToExecute?.name]);

  const handleStreamError = useCallback((error: Error) => {
    const errorMessage = error.message || "An error occurred during workflow execution.";
    setStreamError(errorMessage);
    setIsStreaming(false);
    setProcessedContent(removeThinkTags(accumulatedStreamedContentRef.current));
    toast.error(errorMessage);
  }, []);

  useEffect(() => {
    if (isOpen && workflowToExecute) {
      setAccumulatedStreamedContent("");
      accumulatedStreamedContentRef.current = "";
      setProcessedContent("");
      setFinalOutput(null);
      setStreamError(null);
      setIsStreaming(true);

      contentService.runWorkflow(
        workflowToExecute.item_id,
        handleStreamChunk,
        handleStreamComplete,
        handleStreamError,
        initialPayload
      ).catch(setupError => {
        console.error("Error initiating workflow execution stream:", setupError);
        handleStreamError(new Error(setupError.message || "Failed to initiate workflow stream."));
      });
    }
  }, [isOpen, workflowToExecute, initialPayload, handleStreamChunk, handleStreamComplete, handleStreamError]);

  if (!isOpen) return null;

  const hasError = !!streamError;
  const currentError = streamError;
  const hasSuccess = finalOutput && !hasError && finalOutput.output_document;

  const copyToClipboard = (textToCopy: string | undefined | null) => {
    const content = textToCopy ? removeThinkTags(textToCopy) : "";
    if (!content && !isStreaming) {
        toast.error("No content to copy.");
        return;
    }
    if (content){
        navigator.clipboard.writeText(content)
        .then(() => toast.success("Output copied to clipboard!"))
        .catch(err => {
            console.error("Failed to copy text: ", err);
            toast.error("Failed to copy output.");
        });
    }
  };

  const contentForDisplay = isStreaming ? accumulatedStreamedContent : processedContent;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-auto transform transition-all max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-ulacm-gray-50 border-b border-ulacm-gray-200">
          <h3 className="text-lg leading-6 font-semibold text-ulacm-gray-900" id="modal-title">
            Run Workflow: {workflowToExecute?.name || 'Workflow'}
          </h3>
          <button
            onClick={onClose}
            disabled={isStreaming}
            className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Area */}
        <div className="px-6 py-5 max-h-[65vh] overflow-y-auto">
          {isStreaming && !accumulatedStreamedContent && !streamError && (
            <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
              <LoadingSpinner size="lg" color="text-purple-600" />
              <p className="mt-4 text-lg font-medium text-ulacm-gray-700">Executing Workflow...</p>
              <p className="text-sm text-ulacm-gray-500">Please wait while the AI processes your request.</p>
            </div>
          )}

          { ( (isStreaming && accumulatedStreamedContent) || (!isStreaming && (processedContent || streamError)) ) && (
            <div className="space-y-3">
              {isStreaming && accumulatedStreamedContent && (
                <div className="flex items-center text-purple-600">
                  <LoadingSpinner size="sm" color="text-purple-600" className="mr-2"/>
                  <span>AI is generating response...</span>
                </div>
              )}
              <div ref={streamDisplayRef} className="bg-ulacm-gray-50 p-4 rounded-lg border border-ulacm-gray-200 text-sm text-ulacm-gray-800 max-h-80 overflow-y-auto prose prose-sm max-w-none">
                <pre className="whitespace-pre-wrap break-words font-sans">
                    {contentForDisplay || (isStreaming ? "Waiting for stream..." : (streamError ? "Error during stream." : "(No content generated)"))}
                </pre>
              </div>
            </div>
          )}


          {!isStreaming && hasError && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg mt-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <AlertTriangle className="h-6 w-6 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h4 className="text-md font-semibold text-red-800 mb-1">Workflow Execution Failed</h4>
                  <p className="text-sm text-red-700 bg-red-100 p-3 rounded break-words">
                    {currentError || 'An unknown error occurred.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {!isStreaming && hasSuccess && finalOutput?.output_document && (
            <div className="space-y-5 mt-4">
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <CheckCircle className="h-6 w-6 text-green-500" aria-hidden="true" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-md font-semibold text-green-800 mb-1">Workflow Executed Successfully!</h4>
                    <p className="text-sm text-green-700">
                      Output document "<span className="font-medium">{finalOutput.output_document.name}</span>" has been created/updated.
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex justify-end">
                  <button
                    onClick={() => copyToClipboard(processedContent)}
                    className="text-xs flex items-center text-ulacm-gray-500 hover:text-ulacm-primary p-1 rounded hover:bg-ulacm-gray-100 transition-colors"
                    title="Copy final output to clipboard"
                  >
                    <CopyIcon size={14} className="mr-1"/> Copy Final Output
                  </button>
              </div>
            </div>
          )}
           {!isStreaming && !hasSuccess && !hasError && !accumulatedStreamedContent && !processedContent && (
              <div className="text-center py-10 text-ulacm-gray-500 italic">
                Workflow data not available or execution not started.
              </div>
           )}
        </div>

        {/* Footer Actions */}
        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3 border-t border-ulacm-gray-200">
          <button
            type="button"
            onClick={onClose}
            disabled={isStreaming}
            className="w-full sm:w-auto inline-flex justify-center rounded-md border border-ulacm-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light sm:text-sm transition-colors"
          >
            Close
          </button>
          {!isStreaming && hasSuccess && finalOutput?.output_document && (
            <button
              type="button"
              onClick={() => onViewOutput(finalOutput.output_document.item_id)}
              className="w-full sm:w-auto inline-flex items-center justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors bg-ulacm-primary hover:bg-ulacm-primary-dark text-white focus:ring-ulacm-primary sm:text-sm"
            >
              <FileText size={16} className="mr-1.5"/> View Output Document
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RunWorkflowModal;
