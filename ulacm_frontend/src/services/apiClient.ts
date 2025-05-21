// File: ulacm_frontend/src/services/apiClient.ts
// Purpose: Configures and exports an Axios instance for API communication.
// Updated: Ensure cookie is deleted on 401 redirect (attempt only, HttpOnly handled by backend).

import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = '/api/v1';
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // Increased timeout to 300 seconds (5 minutes)
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred.';
    let toastId: string | undefined;
    const statusCode = error.response?.status;
    const responseData = error.response?.data;
    const requestUrl = error.config?.url; // Get the URL of the request that failed

    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        toastId = 'client-timeout-error';
        errorMessage = 'The request timed out. Please try again or check if the task is still running in the background.';
        console.error('API Request Timed Out (Axios):', error);
        toast.error(errorMessage, { id: toastId, duration: 7000 });
    } else if (error.response) {
      console.error('API Error Response:', error.response);

      if (statusCode === 422 && responseData?.detail && Array.isArray(responseData.detail)) {
        errorMessage = responseData.detail.map((err: { loc: string[]; msg: string; type?: string }) => {
            const field = err.loc && err.loc.length > 1 ? err.loc.slice(1).join('.') : (err.loc?.[0] || 'Request');
            return `${field}: ${err.msg}`;
        }).join('; ');
        toastId = 'validation-error-422';
        toast.error(`Validation Error: ${errorMessage}`, { id: toastId, duration: 7000 });

      } else if (responseData?.errors && Array.isArray(responseData.errors)) {
        errorMessage = responseData.errors.map((err: { field: string; message: string; }) => `${err.field}: ${err.message}`).join('; ');
        toastId = 'validation-error-custom';
        toast.error(`Validation Error: ${errorMessage}`, { id: toastId, duration: 7000 });
      } else {
        errorMessage = responseData?.detail || responseData?.message || `Request failed with status ${statusCode}`;

        if (statusCode === 401) {
          // Only trigger the global redirect logic if the 401 is NOT from one of the session check endpoints.
          // AuthContext is responsible for handling 401s from these endpoints and then navigating.
          const isAuthCheckEndpoint = requestUrl === '/auth/me' || requestUrl === '/admin/auth/me';

          if (!isAuthCheckEndpoint) {
            toastId = 'auth-error-redirect';
            console.warn(`API returned 401 Unauthorized from general URL: ${requestUrl}. Attempting redirect.`);

            document.cookie = "team_session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "admin_session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            console.log("Attempted to clear team_session_id and admin_session_id cookies (effective if not HttpOnly).");

            toast.error('Your session has expired or you are unauthorized. Redirecting to login...', {
              id: toastId,
              duration: 3500,
            });

            const currentPath = window.location.pathname.toLowerCase();
            const isAdminPageContext = currentPath.startsWith('/admin');
            const isAlreadyOnLoginPage = currentPath.includes('/login');

            console.log(`Current path for 401 (general API): ${currentPath}, IsAdminPageContext: ${isAdminPageContext}, IsAlreadyOnLoginPage: ${isAlreadyOnLoginPage}`);

            if (!isAlreadyOnLoginPage) {
              setTimeout(() => {
                const targetLoginPath = isAdminPageContext ? '/admin/login' : '/login';
                console.log(`Redirecting to ${targetLoginPath} due to 401 on ${requestUrl}`);
                window.location.href = targetLoginPath;
              }, 100);
            } else {
              console.log(`Redirect skipped for general API 401: Already on a login page (${currentPath}).`);
            }
          } else {
            console.log(`401 from auth check endpoint (${requestUrl}) - redirect will be handled by AuthContext/ProtectedRoute if necessary.`);
            // The error will still be propagated to the caller (e.g., AuthContext's checkSession)
            // which will then update its state, leading ProtectedRoute to navigate.
          }
        } else if (statusCode === 403) {
          toastId = 'forbidden-error';
          toast.error('Forbidden: You do not have permission to perform this action or access this resource.', { id: toastId, duration: 5000 });
        } else if (statusCode === 404) {
          // console.warn(`API Resource not found: ${error.config.url}`);
        } else if (statusCode === 409) {
          toastId = 'conflict-error';
          toast.error(`Conflict: ${errorMessage}`, { id: toastId, duration: 5000 });
        } else if (statusCode >= 500) {
          toastId = 'server-error';
          toast.error(`Server error (${statusCode}). Please try again later.`, { id: toastId });
        } else if (statusCode >= 400 && statusCode < 500 && ![401, 403, 404, 409, 422].includes(statusCode)) {
            toastId = `client-error-${statusCode}`;
            toast.error(`Error: ${errorMessage}`, { id: toastId });
        }
      }
    } else if (error.request) {
      toastId = 'network-error';
      console.error('API No Response (Network Error):', error.request);
      errorMessage = 'Network error: Could not reach the server. Please check your connection.';
      toast.error(errorMessage, { id: toastId });
    } else {
      console.error('API Request Setup Error:', error.message);
      errorMessage = `Request setup error: ${error.message}`;
    }

    return Promise.reject({
        message: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage),
        status: error.response?.status,
        data: error.response?.data,
        originalError: error,
        isAxiosTimeout: error.code === 'ECONNABORTED' && error.message.includes('timeout'),
    });
  }
);

export default apiClient;
