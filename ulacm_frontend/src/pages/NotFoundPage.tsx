// File: ulacm_frontend/src/pages/NotFoundPage.tsx
// Purpose: Page displayed for 404 errors (route not found).
// No changes needed here for styling.

import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-ulacm-gray-100 p-4 text-center">
      <AlertTriangle className="w-24 h-24 text-yellow-500 mb-6" />
      <h1 className="text-6xl font-bold text-ulacm-gray-800 mb-4">404</h1>
      <h2 className="text-3xl font-semibold text-ulacm-gray-700 mb-3">Page Not Found</h2>
      <p className="text-ulacm-gray-600 mb-8 max-w-md">
        Oops! The page you are looking for does not exist. It might have been moved or deleted.
      </p>
      <div className="flex space-x-4">
        <Link
          to="/app/dashboard" // Or simply "/" which might redirect based on auth
          className="px-6 py-3 bg-ulacm-primary text-white font-semibold rounded-lg shadow hover:bg-ulacm-primary-dark transition-colors duration-150"
        >
          Go to Dashboard
        </Link>
        <Link
          to={-1 as any} // Go back to previous page
          className="px-6 py-3 bg-ulacm-gray-300 text-ulacm-gray-800 font-semibold rounded-lg shadow hover:bg-ulacm-gray-400 transition-colors duration-150"
        >
          Go Back
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
