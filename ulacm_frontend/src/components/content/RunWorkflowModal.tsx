// File: ulacm_frontend/src/components/content/RunWorkflowModal.tsx
// Purpose: Modal to display workflow execution status and results.
// Refinements: Improved layout, styling, feedback states.
// Updated: Display output document name in success message.

import React from 'react';
import { X, CheckCircle, AlertTriangle, Copy as CopyIcon, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import { RunWorkflowResponse } from '@/types/api'; // Import the response type
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface RunWorkflowModalProps {
  isOpen: boolean;
  workflowName?: string;
  isLoading: boolean; // Is the workflow currently running?
  output: RunWorkflowResponse | { error: string } | null; // Contains success data or error message
  onClose: () => void;
  onViewOutput: (itemId: string) => void; // Callback to navigate to the generated document
}

const RunWorkflowModal: React.FC<RunWorkflowModalProps> = ({
  isOpen,
  workflowName,
  isLoading,
  output,
  onClose,
  onViewOutput,
}) => {
  if (!isOpen) return null;

  const hasError = output && 'error' in output;
  const hasSuccess = output && !hasError && output.output_document; // Ensure output_document exists

  const copyToClipboard = (text: string | undefined | null) => {
    if (!text) {
        toast.error("No content to copy.");
        return;
    }
    navigator.clipboard.writeText(text)
      .then(() => toast.success("Output copied to clipboard!"))
      .catch(err => {
        console.error("Failed to copy text: ", err);
        toast.error("Failed to copy output.");
      });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-ulacm-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        {/* Centering trick */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 bg-ulacm-gray-50 border-b border-ulacm-gray-200">
            <h3 className="text-lg leading-6 font-semibold text-ulacm-gray-900" id="modal-title">
              Run Workflow: {workflowName || 'Workflow'}
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
          <div className="px-6 py-5 max-h-[65vh] overflow-y-auto"> {/* Max height for content */}
            {isLoading && (
              <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
                <LoadingSpinner size="lg" color="text-purple-600" />
                <p className="mt-4 text-lg font-medium text-ulacm-gray-700">Executing Workflow...</p>
                <p className="text-sm text-ulacm-gray-500">Please wait while the AI processes your request.</p>
              </div>
            )}

            {!isLoading && hasError && (
              <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                <div className="flex items-start">
                    <div className="flex-shrink-0">
                        <AlertTriangle className="h-6 w-6 text-red-400" aria-hidden="true" />
                    </div>
                    <div className="ml-3">
                        <h4 className="text-md font-semibold text-red-800 mb-1">Workflow Execution Failed</h4>
                        <p className="text-sm text-red-700 bg-red-100 p-3 rounded break-words">
                            {output.error || 'An unknown error occurred.'}
                        </p>
                    </div>
                </div>
              </div>
            )}

            {!isLoading && hasSuccess && output.output_document && ( // Added null check for output.output_document
              <div className="space-y-5">
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <div className="flex items-start">
                      <div className="flex-shrink-0">
                          <CheckCircle className="h-6 w-6 text-green-500" aria-hidden="true" />
                      </div>
                      <div className="ml-3">
                          <h4 className="text-md font-semibold text-green-800 mb-1">Workflow Executed Successfully!</h4>
                          <p className="text-sm text-green-700">
                            Output document "<span className="font-medium">{output.output_document.name}</span>" has been created/updated.
                          </p>
                      </div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                       <h5 className="text-md font-semibold text-ulacm-gray-700">Generated Output Preview:</h5>
                       <button
                          onClick={() => copyToClipboard(output.output_document?.markdown_content)}
                          className="text-xs flex items-center text-ulacm-gray-500 hover:text-ulacm-primary p-1 rounded hover:bg-ulacm-gray-100 transition-colors"
                          title="Copy output to clipboard"
                      >
                          <CopyIcon size={14} className="mr-1"/> Copy Output
                      </button>
                  </div>
                  {/* Improved output display */}
                  <div className="bg-ulacm-gray-50 p-4 rounded-lg border border-ulacm-gray-200 text-sm text-ulacm-gray-800 max-h-80 overflow-y-auto prose prose-sm max-w-none">
                     {/* Render basic markdown or just preformatted text */}
                     <pre className="whitespace-pre-wrap break-words font-sans">
                        {output.output_document.markdown_content || '(No content generated)'}
                     </pre>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3 border-t border-ulacm-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="w-full sm:w-auto inline-flex justify-center rounded-md border border-ulacm-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light sm:text-sm transition-colors"
            >
              Close
            </button>
            {hasSuccess && output.output_document && ( // Added null check
               <button
                  type="button"
                  onClick={() => onViewOutput(output.output_document.item_id)}
                  className="w-full sm:w-auto inline-flex items-center justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors bg-ulacm-primary hover:bg-ulacm-primary-dark text-white focus:ring-ulacm-primary sm:text-sm"
              >
                  <FileText size={16} className="mr-1.5"/> View Output Document
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunWorkflowModal;
