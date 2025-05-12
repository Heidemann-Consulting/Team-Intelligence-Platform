// File: ulacm_frontend/src/pages/team/TeamDashboardPage.tsx
// Purpose: Dashboard page for authenticated team users.
// Refinements: Added subtle hover effects, adjusted spacing.

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Link } from 'react-router-dom';
// import { FileText, FileCode2, FolderGit2, Search, PlusCircle, Activity } from 'lucide-react';
import { FileText, FolderGit2, Activity } from 'lucide-react';

const TeamDashboardPage: React.FC = () => {
  const { currentTeam } = useAuth();

  const quickLinkCards = [
    { title: 'Manage Knowledge', icon: FileText, path: '/app/documents', description: 'Access and manage your team documents.' },
    { title: 'Run Workflows', icon: FolderGit2, path: '/app/execute-workflow', description: 'Automate tasks with AI workflows.' },
    // { title: 'Search Documents', icon: Search, path: '/app/search', description: 'Search for specific documents.' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <header className="bg-gradient-to-r from-ulacm-primary to-blue-600 text-white shadow-lg rounded-xl p-6 md:p-8"> {/* Gradient header */}
        <h1 className="text-3xl md:text-4xl font-bold">
          Welcome, {currentTeam?.team_name || 'Team User'}!
        </h1>
        <p className="mt-2 text-blue-100">
          Your Team Intelligence Platform dashboard. Manage documents and run workflows efficiently.
        </p>
      </header>

      {/* Quick Actions */}
      <section>
        <h2 className="text-2xl font-semibold text-ulacm-gray-700 mb-5">Quick Actions</h2> {/* Increased margin */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickLinkCards.map((card) => (
            <Link
              key={card.title}
              to={card.path}
              className="block bg-white p-6 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-200 group border border-ulacm-gray-100 hover:border-ulacm-primary" /* Hover effect */
            >
              <card.icon className="h-10 w-10 text-ulacm-primary mb-4 group-hover:scale-110 transition-transform duration-200" /> {/* Larger margin */}
              <h3 className="text-lg font-semibold text-ulacm-gray-800 mb-1 group-hover:text-ulacm-primary transition-colors">{card.title}</h3>
              <p className="text-sm text-ulacm-gray-600">{card.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Recent Activity Placeholder */}
      <section>
        <h2 className="text-2xl font-semibold text-ulacm-gray-700 mb-5 flex items-center">
            <Activity size={24} className="mr-2 text-ulacm-gray-400"/> Recent Activity
        </h2>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-ulacm-gray-100 min-h-[150px] flex items-center justify-center">
          <p className="text-ulacm-gray-500 italic">Recent activity feed coming soon...</p>
        </div>
      </section>
    </div>
  );
};

export default TeamDashboardPage;
