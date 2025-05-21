// File: ulacm_frontend/src/services/adminService.ts
// Purpose: Service for API calls related to administrator functionalities.

import apiClient from './apiClient';
// import { Team, TeamLoginResponse } from '@/types/auth'; // Assuming Team type is in auth.ts
import { Team } from '@/types/auth'; // Assuming Team type is in auth.ts
import { TeamListResponse as ApiTeamListResponse } from '@/types/api'; // Define this type for backend's paginated response

// Define a more specific type for the backend's team list response if it differs from frontend's Team[]
// For now, assuming backend returns a structure like: { teams: Team[], total_count: number, offset: number, limit: number }
// We'll use the TeamListResponse from the backend schema definition (SRS 8.3.2)

export interface TeamCreatePayload {
  team_name: string;
  username: string;
  password?: string; // Password is required for creation
}

export interface TeamUpdatePayload {
  team_name?: string;
  password?: string; // Optional for update
  is_active?: boolean;
}


const adminService = {
  // Fetch all teams (FR-ADM-004, SRS 8.3.2)
  getTeams: async (offset: number = 0, limit: number = 50): Promise<ApiTeamListResponse> => {
    const response = await apiClient.get<ApiTeamListResponse>('/admin/teams', {
      params: { offset, limit },
    });
    return response.data;
  },

  // Create a new team (FR-ADM-003, SRS 8.3.1)
  createTeam: async (teamData: TeamCreatePayload): Promise<Team> => {
    const response = await apiClient.post<Team>('/admin/teams', teamData);
    return response.data;
  },

  // Get a specific team's details (SRS 8.3.3) - May not be directly used by list page, but good for edit form
  getTeamDetails: async (teamId: string): Promise<Team> => {
    const response = await apiClient.get<Team>(`/admin/teams/${teamId}`);
    return response.data;
  },

  // Update a team (FR-ADM-005, SRS 8.3.4)
  updateTeam: async (teamId: string, teamData: TeamUpdatePayload): Promise<Team> => {
    const response = await apiClient.put<Team>(`/admin/teams/${teamId}`, teamData);
    return response.data;
  },

  // Deactivate a team (FR-ADM-006, SRS 8.3.5)
  deactivateTeam: async (teamId: string): Promise<Team> => { // Backend returns updated team object
    const response = await apiClient.post<Team>(`/admin/teams/${teamId}/deactivate`);
    return response.data;
  },

  // Reactivate a team (FR-ADM-007, SRS 8.3.6)
  reactivateTeam: async (teamId: string): Promise<Team> => { // Backend returns updated team object
    const response = await apiClient.post<Team>(`/admin/teams/${teamId}/reactivate`);
    return response.data;
  },

  // Delete a team (FR-ADM-008, SRS 8.3.7)
  deleteTeam: async (teamId: string): Promise<{ message: string }> => { // Backend returns a Msg object
    const response = await apiClient.delete<{ message: string }>(`/admin/teams/${teamId}`);
    return response.data;
  },
};

export default adminService;
