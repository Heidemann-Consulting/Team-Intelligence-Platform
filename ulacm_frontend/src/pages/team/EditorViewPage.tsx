// File: ULACM2/ulacm_frontend/src/pages/team/EditorViewPage.tsx
// Purpose: Page for viewing and editing a specific content item.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  Save, Trash2, Copy, Eye, Globe, History, Undo, Redo, Settings, FileText, FileCode2, FolderGit2, AlertCircle, Info, Clock, User, Play
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

import { ContentItemDetail, ContentItemType, RunWorkflowResponse, ContentItemDuplicatePayload } from '@/types/api';
import { VersionMeta } from '@/types/content';
import contentService, { ContentItemCreatePayload } from '@/services/contentService';
import { useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmationModal from '@/components/common/ConfirmationModal';
import ReactSimpleMDEEditor from '@/components/content/ReactSimpleMDEEditor';
import RunWorkflowModal from '@/components/content/RunWorkflowModal';
import { ADMIN_SYSTEM_TEAM_ID_STRING } from '@/utils/constants';

const EditorViewPage: React.FC = () => {
  const { itemId: routeItemId } = useParams<{ itemId?: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { currentTeam, isAdminAuthenticated } = useAuth();

  const pathSegments = location.pathname.split('/');
  // Determine item type segment based on whether the user is admin or team user
  // Admin path: /admin/templates/:itemId -> segments[2] is 'templates'
  // Team path:  /app/documents/:itemId   -> segments[2] is 'documents'
  const itemTypeSegment = isAdminAuthenticated ? pathSegments[2] : pathSegments[2];

  const isCreatingNewItem = location.pathname.endsWith('/new');
  const actualItemId = isCreatingNewItem ? undefined : routeItemId;

  // State hooks
  const [itemDetails, setItemDetails] = useState<ContentItemDetail | null>(null);
  const [newItemType, setNewItemType] = useState<ContentItemType | null>(null); // For /new route, derived from path
  const [editorItemType, setEditorItemType] = useState<ContentItemType | null>(null); // Actual type being edited, from itemDetails or newItemType
  const [newItemName, setNewItemName] = useState<string>(''); // For /new route
  const [editorContent, setEditorContent] = useState<string>('');
  const [isDirty, setIsDirty] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [versionHistory, setVersionHistory] = useState<VersionMeta[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRunWorkflowModal, setShowRunWorkflowModal] = useState(false);
  const [workflowOutput, setWorkflowOutput] = useState<RunWorkflowResponse | { error: string } | null>(null);

  const [isRunningWorkflow, setIsRunningWorkflow] = useState(false); // Added state for workflow running
  const [loadedVersionNumber, setLoadedVersionNumber] = useState<number | null>(null);

  // Cache for team names to avoid repeated fetches if ever needed, though not actively used for fetching here
  const [teamDataCache] = useState<Record<string, string>>({});

  const lastSavedContentRef = useRef<string>('');
  const itemJustCreatedIdRef = useRef<string | null>(null); // Used if creating an item leads to an error during first version save

  // Permissions
  const isOwner = itemDetails && currentTeam && itemDetails.team_id === currentTeam.team_id;

  // Determine if the current user can edit the content
  const canEditContent = isCreatingNewItem || // Always true if creating a new item (permissions checked during save)
                         (isAdminAuthenticated && itemDetails && // Admin editing specific types
                            ((itemDetails.item_type === ContentItemType.TEMPLATE && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                             (itemDetails.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                             (itemDetails.item_type === ContentItemType.DOCUMENT))) || // Admin can edit any document's content
                         (!isAdminAuthenticated && itemDetails && itemDetails.item_type === ContentItemType.DOCUMENT && isOwner); // Team user editing their own document

  // Determine if the current user can perform metadata actions (visibility, delete, duplicate)
  const canPerformMetaActions = isCreatingNewItem ? false : // No meta actions for unsaved new items
                                (isAdminAuthenticated && itemDetails && // Admin meta actions
                                    ((itemDetails.item_type === ContentItemType.TEMPLATE && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                                     (itemDetails.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
                                     (itemDetails.item_type === ContentItemType.DOCUMENT))) || // Admin can change meta for any document
                                (!isAdminAuthenticated && itemDetails && itemDetails.item_type === ContentItemType.DOCUMENT && isOwner); // Team user meta actions for their own document


  // Load item details if an itemId is present
  const loadItemDetails = useCallback(async (idToLoad: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const details = await contentService.getItemDetails(idToLoad);
      setItemDetails(details);
      setEditorItemType(details.item_type); // Set editor type from loaded details
      const initialContentForEditor = details.markdown_content ?? '';
      setEditorContent(initialContentForEditor);
      lastSavedContentRef.current = initialContentForEditor;
      setLoadedVersionNumber(details.current_version_number ?? null);
      setIsDirty(false);
      itemJustCreatedIdRef.current = null; // Clear this if we successfully load an existing item
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
  }, [isAdminAuthenticated, navigate]); // Dependencies for loadItemDetails

  // Effect to initialize component based on route (new or existing item)
  useEffect(() => {
    let typeFromPath: ContentItemType | null = null;
    if (itemTypeSegment === 'documents') typeFromPath = ContentItemType.DOCUMENT;
    else if (itemTypeSegment === 'templates') typeFromPath = ContentItemType.TEMPLATE;
    else if (itemTypeSegment === 'workflows') typeFromPath = ContentItemType.WORKFLOW;

    setEditorItemType(typeFromPath); // Set editor type based on path

    if (isCreatingNewItem) {
      setIsLoading(true); // Start loading
      setNewItemType(typeFromPath);

      // Permissions checks for new items
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
        // This case should ideally be prevented by UI (e.g., no direct "/new" link for team documents)
        // Team users create documents via a modal that requires a template.
        setError("New documents must be created from a template via the 'New Document' button on the Documents page.");
        toast.error("Please use the 'New Document' button.");
        navigate('/app/documents', { replace: true });
        setIsLoading(false);
        return;
      }

      // Set default content and name for new items
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
        defaultContent = `inputDocumentSelector: "Input_Doc_*" # Glob pattern for document names
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

      setItemDetails(null); // No existing details for new item
      setNewItemName(defaultName);
      setEditorContent(defaultContent);
      lastSavedContentRef.current = defaultContent; // Treat default content as "saved" initially for new items
      setIsDirty(false); // Not dirty initially for new items
      setError(null);
      setLoadedVersionNumber(null);
      setIsLoading(false); // Done "loading" new item setup
    } else if (actualItemId && actualItemId !== "undefined") {
      setNewItemType(null); // Not creating a new item type
      loadItemDetails(actualItemId);
    } else {
      // Handle cases where itemId might be the literal string "undefined" or missing
      setIsLoading(false);
      setError(routeItemId === "undefined" ? "Invalid item ID in URL: received 'undefined' string." : "Invalid or missing item ID in URL.");
    }
  }, [isCreatingNewItem, actualItemId, itemTypeSegment, location.pathname, isAdminAuthenticated, navigate, loadItemDetails, routeItemId]);

  // Load version history for existing items
  const loadVersionHistory = useCallback(async () => {
    if (isCreatingNewItem || !actualItemId || actualItemId === itemJustCreatedIdRef.current || !itemDetails) {
      // No history for new items, or if item ID is temporary from a failed create, or itemDetails not loaded
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
  }, [actualItemId, isCreatingNewItem, itemDetails]); // itemDetails dependency ensures we only load history for existing, loaded items

  useEffect(() => {
    if (!isCreatingNewItem && actualItemId && itemDetails) {
      loadVersionHistory();
    } else {
      setVersionHistory([]); // Clear history for new or unloaded items
    }
  }, [actualItemId, isCreatingNewItem, loadVersionHistory, itemDetails]);


  // Handle editor content changes
  const handleEditorChange = useCallback((markdownContent: string) => {
    setEditorContent(markdownContent);
    setIsDirty(markdownContent !== lastSavedContentRef.current);
  }, []); // No dependencies, relies on current state values


  // Handle saving content (new item or new version)
  const handleSave = async () => {
    if (!canEditContent) {
        toast.error("You do not have permission to save this item.");
        return;
    }
    setIsSaving(true);
    setError(null);
    const currentContent = editorContent;
    // Use a more robust toast ID generation
    const toastIdPrefix = isCreatingNewItem && !itemJustCreatedIdRef.current ? (newItemName || 'new-item').trim() : (actualItemId || itemDetails?.item_id || 'existing-item');
    const toastId = `save-${toastIdPrefix}-${Date.now()}`; // Add timestamp for uniqueness

    if (isCreatingNewItem && !itemJustCreatedIdRef.current) { // Truly new item creation
      const typeToCreate = newItemType || editorItemType; // newItemType should be set
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
        // Step 1: Create the ContentItem metadata
        const createPayload: ContentItemCreatePayload = { name: newItemName.trim(), item_type: typeToCreate };
        // For Documents by teams, template_id would be handled by CreateDocumentModal, not here.
        // For Admin creating Templates/Workflows, no template_id is needed.
        const createdItemMeta = await contentService.createItem(createPayload);
        itemJustCreatedIdRef.current = createdItemMeta.item_id; // Store the ID temporarily

        // Step 2: Save the first version with content
        const versionPayload = { markdown_content: currentContent };
        // Use the new item's ID for saving the version
        await contentService.saveNewVersion(createdItemMeta.item_id, versionPayload);

        toast.success(`${typeToCreate} "${createdItemMeta.name}" created successfully!`, { id: toastId });
        itemJustCreatedIdRef.current = null; // Clear temporary ID
        // Navigate to the edit page of the newly created item
        const basePath = isAdminAuthenticated ? '/admin' : '/app';
        navigate(`${basePath}/${typeToCreate.toLowerCase()}s/${createdItemMeta.item_id}`, { replace: true });
      } catch (err: any) {
        const apiErrorDetail = err.response?.data?.detail || err.message;
        let userFriendlyError = `Failed to create ${typeToCreate}: ${apiErrorDetail}`;
        // If item metadata was created but version save failed (e.g., workflow validation error)
        if (itemJustCreatedIdRef.current && typeToCreate === ContentItemType.WORKFLOW && err.response?.status === 400) {
             userFriendlyError = `Error in ${typeToCreate} content: ${apiErrorDetail || 'Invalid YAML syntax.'} The item metadata for '${newItemName}' was created. Please correct the content; you are now editing this item.`;
             // Navigate to the edit page of the partially created item
             navigate(`/admin/workflows/${itemJustCreatedIdRef.current}`, { replace: true, state: { initialContent: currentContent, isNewlyCreatedWithError: true, specificError: userFriendlyError } });
        } else {
            itemJustCreatedIdRef.current = null; // Clear if full creation failed
        }
        setError(userFriendlyError);
        toast.error(userFriendlyError, { id: toastId, duration: 8000 });
      } finally {
        setIsSaving(false);
      }
    } else { // Saving an existing item or a newly created item that had a version save error
      const idToSave = itemJustCreatedIdRef.current || actualItemId; // Use temp ID if it exists (from failed first save)
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

        if (itemJustCreatedIdRef.current) { // This was a save after a failed initial version save
            toast.success(`Item "${itemDetails?.name || newItemName}" content saved!`, { id: toastId });
            itemJustCreatedIdRef.current = null; // Clear the temporary ID

            // Ensure we are on the correct edit page, not /new
            const currentBasePath = isAdminAuthenticated ? '/admin' : '/app';
            const itemTypePathSegment = (itemDetails?.item_type || editorItemType || newItemType )!.toLowerCase() + 's';
            // If we were on /new or a special error state, navigate to the proper edit URL
            if (location.pathname.endsWith('/new') || (location.state as any)?.isNewlyCreatedWithError) {
                 navigate(`${currentBasePath}/${itemTypePathSegment}/${idToSave}`, { replace: true });
            } else {
                loadItemDetails(idToSave); // Reload details if already on edit page
            }
        } else if (itemDetails) { // Standard save for an existing item
            setItemDetails(prev => prev ? {
              ...prev,
              current_version_number: result.new_version.version_number,
              updated_at: result.item_updated_at,
              markdown_content: result.new_version.markdown_content, // Keep detail in sync
              version_created_at: result.new_version.created_at,
              version_saved_by_team_id: result.new_version.saved_by_team_id
            } : null);
            setEditorContent(result.new_version.markdown_content); // Update editor with saved content
            lastSavedContentRef.current = result.new_version.markdown_content;
            setLoadedVersionNumber(result.new_version.version_number);
            setIsDirty(false);
            toast.success('Saved successfully!', { id: toastId });
            loadVersionHistory(); // Refresh version history
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

  // Effect to handle loading initial content after a partially failed creation (e.g. workflow YAML error on first save)
  useEffect(() => {
    if ((location.state as any)?.isNewlyCreatedWithError && actualItemId) {
      if ((location.state as any)?.initialContent) {
        setEditorContent((location.state as any).initialContent);
        lastSavedContentRef.current = ""; // Force dirty state to encourage re-save
        setIsDirty(true);
      }
      setError((location.state as any)?.specificError || "Please review content and save again.");
      // Clear the state to prevent re-triggering
      const currentBasePath = isAdminAuthenticated ? '/admin' : '/app';
      const itemTypePathSegment = (editorItemType)!.toLowerCase() + 's'; // editorItemType should be set by now
      navigate(`${currentBasePath}/${itemTypePathSegment}/${actualItemId}`, { replace: true, state: {} });
    }
  }, [location.state, actualItemId, navigate, isAdminAuthenticated, editorItemType]);


  // Load a specific version's content into the editor
  const loadVersion = useCallback(async (versionId: string) => {
    const currentActualItemId = itemJustCreatedIdRef.current || actualItemId; // Use temporary ID if it exists
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
      // Update the itemDetails to reflect the loaded version's metadata (if itemDetails exists)
      if(itemDetails) {
        setItemDetails(prev => prev ? {
          ...prev,
          // Note: current_version_number on itemDetails might differ from loadedVersionNumber
          // if the user is browsing history. The main item still points to its "current".
          // We update display fields based on the specific version loaded.
          version_created_at: versionDetails.created_at, // Displaying this version's save time
          version_saved_by_team_id: versionDetails.saved_by_team_id, // And this version's saver
        } : null);
      }
      toast.success(`Loaded version ${versionDetails.version_number}.`, { id: toastId });
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to load version content.';
      toast.error(msg, { id: toastId });
    }
  }, [actualItemId, isDirty, itemDetails, canEditContent]); // Removed loadItemDetails dependency as it caused loops

  // Toggle item visibility (global/private)
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

  // Initiate item deletion
  const handleDelete = () => {
    if (canPerformMetaActions && itemDetails && !itemJustCreatedIdRef.current) {
      setShowDeleteModal(true);
    } else {
      toast.error("Cannot delete this item or item not saved yet.");
    }
  };

  // Confirm and execute item deletion
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

  // Handle item duplication
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
      // Prioritize the currently loaded version in the editor for duplication if it's a specific historical one
      if (loadedVersionNumber && versionHistory.find(v => v.version_number === loadedVersionNumber)) {
        versionToDuplicateId = versionHistory.find(v => v.version_number === loadedVersionNumber)?.version_id;
      } else if (itemDetails.current_version_id) { // Otherwise, use the item's actual current version
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


  // Handle running a workflow (Admin test execution of their own workflows)
  const handleRunWorkflow = useCallback(async () => { // For Admin test running their own workflows
    if (!isAdminAuthenticated || !itemDetails || itemDetails.item_type !== ContentItemType.WORKFLOW || itemDetails.team_id !== ADMIN_SYSTEM_TEAM_ID_STRING) {
      toast.error("This action is only for Admins running their own workflows.");
      return;
    }
    if (isDirty) {
      toast.error("Please save your changes before running the workflow.");
      return;
    }
    setShowRunWorkflowModal(true);
    setIsRunningWorkflow(true);
    setWorkflowOutput(null);
    try {
      const result = await contentService.runWorkflow(itemDetails.item_id);
      setWorkflowOutput(result);
      toast.success(`Workflow "${itemDetails.name}" executed (Admin Test).`);
    } catch (err: any) {
      const msg = err.message || "Workflow execution failed (Admin Test).";
      setWorkflowOutput({ error: msg });
      toast.error(msg);
    } finally {
      setIsRunningWorkflow(false);
    }
  }, [isAdminAuthenticated, itemDetails, isDirty]);


  // Helper to get team name for display
  const getTeamName = useCallback((teamId: string | null | undefined): string => {
    if (!teamId) return 'Unknown Team';
    if (teamId === ADMIN_SYSTEM_TEAM_ID_STRING) return 'ULACM System';
    if (currentTeam && teamId === currentTeam.team_id) return currentTeam.team_name;
    // Basic caching or placeholder for other team IDs, not critical for this page's primary user (owner/admin)
    return teamDataCache[teamId] || `Team ID: ${teamId.substring(0, 8)}...`;
  }, [currentTeam, teamDataCache]);

  // Helper to get item icon based on type
  const getItemDisplayIcon = (type: ContentItemType | null) => {
    if (!type) return <FileText className="mr-2 text-ulacm-gray-400 flex-shrink-0" />;
    switch (type) {
      case ContentItemType.DOCUMENT: return <FileText className="mr-2 text-ulacm-primary flex-shrink-0" />;
      case ContentItemType.TEMPLATE: return <FileCode2 className="mr-2 text-green-600 flex-shrink-0" />;
      case ContentItemType.WORKFLOW: return <FolderGit2 className="mr-2 text-purple-600 flex-shrink-0" />;
      default: return <FileText className="mr-2 text-ulacm-gray-400 flex-shrink-0" />;
    }
  };

  // Callbacks for workflow modal
  const closeWorkflowModal = useCallback(() => { setShowRunWorkflowModal(false); setWorkflowOutput(null); }, []);

  const viewWorkflowOutputDocument = useCallback((outputItemId: string) => {
    closeWorkflowModal();
    // This navigation is tricky for Admin-run workflows as their output is system-owned.
    // For now, just toast the ID. A proper admin view for any document might be needed.
    toast(`Admin test output document ID: ${outputItemId}. View via admin tools if applicable or if a general document viewer exists.`);
    // Example: navigate(`/app/documents/${outputItemId}`); // If admin can view team docs
  }, [closeWorkflowModal, navigate]);


  // Loading and error states rendering
  if (isLoading && !itemJustCreatedIdRef.current && !(location.state as any)?.isNewlyCreatedWithError) {
    return <div className="flex flex-col items-center justify-center h-full"><LoadingSpinner size="lg" /><p className="mt-2 text-ulacm-gray-600">Loading editor...</p></div>;
  }

  // If there's an error and no item details are loaded (and not in a post-creation error state)
  if (error && !itemDetails && !itemJustCreatedIdRef.current && !(location.state as any)?.isNewlyCreatedWithError) {
    return <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow max-w-2xl mx-auto my-8"><div className="flex"><div className="flex-shrink-0"><AlertCircle className="h-5 w-5 text-red-400" /></div><div className="ml-3"><p className="text-sm font-semibold text-red-800">Error</p><p className="mt-1 text-sm text-red-700">{error}</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-2 text-sm text-red-700 hover:text-red-900 underline block">Go to Dashboard</Link></div></div></div>;
  }

  // If creating new but item type couldn't be determined
  if (isCreatingNewItem && !newItemType) {
    return <div className="text-center py-10"><AlertCircle size={48} className="mx-auto text-yellow-500 mb-4" /><h2 className="text-xl font-semibold text-ulacm-gray-700">Cannot Create Item</h2><p className="text-ulacm-gray-500 mt-2">Item type undetermined. Please use navigation links.</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-4 inline-block px-4 py-2 bg-ulacm-primary text-white rounded hover:bg-ulacm-primary-dark">Go to Dashboard</Link></div>;
  }
  // If not creating, not loading, no error, but still no itemDetails (e.g., item ID was valid format but not found)
  if (!isCreatingNewItem && !itemDetails && !isLoading && !error) {
    // This implies item ID was provided, but loading failed or item not found, and not in initial loading state.
    return <div className="text-center py-10"><AlertCircle size={48} className="mx-auto text-yellow-500 mb-4" /><h2 className="text-xl font-semibold text-ulacm-gray-700">Item Not Found</h2><p className="text-ulacm-gray-500 mt-2">The requested item could not be loaded.</p><Link to={isAdminAuthenticated ? "/admin/dashboard" : "/app/dashboard"} className="mt-4 inline-block px-4 py-2 bg-ulacm-primary text-white rounded hover:bg-ulacm-primary-dark">Go to Dashboard</Link></div>;
  }

  const currentItemTypeForDisplay = itemDetails?.item_type || newItemType;
  const currentItemNameForDisplay = itemDetails?.name || newItemName;

  return (
    <div className="flex flex-col h-[calc(100vh-theme(space.24))]"> {/* Adjusted for typical header/padding */}
      {/* Header Section: Item Name, Info, Save Button */}
      <div className="flex-shrink-0 mb-4">
        <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-3 bg-white p-4 rounded-lg shadow border border-ulacm-gray-100">
          {/* Item Name and Info */}
          <div className="flex-grow min-w-0">
            {isCreatingNewItem && !itemDetails ? ( // Display input for new item name
              <div>
                <label htmlFor="newItemNameInput" className="sr-only">Item Name</label>
                <input
                  id="newItemNameInput" type="text" value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  placeholder={`Enter name for New ${currentItemTypeForDisplay}...`}
                  className="text-2xl font-bold text-ulacm-gray-800 border-b-2 border-transparent focus:border-ulacm-primary focus:outline-none w-full pb-1"
                  disabled={!canEditContent} // Should always be editable if creating
                />
                <p className="text-xs text-ulacm-gray-500 mt-1 flex items-center">
                  <Info size={14} className="mr-1"/>
                  {`Creating a new ${currentItemTypeForDisplay}. Save to create the first version.`}
                </p>
              </div>
            ) : ( // Display existing item details
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
          {/* Action Buttons */}
          <div className="flex items-center flex-wrap gap-2 flex-shrink-0 mt-2 sm:mt-0">
            <button
              onClick={handleSave}
              disabled={isSaving || (!isDirty && !isCreatingNewItem && !itemJustCreatedIdRef.current) || !canEditContent || (isCreatingNewItem && !newItemName.trim())}
              className="flex items-center bg-ulacm-primary hover:bg-ulacm-primary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              <Save size={16} className="mr-1.5" /> {isSaving ? 'Saving...' : (isCreatingNewItem && !itemJustCreatedIdRef.current ? 'Create & Save' : 'Save Changes')}
            </button>
            {/* Run Workflow button only for Admin viewing an Admin-owned workflow */}
            {isAdminAuthenticated && itemDetails?.item_type === ContentItemType.WORKFLOW && itemDetails.team_id === ADMIN_SYSTEM_TEAM_ID_STRING && (
              <button
                onClick={handleRunWorkflow}
                disabled={isRunningWorkflow || isDirty || !canEditContent} // Ensure canEditContent (proxy for ownership/admin rights for workflow)
                className="flex items-center bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 disabled:opacity-50 text-sm"
                title={isDirty ? "Save changes before running workflow" : "Run Workflow (Admin Test)"}
              >
                <Play size={16} className="mr-1.5" /> Run Workflow
              </button>
            )}
          </div>
        </div>
        {/* General Error Display */}
        {error && ( // Display general errors here, not just loading errors
             <div className="mt-3 bg-red-100 border-l-4 border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <strong className="font-bold">Error: </strong>
                <span className="block sm:inline">{error}</span>
             </div>
        )}
      </div>

      {/* Main Editor and Sidebar Area */}
      <div className="flex flex-col lg:flex-row gap-6 flex-grow min-h-0">
        {/* Editor Area */}
        <div className="flex-grow min-w-0 h-full">
          <ReactSimpleMDEEditor
            key={actualItemId || `new-${newItemType}`} // Ensure re-keying if item changes
            value={editorContent}
            onChange={handleEditorChange}
            editable={Boolean(canEditContent)} // Ensure this is a boolean
            placeholder={`Enter content for ${currentItemNameForDisplay || 'new item'}...`}
          />
        </div>

        {/* Sidebar for existing items */}
        {!isCreatingNewItem && itemDetails && (
          <aside className="lg:w-72 xl:w-80 flex-shrink-0 space-y-5">
            {/* Actions Panel */}
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
            {/* Version History Panel */}
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
         {isCreatingNewItem && !itemDetails && ( // Sidebar for new items before first save
          <aside className="lg:w-72 xl:w-80 flex-shrink-0 space-y-5">
            <div className="bg-white p-4 rounded-lg shadow border border-ulacm-gray-100 space-y-3">
              <h2 className="text-base font-semibold text-ulacm-gray-700 border-b pb-2 mb-3 flex items-center"><Info size={16} className="mr-2"/> New {newItemType || 'Item'}</h2>
              <p className="text-sm text-ulacm-gray-600">Enter a name and content. Click "Create & Save" to save the first version.</p>
              <p className="text-sm text-ulacm-gray-600">Additional actions like version history and visibility settings will become available after the item is created.</p>
            </div>
          </aside>
        )}
      </div>

      {/* Modals */}
      {showDeleteModal && itemDetails && ( // Ensure itemDetails exists for modal context
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
      {showRunWorkflowModal && itemDetails && ( // Ensure itemDetails exists for workflowName
        <RunWorkflowModal
          isOpen={showRunWorkflowModal}
          workflowName={itemDetails.name}
          isLoading={isRunningWorkflow}
          output={workflowOutput}
          onClose={closeWorkflowModal}
          onViewOutput={viewWorkflowOutputDocument} // This will be called with output_document.item_id
        />
      )}
    </div>
  );
};

export default EditorViewPage;
