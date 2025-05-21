// File: ulacm_frontend/src/contexts/AuthContext.tsx
// Purpose: Provides authentication state and functions to the application.
// Updated: Implemented checkSession using assumed /me endpoints.
// Removed unused axiosError variable.

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import apiClient from '@/services/apiClient';
import { AuthState, AuthContextType, Team, TeamLoginResponse, AdminLoginResponse } from '@/types/auth';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { AxiosError } from 'axios';

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

  const handleApiError = (error: any, defaultMessage: string) => {
    const message = error?.message || defaultMessage;
    setAuthState(prev => ({ ...prev, isLoading: false, error: message }));
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
      throw error;
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
      throw error;
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
      console.error("Logout API call failed:", error);
      handleApiError(error, 'Logout failed on server, logging out locally.');
    } finally {
      setTeamUser(null);
      setAdminAuthenticated(false);
      setAuthLoading(false);
      navigate(redirectUrl);
    }
  };

  const checkSession = useCallback(async (): Promise<void> => {
    setAuthLoading(true);
    try {
      try {
        const teamResponse = await apiClient.get<Team>('/auth/me');
        if (teamResponse.data) {
          setTeamUser(teamResponse.data);
          return;
        }
      } catch (teamError) {
        // const axiosError = teamError as AxiosError; // Removed as unused
        // If 401/403 or other error, proceed to check admin session
      }

      try {
        await apiClient.get('/admin/auth/me');
        setAdminAuthenticated(true);
      } catch (adminError) {
        setTeamUser(null);
        setAdminAuthenticated(false);
        const axiosErrorCheckAdmin = adminError as AxiosError; // Renamed to avoid conflict if used
        if (axiosErrorCheckAdmin.response?.status !== 401 && axiosErrorCheckAdmin.response?.status !== 403) {
            console.warn("Unexpected error checking admin session:", adminError);
        }
      }
    } catch (error) {
      console.error("Error during session check:", error);
      setTeamUser(null);
      setAdminAuthenticated(false);
    } finally {
      setAuthLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    checkSession();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
