// File: ulacm_frontend/src/contexts/AuthContext.tsx
// Purpose: Provides authentication state and functions to the application.
// Updated: Implemented checkSession using assumed /me endpoints.

// import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import apiClient from '@/services/apiClient'; // Using path alias
import { AuthState, AuthContextType, Team, TeamLoginResponse, AdminLoginResponse } from '@/types/auth'; // Using path alias
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { AxiosError } from 'axios'; // Import AxiosError type

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isAdminAuthenticated: false,
    currentTeam: null,
    isLoading: true,
    error: null,
  });
  const navigate = useNavigate();

  const setAuthLoading = (loading: boolean) => {
    setAuthState(prev => ({ ...prev, isLoading: loading, error: null }));
  };

  const setTeamUser = (team: Team | null) => {
    setAuthState(prev => ({
      ...prev,
      isAuthenticated: !!team,
      currentTeam: team,
      isAdminAuthenticated: false,
      isLoading: false,
      error: null,
    }));
  };

  const setAdminAuthenticated = (isAdmin: boolean) => {
    setAuthState(prev => ({
      ...prev,
      isAdminAuthenticated: isAdmin,
      isAuthenticated: false,
      currentTeam: null,
      isLoading: false,
      error: null,
    }));
  };

  const clearAuthError = () => {
    setAuthState(prev => ({ ...prev, error: null }));
  };

  // Simplified error handler using the message from the rejected promise
  const handleApiError = (error: any, defaultMessage: string) => {
    const message = error?.message || defaultMessage; // Use message from structured error
    setAuthState(prev => ({ ...prev, isLoading: false, error: message }));
    // Toasting is now primarily handled by the apiClient interceptor
    // toast.error(message);
  };

  const teamLogin = async (username: string, password: string): Promise<void> => {
    setAuthLoading(true);
    try {
      const response = await apiClient.post<TeamLoginResponse>('/auth/login', { username, password });
      setTeamUser(response.data);
      toast.success(`Welcome, ${response.data.team_name}!`);
      navigate('/app/dashboard');
    } catch (error: any) {
      handleApiError(error, 'Team login failed.');
      throw error; // Re-throw for component-level handling if needed
    }
  };

  const adminLogin = async (password: string): Promise<void> => {
    setAuthLoading(true);
    try {
      await apiClient.post<AdminLoginResponse>('/admin/auth/login', { password });
      setAdminAuthenticated(true);
      toast.success('Admin login successful!');
      navigate('/admin/dashboard');
    } catch (error: any) {
      handleApiError(error, 'Admin login failed.');
      throw error; // Re-throw for component-level handling if needed
    }
  };

  const logout = async (): Promise<void> => {
    setAuthLoading(true);
    const wasAdmin = authState.isAdminAuthenticated;
    const logoutUrl = wasAdmin ? '/admin/auth/logout' : '/auth/logout';
    const redirectUrl = wasAdmin ? '/admin/login' : '/login';
    try {
      await apiClient.post(logoutUrl);
      toast.success('Logout successful.');
    } catch (error: any) {
      // Log error but proceed with local logout
      console.error("Logout API call failed:", error);
      handleApiError(error, 'Logout failed on server, logging out locally.');
    } finally {
      // Always clear local state and redirect
      setTeamUser(null);
      setAdminAuthenticated(false);
      setAuthLoading(false); // Ensure loading is set to false
      navigate(redirectUrl);
    }
  };

  // Check session on initial app load
  const checkSession = useCallback(async (): Promise<void> => {
    setAuthLoading(true);
    try {
      // Attempt to fetch team user info first
      try {
        // Assumes backend has GET /api/v1/auth/me endpoint
        const teamResponse = await apiClient.get<Team>('/auth/me');
        if (teamResponse.data) {
          setTeamUser(teamResponse.data);
          return; // Exit if team user is found
        }
      } catch (teamError) {
         const axiosError = teamError as AxiosError;
         if (axiosError.response?.status !== 401 && axiosError.response?.status !== 403) {
             // Log unexpected errors, but don't block checking admin session
             console.warn("Unexpected error checking team session:", teamError);
         }
         // If 401/403 or other error, proceed to check admin session
      }

      // If no team user found, attempt to fetch admin info
      try {
        // Assumes backend has GET /api/v1/admin/auth/me endpoint
        // It might just return a success status (200 OK) or minimal admin info
        await apiClient.get('/admin/auth/me');
        setAdminAuthenticated(true);
      } catch (adminError) {
        // If both checks fail (likely due to 401), clear auth state
        setTeamUser(null);
        setAdminAuthenticated(false);
        const axiosError = adminError as AxiosError;
        if (axiosError.response?.status !== 401 && axiosError.response?.status !== 403) {
            // Log unexpected errors from admin check
            console.warn("Unexpected error checking admin session:", adminError);
        }
      }
    } catch (error) {
      // Catch any truly unexpected errors during the process
      console.error("Error during session check:", error);
      setTeamUser(null);
      setAdminAuthenticated(false);
    } finally {
      setAuthLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Dependencies are stable (setters, navigate)

  useEffect(() => {
    checkSession();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount

  return (
    <AuthContext.Provider value={{ ...authState, setAuthLoading, setTeamUser, setAdminAuthenticated, clearAuthError, teamLogin, adminLogin, logout, checkSession }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
