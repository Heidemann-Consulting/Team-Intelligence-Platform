// File: ulacm_frontend/src/layouts/MainLayout.tsx
// Purpose: Layout component for the main application (team user interface).
// Updated: Removed direct Template/Workflow management links for teams. Added "Execute Workflows" link.

import React, { ReactNode } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { LogOut, LayoutDashboard, FileText, FolderGit2 as ExecuteIcon } from 'lucide-react'; // Using Zap for Execute
import { useAuth } from '@/contexts/AuthContext';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { currentTeam, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed in MainLayout:", error);
    }
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center px-3 py-2.5 rounded-lg transition-colors duration-150 ease-in-out text-sm font-medium group ${
      isActive
        ? 'bg-ulacm-primary/10 text-ulacm-primary font-semibold shadow-sm border border-ulacm-primary/20'
        : 'text-ulacm-gray-600 hover:bg-ulacm-gray-100 hover:text-ulacm-primary'
    }`;
  const iconClass = "mr-3 h-5 w-5 flex-shrink-0";

  return (
    <div className="flex h-screen bg-ulacm-gray-50">
      <aside className="w-64 flex-shrink-0 bg-white border-r border-ulacm-gray-200 flex flex-col shadow-sm">
        <div className="h-16 flex items-center justify-center px-4 border-b border-ulacm-gray-200">
          <Link to="/app/dashboard" className="flex items-center text-xl font-bold text-ulacm-primary hover:opacity-80 transition-opacity">
            <img src="../tip-logo-only-32-transparent.png" alt="TIP Logo" className="h-8 w-8 mr-2" />Team Intelligence Platform
          </Link>
        </div>
        <nav className="flex-grow p-3 space-y-1 overflow-y-auto">
          <NavLink to="/app/dashboard" className={navLinkClass} end>
            <LayoutDashboard className={iconClass} /> Dashboard
          </NavLink>
          <NavLink to="/app/documents" className={navLinkClass}>
            <FileText className={iconClass} /> Manage Knowledge
          </NavLink>
          {/* New "Execute Workflows" link for teams */}
          <NavLink to="/app/execute-workflow" className={navLinkClass}>
            <ExecuteIcon className={iconClass} /> Run Workflows
          </NavLink>
          {/* <NavLink to="/app/search" className={navLinkClass}>
            <Search className={iconClass} /> Search
          </NavLink> */}
        </nav>
        <div className="p-4 border-t border-ulacm-gray-200 mt-auto">
           {currentTeam && (
            <div className="mb-3 text-sm p-3 bg-ulacm-gray-50 rounded-lg border border-ulacm-gray-200">
               <p className="font-semibold text-ulacm-gray-800 truncate" title={currentTeam.team_name}>{currentTeam.team_name}</p>
              <p className="text-ulacm-gray-500 truncate" title={currentTeam.username}>@{currentTeam.username}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-3 py-2.5 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors duration-150 ease-in-out shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1"
          >
            <LogOut className="mr-2 h-5 w-5" /> Logout
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

export default MainLayout;
