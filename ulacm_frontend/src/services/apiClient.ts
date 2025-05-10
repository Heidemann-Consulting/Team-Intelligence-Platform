// File: ulacm_frontend/src/services/apiClient.ts
// Purpose: Configures and exports an Axios instance for API communication.
// Increased global timeout and corrected 401 redirect logic.
// Updated: Improved handling of 422 Unprocessable Entity errors from Pydantic.

import axios from 'axios';
import toast from 'react-hot-toast';

// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // Increased timeout to 300 seconds (5 minutes)
});

// Interceptor for API responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'An unexpected error occurred.';
    let toastId: string | undefined;
    const statusCode = error.response?.status;
    const responseData = error.response?.data;

    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        toastId = 'client-timeout-error';
        errorMessage = 'The request timed out. Please try again or check if the task is still running in the background.';
        console.error('API Request Timed Out (Axios):', error);
        toast.error(errorMessage, { id: toastId, duration: 7000 });
    } else if (error.response) {
      console.error('API Error Response:', error.response);

      if (statusCode === 422 && responseData?.detail && Array.isArray(responseData.detail)) {
        // Handle Pydantic's array of error objects in 'detail' for 422 errors
        errorMessage = responseData.detail.map((err: { loc: string[]; msg: string; type?: string }) => {
            // Construct a user-friendly field name from the 'loc' array
            // e.g., ["body", "template_id"] becomes "template_id"
            const field = err.loc && err.loc.length > 1 ? err.loc.slice(1).join('.') : (err.loc?.[0] || 'Request');
            return `${field}: ${err.msg}`;
        }).join('; ');
        toastId = 'validation-error-422';
        toast.error(`Validation Error: ${errorMessage}`, { id: toastId, duration: 7000 });

      } else if (responseData?.errors && Array.isArray(responseData.errors)) {
        // Handle custom array of error objects in 'errors' (if any endpoint uses this)
        errorMessage = responseData.errors.map((err: { field: string; message: string; }) => `${err.field}: ${err.message}`).join('; ');
        toastId = 'validation-error-custom';
        toast.error(`Validation Error: ${errorMessage}`, { id: toastId, duration: 7000 });
      } else {
        // Handle single string detail or message for other errors
        errorMessage = responseData?.detail || responseData?.message || `Request failed with status ${statusCode}`;

        if (statusCode === 401) {
          toastId = 'auth-error-redirect';
          console.warn("API returned 401 Unauthorized. Redirecting to login.");
          toast.error('Your session has expired or you are unauthorized. Redirecting to login...', {
            id: toastId,
            duration: 4000,
          });
          setTimeout(() => {
              if (!window.location.pathname.toLowerCase().includes('/login')) {
                  window.location.href = '/login';
              }
          }, 4000);
        } else if (statusCode === 403) {
          toastId = 'forbidden-error';
          toast.error('Forbidden: You do not have permission.', { id: toastId });
        } else if (statusCode === 404) {
          // Usually handled more specifically by the calling component
          // console.warn(`API Resource not found: ${error.config.url}`);
          // No generic toast for 404, let component decide.
        } else if (statusCode === 409) {
          toastId = 'conflict-error';
          toast.error(`Conflict: ${errorMessage}`, { id: toastId, duration: 5000 });
        } else if (statusCode >= 500) {
          toastId = 'server-error';
          toast.error(`Server error (${statusCode}). Please try again later.`, { id: toastId });
        } else if (statusCode >= 400 && statusCode < 500 && ![401, 403, 404, 409, 422].includes(statusCode)) {
            // Generic client error toast for other 4xx errors not specifically handled above
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
      // Potentially a generic toast here if desired, but usually indicates a coding error.
    }

    // Ensure the rejected promise's message is always a string
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
