// File: ulacm_frontend/src/pages/team/SearchPage.tsx
// Purpose: Page for searching content items.
// Updated to render the snippet using dangerouslySetInnerHTML and add basic highlight styling.
// Refined useEffect and performSearch to ensure pagination resets correctly for new searches.
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, X, FileText, FileCode2, FolderGit2, AlertCircle, ChevronLeft, ChevronRight, Loader } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
// import toast from 'react-hot-toast';
import { ContentItemSearchResult, ContentItemType, PaginatedResponse } from '@/types/api';
import contentService, { SearchParams } from '@/services/contentService';
import LoadingSpinner from '@/components/common/LoadingSpinner';

// Add basic CSS for highlighting - this should ideally be in a global CSS file or styled component
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

const SearchPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [itemTypes, setItemTypes] = useState<ContentItemType[]>([]);
  const [results, setResults] = useState<ContentItemSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 10,
    total_count: 0,
  });
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Debounce search query
  useEffect(() => {
    setIsTyping(true);
    const handler = setTimeout(() => {
      setDebouncedQuery(searchQuery);
      // When debouncedQuery changes, it will trigger the main search useEffect,
      // which should handle resetting pagination offset for a *new* search.
      setIsTyping(false);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [searchQuery]);

  const performSearch = useCallback(async (fetchOffset = 0) => {
    const currentQuery = debouncedQuery.trim();
    const currentTypes = itemTypes;

    if (!currentQuery && currentTypes.length === 0) {
      setResults([]);
      setPagination(prev => ({ ...prev, total_count: 0, offset: 0 }));
      setHasSearched(false);
      setIsLoading(false);
      return;
    }

    setHasSearched(true);
    setIsLoading(true);
    setError(null);

    try {
      const params: SearchParams = {
        query: currentQuery || undefined,
        item_types: currentTypes.length > 0 ? currentTypes.join(',') : undefined,
        offset: fetchOffset,
        limit: pagination.limit,
      };
      const data: PaginatedResponse<ContentItemSearchResult> = await contentService.searchItems(params);
      setResults(data.items);
      // Update pagination state with the offset used for this fetch and the new total_count
      setPagination(prev => ({ ...prev, offset: fetchOffset, total_count: data.total_count }));
    } catch (err: any) {
      console.error("Search failed:", err);
      const errorMessage = err.message || 'Failed to perform search.';
      setError(errorMessage);
      setResults([]); // Clear results on error
      setPagination(prev => ({ ...prev, total_count: 0, offset: fetchOffset })); // Reset total_count but keep offset
    } finally {
      setIsLoading(false);
    }
  }, [debouncedQuery, itemTypes, pagination.limit]); // pagination.limit is a stable dependency for performSearch

  // Effect to trigger new search when debouncedQuery or itemTypes change
  useEffect(() => {
    // Only perform search if user is not typing and there's something to search for
    // or if filters are applied.
    // This always performs a new search from offset 0.
    if (!isTyping) {
        if (debouncedQuery.trim() || itemTypes.length > 0) {
            performSearch(0); // Perform new search from page 1 (offset 0)
        } else {
            // If query and types are cleared, reset everything
            setResults([]);
            setPagination(prev => ({ ...prev, total_count: 0, offset: 0 }));
            setHasSearched(false);
        }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, itemTypes, isTyping]); // performSearch is memoized, safe to include if its own deps are correct


  const handleItemTypeChange = (type: ContentItemType) => {
    setItemTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
    // The change in itemTypes will trigger the useEffect above, which calls performSearch(0).
  };

  const clearFilters = () => {
    setItemTypes([]);
    // The change in itemTypes will trigger the useEffect above.
  };

  const handlePageChange = (newOffset: number) => {
    // This is for navigating pages of an existing result set.
    // The total_count for this check should be the one from the current result set.
    if (newOffset >= 0 && (newOffset < pagination.total_count || pagination.total_count === 0)) {
        performSearch(newOffset); // Fetch specific page
    }
  };

  const getItemIcon = (type: ContentItemType) => {
     switch (type) {
      case ContentItemType.DOCUMENT: return <FileText className="h-5 w-5 mr-2 text-ulacm-primary flex-shrink-0" />;
      case ContentItemType.TEMPLATE: return <FileCode2 className="h-5 w-5 mr-2 text-green-600 flex-shrink-0" />;
      case ContentItemType.WORKFLOW: return <FolderGit2 className="h-5 w-5 mr-2 text-purple-600 flex-shrink-0" />;
      default: return <FileText className="h-5 w-5 mr-2 text-ulacm-gray-500 flex-shrink-0" />;
    }
  };

  const totalPages = Math.max(1, Math.ceil(pagination.total_count / pagination.limit));
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="space-y-6">
       <style>{highlightStyle}</style>

      <h1 className="text-3xl font-bold text-ulacm-gray-800 flex items-center">
          <Search size={30} className="mr-3 text-ulacm-primary"/> Search Content
      </h1>

      <div className="bg-white p-4 rounded-xl shadow-lg border border-ulacm-gray-100 space-y-4">
        <div className="relative">
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name or content..."
            className="w-full pl-10 pr-4 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out"
          />
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-ulacm-gray-400 pointer-events-none">
             {isTyping || isLoading ? <Loader size={20} className="animate-spin"/> : <Search size={20} />}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <span className="text-sm font-medium text-ulacm-gray-600 flex items-center shrink-0"><Filter size={16} className="mr-1"/> Type:</span>
          <div className="flex flex-wrap gap-2">
            {Object.values(ContentItemType).map((type) => (
             <button
                key={type}
                onClick={() => handleItemTypeChange(type)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors duration-150 ${
                    itemTypes.includes(type)
                    ? 'bg-ulacm-primary border-ulacm-primary text-white font-medium shadow-sm'
                    : 'bg-white border-ulacm-gray-300 text-ulacm-gray-600 hover:bg-ulacm-gray-50 hover:border-ulacm-gray-400'
                }`}
                >
                {type}
             </button>
             ))}
          </div>
          {itemTypes.length > 0 && (
             <button
                onClick={clearFilters}
                className="text-xs text-ulacm-gray-500 hover:text-red-600 flex items-center ml-auto shrink-0"
                title="Clear type filters"
             >
                <X size={14} className="mr-0.5"/> Clear
             </button>
          )}
        </div>
      </div>

      <div className="space-y-4 min-h-[300px]">
        {isLoading && (
            <div className="flex flex-col items-center justify-center text-center py-16">
                <LoadingSpinner size="md" />
                <p className="mt-3 text-ulacm-gray-600">Searching...</p>
            </div>
        )}

        {error && !isLoading && (
           <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md shadow">
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-5 w-5 text-yellow-400" aria-hidden="true" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">Search Error</h3>
                  <p className="mt-1 text-sm text-yellow-700">{error}</p>
                </div>
              </div>
            </div>
        )}

        {!isLoading && !error && hasSearched && (
          <>
            <p className="text-sm text-ulacm-gray-600">
              Found {pagination.total_count} result{pagination.total_count !== 1 ? 's' : ''}.
            </p>

            {results.length > 0 ? (
              <ul className="space-y-3">
                {results.map((item) => (
                  <li key={item.item_id} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow border border-ulacm-gray-100">
                    <Link to={`/app/${item.item_type.toLowerCase()}s/${item.item_id}`} className="block group">
                      <div className="flex items-center justify-between mb-1">
                         <div className="flex items-center min-w-0">
                             {getItemIcon(item.item_type)}
                             <h3 className="text-lg font-semibold text-ulacm-primary group-hover:underline truncate" title={item.name}>{item.name}</h3>
                         </div>
                         <span className="ml-3 text-xs px-2 py-0.5 bg-ulacm-gray-100 text-ulacm-gray-600 rounded-full shrink-0">{item.item_type}</span>
                      </div>

                      {item.snippet && (
                          <p className="text-sm text-ulacm-gray-700 border-l-2 border-ulacm-primary/30 pl-2 ml-1 my-2 italic"
                             dangerouslySetInnerHTML={{ __html: item.snippet }}
                          />
                      )}

                       <p className="text-xs text-ulacm-gray-500 mt-1">
                          Updated: {formatDistanceToNow(new Date(item.updated_at), { addSuffix: true })} | v{item.current_version_number ?? 0}
                       </p>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-center py-16 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                    <Search size={48} className="mx-auto text-ulacm-gray-300"/>
                    <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No results found</h3>
                    <p className="mt-1 text-sm text-ulacm-gray-500">Try adjusting your search query or filters.</p>
              </div>
            )}

            {pagination.total_count > pagination.limit && (
              <div className="mt-6 flex flex-col sm:flex-row items-center justify-between text-sm text-ulacm-gray-600">
                  <div>
                    Showing <span className="font-semibold">{pagination.offset + 1}</span> to <span className="font-semibold">{Math.min(pagination.offset + pagination.limit, pagination.total_count)}</span> of <span className="font-semibold">{pagination.total_count}</span> results
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

         {!isLoading && !error && !hasSearched && (
             <div className="text-center py-16 px-6 bg-white rounded-lg shadow border border-ulacm-gray-100">
                <Search size={48} className="mx-auto text-ulacm-gray-300"/>
                <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">Search for Content</h3>
                <p className="mt-1 text-sm text-ulacm-gray-500">Enter keywords or filter by type to find documents, templates, and workflows.</p>
            </div>
         )}
      </div>
    </div>
  );
};

export default SearchPage;
