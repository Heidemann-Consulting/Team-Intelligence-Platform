// File: ulacm_frontend/src/pages/team/ContentListPage.tsx
// Purpose: Page for listing items.
// - For Teams: Primarily lists their Documents.
// - For Admins: Lists Templates or Workflows (owned by ADMIN_SYSTEM_TEAM_ID) or Documents.

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  FileText, FileCode2, FolderGit2, PlusCircle, RefreshCw, AlertCircle,
  Eye, Globe, Edit3, Trash2, Copy, ChevronLeft, ChevronRight, Settings,
  Search as SearchIcon, X as ClearSearchIcon, ArrowDownUp, SortAsc, SortDesc
} from 'lucide-react';
import toast from 'react-hot-toast';
import { formatDistanceToNow, format } from 'date-fns';

import { ContentItemListed, ContentItemType, ContentItemDuplicatePayload, ContentItemSearchResult } from '@/types/api'; // Use ContentItemListed
import contentService, { SearchParams } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmationModal from '@/components/common/ConfirmationModal';
import CreateDocumentModal from '@/components/content/CreateDocumentModal';
import { useAuth } from '@/contexts/AuthContext';
import { ADMIN_SYSTEM_TEAM_ID_STRING } from '@/utils/constants';

const highlightStyle = `
  .search-highlight {
    background-color: #fef08a; /* yellow-200 */
    padding: 0.1em 0.1em;
    margin: 0 -0.1em;
    border-radius: 0.2em;
    font-style: normal;
    font-weight: 600; /* Semibold */
  }
`;

type SortOption = 'name' | 'updated_at'; // updated_at for item maps to latest version date
type SortOrder = 'asc' | 'desc';

