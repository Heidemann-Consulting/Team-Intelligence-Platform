// File: ulacm_frontend/src/pages/admin/TeamManagementPage.tsx
// Purpose: Page for listing and managing team accounts by an admin.
// Refinements: Improved table styling, button styles, loading/error states, pagination feedback.

import React, { useState, useEffect, useCallback } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { useNavigate } from 'react-router-dom';
import { PlusCircle, Edit3, Trash2, Eye, EyeOff, RefreshCw, AlertCircle, ChevronLeft, ChevronRight, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns'; // For better date formatting

import { Team } from '@/types/auth';
import { TeamListResponse as ApiTeamListResponse } from '@/types/api';
import adminService from '@/services/adminService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmationModal from '@/components/common/ConfirmationModal';
import TeamFormModal from '@/components/admin/TeamFormModal';

const TeamManagementPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    offset: 0,
    limit: 10,
    total_count: 0,
  });

  const [showDeleteModal, setShowDeleteModal] = useState<Team | null>(null);
  const [showTeamFormModal, setShowTeamFormModal] = useState<Team | 'new' | null>(null);
  // State to track which row's action is in progress (optional, for finer feedback)
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  // const navigate = useNavigate();

  const fetchTeams = useCallback(async (offset = 0) => {
    setIsLoading(true);
    setError(null);
    try {
      const data: ApiTeamListResponse = await adminService.getTeams(offset, pagination.limit);
      setTeams(data.teams);
      setPagination(prev => ({ ...prev, offset, total_count: data.total_count }));
    } catch (err: any) {
      console.error("Failed to fetch teams:", err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load teams.';
      setError(errorMessage);
      // Toast handled by interceptor usually
    } finally {
      setIsLoading(false);
    }
  }, [pagination.limit]);

  useEffect(() => {
    fetchTeams(pagination.offset);
  }, [fetchTeams, pagination.offset]);

  const handleCreateTeam = () => {
    setShowTeamFormModal('new');
  };

  const handleEditTeam = (team: Team) => {
    setShowTeamFormModal(team);
  };

  const handleToggleActive = async (team: Team) => {
    const action = team.is_active ? adminService.deactivateTeam : adminService.reactivateTeam;
    const actionVerb = team.is_active ? 'Deactivating' : 'Activating';
    const successVerb = team.is_active ? 'deactivated' : 'activated';
    const toastId = `toggle-${team.team_id}`;

    setActionLoading(prev => ({ ...prev, [team.team_id]: true })); // Indicate loading for this specific action
    toast.loading(`${actionVerb} team ${team.team_name}...`, { id: toastId });

    try {
      const updatedTeam = await action(team.team_id);
      // Update state more reliably after API success
      setTeams(prevTeams => prevTeams.map(t => t.team_id === updatedTeam.team_id ? updatedTeam : t));
      toast.success(`Team ${team.team_name} ${successVerb}.`, { id: toastId });
    } catch (err: any) {
      // Error toast handled by interceptor
      console.error(`Failed to toggle active status for team ${team.team_id}`, err);
      // No need to revert optimistic UI as we update after success now
    } finally {
       setActionLoading(prev => ({ ...prev, [team.team_id]: false }));
    }
  };

  const handleDeleteTeam = (team: Team) => {
    setShowDeleteModal(team);
  };

  const confirmDeleteTeam = async () => {
    if (!showDeleteModal) return;
    const teamToDelete = showDeleteModal;
    const toastId = `delete-${teamToDelete.team_id}`;
    setShowDeleteModal(null);

    setActionLoading(prev => ({ ...prev, [teamToDelete.team_id]: true }));
    toast.loading(`Deleting team ${teamToDelete.team_name}...`, { id: toastId });
    try {
      await adminService.deleteTeam(teamToDelete.team_id);
      toast.success(`Team ${teamToDelete.team_name} deleted successfully.`, { id: toastId });
      // Refetch or remove locally
      setTeams(prevTeams => prevTeams.filter(t => t.team_id !== teamToDelete.team_id));
      setPagination(prev => ({...prev, total_count: prev.total_count -1}));
    } catch (err: any) {
       // Error toast handled by interceptor
       console.error(`Failed to delete team ${teamToDelete.team_id}`, err);
    } finally {
        setActionLoading(prev => ({ ...prev, [teamToDelete.team_id]: false }));
    }
  };

  const handlePageChange = (newOffset: number) => {
    if (newOffset >= 0 && newOffset < pagination.total_count) {
        setPagination(prev => ({ ...prev, offset: newOffset }));
    }
  };

  const totalPages = Math.ceil(pagination.total_count / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row justify-between md:items-center">
        <h1 className="text-3xl font-bold text-ulacm-gray-800 flex items-center">
            <Users size={30} className="mr-3 text-ulacm-secondary"/> Team Management
        </h1>
        <div className="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
          <button
            onClick={() => fetchTeams(pagination.offset)} // Refresh current page
            disabled={isLoading}
            className="p-2.5 text-ulacm-gray-500 hover:text-ulacm-secondary hover:bg-ulacm-gray-100 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-secondary/50"
            title="Refresh Teams List"
          >
            <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
          </button>
          <button
            onClick={handleCreateTeam}
            className="flex items-center bg-ulacm-secondary hover:bg-ulacm-secondary-dark focus:bg-ulacm-secondary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-ulacm-secondary focus:ring-offset-1"
          >
            <PlusCircle className="mr-1.5 h-5 w-5" /> Create Team
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !teams.length && ( // Show full page loader only on initial load
          <div className="flex justify-center items-center py-20 bg-white rounded-xl shadow-md">
              <LoadingSpinner size="lg" color="text-ulacm-secondary" />
              <p className="ml-3 text-ulacm-gray-600">Loading teams...</p>
          </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-md shadow">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Failed to Load Teams</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
               <div className="mt-4">
                  <button
                    onClick={() => fetchTeams(0)}
                    className="text-sm font-medium text-red-800 hover:text-red-600 underline"
                  >
                    Try again
                  </button>
                </div>
            </div>
          </div>
        </div>
      )}

      {/* Table and Content Area */}
      {!isLoading && !error && (
        <>
          <div className="bg-white shadow-xl rounded-xl overflow-hidden border border-ulacm-gray-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-ulacm-gray-200">
                <thead className="bg-ulacm-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Team Name</th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Username</th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3.5 text-left text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Created At</th>
                    <th scope="col" className="px-6 py-3.5 text-center text-xs font-semibold text-ulacm-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ulacm-gray-200 bg-white">
                  {teams.map((team) => (
                    <tr key={team.team_id} className={`hover:bg-ulacm-gray-50 transition-colors ${actionLoading[team.team_id] ? 'opacity-70' : ''}`}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-ulacm-gray-900">{team.team_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600 font-mono">@{team.username}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          team.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {team.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-ulacm-gray-600">
                        {format(new Date(team.created_at), 'PP')} {/* Format date nicely */}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium space-x-1 md:space-x-2">
                        {/* Action Buttons with Loading State */}
                        <button
                          onClick={() => handleEditTeam(team)}
                          disabled={actionLoading[team.team_id]}
                          title="Edit Team"
                          className="text-blue-600 hover:text-blue-800 p-1.5 rounded-md hover:bg-blue-500/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Edit3 size={16} />
                        </button>
                        <button
                          onClick={() => handleToggleActive(team)}
                          disabled={actionLoading[team.team_id]}
                          title={team.is_active ? "Deactivate Team" : "Activate Team"}
                          className={`${team.is_active ? 'text-yellow-600 hover:text-yellow-700' : 'text-green-600 hover:text-green-700'} p-1.5 rounded-md ${team.is_active ? 'hover:bg-yellow-500/10' : 'hover:bg-green-500/10'} transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                          {actionLoading[team.team_id] && !showDeleteModal ? <LoadingSpinner size="sm" color={team.is_active ? 'text-yellow-600' : 'text-green-600'} /> : (team.is_active ? <EyeOff size={16} /> : <Eye size={16} />)}
                        </button>
                        <button
                          onClick={() => handleDeleteTeam(team)}
                          disabled={actionLoading[team.team_id]}
                          title="Delete Team"
                          className="text-red-600 hover:text-red-700 p-1.5 rounded-md hover:bg-red-500/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                           {actionLoading[team.team_id] && showDeleteModal?.team_id === team.team_id ? <LoadingSpinner size="sm" color="text-red-600" /> : <Trash2 size={16} />}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {/* Empty State */}
              {teams.length === 0 && !isLoading && (
                <div className="text-center py-12 px-6">
                    <Users size={48} className="mx-auto text-ulacm-gray-300"/>
                    <h3 className="mt-2 text-lg font-medium text-ulacm-gray-800">No teams found</h3>
                    <p className="mt-1 text-sm text-ulacm-gray-500">Get started by creating a new team.</p>
                    <div className="mt-6">
                        <button
                            onClick={handleCreateTeam}
                            className="inline-flex items-center bg-ulacm-secondary hover:bg-ulacm-secondary-dark text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150"
                        >
                            <PlusCircle className="mr-2 h-5 w-5" /> Create New Team
                        </button>
                    </div>
                </div>
              )}
            </div>
          </div>
          {/* Pagination Controls */}
          {pagination.total_count > pagination.limit && (
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between text-sm text-ulacm-gray-600">
              <div>
                Showing <span className="font-semibold">{pagination.offset + 1}</span> to <span className="font-semibold">{Math.min(pagination.offset + pagination.limit, pagination.total_count)}</span> of <span className="font-semibold">{pagination.total_count}</span> teams
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

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <ConfirmationModal
          isOpen={!!showDeleteModal}
          title={`Delete Team: ${showDeleteModal.team_name}`}
          message={
             <div className="space-y-2">
                <p>Are you sure you want to permanently delete the team:</p>
                <p className="font-semibold">{showDeleteModal.team_name} (@{showDeleteModal.username})?</p>
                <p className="text-red-700 font-medium">This action will also delete all content exclusively owned by this team and cannot be undone.</p>
             </div>
          }
          onConfirm={confirmDeleteTeam}
          onCancel={() => setShowDeleteModal(null)}
          confirmButtonText="Yes, Delete Team"
          confirmButtonVariant="danger"
        />
      )}
      {/* Create/Edit Team Modal */}
      {showTeamFormModal !== null && (
        <TeamFormModal
          isOpen={showTeamFormModal !== null}
          mode={showTeamFormModal === 'new' ? 'create' : 'edit'}
          initialData={showTeamFormModal === 'new' ? undefined : showTeamFormModal}
          onClose={() => setShowTeamFormModal(null)}
          onSuccess={() => {
            setShowTeamFormModal(null);
            fetchTeams(showTeamFormModal === 'new' ? 0 : pagination.offset); // Refresh list
          }}
        />
      )}

    </div>
  );
};

export default TeamManagementPage;
