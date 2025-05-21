// File: ulacm_frontend/src/pages/AdminLoginPage.tsx
// Purpose: Page for administrator login.
// Refinements: Similar improvements as LoginPage, using secondary color theme.

import React, { useState, FormEvent } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext'; // Using path alias
import toast from 'react-hot-toast';
import { ShieldCheck, LogIn, AlertCircle } from 'lucide-react'; // Example icon
import LoadingSpinner from '@/components/common/LoadingSpinner'; // Import spinner

const AdminLoginPage: React.FC = () => {
  const [password, setPassword] = useState('');
  const { adminLogin, isLoading, error, clearAuthError, isAdminAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/admin/dashboard';

  // If already admin authenticated, redirect
  React.useEffect(() => {
    if (isAdminAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAdminAuthenticated, navigate, from]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearAuthError();
    if (!password) {
      toast.error('Admin password is required.');
      return;
    }
    try {
      await adminLogin(password);
      // Navigation is handled by adminLogin on success
    } catch (err) {
      // Error is handled by adminLogin
      console.error("Admin login page catch:", err)
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-ulacm-gray-700 to-ulacm-gray-900 p-4"> {/* Darker gradient for admin */}
      <div className="w-full max-w-sm bg-white shadow-xl rounded-xl p-8 md:p-10 border border-ulacm-gray-300">
        <div className="text-center mb-8">
          <ShieldCheck className="mx-auto h-12 w-12 text-ulacm-secondary mb-3" />
          <h1 className="text-3xl font-bold text-ulacm-secondary">Admin Login</h1>
          <p className="text-ulacm-gray-600 mt-2">Team Intelligence Platform Service Administration</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="admin-password"
              className="block text-sm font-medium text-ulacm-gray-700 mb-1.5"
            >
              Administrator Password
            </label>
            <input
              id="admin-password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-secondary/50 focus:border-ulacm-secondary transition duration-150 ease-in-out" /* Refined focus */
              placeholder="••••••••"
            />
          </div>

          {/* Improved Error Display */}
          {error && (
             <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded-md flex items-start">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center bg-ulacm-secondary hover:bg-ulacm-secondary-dark focus:bg-ulacm-secondary-dark text-white font-semibold py-3 px-4 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-ulacm-secondary focus:ring-offset-2 transition-all duration-150 ease-in-out disabled:opacity-70 disabled:cursor-not-allowed group"
            >
              {isLoading ? (
                 <LoadingSpinner size="sm" color="text-white" className="mr-2" />
              ) : (
                <LogIn className="mr-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              )}
              {isLoading ? 'Authenticating...' : 'Login as Admin'}
            </button>
          </div>
        </form>
        <p className="mt-8 text-center text-sm text-ulacm-gray-600">
          Not an admin?{' '}
          <Link to="/login" className="font-medium text-ulacm-secondary hover:text-ulacm-secondary-dark hover:underline">
            Go to Team Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default AdminLoginPage;
