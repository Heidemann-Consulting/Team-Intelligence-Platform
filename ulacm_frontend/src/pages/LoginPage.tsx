// File: ulacm_frontend/src/pages/LoginPage.tsx
// Purpose: Page for team user login.
// Refinements: Improved input styling, error display, button feedback.

import React, { useState, FormEvent } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext'; // Using path alias
import toast from 'react-hot-toast';
import { LogIn, AlertCircle } from 'lucide-react'; // Example icon
import LoadingSpinner from '@/components/common/LoadingSpinner'; // Import spinner

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { teamLogin, isLoading, error, clearAuthError, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/app/dashboard';

  // If already authenticated, redirect from login page
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);


  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearAuthError(); // Clear previous errors
    if (!username || !password) {
      toast.error('Username and password are required.');
      return;
    }
    try {
      await teamLogin(username, password);
      // Navigation is handled by teamLogin on success
    } catch (err) {
      // Error is handled by teamLogin (sets state, toasts)
      // No additional handling needed here unless specific UI update is required
      console.error("Login page catch:", err)
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-ulacm-gray-50 to-ulacm-gray-100 p-4"> {/* Subtle gradient */}
      <div className="w-full max-w-md bg-white shadow-xl rounded-xl p-8 md:p-10 border border-ulacm-gray-200"> {/* Added border */}
        <div className="text-center mb-8">
          <img src="../tip-logo-login.png" alt="TIP Logo"  width="512" height="256" />
          <br />
          <h1 className="text-3xl font-bold text-ulacm-primary">Team Login</h1>
          <p className="text-ulacm-gray-600 mt-2">Access your Team Intelligence Platform workspace.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-ulacm-gray-700 mb-1.5" /* Increased margin */
            >
              Team Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out" /* Refined focus */
              placeholder="e.g., linux_team"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-ulacm-gray-700 mb-1.5" /* Increased margin */
            >
              Team Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-ulacm-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-ulacm-primary/50 focus:border-ulacm-primary transition duration-150 ease-in-out" /* Refined focus */
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
              className="w-full flex justify-center items-center bg-ulacm-primary hover:bg-ulacm-primary-dark focus:bg-ulacm-primary-dark text-white font-semibold py-3 px-4 rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-ulacm-primary focus:ring-offset-2 transition-all duration-150 ease-in-out disabled:opacity-70 disabled:cursor-not-allowed group" /* Added group for potential icon animation */
            >
              {isLoading ? (
                <LoadingSpinner size="sm" color="text-white" className="mr-2" />
              ) : (
                <LogIn className="mr-2 h-5 w-5 group-hover:translate-x-1 transition-transform" /> /* Subtle hover effect */
              )}
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </form>
        <p className="mt-8 text-center text-sm text-ulacm-gray-600">
          Administrator?{' '}
          <Link to="/admin/login" className="font-medium text-ulacm-primary hover:text-ulacm-primary-dark hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