const ContentListPage: React.FC = () => {
  const [items, setItems] = useState<(ContentItemListed | ContentItemSearchResult)[]>([]); // Can hold both types
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 15,
    total_count: 0,
  });
  const [itemTypeForPage, setItemTypeForPage] = useState<ContentItemType | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState<ContentItemListed | ContentItemSearchResult | null>(null);
  const [showCreateDocModal, setShowCreateDocModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const location = useLocation();
  const navigate = useNavigate();
  const { currentTeam, isAdminAuthenticated } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [sortBy, setSortBy] = useState<SortOption>('updated_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');


  useEffect(() => {
    const pathSegments = location.pathname.split('/');
    const typeSegmentIndex = isAdminAuthenticated ? 2 : 2;
    const typeSegment = pathSegments[typeSegmentIndex];

    let type: ContentItemType | null = null;
    if (typeSegment === 'documents') type = ContentItemType.DOCUMENT;
    else if (typeSegment === 'templates' && isAdminAuthenticated) type = ContentItemType.TEMPLATE;
    else if (typeSegment === 'workflows' && isAdminAuthenticated) type = ContentItemType.WORKFLOW;

    if (itemTypeForPage !== type) {
      setItemTypeForPage(type);
      setPagination(p => ({ ...p, offset: 0 }));
      setSearchQuery(''); // Reset search on type change
      setDebouncedSearchQuery('');
      setItems([]);
    }
  }, [location.pathname, isAdminAuthenticated, itemTypeForPage]);

  // Debounce search query
  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setPagination(p => ({ ...p, offset: 0 })); // Reset pagination on new search
    }, 500);
    return () => clearTimeout(timerId);
  }, [searchQuery]);


  const fetchItems = useCallback(async (offset = 0, showLoadingIndicator = true) => {
    if (!itemTypeForPage && !isAdminAuthenticated) {
        setError("No content type specified for listing.");
        if (showLoadingIndicator) setIsLoading(false);
        return;
    }
    if (!itemTypeForPage && isAdminAuthenticated && !location.pathname.endsWith('/documents')) {
      if (showLoadingIndicator) setIsLoading(false);
      return;
    }

    if (showLoadingIndicator) setIsLoading(true);
    setError(null);

    try {
      const effectiveItemType = itemTypeForPage; // Use itemTypeForPage for filtering if not searching
                                                 // or if search should be constrained to the current page type.

      if (debouncedSearchQuery.trim()) {
        // Perform search
        const searchParams: SearchParams = {
          query: debouncedSearchQuery.trim(),
          item_types: effectiveItemType ? effectiveItemType : undefined, // Search within current type or all if no type context
          offset,
          limit: pagination.limit,
          sort_by: sortBy, // Add sort to search
          sort_order: sortOrder,
        };
        const data = await contentService.searchItems(searchParams);
        setItems(data.items);
        setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
      } else {
        // Perform regular listing
        const listParams: Parameters<typeof contentService.getItems>[0] = {
          item_type: effectiveItemType ?? undefined, // Handle null case properly
          offset,
          limit: pagination.limit,
          sort_by: sortBy,
          sort_order: sortOrder,
        };
        const data = await contentService.getItems(listParams);
        setItems(data.items);
        setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
      }
    } catch (err: any) {
      console.error("Failed to fetch content items:", err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load items.';
      setError(errorMessage);
    } finally {
      if (showLoadingIndicator) setIsLoading(false);
    }
  }, [itemTypeForPage, isAdminAuthenticated, location.pathname, pagination.limit, debouncedSearchQuery, sortBy, sortOrder]);

  useEffect(() => {
     if (itemTypeForPage || (isAdminAuthenticated && location.pathname.includes('/documents'))) {
        fetchItems(pagination.offset, true); // Show full loading indicator on initial load or type change
     }
  }, [fetchItems, pagination.offset, itemTypeForPage, isAdminAuthenticated, location.pathname, debouncedSearchQuery, sortBy, sortOrder]);


  const handleNewItemClick = () => {
    if (isAdminAuthenticated) {
        if (itemTypeForPage === ContentItemType.TEMPLATE) {
            navigate('/admin/templates/new');
        } else if (itemTypeForPage === ContentItemType.WORKFLOW) {
            navigate('/admin/workflows/new');
        } else if (itemTypeForPage === ContentItemType.DOCUMENT) {
            toast.error("Admin document creation not directly supported here. Manage team documents or system templates/workflows.");
        } else {
            toast.error("Select a content type section (Templates or Workflows) to create new admin content.");
        }
    } else {
        if (itemTypeForPage === ContentItemType.DOCUMENT) {
            setShowCreateDocModal(true);
        } else {
            toast.error("Teams can only create Documents. Templates and Workflows are managed by Admins.");
        }
    }
  };

  const getPageTitleAndIcon = useMemo(() => {
    if (isAdminAuthenticated) {
        switch (itemTypeForPage) {
            case ContentItemType.TEMPLATE: return { title: 'Template Management', icon: FileCode2 };
            case ContentItemType.WORKFLOW: return { title: 'Workflow Management', icon: FolderGit2 };
            case ContentItemType.DOCUMENT: return { title: 'All Documents (Admin View)', icon: FileText };
            default: return { title: 'Manage Content', icon: Settings };
        }
    } else {
        switch (itemTypeForPage) {
            case ContentItemType.DOCUMENT: return { title: 'My Documents', icon: FileText };
            default: return { title: 'Content', icon: FileText };
        }
    }
  }, [itemTypeForPage, isAdminAuthenticated]);

  const getItemDisplayIcon = (type: ContentItemType) => {
     switch (type) {
      case ContentItemType.DOCUMENT: return <FileText className="h-5 w-5 mr-2 text-ulacm-primary flex-shrink-0" />;
      case ContentItemType.TEMPLATE: return <FileCode2 className="h-5 w-5 mr-2 text-green-600 flex-shrink-0" />;
      case ContentItemType.WORKFLOW: return <FolderGit2 className="h-5 w-5 mr-2 text-purple-600 flex-shrink-0" />;
      default: return <FileText className="h-5 w-5 mr-2 text-ulacm-gray-500 flex-shrink-0" />;
    }
  };

  const handlePageChange = (newOffset: number) => {
     if (newOffset >= 0 && newOffset < pagination.total_count) {
        setPagination(prev => ({ ...prev, offset: newOffset }));
        // Fetch will be triggered by useEffect watching pagination.offset
     }
  };

  const handleDeleteItem = (item: ContentItemListed | ContentItemSearchResult) => {
    setShowDeleteModal(item);
  };

  const confirmDeleteItem = async () => {
     if (!showDeleteModal) return;
     const itemToDelete = showDeleteModal;
     const toastId = `delete-${itemToDelete.item_id}`;
     setShowDeleteModal(null);
     setActionLoading(prev => ({ ...prev, [itemToDelete.item_id]: true }));
     toast.loading(`Deleting ${itemToDelete.item_type} "${itemToDelete.name}"...`, { id: toastId });
     try {
       await contentService.deleteItem(itemToDelete.item_id);
       toast.success(`${itemToDelete.item_type} "${itemToDelete.name}" deleted.`, { id: toastId });
       // Re-fetch items for the current page after deletion
       fetchItems(pagination.offset, false); // false to avoid full page loading indicator
     } catch (err: any) {
       console.error(`Failed to delete ${itemToDelete.item_type}`, err);
       toast.error(err.message || `Failed to delete ${itemToDelete.item_type}.`);
     } finally {
        setActionLoading(prev => ({ ...prev, [itemToDelete.item_id]: false }));
     }
  };

  const handleDuplicateItem = (item: ContentItemListed | ContentItemSearchResult) => {
      const newName = prompt(`Enter a name for the duplicated ${item.item_type}:`, `Copy of ${item.name}`);
      if (newName) {
          setActionLoading(prev => ({ ...prev, [item.item_id]: true }));
          const duplicatePayload: ContentItemDuplicatePayload = { new_name: newName };
          toast.promise(
              contentService.duplicateItem(item.item_id, duplicatePayload),
              {
                  loading: `Duplicating ${item.item_type}...`,
                  success: (duplicatedItem) => {
                      const basePath = isAdminAuthenticated ? '/admin' : '/app';
                      navigate(`${basePath}/${duplicatedItem.item_type.toLowerCase()}s/${duplicatedItem.item_id}`);
                      return `Duplicated as "${duplicatedItem.name}".`;
                  },
                  error: (err) => err.message || `Failed to duplicate ${item.item_type}.`,
              }
          ).finally(() => setActionLoading(prev => ({ ...prev, [item.item_id]: false })));
      }
  };

  const totalPages = Math.ceil(pagination.total_count / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const { title: pageTitle, icon: PageIcon } = getPageTitleAndIcon;

  const getEditPath = (item: ContentItemListed | ContentItemSearchResult) => {
    const typePath = item.item_type.toLowerCase() + 's';
    if (isAdminAuthenticated) {
        if (item.item_type === ContentItemType.TEMPLATE || item.item_type === ContentItemType.WORKFLOW) {
            return `/admin/${typePath}/${item.item_id}`;
        } else if (item.item_type === ContentItemType.DOCUMENT) {
            return `/app/${typePath}/${item.item_id}`; // Admins view documents in team context
        }
    } else {
        if (item.item_type === ContentItemType.DOCUMENT) {
            return `/app/${typePath}/${item.item_id}`;
        }
    }
    return '#'; // Should not happen for accessible items
  };

  const canEditItem = (item: ContentItemListed | ContentItemSearchResult): boolean => {
    if (isAdminAuthenticated) {
        return (item.item_type === ContentItemType.TEMPLATE && item.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
               (item.item_type === ContentItemType.WORKFLOW && item.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
               item.item_type === ContentItemType.DOCUMENT; // Admin can view/potentially edit metadata of any document
    }
    return item.item_type === ContentItemType.DOCUMENT && item.team_id === currentTeam?.team_id;
  };

  const canDeleteItem = (item: ContentItemListed | ContentItemSearchResult): boolean => {
    return canEditItem(item); // Same logic for now
  };

  const handleSortChange = (newSortBy: SortOption) => {
    if (sortBy === newSortBy) {
      setSortOrder(prevOrder => (prevOrder === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc'); // Default to ascending when changing column
    }
    setPagination(p => ({ ...p, offset: 0 })); // Reset to first page on sort change
  };

  const renderSortIcon = (column: SortOption) => {
    if (sortBy !== column) return <ArrowDownUp size={14} className="ml-1 text-ulacm-gray-400" />;
    return sortOrder === 'asc' ? <SortAsc size={14} className="ml-1 text-ulacm-primary" /> : <SortDesc size={14} className="ml-1 text-ulacm-primary" />;
  };


  if (!itemTypeForPage && !error && !(isAdminAuthenticated && location.pathname.includes('/documents'))) {
    if (isAdminAuthenticated && (location.pathname.startsWith("/admin/templates") || location.pathname.startsWith("/admin/workflows"))) {
      return <div className="flex justify-center items-center py-20"><LoadingSpinner size="lg" /></div>;
    } else if (!isAdminAuthenticated && location.pathname.startsWith("/app/documents")) {
      return <div className="flex justify-center items-center py-20"><LoadingSpinner size="lg" /></div>;
    }
    // If no specific type is determined and not an admin viewing all documents, show an error or guidance.
    return (
        <div className="text-center py-10">
            <AlertCircle size={48} className="mx-auto text-yellow-500 mb-4" />
            <h2 className="text-xl font-semibold text-ulacm-gray-700">Content Type Not Specified</h2>
            <p className="text-ulacm-gray-500 mt-2">Please navigate using the sidebar links.</p>
        </div>
    );
  }


  return (
    <div className="space-y-6">
      <style>{highlightStyle}</style> {/* Inject highlight styles */}
      <div className="flex flex-col gap-4 md:flex-row justify-between md:items-center">
        <h1 className="text-3xl font-bold text-ulacm-gray-800 flex items-center">
            {PageIcon && <PageIcon size={30} className="mr-3 text-ulacm-primary"/>} {pageTitle}
        </h1>
        <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
          <button
             onClick={() => fetchItems(pagination.offset)}
             disabled={isLoading}
            className="p-2.5 text-ulacm-gray-500 hover:text-ulacm-primary hover:bg-ulacm-gray-100 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-primary/50"
            title="Refresh List"
          >
            <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
          </button>
          {((isAdminAuthenticated && (itemTypeForPage === ContentItemType.TEMPLATE || itemTypeForPage === ContentItemType.WORKFLOW)) ||
           (!isAdminAuthenticated && itemTypeForPage === ContentItemType.DOCUMENT)) && (
            <button
                onClick={handleNewItemClick}
                disabled={isLoading}
                className="flex items-center bg-ulacm-primary hover:bg-ulacm-primary-dark focus:bg-ulacm-primary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-primary focus:ring-offset-1"
                title={`Create New ${itemTypeForPage}`}
              >
                <PlusCircle className="mr-1.5 h-5 w-5" /> New {itemTypeForPage}
              </button>
          )}
        </div>
      </div>

      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 text-ulacm-gray-400" aria-hidden="true" />
        </div>
        <input
          ref={searchInputRef}
          type="search"
          name="search"
          id="search"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="block w-full pl-10 pr-10 py-2 border border-ulacm-gray-300 rounded-md leading-5 bg-white placeholder-ulacm-gray-500 focus:outline-none focus:placeholder-ulacm-gray-400 focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary sm:text-sm shadow-sm"
          placeholder={`Search ${pageTitle.toLowerCase()}...`}
        />
        {searchQuery && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              onClick={() => { setSearchQuery(''); searchInputRef.current?.focus(); }}
              className="text-ulacm-gray-400 hover:text-ulacm-gray-600"
              title="Clear search"
            >
              <ClearSearchIcon className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>


      {isLoading && items.length === 0 && (
           <div className="flex justify-center items-center py-20 bg-white rounded-xl shadow-md border border-ulacm-gray-100">
              <LoadingSpinner size="lg" color="text-ulacm-primary" />
              <p className="ml-3 text-ulacm-gray-600">Loading {pageTitle.toLowerCase()}...</p>
          </div>
      )}

      {error && !isLoading && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Failed to Load {pageTitle}</h3>
              <div className="mt-2 text-sm text-red-700"><p>{error}</p></div>
               <div className="mt-4">
                  <button onClick={() => fetchItems(0)} className="text-sm font-medium text-red-800 hover:text-red-600 underline">
                    Try again
                  </button>
               </div>
            </div>
          </div>
        </div>
      )}

      {!error && (!isLoading || items.length > 0) && (
        <>
          <div className="bg-white shadow-xl rounded-xl overflow-hidden border border-ulacm-gray-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-ulacm-gray-200">
                <thead className="bg-ulacm-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">
                      <button onClick={() => handleSortChange('name')} className="flex items-center hover:text-ulacm-primary">
                        Name {renderSortIcon('name')}
                      </button>
                    </th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Visibility</th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Version</th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">
                       <button onClick={() => handleSortChange('updated_at')} className="flex items-center hover:text-ulacm-primary">
                        Last Updated / Version Date {renderSortIcon('updated_at')}
                      </button>
                    </th>
                    <th scope="col" className="relative px-6 py-3.5"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ulacm-gray-200 bg-white">
                  {items.map((item) => {
                    const editPath = getEditPath(item);
                    const itemCanBeEdited = canEditItem(item);
                    const itemCanBeDeleted = canDeleteItem(item);

                    // Use version_created_at if available (from ContentItemListed), otherwise item's updated_at (from ContentItemSearchResult)
                    const displayDate = item.version_created_at || item.updated_at;
                    const displayDateTitle = item.version_created_at ?
                                             `Version created at ${new Date(item.version_created_at).toLocaleString()}` :
                                             `Item updated at ${new Date(item.updated_at).toLocaleString()}`;


                    return (
                        <tr key={item.item_id} className={`hover:bg-ulacm-gray-50 transition-opacity duration-150 ${actionLoading[item.item_id] ? 'opacity-60' : ''}`}>
                         <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-ulacm-gray-900 max-w-xs truncate">
                           <Link to={editPath} className="group inline-flex items-center hover:text-ulacm-primary" title={item.name}>
                            {getItemDisplayIcon(item.item_type)}
                            <span className="group-hover:underline truncate">{item.name}</span>
                            </Link>
                          </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600">
                             {item.is_globally_visible ?
                             (<span title="Globally Visible" className="inline-flex items-center text-blue-600"><Globe size={16} className="mr-1"/> Global</span>)
                            : (<span title="Private to Owner" className="inline-flex items-center text-ulacm-gray-500"><Eye size={16} className="mr-1"/> Private</span>)
                            }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600">
                             v{item.current_version_number ?? 0}
                             {item.version_created_at && (
                                <span className="ml-1 text-ulacm-gray-400 text-xs" title={`Version created: ${format(new Date(item.version_created_at), 'PP p')}`}>
                                    ({format(new Date(item.version_created_at), 'MMM d, yyyy')})
                                </span>
                             )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600" title={displayDateTitle}>
                            {formatDistanceToNow(new Date(displayDate), { addSuffix: true })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-1">
                            <Link to={editPath} title={itemCanBeEdited ? "View / Edit" : "View"} className={`inline-flex items-center justify-center h-8 w-8 rounded-md transition-colors ${itemCanBeEdited ? 'text-ulacm-primary hover:text-ulacm-primary-dark hover:bg-ulacm-primary/10' : 'text-ulacm-gray-400 cursor-not-allowed'}`}>
                                <span className="sr-only">{itemCanBeEdited ? "Edit" : "View"}</span>
                                <Edit3 size={16} />
                            </Link>
                            <button
                                onClick={() => handleDuplicateItem(item)}
                                disabled={actionLoading[item.item_id]}
                                title="Duplicate Item"
                                className="inline-flex items-center justify-center h-8 w-8 text-purple-600 hover:text-purple-700 hover:bg-purple-500/10 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <span className="sr-only">Duplicate</span>
                                {actionLoading[item.item_id] && !showDeleteModal ? <LoadingSpinner size="sm" color="text-purple-600" /> : <Copy size={16} />}
                            </button>
                            <button
                                onClick={() => handleDeleteItem(item)}
                                disabled={!itemCanBeDeleted || actionLoading[item.item_id]}
                                title={!itemCanBeDeleted ? "Cannot delete (not owner/admin)" : "Delete Item"}
                                className={`inline-flex items-center justify-center h-8 w-8 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                                    itemCanBeDeleted ? 'text-red-600 hover:text-red-700 hover:bg-red-500/10' : 'text-ulacm-gray-400'
                                }`}
                            >
                                <span className="sr-only">Delete</span>
                                {actionLoading[item.item_id] && showDeleteModal?.item_id === item.item_id ? <LoadingSpinner size="sm" color="text-red-600" /> : <Trash2 size={16} />}
                            </button>
                        </td>
                        </tr>
                      );
                   })}
                </tbody>
              </table>
              {items.length === 0 && !isLoading && (
                <div className="text-center py-12 px-6">
                    {debouncedSearchQuery ? (
                        <>
                            <SearchIcon size={48} className="mx-auto text-ulacm-gray-300"/>
                            <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No results found for "{debouncedSearchQuery}"</h3>
                            <p className="mt-1 text-sm text-ulacm-gray-500">Try adjusting your search query.</p>
                        </>
                    ) : (
                        <>
                             {PageIcon && <PageIcon size={48} className="mx-auto text-ulacm-gray-300"/>}
                            <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No {pageTitle.toLowerCase()} found</h3>
                            <p className="mt-1 text-sm text-ulacm-gray-500">Get started by creating a new one.</p>
                        </>
                    )}
                    {((isAdminAuthenticated && (itemTypeForPage === ContentItemType.TEMPLATE || itemTypeForPage === ContentItemType.WORKFLOW)) ||
                     (!isAdminAuthenticated && itemTypeForPage === ContentItemType.DOCUMENT)) && !debouncedSearchQuery && (
                        <div className="mt-6">
                            <button
                                onClick={handleNewItemClick}
                                className="inline-flex items-center bg-ulacm-primary hover:bg-ulacm-primary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150"
                            >
                                <PlusCircle className="mr-2 h-5 w-5" /> New {itemTypeForPage}
                            </button>
                        </div>
                    )}
                </div>
              )}
            </div>
          </div>
          {pagination.total_count > pagination.limit && (
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between text-sm text-ulacm-gray-600">
              <div>
                Showing <span className="font-semibold">{pagination.offset + 1}</span> to <span className="font-semibold">{Math.min(pagination.offset + pagination.limit, pagination.total_count)}</span> of <span className="font-semibold">{pagination.total_count}</span> items
              </div>
              <div className="flex items-center space-x-2 mt-3 sm:mt-0">
                  <button
                    onClick={() => handlePageChange(pagination.offset - pagination.limit)}
                    disabled={currentPage === 1 || isLoading}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-ulacm-gray-600 bg-white border border-ulacm-gray-300 rounded-md hover:bg-ulacm-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft size={16} className="mr-1"/> Previous
                  </button>
                  <span>Page {currentPage} of {totalPages}</span>
                  <button
                    onClick={() => handlePageChange(pagination.offset + pagination.limit)}
                    disabled={currentPage === totalPages || isLoading}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-ulacm-gray-600 bg-white border border-ulacm-gray-300 rounded-md hover:bg-ulacm-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                     Next <ChevronRight size={16} className="ml-1"/>
                  </button>
              </div>
            </div>
          )}
        </>
      )}

       {showDeleteModal && (
        <ConfirmationModal
          isOpen={!!showDeleteModal}
          title={`Delete ${showDeleteModal.item_type}: ${showDeleteModal.name}`}
          message={`Are you sure you want to permanently delete the ${showDeleteModal.item_type.toLowerCase()} "${showDeleteModal.name}"? This action will also delete all its versions and cannot be undone.`}
          onConfirm={confirmDeleteItem}
          onCancel={() => setShowDeleteModal(null)}
          confirmButtonText={`Yes, Delete ${showDeleteModal.item_type}`}
          confirmButtonVariant="danger"
        />
      )}
      {!isAdminAuthenticated && itemTypeForPage === ContentItemType.DOCUMENT && (
           <CreateDocumentModal
            isOpen={showCreateDocModal}
            onClose={() => setShowCreateDocModal(false)}
            onSuccess={(newDocument) => {
              setShowCreateDocModal(false);
              navigate(`/app/documents/${newDocument.item_id}`);
            }}
          />
      )}
    </div>
  );
};

export default ContentListPage;
