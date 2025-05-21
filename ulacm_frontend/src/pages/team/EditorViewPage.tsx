// File: ulacm_frontend/src/pages/team/EditorViewPage.tsx
// Purpose: Page for viewing and editing a specific content item.
// Updated to pass necessary props for AskAIResponseModal streaming.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Save, Trash2, Copy, Eye, Globe, History, Undo, Redo, Settings, FileText, FileCode2, FolderGit2, AlertCircle, Info, Clock, User, Play, Brain
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

import { ContentItemDetail, ContentItemType, ContentItemDuplicatePayload, PaginatedResponse, ContentItemListed } from '@/types/api';
import { VersionMeta } from '@/types/content';
import contentService, { ContentItemCreatePayload, RunWorkflowPayload } from '@/services/contentService';
import { useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmationModal from '@/components/common/ConfirmationModal';
import ReactSimpleMDEEditor from '@/components/content/ReactSimpleMDEEditor';
import RunWorkflowModal from '@/components/content/RunWorkflowModal';
import AskAIResponseModal from '@/components/content/AskAIResponseModal';
import { ADMIN_SYSTEM_TEAM_ID_STRING } from '@/utils/constants';

const EditorViewPage: React.FC = () => {
  const { itemId: routeItemId } = useParams<{ itemId?: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { currentTeam, isAdminAuthenticated } = useAuth();

  const pathSegments = location.pathname.split('/');
  const itemTypeSegment = isAdminAuthenticated ? pathSegments[2] : pathSegments[2];

  const isCreatingNewItem = location.pathname.endsWith('/new');
  const actualItemId = isCreatingNewItem ? undefined : routeItemId;

  const [itemDetails, setItemDetails] = useState<ContentItemDetail | null>(null);
  const [newItemType, setNewItemType] = useState<ContentItemType | null>(null);
  const [editorItemType, setEditorItemType] = useState<ContentItemType | null>(null);
  const [newItemName, setNewItemName] = useState<string>('');
  const [editorContent, setEditorContent] = useState<string>('');
  const [isDirty, setIsDirty] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [versionHistory, setVersionHistory] = useState<VersionMeta[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [selectedWorkflowForAdminRun, setSelectedWorkflowForAdminRun] = useState<ContentItemListed | null>(null);
  const [showAdminRunWorkflowModal, setShowAdminRunWorkflowModal] = useState(false);
  const [adminRunInitialPayload, setAdminRunInitialPayload] = useState<RunWorkflowPayload | undefined>(undefined);

  const [loadedVersionNumber, setLoadedVersionNumber] = useState<number | null>(null);
  const [teamDataCache] = useState<Record<string, string>>({});
  const lastSavedContentRef = useRef<string>('');
  const itemJustCreatedIdRef = useRef<string | null>(null);

  // State for "Ask AI" feature
  const [askAiQueryInput, setAskAiQueryInput] = useState(''); // Input field for the query
  const [askAiQueryToSubmit, setAskAiQueryToSubmit] = useState(''); // Query that gets submitted
  const [showAskAIResponseModal, setShowAskAIResponseModal] = useState(false);
  // isAskingAI, askAIResponse, askAIError are now managed within AskAIResponseModal

  const isOwner = itemDetails && currentTeam && itemDetails.team_id === currentTeam.team_id;
  const canEditContent = isCreatingNewItem ||
                         (isAdminAuthenticated && itemDetails &&
                            ((itemDetails.item_type === ContentItemType.TEMPLATE && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                             (itemDetails.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                             (itemDetails.item_type === ContentItemType.DOCUMENT))) ||
                         (!isAdminAuthenticated && itemDetails && itemDetails.item_type === ContentItemType.DOCUMENT && isOwner);

  const canPerformMetaActions = isCreatingNewItem ? false :
                                (isAdminAuthenticated && itemDetails &&
                                    ((itemDetails.item_type === ContentItemType.TEMPLATE && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                                     (itemDetails.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                                     (itemDetails.item_type === ContentItemType.DOCUMENT))) ||
                                (!isAdminAuthenticated && itemDetails && itemDetails.item_type === ContentItemType.DOCUMENT && isOwner);

  const loadItemDetails = useCallback(async (idToLoad: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const details = await contentService.getItemDetails(idToLoad);
      setItemDetails(details);
      setEditorItemType(details.item_type);
      const initialContentForEditor = details.markdown_content ?? '';
      setEditorContent(initialContentForEditor);
      lastSavedContentRef.current = initialContentForEditor;
      setLoadedVersionNumber(details.current_version_number ?? null);
      setIsDirty(false);
      itemJustCreatedIdRef.current = null;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load item.';
      setError(errorMessage);
      if (err.response?.status === 403) {
        toast.error("You don't have permission to view this item's details.");
        navigate(isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard", {replace: true});
      }
    } finally {
      setIsLoading(false);
    }
  }, [isAdminAuthenticated, navigate]);

  useEffect(() => {
    let typeFromPath: ContentItemType | null = null;
    if (itemTypeSegment === 'documents') typeFromPath = ContentItemType.DOCUMENT;
    else if (itemTypeSegment === 'templates') typeFromPath = ContentItemType.TEMPLATE;
    else if (itemTypeSegment === 'workflows') typeFromPath = ContentItemType.WORKFLOW;

    setEditorItemType(typeFromPath);

    if (isCreatingNewItem) {
      setIsLoading(true);
      setNewItemType(typeFromPath);

      if ((typeFromPath === ContentItemType.TEMPLATE || typeFromPath === ContentItemType.WORKFLOW) && !isAdminAuthenticated) {
        setError("Only Admins can create new Templates or Workflows.");
        toast.error("Access Denied.");
        navigate("/app/dashboard", { replace: true });
        setIsLoading(false);
        return;
      }
      if (typeFromPath === ContentItemType.DOCUMENT && isAdminAuthenticated) {
        setError("Admins do not create team documents directly. Use a team account.");
        toast.error("Operation not permitted for Admin.");
        navigate("/admin/dashboard", { replace: true });
        setIsLoading(false);
        return;
      }
       if (typeFromPath === ContentItemType.DOCUMENT && !isAdminAuthenticated) {
        setError("New documents must be created from a template via the 'New Document' button on the Documents page.");
        toast.error("Please use the 'New Document' button.");
        navigate('/app/documents', { replace: true });
        setIsLoading(false);
        return;
      }

      let defaultContent = '';
      let defaultName = '';
      if (typeFromPath === ContentItemType.TEMPLATE) {
        defaultName = 'New Template';
        defaultContent = `---
title: My New Template
author: Template Author
date: ${new Date().toISOString().split('T')[0]}
---

# Template Heading

This is a new template. Replace with your content.
`;
      } else if (typeFromPath === ContentItemType.WORKFLOW) {
        defaultName = 'New Workflow';
        defaultContent = `inputDocumentSelectors: ["Input_Doc_*"] # List of glob patterns for document names
inputDateSelector: newerThanDays 7 # Optional: olderThanDays N, newerThanDays N, or between_YYYY-MM-DD_YYYY-MM-DD
outputName: "Output_{{WorkflowName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  SYSTEM: You are an AI assistant. Your task is to process the provided document(s).
  CONTEXT:
    {{DocumentContext}} # This will be replaced with the content of selected documents.
  TASK:
    Based on the document(s) in the CONTEXT, please perform the following:
    1. Summarize the key findings.
    2. Identify action items.
    3. Provide a brief analysis.

  Current date: {{CurrentDate}}
  Workflow name: {{WorkflowName}}
  Input file names: {{InputFileNames}}
  Input file count: {{InputFileCount}}
`;
      }

      setItemDetails(null);
      setNewItemName(defaultName);
      setEditorContent(defaultContent);
      lastSavedContentRef.current = defaultContent;
      setIsDirty(false);
      setError(null);
      setLoadedVersionNumber(null);
      setIsLoading(false);
    } else if (actualItemId && actualItemId !== "undefined") {
      setNewItemType(null);
      loadItemDetails(actualItemId);
    } else {
      setIsLoading(false);
      setError(routeItemId === "undefined" ? "Invalid item ID in URL: received 'undefined' string." : "Invalid or missing item ID in URL.");
    }
  }, [isCreatingNewItem, actualItemId, itemTypeSegment, location.pathname, isAdminAuthenticated, navigate, loadItemDetails, routeItemId]);

  const loadVersionHistory = useCallback(async () => {
    if (isCreatingNewItem || !actualItemId || actualItemId === itemJustCreatedIdRef.current || !itemDetails) {
      setVersionHistory([]);
      return;
    }
    setIsLoadingHistory(true);
    try {
      const historyData = await contentService.listVersions(actualItemId, { limit: 100, sort_order: 'desc' });
      setVersionHistory(historyData.versions);
    } catch (err) {
      console.error("Failed to load version history:", err);
      toast.error("Failed to load version history.");
    } finally {
      setIsLoadingHistory(false);
    }
  }, [actualItemId, isCreatingNewItem, itemDetails]);

  useEffect(() => {
    if (!isCreatingNewItem && actualItemId && itemDetails) {
      loadVersionHistory();
    } else {
      setVersionHistory([]);
    }
  }, [actualItemId, isCreatingNewItem, loadVersionHistory, itemDetails]);

  const handleEditorChange = useCallback((markdownContent: string) => {
    setEditorContent(markdownContent);
    setIsDirty(markdownContent !== lastSavedContentRef.current);
  }, []);

  const handleSave = async () => {
    if (!canEditContent) {
        toast.error("You do not have permission to save this item.");
        return;
    }
    setIsSaving(true);
    setError(null);
    const currentContent = editorContent;
    const toastIdPrefix = isCreatingNewItem && !itemJustCreatedIdRef.current ? (newItemName || 'new-item').trim() : (actualItemId || itemDetails?.item_id || 'existing-item');
    const toastId = `save-${toastIdPrefix}-${Date.now()}`;

    if (isCreatingNewItem && !itemJustCreatedIdRef.current) {
      const typeToCreate = newItemType || editorItemType;
      if (!typeToCreate) {
        toast.error("Item type unknown. Cannot save.", { id: toastId });
        setIsSaving(false);
        return;
      }
      if (!newItemName.trim()) {
        toast.error("Please enter a name for the new item.", { id: toastId });
        setIsSaving(false); return;
      }
      toast.loading(`Creating ${typeToCreate}...`, { id: toastId });
      try {
        const createPayload: ContentItemCreatePayload = { name: newItemName.trim(), item_type: typeToCreate };
        const createdItemMeta = await contentService.createItem(createPayload);
        itemJustCreatedIdRef.current = createdItemMeta.item_id;

        const versionPayload = { markdown_content: currentContent };
        await contentService.saveNewVersion(createdItemMeta.item_id, versionPayload);
        toast.success(`${typeToCreate} "${createdItemMeta.name}" created successfully!`, { id: toastId });
        itemJustCreatedIdRef.current = null;
        const basePath = isAdminAuthenticated ? '/admin' : '/app';
        navigate(`${basePath}/${typeToCreate.toLowerCase()}s/${createdItemMeta.item_id}`, { replace: true });
      } catch (err: any) {
        const apiErrorDetail = err.response?.data?.detail || err.message;
        let userFriendlyError = `Failed to create ${typeToCreate}: ${apiErrorDetail}`;
        if (itemJustCreatedIdRef.current && typeToCreate === ContentItemType.WORKFLOW && err.response?.status === 400) {
             userFriendlyError = `Error in ${typeToCreate} content: ${apiErrorDetail || 'Invalid YAML syntax.'} The item metadata for '${newItemName}' was created. Please correct the content; you are now editing this item.`;
             navigate(`/admin/workflows/${itemJustCreatedIdRef.current}`, { replace: true, state: { initialContent: currentContent, isNewlyCreatedWithError: true, specificError: userFriendlyError } });
        } else {
            itemJustCreatedIdRef.current = null;
        }
        setError(userFriendlyError);
        toast.error(userFriendlyError, { id: toastId, duration: 8000 });
      } finally {
        setIsSaving(false);
      }
    } else {
      const idToSave = itemJustCreatedIdRef.current || actualItemId;
      if (!idToSave || (!itemDetails && !itemJustCreatedIdRef.current)) {
         toast.error("Item details not available for saving.");
         setIsSaving(false); return;
      }
      if (!isDirty) {
        toast.success("No changes to save.");
        setIsSaving(false); return;
      }
      toast.loading('Saving...', { id: toastId });
      try {
        const payload = { markdown_content: currentContent };
        const result = await contentService.saveNewVersion(idToSave, payload);

        if (itemJustCreatedIdRef.current) {
            toast.success(`Item "${itemDetails?.name || newItemName}" content saved!`, { id: toastId });
            itemJustCreatedIdRef.current = null;
            const currentBasePath = isAdminAuthenticated ? '/admin' : '/app';
            const itemTypePathSegment = (itemDetails?.item_type || editorItemType || newItemType )!.toLowerCase() + 's';
            if (location.pathname.endsWith('/new') || (location.state as any)?.isNewlyCreatedWithError) {
                 navigate(`${currentBasePath}/${itemTypePathSegment}/${idToSave}`, { replace: true });
            } else {
                loadItemDetails(idToSave);
            }
        } else if (itemDetails) {
            setItemDetails(prev => prev ? {
              ...prev,
              current_version_number: result.new_version.version_number,
              updated_at: result.item_updated_at,
              markdown_content: result.new_version.markdown_content,
              version_created_at: result.new_version.created_at,
              version_saved_by_team_id: result.new_version.saved_by_team_id
            } : null);
            setEditorContent(result.new_version.markdown_content);
            lastSavedContentRef.current = result.new_version.markdown_content;
            setLoadedVersionNumber(result.new_version.version_number);
            setIsDirty(false);
            toast.success('Saved successfully!', { id: toastId });
            loadVersionHistory();
        }
      } catch (err: any) {
        const msg = err.response?.data?.detail || 'Failed to save changes.';
        setError(msg);
        toast.error(msg, { id: toastId, duration: 6000 });
      } finally {
        setIsSaving(false);
      }
    }
  };

  useEffect(() => {
    if ((location.state as any)?.isNewlyCreatedWithError && actualItemId) {
      if ((location.state as any)?.initialContent) {
        setEditorContent((location.state as any).initialContent);
        lastSavedContentRef.current = "";
        setIsDirty(true);
      }
      setError((location.state as any)?.specificError || "Please review content and save again.");
      const currentBasePath = isAdminAuthenticated ? '/admin' : '/app';
      const itemTypePathSegment = (editorItemType)!.toLowerCase() + 's';
      navigate(`${currentBasePath}/${itemTypePathSegment}/${actualItemId}`, { replace: true, state: {} });
    }
  }, [location.state, actualItemId, navigate, isAdminAuthenticated, editorItemType]);

  const loadVersion = useCallback(async (versionId: string) => {
    const currentActualItemId = itemJustCreatedIdRef.current || actualItemId;
    if (!currentActualItemId || (!itemDetails && !itemJustCreatedIdRef.current)) return;

    if (isDirty && canEditContent) {
      const discard = window.confirm("You have unsaved changes. Are you sure you want to discard them and load a different version?");
      if (!discard) return;
    }

    const toastId = `load-version-${versionId}`;
    toast.loading('Loading version...', { id: toastId });
    try {
      const versionDetails = await contentService.getVersionContent(currentActualItemId, versionId);
      setEditorContent(versionDetails.markdown_content);
      lastSavedContentRef.current = versionDetails.markdown_content;
      setLoadedVersionNumber(versionDetails.version_number);
      setIsDirty(false);
      if(itemDetails) {
        setItemDetails(prev => prev ? {
          ...prev,
          version_created_at: versionDetails.created_at,
          version_saved_by_team_id: versionDetails.saved_by_team_id,
        } : null);
      }
      toast.success(`Loaded version ${versionDetails.version_number}.`, { id: toastId });
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to load version content.';
      toast.error(msg, { id: toastId });
    }
  }, [actualItemId, isDirty, itemDetails, canEditContent]);

  const handleToggleVisibility = useCallback(async () => {
    if (!canPerformMetaActions || !itemDetails || itemJustCreatedIdRef.current) return;
    const targetVisibility = !itemDetails.is_globally_visible;
    const toastId = `visibility-${itemDetails.item_id}`;
    toast.loading(`Updating visibility...`, { id: toastId });
    try {
      const updatedItemMeta = await contentService.updateItemMeta(itemDetails.item_id, { is_globally_visible: targetVisibility });
      setItemDetails(prev => prev ? { ...prev, is_globally_visible: updatedItemMeta.is_globally_visible, updated_at: updatedItemMeta.updated_at } : null);
      toast.success(`Item is now ${targetVisibility ? 'globally visible' : 'private'}.`, { id: toastId });
    } catch (err: any) {
      toast.error(err.message || 'Failed to update visibility.', { id: toastId });
    }
  }, [canPerformMetaActions, itemDetails]);

  const handleDelete = () => {
    if (canPerformMetaActions && itemDetails && !itemJustCreatedIdRef.current) {
      setShowDeleteModal(true);
    } else {
      toast.error("Cannot delete this item or item not saved yet.");
    }
  };

  const confirmDelete = useCallback(async () => {
    if (!canPerformMetaActions || !itemDetails || itemJustCreatedIdRef.current) return;
    const nameToDelete = itemDetails.name;
    const typeToDelete = itemDetails.item_type;
    const idToDelete = itemDetails.item_id;
    const toastId = `delete-${idToDelete}`;
    setShowDeleteModal(false);
    toast.loading(`Deleting ${typeToDelete}...`, { id: toastId });
    try {
      await contentService.deleteItem(idToDelete);
      toast.success(`${typeToDelete} "${nameToDelete}" deleted.`, { id: toastId });
      const basePath = isAdminAuthenticated ? '/admin' : '/app';
      navigate(`${basePath}/${typeToDelete.toLowerCase()}s`, {replace: true});
    } catch (err: any) {
      toast.error(err.message || `Failed to delete ${typeToDelete}.`, { id: toastId });
    }
  }, [canPerformMetaActions, itemDetails, navigate, isAdminAuthenticated]);

  const handleDuplicate = useCallback(() => {
    if (!canPerformMetaActions || !itemDetails || itemJustCreatedIdRef.current) {
        toast.error("Save the item first or ensure you have rights to duplicate.");
        return;
    }
    const nameForPrompt = itemDetails.name;
    const typeForPrompt = itemDetails.item_type;
    const newName = prompt(`Enter name for duplicated ${typeForPrompt}:`, `Copy of ${nameForPrompt}`);
    if (newName) {
      let versionToDuplicateId: string | undefined = undefined;
      if (loadedVersionNumber && versionHistory.find(v => v.version_number === loadedVersionNumber)) {
        versionToDuplicateId = versionHistory.find(v => v.version_number === loadedVersionNumber)?.version_id;
      } else if (itemDetails.current_version_id) {
        versionToDuplicateId = itemDetails.current_version_id;
      }
      const duplicatePayload: ContentItemDuplicatePayload = { new_name: newName, source_version_id: versionToDuplicateId };
      toast.promise(
        contentService.duplicateItem(itemDetails.item_id, duplicatePayload),
        {
          loading: `Duplicating ${typeForPrompt}...`,
          success: (duplicatedItem) => {
            const basePath = isAdminAuthenticated ? '/admin' : '/app';
            navigate(`${basePath}/${duplicatedItem.item_type.toLowerCase()}s/${duplicatedItem.item_id}`);
            return `Duplicated as "${duplicatedItem.name}".`;
          },
          error: (err) => err.message || `Failed to duplicate ${typeForPrompt}.`,
        }
      );
    }
  }, [canPerformMetaActions, itemDetails, navigate, isAdminAuthenticated, loadedVersionNumber, versionHistory]);

  const handleAdminRunWorkflow = useCallback(async () => {
    if (!isAdminAuthenticated || !itemDetails || itemDetails.item_type !== ContentItemType.WORKFLOW || itemDetails.team_id !== ADMIN_SYSTEM_TEAM_ID_STRING) {
      toast.error("This action is only for Admins running their own workflows.");
      return;
    }
    if (isDirty) {
      toast.error("Please save your changes before running the workflow.");
      return;
    }
    const workflowToRun = itemDetails as unknown as ContentItemListed; // Cast for modal
    setSelectedWorkflowForAdminRun(workflowToRun);
    setAdminRunInitialPayload({}); // No specific payload from here for admin test run
    setShowAdminRunWorkflowModal(true);
  }, [isAdminAuthenticated, itemDetails, isDirty]);


  const handleTriggerAskAI = async () => { // Renamed to avoid conflict with modal's internal handler
    if (!askAiQueryInput.trim()) {
        toast.error("Please enter a question or instruction for the AI.");
        return;
    }
    const contentForAI = editorContent;
    if (!contentForAI && !itemDetails?.markdown_content) {
        toast.error("There is no document content to ask AI about. Please type some content or load an existing document.");
        return;
    }
    setAskAiQueryToSubmit(askAiQueryInput); // Set the query to be submitted
    setShowAskAIResponseModal(true); // Open the modal, which will then trigger the stream
  };

  const handleSaveAskAIResponseAsNewDocument = async (documentName: string, contentToSave: string) => {
    if (!documentName.trim()) {
        toast.error("Document name cannot be empty.");
        return;
    }
    const toastId = `save-ai-response-${Date.now()}`;
    toast.loading("Saving AI response...", { id: toastId });

    try {
        if (isAdminAuthenticated) {
            toast.error("Admins currently cannot save AI responses as documents. Please copy the content manually.", {id: toastId, duration: 6000});
            setShowAskAIResponseModal(false); // Close modal even on admin "error"
            return;
        }
        if (!currentTeam?.team_id) {
            toast.error("Team context not found. Cannot save document.", { id: toastId });
            return;
        }

        const searchParams = { name_query: documentName.trim(), item_type: ContentItemType.DOCUMENT, limit: 1 };
        const existingDocs: PaginatedResponse<ContentItemListed> = await contentService.getItems(searchParams);

        let existingTeamDoc: ContentItemListed | undefined = undefined;
        if (existingDocs.items && existingDocs.items.length > 0) {
             existingTeamDoc = existingDocs.items.find(
                (doc) => doc.name.toLowerCase() === documentName.trim().toLowerCase() && doc.team_id === currentTeam?.team_id
            );
        }

        if (existingTeamDoc) {
            toast.loading(`Updating existing document "${existingTeamDoc.name}" with new version...`, { id: toastId });
            const versionPayload = { markdown_content: contentToSave };
            await contentService.saveNewVersion(existingTeamDoc.item_id, versionPayload);
            toast.success(`New version saved to document "${existingTeamDoc.name}"!`, { id: toastId });
            setShowAskAIResponseModal(false);
            setAskAiQueryInput(''); // Clear input query
            setAskAiQueryToSubmit('');
            navigate(`/app/documents/${existingTeamDoc.item_id}`);
        } else {
            toast.loading(`Creating new document "${documentName.trim()}"...`, { id: toastId });
            const createPayload: ContentItemCreatePayload = {
                name: documentName.trim(),
                item_type: ContentItemType.DOCUMENT,
            };
            const createdDocMeta = await contentService.createItem(createPayload);
            const versionPayload = { markdown_content: contentToSave };
            await contentService.saveNewVersion(createdDocMeta.item_id, versionPayload);
            toast.success(`Document "${createdDocMeta.name}" created successfully from AI response!`, { id: toastId });
            setShowAskAIResponseModal(false);
            setAskAiQueryInput(''); // Clear input query
            setAskAiQueryToSubmit('');
            navigate(`/app/documents/${createdDocMeta.item_id}`);
        }

    } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to save AI response as document.';
        toast.error(errorMessage, { id: toastId });
    }
  };


  const getTeamName = useCallback((teamId: string | null | undefined): string => {
    if (!teamId) return 'Unknown Team';
    if (teamId === ADMIN_SYSTEM_TEAM_ID_STRING) return 'ULACM System';
    if (currentTeam && teamId === currentTeam.team_id) return currentTeam.team_name;
    return teamDataCache[teamId] || `Team ID: ${teamId.substring(0, 8)}...`;
  }, [currentTeam, teamDataCache]);

  const getItemDisplayIcon = (type: ContentItemType | null) => {
    if (!type) return <FileText className="mr-2 text-ulacm-gray-400 flex-shrink-0" />;
    switch (type) {
      case ContentItemType.DOCUMENT: return <FileText className="mr-2 text-ulacm-primary flex-shrink-0" />;
      case ContentItemType.TEMPLATE: return <FileCode2 className="mr-2 text-green-600 flex-shrink-0" />;
      case ContentItemType.WORKFLOW: return <FolderGit2 className="mr-2 text-purple-600 flex-shrink-0" />;
      default: return <FileText className="mr-2 text-ulacm-gray-400 flex-shrink-0" />;
    }
  };

  const closeAdminRunWorkflowModal = useCallback(() => {
    setShowAdminRunWorkflowModal(false);
    setSelectedWorkflowForAdminRun(null);
    setAdminRunInitialPayload(undefined);
  }, []);

  const viewAdminRunWorkflowOutputDocument = useCallback((outputItemId: string) => {
    closeAdminRunWorkflowModal();
    navigate(`/app/documents/${outputItemId}`);
    toast(`Admin test run created document ID: ${outputItemId}. Navigating to view.`);
  }, [closeAdminRunWorkflowModal, navigate]);


  if (isLoading && !itemJustCreatedIdRef.current && !(location.state as any)?.isNewlyCreatedWithError) {
    return <div className="flex flex-col items-center justify-center h-full"><LoadingSpinner size="lg" /><p className="mt-2 text-ulacm-gray-600">Loading editor...</p></div>;
  }

  if (error && !itemDetails && !itemJustCreatedIdRef.current && !(location.state as any)?.isNewlyCreatedWithError) {
    return <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow max-w-2xl mx-auto my-8"><div className="flex"><div className="flex-shrink-0"><AlertCircle className="h-5 w-5 text-red-400" /></div><div className="ml-3"><p className="text-sm font-semibold text-red-800">Error</p><p className="mt-1 text-sm text-red-700">{error}</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-2 text-sm text-red-700 hover:text-red-900 underline block">Go to Dashboard</Link></div></div></div>;
  }

  if (isCreatingNewItem && !newItemType) {
    return <div className="text-center py-10"><AlertCircle size={48} className="mx-auto text-yellow-500 mb-4" /><h2 className="text-xl font-semibold text-ulacm-gray-700">Cannot Create Item</h2><p className="text-ulacm-gray-500 mt-2">Item type undetermined. Please use navigation links.</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-4 inline-block px-4 py-2 bg-ulacm-primary text-white rounded hover:bg-ulacm-primary-dark">Go to Dashboard</Link></div>;
  }
  if (!isCreatingNewItem && !itemDetails && !isLoading && !error) {
    return <div className="text-center py-10"><AlertCircle size={48} className="mx-auto text-yellow-500 mb-4" /><h2 className="text-xl font-semibold text-ulacm-gray-700">Item Not Found</h2><p className="text-ulacm-gray-500 mt-2">The requested item could not be loaded.</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-4 inline-block px-4 py-2 bg-ulacm-primary text-white rounded hover:bg-ulacm-primary-dark">Go to Dashboard</Link></div>;
  }

  const currentItemTypeForDisplay = itemDetails?.item_type || newItemType;
  const currentItemNameForDisplay = itemDetails?.name || newItemName;

  return (
    <div className="flex flex-col h-[calc(100vh-theme(space.24))]">
      <div className="flex-shrink-0 mb-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-3 bg-white p-4 rounded-lg shadow border border-ulacm-gray-100">
          <div className="flex-grow min-w-0">
            {isCreatingNewItem && !itemDetails ? (
              <div>
                <label htmlFor="newItemNameInput" className="sr-only">Item Name</label>
                <input
                  id="newItemNameInput" type="text" value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  placeholder={`Enter name for New ${currentItemTypeForDisplay}...`}
                  className="text-2xl font-bold text-ulacm-gray-800 border-b-2 border-transparent focus:border-ulacm-primary focus:outline-none w-full pb-1"
                  disabled={!canEditContent}
                />
                <p className="text-xs text-ulacm-gray-500 mt-1 flex items-center">
                  <Info size={14} className="mr-1"/>
                  {`Creating a new ${currentItemTypeForDisplay}. Save to create the first version.`}
                </p>
              </div>
            ) : (
              itemDetails && (
                <div>
                  <h1 className="text-2xl font-bold text-ulacm-gray-800 flex items-center truncate" title={itemDetails.name}>
                    {getItemDisplayIcon(itemDetails.item_type)}
                    <span className="truncate">{itemDetails.name}</span>
                  </h1>
                  <div className="text-xs text-ulacm-gray-500 mt-1.5 space-x-3 flex items-center flex-wrap">
                    <span className="flex items-center" title="Currently loaded version number">
                      <Settings size={12} className="mr-1"/> Version: v{loadedVersionNumber ?? itemDetails.current_version_number ?? 0}
                    </span>
                    <span className="flex items-center" title={`Saved at ${itemDetails.version_created_at ? format(new Date(itemDetails.version_created_at), 'PP p') : 'N/A'}`}>
                      <Clock size={12} className="mr-1"/>
                        Last Saved: {itemDetails.version_created_at ? formatDistanceToNow(new Date(itemDetails.version_created_at), { addSuffix: true }) : 'Never'}
                    </span>
                    {itemDetails.version_saved_by_team_id && (
                      <span className="flex items-center" title={`Team ID: ${itemDetails.version_saved_by_team_id}`}>
                        <User size={12} className="mr-1"/> Saved by: {getTeamName(itemDetails.version_saved_by_team_id)}
                      </span>
                    )}
                  </div>
                </div>
              )
            )}
          </div>
          <div className="flex items-center flex-wrap gap-2 flex-shrink-0 mt-2 sm:mt-0">
            <button
              onClick={handleSave}
              disabled={isSaving || (!isDirty && !isCreatingNewItem && !itemJustCreatedIdRef.current) || !canEditContent || (isCreatingNewItem && !newItemName.trim())}
              className="flex items-center bg-ulacm-primary hover:bg-ulacm-primary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <Save size={16} className="mr-1.5" /> {isSaving ? 'Saving...' : (isCreatingNewItem && !itemJustCreatedIdRef.current ? 'Create & Save' : 'Save Changes')}
            </button>
            {isAdminAuthenticated && itemDetails?.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING && (
              <button
                onClick={handleAdminRunWorkflow}
                disabled={isDirty || !canEditContent}
                className="flex items-center bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 disabled:opacity-50 text-sm"
                title={isDirty ? "Save changes before running workflow" : "Run Workflow (Admin Test)"}
              >
                <Play size={16} className="mr-1.5" /> Run Workflow
              </button>
            )}
          </div>
        </div>
        {error && (
           <div className="mt-3 bg-red-100 border-l-4 border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error: </strong>
                <span className="block sm:inline">{error}</span>
             </div>
        )}
      </div>

      { (itemDetails || (isCreatingNewItem && editorContent !== undefined)) && ( // Check editorContent is not undefined
        <div className="flex-shrink-0 my-4 p-4 bg-white rounded-lg shadow border border-ulacm-gray-100">
            <div className="flex items-center gap-3">
                <div className="flex-grow">
                    <label htmlFor="askAiInput" className="sr-only">Ask AI about this document</label>
                    <input
                        id="askAiInput"
                        type="text"
                        value={askAiQueryInput}
                        onChange={(e) => setAskAiQueryInput(e.target.value)}
                        placeholder="Ask AI a question or give an instruction about this document's current content..."
                        className="w-full px-3 py-2 border border-ulacm-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-ulacm-secondary/50 focus:border-ulacm-secondary transition duration-150"
                        // disabled={isAskingAI} // isAskingAI is now internal to modal
                    />
                </div>
                <button
                    onClick={handleTriggerAskAI}
                    disabled={!askAiQueryInput.trim()} // Disable if input is empty
                    className="flex items-center bg-ulacm-secondary hover:bg-ulacm-secondary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 disabled:opacity-60"
                >
                    <Brain size={18} className="mr-1.5" /> Ask AI
                </button>
            </div>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6 flex-grow min-h-0">
        <div className="flex-grow min-w-0 h-full">
          <ReactSimpleMDEEditor
            key={actualItemId || `new-${newItemType}`}
            value={editorContent}
            onChange={handleEditorChange}
            editable={Boolean(canEditContent)}
            placeholder={`Enter content for ${currentItemNameForDisplay || 'new item'}...`}
          />
        </div>

        {!isCreatingNewItem && itemDetails && (
          <aside className="lg:w-72 xl:w-80 flex-shrink-0 space-y-5">
            <div className="bg-white p-4 rounded-lg shadow border border-ulacm-gray-100 space-y-2.5">
              <h2 className="text-base font-semibold text-ulacm-gray-700 border-b pb-2 mb-3">Actions</h2>
              <div className="flex space-x-2">
                 <button onClick={() => { toast('Undo via editor (Ctrl/Cmd+Z)')}} disabled={!canEditContent} className="flex-1 flex items-center justify-center text-sm py-2 px-3 rounded-md border border-ulacm-gray-300 bg-white hover:bg-ulacm-gray-50 disabled:opacity-50" title="Undo (Editor)"><Undo size={16} className="mr-1" /> Undo</button>
                 <button onClick={() => { toast('Redo via editor (Ctrl/Cmd+Y)')}} disabled={!canEditContent} className="flex-1 flex items-center justify-center text-sm py-2 px-3 rounded-md border border-ulacm-gray-300 bg-white hover:bg-ulacm-gray-50 disabled:opacity-50" title="Redo (Editor)"><Redo size={16} className="mr-1" /> Redo</button>
              </div>
              {canPerformMetaActions && (
                <>
                  <button onClick={handleToggleVisibility} disabled={!canPerformMetaActions} className="w-full flex items-center text-sm py-2 px-3 rounded-md border border-ulacm-gray-300 bg-white hover:bg-ulacm-gray-50 disabled:opacity-50" title={itemDetails.is_globally_visible ? "Make Private" : "Make Globally Visible"}>
                    {itemDetails.is_globally_visible ? <><Eye size={16} className="mr-2"/> Make Private</> : <><Globe size={16} className="mr-2"/> Make Global</>}
                  </button>
                  <button onClick={handleDuplicate} disabled={!canPerformMetaActions} className="w-full flex items-center text-sm py-2 px-3 rounded-md border border-ulacm-gray-300 bg-white hover:bg-ulacm-gray-50 disabled:opacity-50" title="Duplicate Item"><Copy size={16} className="mr-2"/> Duplicate</button>
                  <button onClick={handleDelete} disabled={!canPerformMetaActions} className="w-full flex items-center text-sm py-2 px-3 rounded-md border border-red-300 bg-red-50 text-red-600 hover:bg-red-100 disabled:opacity-50" title="Delete Item"><Trash2 size={16} className="mr-2"/> Delete Item</button>
                </>
              )}
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-ulacm-gray-100">
              <h2 className="text-base font-semibold text-ulacm-gray-700 border-b pb-2 mb-3 flex items-center"><History size={16} className="mr-2"/> Version History</h2>
              {isLoadingHistory ? <div className="flex justify-center py-4"><LoadingSpinner size="sm" /></div> : (
                <ul className="space-y-1.5 max-h-64 overflow-y-auto text-sm pr-1">
                  {versionHistory.length > 0 ? versionHistory.map(version => (
                    <li key={version.version_id}>
                      <button
                        onClick={() => loadVersion(version.version_id)}
                        disabled={version.version_number === loadedVersionNumber}
                        className={`w-full text-left p-2 rounded transition-colors duration-100 ${version.version_number === loadedVersionNumber ? 'bg-ulacm-primary/10 font-semibold text-ulacm-primary cursor-default' : 'hover:bg-ulacm-gray-100 text-ulacm-gray-700'}`}
                        title={`Load Version ${version.version_number}. Saved: ${format(new Date(version.created_at), 'PP p')}`}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium">v{version.version_number}</span>
                          <span className="text-xs text-ulacm-gray-500" title={format(new Date(version.created_at), 'PPPP p')}>
                            {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                          </span>
                        </div>
                        <div className="text-xs text-ulacm-gray-500 mt-0.5 flex items-center" title={`Team ID: ${version.saved_by_team_id}`}>
                          <User size={10} className="mr-1 opacity-80"/> {getTeamName(version.saved_by_team_id)}
                        </div>
                      </button>
                    </li>
                  )) :  <p className="text-ulacm-gray-500 text-xs py-2 text-center italic">No version history available.</p>}
                </ul>
              )}
            </div>
          </aside>
        )}
         {isCreatingNewItem && !itemDetails && (
          <aside className="lg:w-72 xl:w-80 flex-shrink-0 space-y-5">
            <div className="bg-white p-4 rounded-lg shadow border border-ulacm-gray-100 space-y-3">
              <h2 className="text-base font-semibold text-ulacm-gray-700 border-b pb-2 mb-3 flex items-center"><Info size={16} className="mr-2"/> New {newItemType || 'Item'}</h2>
              <p className="text-sm text-ulacm-gray-600">Enter a name and content. Click "Create & Save" to save the first version.</p>
              <p className="text-sm text-ulacm-gray-600">Additional actions like version history and visibility settings will become available after the item is created.</p>
            </div>
          </aside>
        )}
      </div>

      {showDeleteModal && itemDetails && (
         <ConfirmationModal
          isOpen={showDeleteModal}
          title={`Delete ${itemDetails.item_type}: ${itemDetails.name}`}
          message={`Are you sure you want to permanently delete this ${itemDetails.item_type.toLowerCase()} "${itemDetails.name}"? This action will also delete all its versions and cannot be undone.`}
          onConfirm={confirmDelete}
          onCancel={() => setShowDeleteModal(false)}
          confirmButtonText="Delete"
          confirmButtonVariant="danger"
        />
      )}

      {selectedWorkflowForAdminRun && showAdminRunWorkflowModal && (
        <RunWorkflowModal
          isOpen={showAdminRunWorkflowModal}
          workflowToExecute={selectedWorkflowForAdminRun}
          initialPayload={adminRunInitialPayload}
          onClose={closeAdminRunWorkflowModal}
          onViewOutput={viewAdminRunWorkflowOutputDocument}
        />
      )}

      {showAskAIResponseModal && (
        <AskAIResponseModal
            isOpen={showAskAIResponseModal}
            onClose={() => {
                setShowAskAIResponseModal(false);
                setAskAiQueryToSubmit(''); // Clear the submitted query so modal doesn't re-trigger stream
            }}
            askAiQuery={askAiQueryToSubmit} // Pass the query that should trigger the stream
            currentEditorContent={editorContent}
            onSaveAsNewDocument={handleSaveAskAIResponseAsNewDocument}
            currentDocumentName={itemDetails?.name || newItemName || "Document"}
        />
      )}
    </div>
  );
};

export default EditorViewPage;
