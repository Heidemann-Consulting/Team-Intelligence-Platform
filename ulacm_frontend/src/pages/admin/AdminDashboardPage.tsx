// File: ulacm_frontend/src/pages/admin/AdminDashboardPage.tsx
// Purpose: Dashboard page for administrators.
// Refinements: Similar improvements as Team Dashboard.

import React from 'react';
import { Link } from 'react-router-dom';
// import { Users, ShieldAlert, Activity, BarChart } from 'lucide-react'; // Example icons
import { Users, Activity, NotepadTextDashed, Workflow } from 'lucide-react'; // Example icons

const AdminDashboardPage: React.FC = () => {
  const adminQuickLinks = [
    { title: 'Manage Teams', icon: Users, path: '/admin/teams', description: 'View, create, and manage team accounts.' },
    { title: 'Manage Templates', icon: NotepadTextDashed, path: '/admin/templates', description: 'View, create, and manage templates.' },
    { title: 'Manage Workflows', icon: Workflow, path: '/admin/workflows', description: 'View, create, and manage workflows.' },
    // { title: 'System Stats', icon: BarChart, path: '/admin/stats', description: 'View usage statistics (future).' },
    // { title: 'Security Logs', icon: ShieldAlert, path: '/admin/logs', description: 'Review important security events (future).' },
  ];

  return (
    <div className="space-y-8">
       {/* Header */}
      <header className="bg-gradient-to-r from-ulacm-secondary to-pink-600 text-white shadow-lg rounded-xl p-6 md:p-8"> {/* Gradient header */}
        <h1 className="text-3xl md:text-4xl font-bold">
          Administrator Dashboard
        </h1>
        <p className="mt-2 text-pink-100">
          Manage Team Intelligence Platform team accounts, templates and workflows and monitor the system.
        </p>
      </header>

      {/* Admin Tools */}
      <section>
        <h2 className="text-2xl font-semibold text-ulacm-gray-700 mb-5">Admin Tools</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {adminQuickLinks.map((card) => (
            <Link
              key={card.title}
              to={card.path}
              className="block bg-white p-6 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-200 group border border-ulacm-gray-100 hover:border-ulacm-secondary" /* Hover effect */
            >
              <card.icon className="h-10 w-10 text-ulacm-secondary mb-4 group-hover:scale-110 transition-transform duration-200" />
              <h3 className="text-lg font-semibold text-ulacm-gray-800 mb-1 group-hover:text-ulacm-secondary transition-colors">{card.title}</h3>
              <p className="text-sm text-ulacm-gray-600">{card.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* System Overview Placeholder */}
      <section>
         <h2 className="text-2xl font-semibold text-ulacm-gray-700 mb-5 flex items-center">
            <Activity size={24} className="mr-2 text-ulacm-gray-400"/> System Overview
        </h2>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-ulacm-gray-100 min-h-[150px] flex items-center justify-center">
          <p className="text-ulacm-gray-500 italic">System statistics coming soon...</p>
        </div>
      </section>
    </div>
  );
};

export default AdminDashboardPage;
