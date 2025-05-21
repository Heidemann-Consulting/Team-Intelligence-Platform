// File: ulacm_frontend/src/types/auth.ts
// Purpose: TypeScript types related to authentication and user/team data.
// No changes needed here for styling.

export interface Team {
  team_id: string;
  team_name: string;
  username: string;
  is_active: boolean;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// For team login response (SRS 8.2.2)
export interface TeamLoginResponse extends Team {}

// For admin login response (SRS 8.2.1 - just a message)
export interface AdminLoginResponse {
  message: string;
}

export interface AuthState {
  isAuthenticated: boolean; // Team user authentication status
  isAdminAuthenticated: boolean;
  currentTeam: Team | null;
  isLoading: boolean; // For async auth operations
  error: string | null;
}

export interface AuthContextType extends AuthState {
  setAuthLoading: (loading: boolean) => void;
  setTeamUser: (team: Team | null) => void;
  setAdminAuthenticated: (isAdmin: boolean) => void;
  clearAuthError: () => void;
  teamLogin: (username: string, password: string) => Promise<void>;
  adminLogin: (password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>; // To check if session is still valid on app load
}
