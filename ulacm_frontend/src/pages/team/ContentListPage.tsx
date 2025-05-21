// File: ulacm_frontend/src/pages/team/ContentListPage.tsx
// Purpose: Page for listing items with enhanced filtering including content search.
// - For Teams: Primarily lists their Documents.
// - For Admins: Lists Templates or Workflows or Documents.
// Updated: Integrated new filtering for name, content, creation date, and global visibility.
// Fixed: Added robust date parsing and validation for display.

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  FileText, FileCode2, FolderGit2, PlusCircle, RefreshCw, AlertCircle,
  Eye, Globe, Edit3, Trash2, Copy, ChevronLeft, ChevronRight, Settings,
  Search as SearchIcon, X as ClearSearchIcon, ArrowDownUp, SortAsc, SortDesc, Filter as FilterIcon, MessageSquareText
} from 'lucide-react';
import toast from 'react-hot-toast';
import { formatDistanceToNow, format, isValid, parseISO } from 'date-fns';

import { ContentItemListed, ContentItemType, ContentItemDuplicatePayload } from '@/types/api';
import contentService, { GetItemsParams } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmationModal from '@/components/common/ConfirmationModal';
import CreateDocumentModal from '@/components/content/CreateDocumentModal';
import { useAuth } from '@/contexts/AuthContext';
import { ADMIN_SYSTEM_TEAM_ID_STRING } from '@/utils/constants';

type SortOption = 'name' | 'updated_at' | 'created_at' | 'item_type' | 'rank'; // Added rank
type SortOrder = 'asc' | 'desc';
type VisibilityFilterOption = "all" | "global" | "private";

