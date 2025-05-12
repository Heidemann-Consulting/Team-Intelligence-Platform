// File: ulacm_frontend/src/components/content/AskAIResponseModal.tsx
// Purpose: Modal to display AI responses and allow saving as a new document.
import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle, Brain, Copy as CopyIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { format } from 'date-fns';

interface AskAIResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  aiResponseContent: string | null;
  error: string | null;
  isLoading: boolean;
  onSaveAsNewDocument: (documentName: string, content: string) => Promise<void>;
  currentDocumentName?: string; // Optional: to prefill save name
}

const AskAIResponseModal: React.FC<AskAIResponseModalProps> = ({
  isOpen,
  onClose,
  aiResponseContent,
  error,
  isLoading,
  onSaveAsNewDocument,
  currentDocumentName
}) => {
  const [newDocumentName, setNewDocumentName] = useState('');
  const [isSavingAsNew, setIsSavingAsNew] = useState(false);

  useEffect(() => {
    if (isOpen) {
        // Generate a default name when the modal opens and there's AI content
        if (aiResponseContent && !error) {
            const baseName = currentDocumentName ? `AI_Response_to_${currentDocumentName.replace(/\s+/g, '_')}` : 'AI_Generated_Document';
            const dateSuffix = format(new Date(), 'yyyy-MM-dd');
            setNewDocumentName(`${baseName}_${dateSuffix}`);
        } else {
            setNewDocumentName(''); // Clear if no content or error
        }
        setIsSavingAsNew(false); // Reset saving state
    }
  }, [isOpen, aiResponseContent, error, currentDocumentName]);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!newDocumentName.trim()) {
      toast.error("Please enter a name for the new document.");
      return;
    }
    if (!aiResponseContent) {
      toast.error("No AI content available to save.");
      return;
    }
    setIsSavingAsNew(true);
    try {
      await onSaveAsNewDocument(newDocumentName.trim(), aiResponseContent);
      // Success toast and navigation are handled by the parent component's callback
    } catch (e) {
      // Error toast should be handled by the parent or the onSaveAsNewDocument promise
      console.error("Error during save from modal:", e);
    } finally {
      setIsSavingAsNew(false);
    }
  };

  const copyToClipboard = (text: string | undefined | null) => {
    if (!text) {
        toast.error("No content to copy.");
        return;
    }
    navigator.clipboard.writeText(text)
      .then(() => toast.success("AI response copied to clipboard!"))
      .catch(err => {
        console.error("Failed to copy AI response: ", err);
        toast.error("Failed to copy AI response.");
      });
  };


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
            disabled={isLoading || isSavingAsNew}
            className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-secondary/50"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Area */}
        <div className="px-6 py-5 flex-grow overflow-y-auto space-y-4">
          {isLoading && (
            <div className="flex flex-col items-center justify-center text-center p-8 min-h-[200px]">
              <LoadingSpinner size="lg" color="text-ulacm-secondary" />
              <p className="mt-4 text-lg font-medium text-ulacm-gray-700">AI is thinking...</p>
              <p className="text-sm text-ulacm-gray-500">Please wait for the response.</p>
            </div>
          )}

          {!isLoading && error && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-red-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h4 className="text-md font-semibold text-red-800 mb-1">Error from AI</h4>
                  <p className="text-sm text-red-700 bg-red-100 p-3 rounded break-words">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}

          {!isLoading && !error && aiResponseContent && (
            <div className="space-y-3">
                 <div className="flex justify-end">
                     <button
                          onClick={() => copyToClipboard(aiResponseContent)}
                          className="text-xs flex items-center text-ulacm-gray-500 hover:text-ulacm-secondary p-1 rounded hover:bg-ulacm-gray-100 transition-colors"
                          title="Copy AI response to clipboard"
                      >
                          <CopyIcon size={14} className="mr-1"/> Copy Response
                      </button>
                </div>
              <div className="bg-ulacm-gray-50 p-4 rounded-lg border border-ulacm-gray-200 text-sm text-ulacm-gray-800 max-h-[40vh] overflow-y-auto prose prose-sm max-w-none">
                {/* Using 'prose' for basic Markdown-like formatting if response is Markdown */}
                {/* For plain text, <pre> might be better for preserving line breaks */}
                <pre className="whitespace-pre-wrap break-words font-sans">{aiResponseContent}</pre>
              </div>
              <div className="pt-3 space-y-2">
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
            </div>
          )}

           {!isLoading && !error && !aiResponseContent && (
             <div className="text-center py-10 text-ulacm-gray-500 italic">
                No AI response to display.
             </div>
           )}

        </div>

        {/* Footer Actions */}
        <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
          {!isLoading && !error && aiResponseContent && (
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
            disabled={isLoading || isSavingAsNew}
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
