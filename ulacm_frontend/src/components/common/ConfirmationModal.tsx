// File: ulacm_frontend/src/components/common/ConfirmationModal.tsx
// Purpose: A reusable modal component for confirmations.
// Refinements: Slightly improved button styling and layout.

// import React, { Fragment } from 'react';
// import { AlertTriangle, Check, X } from 'lucide-react'; // Import icons
import { AlertTriangle } from 'lucide-react'; // Import icons

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string | React.ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
  confirmButtonText?: string;
  cancelButtonText?: string;
  confirmButtonVariant?: 'primary' | 'danger' | 'secondary';
  icon?: React.ElementType; // Optional icon component
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  confirmButtonText = 'Confirm',
  cancelButtonText = 'Cancel',
  confirmButtonVariant = 'primary',
  icon: Icon = AlertTriangle, // Default to AlertTriangle
}) => {
  if (!isOpen) return null;

  let confirmButtonClass = 'bg-ulacm-primary hover:bg-ulacm-primary-dark focus:ring-ulacm-primary text-white';
  let iconColor = 'text-yellow-500'; // Default icon color for AlertTriangle
  if (confirmButtonVariant === 'danger') {
    confirmButtonClass = 'bg-red-600 hover:bg-red-700 focus:ring-red-500 text-white';
    iconColor = 'text-red-500';
  } else if (confirmButtonVariant === 'secondary') {
    confirmButtonClass = 'bg-ulacm-gray-600 hover:bg-ulacm-gray-700 focus:ring-ulacm-gray-500 text-white';
    iconColor = 'text-ulacm-gray-500';
  }

  return (
    // Using Fragment might be slightly less robust for accessibility overlays than a Portal approach
    // Consider using Headless UI Dialog or Radix Dialog for production apps
    <div
        className="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
    >
        <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            {/* Background overlay */}
            <div className="fixed inset-0 bg-ulacm-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>

            {/* This element is to trick the browser into centering the modal contents. */}
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            {/* Modal panel */}
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <div className="sm:flex sm:items-start">
                        <div className={`mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full ${confirmButtonVariant === 'danger' ? 'bg-red-100' : 'bg-blue-100'} sm:mx-0 sm:h-10 sm:w-10`}>
                            <Icon className={`h-6 w-6 ${iconColor}`} aria-hidden="true" />
                        </div>
                        <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                            <h3 className="text-lg leading-6 font-semibold text-ulacm-gray-900" id="modal-title">
                                {title}
                            </h3>
                            <div className="mt-2 text-sm text-ulacm-gray-600 space-y-2">
                                {typeof message === 'string' ? <p>{message}</p> : message}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="bg-ulacm-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <button
                        type="button"
                        onClick={onConfirm}
                        className={`w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm transition-colors ${confirmButtonClass}`}
                    >
                        {confirmButtonText}
                    </button>
                    <button
                        type="button"
                        onClick={onCancel}
                        className="mt-3 w-full inline-flex justify-center rounded-md border border-ulacm-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-ulacm-gray-700 hover:bg-ulacm-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ulacm-primary-light sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
                    >
                        {cancelButtonText}
                    </button>
                </div>
            </div>
        </div>
    </div>
  );
};

export default ConfirmationModal;