const ContentListPage: React.FC = () => {
  const [items, setItems] = useState<ContentItemListed[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 15,
    total_count: 0,
  });
  const [itemTypeForPage, setItemTypeForPage] = useState<ContentItemType | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState<ContentItemListed | null>(null);
  const [showCreateDocModal, setShowCreateDocModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const location = useLocation();
  const navigate = useNavigate();
  const { currentTeam, isAdminAuthenticated } = useAuth();

  // Filtering State
  const [nameFilterInput, setNameFilterInput] = useState('');
  const [debouncedNameFilter, setDebouncedNameFilter] = useState('');
  const nameFilterInputRef = useRef<HTMLInputElement>(null);

  const [contentFilterInput, setContentFilterInput] = useState(''); // New state for content filter
  const [debouncedContentFilter, setDebouncedContentFilter] = useState(''); // New debounced state
  const contentFilterInputRef = useRef<HTMLInputElement>(null);


  const [dateAfterFilter, setDateAfterFilter] = useState('');
  const [dateBeforeFilter, setDateBeforeFilter] = useState('');
  const [visibilityFilter, setVisibilityFilter] = useState<VisibilityFilterOption>("all");

  const [sortBy, setSortBy] = useState<SortOption>('updated_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [showFilters, setShowFilters] = useState(false);

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
      setNameFilterInput('');
      setDebouncedNameFilter('');
      setContentFilterInput(''); // Reset content filter
      setDebouncedContentFilter(''); // Reset debounced content filter
      setDateAfterFilter('');
      setDateBeforeFilter('');
      setVisibilityFilter("all");
      setItems([]);
      setSortBy('updated_at'); // Reset sort on type change
      setSortOrder('desc');
    }
  }, [location.pathname, isAdminAuthenticated, itemTypeForPage]);

  useEffect(() => {
    const timerId = setTimeout(() => {
      setDebouncedNameFilter(nameFilterInput);
      setPagination(p => ({ ...p, offset: 0 })); // Reset pagination on filter change
    }, 500);
    return () => clearTimeout(timerId);
  }, [nameFilterInput]);

  useEffect(() => { // Debouncer for content filter
    const timerId = setTimeout(() => {
      setDebouncedContentFilter(contentFilterInput);
      setPagination(p => ({ ...p, offset: 0 })); // Reset pagination
    }, 500);
    return () => clearTimeout(timerId);
  }, [contentFilterInput]);


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

    // If content_query is active, default sort to 'rank' unless already name/date
    let currentSortBy = sortBy;
    let currentSortOrder = sortOrder;
    if (debouncedContentFilter.trim() && !['name', 'created_at', 'updated_at'].includes(sortBy)) {
        currentSortBy = 'rank';
        currentSortOrder = 'desc';
    }


    try {
      const params: GetItemsParams = {
        item_type: itemTypeForPage ?? undefined,
        offset,
        limit: pagination.limit,
        sort_by: currentSortBy, // Use potentially adjusted sort
        sort_order: currentSortOrder,
        name_query: debouncedNameFilter.trim() || undefined,
        content_query: debouncedContentFilter.trim() || undefined, // Add content query
        created_after: dateAfterFilter || undefined,
        created_before: dateBeforeFilter || undefined,
        is_globally_visible: visibilityFilter === "global" ? true : visibilityFilter === "private" ? false : undefined,
        for_usage: (itemTypeForPage === ContentItemType.TEMPLATE || itemTypeForPage === ContentItemType.WORKFLOW) && !isAdminAuthenticated ? true : undefined,
      };
      const data = await contentService.getItems(params);
      setItems(data.items);
      setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
    } catch (err: any) {
      console.error("Failed to fetch content items:", err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load items.';
      setError(errorMessage);
    } finally {
      if (showLoadingIndicator) setIsLoading(false);
    }
  // }, [itemTypeForPage, isAdminAuthenticated, location.pathname, pagination.limit, sortBy, sortOrder, debouncedNameFilter, dateAfterFilter, dateBeforeFilter, visibilityFilter]);
}, [itemTypeForPage, isAdminAuthenticated, location.pathname, pagination.limit, sortBy, sortOrder, debouncedNameFilter, debouncedContentFilter, dateAfterFilter, dateBeforeFilter, visibilityFilter]);


  useEffect(() => {
     if (itemTypeForPage || (isAdminAuthenticated && location.pathname.includes('/documents'))) {
        fetchItems(pagination.offset, true);
     }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.offset, itemTypeForPage, isAdminAuthenticated, location.pathname, debouncedNameFilter, debouncedContentFilter, sortBy, sortOrder, dateAfterFilter, dateBeforeFilter, visibilityFilter]);
  // Removed fetchItems from dep array as it's memoized with all its own dependencies

  const handleNewItemClick = () => {
    if (isAdminAuthenticated) {
        if (itemTypeForPage === ContentItemType.TEMPLATE) navigate('/admin/templates/new');
        else if (itemTypeForPage === ContentItemType.WORKFLOW) navigate('/admin/workflows/new');
        else if (itemTypeForPage === ContentItemType.DOCUMENT) toast.error("Admin document creation not directly supported here.");
        else toast.error("Select a content type section (Templates or Workflows) to create new admin content.");
    } else {
        if (itemTypeForPage === ContentItemType.DOCUMENT) setShowCreateDocModal(true);
        else toast.error("Teams can only create Documents.");
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
            case ContentItemType.DOCUMENT: return { title: 'Manage Knowledge', icon: FileText };
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
     if (newOffset >= 0 && (newOffset < pagination.total_count || pagination.total_count === 0) ) {
        setPagination(prev => ({ ...prev, offset: newOffset }));
     }
  };

  const handleDeleteItem = (item: ContentItemListed) => setShowDeleteModal(item);

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
       fetchItems(pagination.offset, false); // Refetch current page data
     } catch (err: any) {
       console.error(`Failed to delete ${itemToDelete.item_type}`, err);
       toast.error(err.message || `Failed to delete ${itemToDelete.item_type}.`);
     } finally {
        setActionLoading(prev => ({ ...prev, [itemToDelete.item_id]: false }));
     }
  };

  const handleDuplicateItem = (item: ContentItemListed) => {
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

  const totalPages = Math.max(1, Math.ceil(pagination.total_count / pagination.limit));
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const { title: pageTitle, icon: PageIcon } = getPageTitleAndIcon;

  const getEditPath = (item: ContentItemListed) => {
    const typePath = item.item_type.toLowerCase() + 's';
    if (isAdminAuthenticated) {
        if (item.item_type === ContentItemType.TEMPLATE || item.item_type === ContentItemType.WORKFLOW) {
            return `/admin/${typePath}/${item.item_id}`;
        } else if (item.item_type === ContentItemType.DOCUMENT) {
            return `/app/${typePath}/${item.item_id}`; // Admin might view/edit Documents via team path
        }
    } else {
        if (item.item_type === ContentItemType.DOCUMENT) {
            return `/app/${typePath}/${item.item_id}`;
        }
    }
    return '#'; // Fallback, should not happen for accessible items
  };

  const canEditItem = (item: ContentItemListed): boolean => {
    if (isAdminAuthenticated) {
        return (item.item_type === ContentItemType.TEMPLATE && item.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
               (item.item_type === ContentItemType.WORKFLOW && item.team_id === ADMIN_SYSTEM_TEAM_ID_STRING) ||
               item.item_type === ContentItemType.DOCUMENT; // Admin can edit metadata of any doc
    }
    return item.item_type === ContentItemType.DOCUMENT && item.team_id === currentTeam?.team_id;
  };
  const canDeleteItem = (item: ContentItemListed): boolean => canEditItem(item);

  const handleSortChange = (newSortBy: SortOption) => {
    if (sortBy === newSortBy) {
      setSortOrder(prevOrder => (prevOrder === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(newSortBy);
      setSortOrder('asc'); // Default to asc when changing column, or 'desc' if it's 'rank'
      if (newSortBy === 'rank') setSortOrder('desc');
    }
    setPagination(p => ({ ...p, offset: 0 }));
  };

  const renderSortIcon = (column: SortOption) => {
    if (sortBy !== column) return <ArrowDownUp size={14} className="ml-1 text-ulacm-gray-400" />;
    return sortOrder === 'asc' ? <SortAsc size={14} className="ml-1 text-ulacm-primary" /> : <SortDesc size={14} className="ml-1 text-ulacm-primary" />;
  };

  const handleClearFilters = () => {
    setNameFilterInput('');
    setDebouncedNameFilter('');
    setContentFilterInput('');
    setDebouncedContentFilter('');
    setDateAfterFilter('');
    setDateBeforeFilter('');
    setVisibilityFilter("all");
    setSortBy('updated_at'); // Reset sort
    setSortOrder('desc');
    setPagination(p => ({ ...p, offset: 0 })); // This will trigger fetchItems
  };

  const formatDateSafe = (dateString: string | undefined | null, formatToken: string): string => {
    if (!dateString) return 'N/A';
    try {
        const parsedDate = parseISO(dateString);
        if (isValid(parsedDate)) {
            if (formatToken === 'relative') {
                return formatDistanceToNow(parsedDate, { addSuffix: true });
            }
            return format(parsedDate, formatToken);
        }
    } catch (e) {
        console.warn(`Error parsing date string: ${dateString}`, e);
    }
    return 'Invalid date';
  };

  const getLocaleStringSafe = (dateString: string | undefined | null): string => {
    if (!dateString) return 'N/A';
    try {
        const parsedDate = parseISO(dateString);
        if (isValid(parsedDate)) {
            return parsedDate.toLocaleString();
        }
    } catch (e) {
        console.warn(`Error parsing date string for toLocaleString: ${dateString}`, e);
    }
    return 'Invalid date';
  }


  if (!itemTypeForPage && !error && !(isAdminAuthenticated && location.pathname.includes('/documents'))) {
    if (isAdminAuthenticated && (location.pathname.startsWith("/admin/templates") || location.pathname.startsWith("/admin/workflows"))) {
      return <div className="flex justify-center items-center py-20"><LoadingSpinner size="lg" /></div>;
    } else if (!isAdminAuthenticated && location.pathname.startsWith("/app/documents")) {
      return <div className="flex justify-center items-center py-20"><LoadingSpinner size="lg" /></div>;
    }
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

      <div className="bg-white p-4 rounded-xl shadow-lg border border-ulacm-gray-100 space-y-4">
        <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-ulacm-gray-700 flex items-center">
                <FilterIcon size={20} className="mr-2 text-ulacm-primary" /> Filters
            </h2>
            <button
                onClick={() => setShowFilters(!showFilters)}
                className="text-sm text-ulacm-primary hover:text-ulacm-primary-dark font-medium"
            >
                {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
        </div>

        {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-3 border-t border-ulacm-gray-200">
                <div>
                    <label htmlFor="nameFilter" className="block text-xs font-medium text-ulacm-gray-600 mb-1">Filter by Name</label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <SearchIcon className="h-4 w-4 text-ulacm-gray-400" />
                        </div>
                        <input
                            ref={nameFilterInputRef}
                            type="search"
                            id="nameFilter"
                            value={nameFilterInput}
                            onChange={(e) => setNameFilterInput(e.target.value)}
                            className="block w-full pl-9 pr-3 py-2 border border-ulacm-gray-300 rounded-md text-sm placeholder-ulacm-gray-400 focus:outline-none focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary"
                            placeholder="Enter name..."
                        />
                    </div>
                </div>
                 <div>
                    <label htmlFor="contentFilter" className="block text-xs font-medium text-ulacm-gray-600 mb-1">Filter by Content</label>
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <MessageSquareText className="h-4 w-4 text-ulacm-gray-400" />
                        </div>
                        <input
                            ref={contentFilterInputRef}
                            type="search"
                            id="contentFilter"
                            value={contentFilterInput}
                            onChange={(e) => setContentFilterInput(e.target.value)}
                            className="block w-full pl-9 pr-3 py-2 border border-ulacm-gray-300 rounded-md text-sm placeholder-ulacm-gray-400 focus:outline-none focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary"
                            placeholder="Enter content keywords..."
                        />
                    </div>
                </div>
                <div>
                    <label htmlFor="dateAfterFilter" className="block text-xs font-medium text-ulacm-gray-600 mb-1">Created After</label>
                    <input
                        type="date"
                        id="dateAfterFilter"
                        value={dateAfterFilter}
                        onChange={(e) => { setDateAfterFilter(e.target.value); setPagination(p => ({ ...p, offset: 0 }));}}
                        className="block w-full py-2 px-3 border border-ulacm-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary"
                    />
                </div>
                <div>
                    <label htmlFor="dateBeforeFilter" className="block text-xs font-medium text-ulacm-gray-600 mb-1">Created Before</label>
                    <input
                        type="date"
                        id="dateBeforeFilter"
                        value={dateBeforeFilter}
                        onChange={(e) => { setDateBeforeFilter(e.target.value); setPagination(p => ({ ...p, offset: 0 }));}}
                        className="block w-full py-2 px-3 border border-ulacm-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary"
                    />
                </div>
                <div>
                    <label htmlFor="visibilityFilter" className="block text-xs font-medium text-ulacm-gray-600 mb-1">Visibility</label>
                    <select
                        id="visibilityFilter"
                        value={visibilityFilter}
                        onChange={(e) => { setVisibilityFilter(e.target.value as VisibilityFilterOption); setPagination(p => ({ ...p, offset: 0 }));}}
                        className="block w-full py-2 px-3 border border-ulacm-gray-300 bg-white rounded-md shadow-sm text-sm focus:outline-none focus:ring-1 focus:ring-ulacm-primary focus:border-ulacm-primary"
                    >
                        <option value="all">All</option>
                        <option value="global">Global</option>
                        <option value="private">Private</option>
                    </select>
                </div>
                <div className="md:col-span-1 lg:col-span-1 flex items-end">
                    <button
                        onClick={handleClearFilters}
                        className="w-full text-sm py-2 px-4 rounded-md border border-ulacm-gray-300 bg-white hover:bg-ulacm-gray-50 text-ulacm-gray-700 flex items-center justify-center"
                    >
                        <ClearSearchIcon size={16} className="mr-1.5" /> Clear All Filters
                    </button>
                </div>
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
            <div className="flex-shrink-0"><AlertCircle className="h-5 w-5 text-red-400" /></div>
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
                        Last Updated {renderSortIcon('updated_at')}
                      </button>
                    </th>
                     <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">
                       <button onClick={() => handleSortChange('created_at')} className="flex items-center hover:text-ulacm-primary">
                        Created {renderSortIcon('created_at')}
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

                    const displayDateTitle = `Item updated at ${getLocaleStringSafe(item.updated_at)}`;
                    const createdDateTitle = `Item created at ${getLocaleStringSafe(item.created_at)}`;

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
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600" title={displayDateTitle}>
                            {formatDateSafe(item.updated_at, 'relative')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600" title={createdDateTitle}>
                            {formatDateSafe(item.created_at, 'PP')}
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
                    {debouncedNameFilter || debouncedContentFilter || dateAfterFilter || dateBeforeFilter || visibilityFilter !== "all" ? (
                        <>
                            <SearchIcon size={48} className="mx-auto text-ulacm-gray-300"/>
                            <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No items match your filters</h3>
                            <p className="mt-1 text-sm text-ulacm-gray-500">Try adjusting your filter criteria or clearing them.</p>
                        </>
                    ) : (
                        <>
                             {PageIcon && <PageIcon size={48} className="mx-auto text-ulacm-gray-300"/>}
                            <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No {pageTitle.toLowerCase()} found</h3>
                            <p className="mt-1 text-sm text-ulacm-gray-500">Get started by creating a new one.</p>
                        </>
                    )}
                    {((isAdminAuthenticated && (itemTypeForPage === ContentItemType.TEMPLATE || itemTypeForPage === ContentItemType.WORKFLOW)) ||
                     (!isAdminAuthenticated && itemTypeForPage === ContentItemType.DOCUMENT)) && !(debouncedNameFilter || debouncedContentFilter || dateAfterFilter || dateBeforeFilter || visibilityFilter !== "all") && (
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
