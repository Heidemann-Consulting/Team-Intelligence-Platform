// File: ulacm_frontend/src/components/content/CreateDocumentModal.tsx
// Purpose: Modal for creating a new Document, requiring template selection.
// Updated: Changed ContentItemBase to ContentItemBaseCore in props.
// Updated: Added template preview functionality.
// Updated: Implemented default document name "Templatename_YYYY_MM_DD" with prefix stripping.
// Updated: Added 'modal-markdown-preview' class for consistent styling with editor preview.
import React, { useState, useEffect, FormEvent, useCallback } from 'react';
import toast from 'react-hot-toast';
import { X, FilePlus, AlertCircle, Eye } from 'lucide-react';
import { ContentItemBaseCore, ContentItemType, PaginatedResponse, ContentItemDetail, ContentItemListed } from '@/types/api';
import contentService, { ContentItemCreatePayload } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { marked } from 'marked';
import { format } from 'date-fns';
// Added for date formatting

interface CreateDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newDocument: ContentItemBaseCore) => void;
}

const CreateDocumentModal: React.FC<CreateDocumentModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [templates, setTemplates] = useState<ContentItemListed[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const [newDocumentName, setNewDocumentName] = useState('');
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [isLoadingCreate, setIsLoadingCreate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

  const [templatePreviewContent, setTemplatePreviewContent] = useState<string |
null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    if (!isOpen) return;

    setIsLoadingTemplates(true);
    setError(null);
    setCreateError(null);
    setTemplatePreviewContent(null);
    setPreviewError(null);
    try {
      const params = {
        item_type: ContentItemType.TEMPLATE,
        limit: 100,
        for_usage: true,
        sort_by: 'name',
        sort_order: 'asc' as 'asc',
      };
      const data: PaginatedResponse<ContentItemListed> = await contentService.getItems(params);
      setTemplates(data.items);
      if (data.items.length === 0) {
          setError("No templates found. An Administrator needs to create and share templates first.");
      }
    } catch (err: any) {
      console.error("Failed to fetch templates:", err);
      const errorMessage = err.message || 'Failed to load templates.';
      setError(errorMessage);
    } finally {
      setIsLoadingTemplates(false);
    }
  }, [isOpen]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const generateDefaultDocumentName = (templateName: string | undefined): string => {
    if (!templateName) return '';
    let name = templateName;
    const prefixesToStrip = ["HORIZON ", "HORIZON_", "A_Lean_Loop_", "LACM ", "Phase 1 ", "Phase 2 ", "Phase 3 "];
    prefixesToStrip.forEach(prefix => {
        if (name.startsWith(prefix)) {
            name = name.substring(prefix.length);
        }
    });
    // Remove spaces in the remaining template name part
    name = name.trim().replace(/\s+/g, '');
    const currentDate = format(new Date(), 'yyyy_MM_dd');
    return `${name.trim()}_${currentDate}`;
  };

  useEffect(() => {
    if (selectedTemplateId) {
      const selectedTemplate = templates.find(t => t.item_id === selectedTemplateId);
      setNewDocumentName(generateDefaultDocumentName(selectedTemplate?.name));
      fetchTemplatePreview(selectedTemplateId);
    } else {
      setNewDocumentName(''); // Clear name if no template selected
      setTemplatePreviewContent(null);
    }
  }, [selectedTemplateId, templates]);

  const fetchTemplatePreview = useCallback(async (templateId: string) => {
    if (!templateId) {
      setTemplatePreviewContent(null);
      setPreviewError(null);
      return;
    }
    setIsLoadingPreview(true);
    setPreviewError(null);
    try {
      const templateDetails: ContentItemDetail = await contentService.getItemDetails(templateId);
      setTemplatePreviewContent(templateDetails.markdown_content || "# Empty Template\n\nThis template has no content.");
    } catch (err: any) {
      console.error("Failed to fetch template preview:", err);
      setTemplatePreviewContent(null);
      setPreviewError("Could not load template preview.");
    } finally {
      setIsLoadingPreview(false);
    }
  }, []);

  useEffect(() => {
    if (!isOpen) {
      setSelectedTemplateId('');
      setNewDocumentName('');
      setError(null);
      setCreateError(null);
      setTemplatePreviewContent(null);
      setPreviewError(null);
    }
  }, [isOpen]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedTemplateId || !newDocumentName.trim()) {
      toast.error("Please select a template and enter a name for the document.");
      return;
    }

    setIsLoadingCreate(true);
    setCreateError(null);
    try {
      const payload: ContentItemCreatePayload = {
        name: newDocumentName.trim(),
        item_type: ContentItemType.DOCUMENT,
        template_id: selectedTemplateId,
      };
      const newDocument = await contentService.createItem(payload); // Returns ContentItemBaseCore
      toast.success(`Document "${newDocument.name}" created successfully!`);
      onSuccess(newDocument);
    } catch (err: any) {
      console.error("Failed to create document:", err);
      const errorMessage = err.response?.data?.detail ||
      err.message || 'Failed to create document.';
      if (err.response?.status === 409 && errorMessage.toLowerCase().includes("name") && errorMessage.toLowerCase().includes("document")) {
        setCreateError(`A document with the name "${newDocumentName.trim()}" already exists. Please choose a different name.`);
      } else {
        setCreateError(errorMessage);
      }
    } finally {
      setIsLoadingCreate(false);
    }
  };

  if (!isOpen) return null;

  const renderPreviewHTML = (): { __html: string } | undefined => {
    if (!templatePreviewContent) {
      return undefined;
    }
    try {
      const parsedOutput = marked.parse(templatePreviewContent);
      if (typeof parsedOutput === 'string') {
        return { __html: parsedOutput };
      } else {
        console.warn("marked.parse returned a Promise for preview. Displaying placeholder.");
        return { __html: "<p class='text-orange-500 italic'>Preview generation is processing (async)...</p>" };
      }
    } catch (parseError) {
      console.error("Error parsing Markdown for preview:", parseError);
      return { __html: "<p class='text-red-500 font-semibold'>Error rendering preview.</p>" };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-auto transform transition-all max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-ulacm-gray-200 flex-shrink-0">
          <h3 className="text-xl font-semibold text-ulacm-gray-800 flex items-center">
            <FilePlus size={20} className="mr-2 text-ulacm-primary" /> Create New Document
          </h3>
          <button onClick={onClose} className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto">
          <div className="px-6 py-5 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Form Fields */}
              <div className="space-y-5">
                <div>
                  <label htmlFor="templateSelect" className="block text-sm font-medium text-ulacm-gray-700 mb-1">
                    Select Template <span className="text-red-600">*</span>
                  </label>
                  {isLoadingTemplates ? (
                    <div className="flex items-center text-sm text-ulacm-gray-500 h-10">
                      <LoadingSpinner size="sm" className="mr-2" /> Loading templates...
                    </div>
                  ) : error ? (
                     <div className="bg-red-50 border border-red-300 text-red-700 px-3 py-2 rounded text-sm flex items-start">
                         <AlertCircle className="h-4 w-4 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                         {error}
                     </div>
                  ) : (
                    <select
                      id="templateSelect" value={selectedTemplateId}
                      onChange={(e) => setSelectedTemplateId(e.target.value)} required
                      className="w-full px-3.5 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition-colors bg-white appearance-none"
                    >
                      <option value="" disabled>-- Select a Template --</option>
                      {templates.map((template) => (
                        <option key={template.item_id} value={template.item_id}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                  )}
                  <p className="mt-1.5 text-xs text-ulacm-gray-500">
                    Templates are managed by Administrators.
                  </p>
                </div>

                <div>
                  <label htmlFor="documentName" className="block text-sm font-medium text-ulacm-gray-700 mb-1">
                    Document Name <span className="text-red-600">*</span>
                  </label>
                  <input
                    id="documentName" type="text" value={newDocumentName}
                    onChange={(e) => setNewDocumentName(e.target.value)} required
                    placeholder="Enter a name for your new document"
                    className="w-full px-3.5 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition-colors"
                  />
                </div>
              </div>

              {/* Template Preview */}
              <div className="space-y-1">
                <h4 className="text-sm font-medium text-ulacm-gray-700 flex items-center">
                  <Eye size={16} className="mr-1.5 text-ulacm-gray-400"/> Template Preview
                </h4>
                {/* Added 'modal-markdown-preview' class and kept 'prose' for baseline */}
                <div className="modal-markdown-preview border border-ulacm-gray-200 rounded-lg p-3 bg-ulacm-gray-50 min-h-[150px] max-h-[300px] overflow-y-auto prose prose-sm max-w-none">
                  {isLoadingPreview ? (
                    <div className="flex flex-col items-center justify-center h-full text-ulacm-gray-500">
                      <LoadingSpinner size="sm" />
                      <p className="mt-1 text-xs">Loading preview...</p>
                    </div>
                  ) : previewError ? (
                    <div className="flex flex-col items-center justify-center h-full text-red-500">
                       <AlertCircle size={20} className="mb-1"/>
                       <p className="text-xs">{previewError}</p>
                    </div>
                  ) : templatePreviewContent ? (
                    <div dangerouslySetInnerHTML={renderPreviewHTML()} />
                  ) : (
                    <p className="text-ulacm-gray-400 italic text-xs text-center py-10">
                      Select a template to see its preview.
                    </p>
                  )}
                </div>
              </div>
            </div>

            {createError && (
              <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded relative flex items-start mt-4" role="alert">
                <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                <span className="block sm:inline text-sm">{createError}</span>
               </div>
            )}
          </div>

          <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
            <button
              type="submit"
              disabled={isLoadingTemplates || isLoadingCreate || !selectedTemplateId || !newDocumentName.trim()}
              className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-ulacm-primary hover:bg-ulacm-primary-dark text-white focus:ring-ulacm-primary disabled:opacity-70"
            >
              {isLoadingCreate ? <LoadingSpinner size="sm" color="text-white" className="mr-2"/> : <FilePlus size={18} className="mr-1.5"/>}
              {isLoadingCreate ? 'Creating...' : 'Create Document'}
            </button>
            <button
              type="button" onClick={onClose} disabled={isLoadingCreate}
              className="mt-3 w-full sm:mt-0 sm:w-auto inline-flex justify-center rounded-lg border border-ulacm-gray-300 shadow-sm px-5 py-2.5 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light transition-colors duration-150 disabled:opacity-70"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDocumentModal;
