// File: ulacm_frontend/src/layouts/AdminLayout.tsx
// Purpose: Layout component for the admin interface.
// Updated: Added links for Template and Workflow Management for Admins.

import React, { ReactNode } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { LogOut, LayoutDashboard, Users, Shield, NotepadTextDashed, Workflow } from 'lucide-react'; // Added FileCode2, FolderGit2
import { useAuth } from '@/contexts/AuthContext';

interface AdminLayoutProps {
  children: ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { logout, isAdminAuthenticated } = useAuth(); // isAdminAuthenticated for potential display logic

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Admin logout failed:", error);
    }
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center px-3 py-2.5 rounded-lg transition-colors duration-150 ease-in-out text-sm font-medium group ${
      isActive
        ? 'bg-ulacm-secondary/10 text-ulacm-secondary font-semibold shadow-sm border border-ulacm-secondary/20'
        : 'text-ulacm-gray-600 hover:bg-ulacm-gray-100 hover:text-ulacm-secondary'
    }`;
  const iconClass = "mr-3 h-5 w-5 flex-shrink-0";

  if (!isAdminAuthenticated) { // Basic check, though AdminProtectedRoute should handle this
    return null; // Or a redirect, but usually handled by the route protector
  }

  return (
    <div className="flex h-screen bg-ulacm-gray-50">
      <aside className="w-64 flex-shrink-0 bg-white border-r border-ulacm-gray-200 flex flex-col shadow-sm">
        <div className="h-16 flex items-center justify-center px-4 border-b border-ulacm-gray-200">
          <Link to="/admin/dashboard" className="flex items-center text-xl font-bold text-ulacm-primary hover:opacity-80 transition-opacity">
            <img src="../tip-logo-only-32-transparent.png" alt="TIP Logo"/>Team Intelligence Platform Admin
          </Link>
        </div>
        <nav className="flex-grow p-3 space-y-1 overflow-y-auto">
          <NavLink to="/admin/dashboard" className={navLinkClass} end>
            <LayoutDashboard className={iconClass} /> Admin Dashboard
          </NavLink>
          <NavLink to="/admin/teams" className={navLinkClass}>
            <Users className={iconClass} /> Team Management
          </NavLink>
          {/* New Links for Admin to manage Templates and Workflows */}
          <NavLink to="/admin/templates" className={navLinkClass}>
            <NotepadTextDashed className={iconClass} /> Template Management
          </NavLink>
          <NavLink to="/admin/workflows" className={navLinkClass}>
            <Workflow className={iconClass} /> Workflow Management
          </NavLink>
        </nav>
        <div className="p-4 border-t border-ulacm-gray-200 mt-auto">
          <div className="mb-3 text-sm p-3 bg-ulacm-gray-50 rounded-lg border border-ulacm-gray-200">
            <p className="font-semibold text-ulacm-gray-800">Administrator</p>
            <p className="text-ulacm-gray-500 flex items-center"><Shield size={14} className="mr-1 text-ulacm-secondary"/> Privileged Access</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-3 py-2.5 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors duration-150 ease-in-out shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1"
          >
            <LogOut className="mr-2 h-5 w-5" /> Logout Admin
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="p-6 md:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
