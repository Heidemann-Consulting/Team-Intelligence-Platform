// File: ulacm_frontend/src/components/admin/TeamFormModal.tsx
// Purpose: Modal for creating or editing a team.
// Refinements: Improved layout, spacing, added focus styles, better error display.

import React, { useState, useEffect, FormEvent } from 'react';
import toast from 'react-hot-toast';
import { Team } from '@/types/auth';
import adminService, { TeamCreatePayload, TeamUpdatePayload } from '@/services/adminService';
import { X, Save, AlertCircle } from 'lucide-react'; // For close button
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface TeamFormModalProps {
  isOpen: boolean;
  mode: 'create' | 'edit';
  initialData?: Team; // Provided in edit mode
  onClose: () => void;
  onSuccess: (updatedTeam: Team) => void; // Callback after successful save
}

const TeamFormModal: React.FC<TeamFormModalProps> = ({
  isOpen,
  mode,
  initialData,
  onClose,
  onSuccess,
}) => {
  const [teamName, setTeamName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // State for inline validation errors (optional)
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (mode === 'edit' && initialData) {
      setTeamName(initialData.team_name);
      setUsername(initialData.username);
      setIsActive(initialData.is_active);
      setPassword('');
    } else {
      setTeamName('');
      setUsername('');
      setPassword('');
      setIsActive(true);
    }
    setError(null);
    setErrors({}); // Clear errors when modal opens or mode changes
  }, [isOpen, mode, initialData]);

  if (!isOpen) return null;

  const validateForm = (): boolean => {
      const newErrors: Record<string, string> = {};
      if (!teamName.trim()) newErrors.teamName = "Team Name is required.";
      if (!username.trim()) newErrors.username = "Username is required.";
      else if (!/^[a-zA-Z0-9_]+$/.test(username)) newErrors.username = "Username can only contain letters, numbers, and underscores.";

      if (mode === 'create' && !password) newErrors.password = "Password is required for new teams.";
      if (password && password.length < 8) newErrors.password = "Password must be at least 8 characters long.";

      setErrors(newErrors);
      return Object.keys(newErrors).length === 0; // Return true if no errors
  };


  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null); // Clear general error
    if (!validateForm()) {
        return; // Stop submission if validation fails
    }

    setIsLoading(true);

    try {
      let savedTeam: Team;
      if (mode === 'create') {
        const payload: TeamCreatePayload = { team_name: teamName.trim(), username: username.trim(), password };
        savedTeam = await adminService.createTeam(payload);
        toast.success(`Team "${savedTeam.team_name}" created successfully!`);
      } else if (initialData) { // Edit mode
        const payload: TeamUpdatePayload = { team_name: teamName.trim(), is_active: isActive };
        if (password) { // Only include password if it's being changed
          payload.password = password;
        }
        savedTeam = await adminService.updateTeam(initialData.team_id, payload);
        toast.success(`Team "${savedTeam.team_name}" updated successfully!`);
      } else {
        throw new Error("Invalid mode or missing data for edit.");
      }
      onSuccess(savedTeam);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || `Failed to ${mode} team.`;
      // Check for specific conflict errors
      if (err.response?.status === 409) {
          if (errorMessage.toLowerCase().includes("username")) {
              setErrors(prev => ({...prev, username: errorMessage}));
          } else if (errorMessage.toLowerCase().includes("team name")) {
              setErrors(prev => ({...prev, teamName: errorMessage}));
          } else {
               setError(errorMessage); // Show general error if conflict source is unclear
          }
      } else {
          setError(errorMessage); // Show general error for other issues
      }
      toast.error(`Failed to ${mode} team.`); // Keep toast generic
    } finally {
      setIsLoading(false);
    }
  };

  const inputClass = (hasError: boolean): string =>
    `w-full px-3.5 py-2 border rounded-md shadow-sm transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-ulacm-secondary/50 ${
        hasError
        ? 'border-red-500 focus:border-red-500'
        : 'border-ulacm-gray-300 focus:border-ulacm-secondary'
    }`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-60 backdrop-blur-sm">
      {/* Modal Dialog */}
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-auto transform transition-all max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-ulacm-gray-200 flex-shrink-0">
          <h3 className="text-xl font-semibold text-ulacm-gray-800">
            {mode === 'create' ? 'Create New Team' : `Edit Team: ${initialData?.team_name}`}
          </h3>
          <button onClick={onClose} className="p-1.5 text-ulacm-gray-400 hover:text-ulacm-gray-600 hover:bg-ulacm-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ulacm-secondary/50">
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-grow overflow-y-auto">
          <div className="px-6 py-5 space-y-4">
            {/* General Error Display */}
            {error && (
                 <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded relative flex items-start" role="alert">
                    <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="block sm:inline text-sm">{error}</span>
                 </div>
            )}
            {/* Team Name */}
            <div>
              <label htmlFor="teamName" className="block text-sm font-medium text-ulacm-gray-700 mb-1">Team Name <span className="text-red-500">*</span></label>
              <input
                id="teamName" type="text" value={teamName}
                onChange={(e) => { setTeamName(e.target.value); setErrors(p => ({...p, teamName: ''})); }} required
                className={inputClass(!!errors.teamName)}
              />
              {errors.teamName && <p className="mt-1 text-xs text-red-600">{errors.teamName}</p>}
            </div>
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-ulacm-gray-700 mb-1">Username <span className="text-red-500">*</span></label>
              <input
                id="username" type="text" value={username}
                onChange={(e) => { setUsername(e.target.value); setErrors(p => ({...p, username: ''})); }} required
                disabled={mode === 'edit'}
                className={`${inputClass(!!errors.username)} ${mode === 'edit' ? 'bg-ulacm-gray-100 cursor-not-allowed' : ''}`}
                pattern="^[a-zA-Z0-9_]+$" // Basic pattern check
                title="Username can only contain letters, numbers, and underscores."
              />
              {errors.username && <p className="mt-1 text-xs text-red-600">{errors.username}</p>}
              {mode === 'edit' && <p className="mt-1 text-xs text-ulacm-gray-500">Username cannot be changed after creation.</p>}
            </div>
            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ulacm-gray-700 mb-1">
                Password {mode === 'create' && <span className="text-red-500">*</span>} {mode === 'edit' && '(leave blank to keep current)'}
              </label>
              <input
                id="password" type="password" value={password}
                onChange={(e) => { setPassword(e.target.value); setErrors(p => ({...p, password: ''})); }}
                required={mode === 'create'}
                minLength={mode === 'create' || (password && password.length > 0) ? 8 : undefined}
                className={inputClass(!!errors.password)}
              />
              {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password}</p>}
            </div>
            {/* Is Active Toggle (Edit Mode Only) */}
            {mode === 'edit' && (
              <div className="flex items-center pt-2">
                <label htmlFor="isActive" className="flex items-center cursor-pointer">
                    <div className="relative">
                        <input
                            id="isActive" type="checkbox" className="sr-only"
                            checked={isActive}
                            onChange={(e) => setIsActive(e.target.checked)}
                        />
                        <div className={`block w-10 h-6 rounded-full transition ${isActive ? 'bg-ulacm-secondary' : 'bg-ulacm-gray-300'}`}></div>
                        <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition transform ${isActive ? 'translate-x-4' : ''}`}></div>
                    </div>
                    <div className="ml-3 text-sm text-ulacm-gray-800 font-medium">
                        Team is Active
                    </div>
                </label>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="bg-ulacm-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse border-t border-ulacm-gray-200 flex-shrink-0">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150 bg-ulacm-secondary hover:bg-ulacm-secondary-dark text-white focus:ring-ulacm-secondary disabled:opacity-70"
            >
              {isLoading ? <LoadingSpinner size="sm" color="text-white" className="mr-2"/> : <Save size={18} className="mr-1.5"/>}
              {isLoading ? 'Saving...' : (mode === 'create' ? 'Create Team' : 'Save Changes')}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
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

export default TeamFormModal;
