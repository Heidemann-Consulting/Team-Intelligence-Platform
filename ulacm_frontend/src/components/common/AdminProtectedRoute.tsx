// File: ulacm_frontend/src/components/common/AdminProtectedRoute.tsx
// Purpose: Component to protect routes that require administrator authentication.
// Refinement: Added slightly better styling for the loading state.

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

interface AdminProtectedRouteProps {
  children: JSX.Element;
}

const AdminProtectedRoute: React.FC<AdminProtectedRouteProps> = ({ children }) => {
  const { isAdminAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
     return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-ulacm-gray-100 bg-opacity-75 z-50">
        <LoadingSpinner size="lg" color="text-ulacm-secondary"/> {/* Use secondary color */}
        <p className="mt-3 text-ulacm-gray-600">Checking admin authentication...</p>
      </div>
    );
  }

  if (!isAdminAuthenticated) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return children;
};

export default AdminProtectedRoute;
