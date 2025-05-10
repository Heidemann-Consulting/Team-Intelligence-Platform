// File: ulacm_frontend/src/components/common/ProtectedRoute.tsx
// Purpose: Component to protect routes that require team user authentication.
// Refinement: Added slightly better styling for the loading state.

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
  children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Centered loading indicator covering the screen
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-ulacm-gray-100 bg-opacity-75 z-50">
        <LoadingSpinner size="lg" />
        <p className="mt-3 text-ulacm-gray-600">Checking authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
