// File: ulacm_frontend/src/App.tsx
// Purpose: Main application component, sets up routing and global layout.
// Updated: Routing changes for Admin T/W management and Team Workflow Execution.

import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { AuthProvider } from '@/contexts/AuthContext';

import MainLayout from '@/layouts/MainLayout';
import AdminLayout from '@/layouts/AdminLayout';

import ProtectedRoute from '@/components/common/ProtectedRoute';
import AdminProtectedRoute from '@/components/common/AdminProtectedRoute';

// Public pages
import LoginPage from '@/pages/LoginPage';
import AdminLoginPage from '@/pages/AdminLoginPage';
import NotFoundPage from '@/pages/NotFoundPage';

// Team User pages
import TeamDashboardPage from '@/pages/team/TeamDashboardPage';
import ContentListPage from '@/pages/team/ContentListPage'; // Used for Documents (Team) and T/W (Admin)
import EditorViewPage from '@/pages/team/EditorViewPage';   // Used for Documents (Team) and T/W (Admin)
import SearchPage from '@/pages/team/SearchPage';
import ExecuteWorkflowPage from '@/pages/team/ExecuteWorkflowPage'; // New page

// Admin pages
import AdminDashboardPage from '@/pages/admin/AdminDashboardPage';
import TeamManagementPage from '@/pages/admin/TeamManagementPage';

const AppLayout = () => (
  <MainLayout>
    <Outlet />
  </MainLayout>
);

const AdminAppLayout = () => (
  <AdminLayout>
    <Outlet />
  </AdminLayout>
);

function AppContent() {
  return (
    <>
      <Toaster position="top-right" reverseOrder={false} />
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />

        {/* Team User Protected Routes */}
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<TeamDashboardPage />} />
          {/* Teams only manage Documents directly now */}
          <Route path="documents" element={<ContentListPage />} />
          <Route path="documents/:itemId" element={<EditorViewPage />} />
          {/* 'new' document creation is via modal, then redirects to /documents/:itemId */}
          {/* New Execute Workflow page for Teams */}
          <Route path="execute-workflow" element={<ExecuteWorkflowPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route index element={<Navigate to="dashboard" replace />} />
        </Route>

        {/* Admin Protected Routes */}
        <Route
          path="/admin"
          element={
            <AdminProtectedRoute>
              <AdminAppLayout />
            </AdminProtectedRoute>
          }
        >
          <Route path="dashboard" element={<AdminDashboardPage />} />
          <Route path="teams" element={<TeamManagementPage />} />
          {/* Admin Management of Templates */}
          <Route path="templates" element={<ContentListPage />} /> {/* Reuses ContentListPage, contextually for Admin */}
          <Route path="templates/new" element={<EditorViewPage />} /> {/* Reuses EditorViewPage for Admin */}
          <Route path="templates/:itemId" element={<EditorViewPage />} /> {/* Reuses EditorViewPage for Admin */}
          {/* Admin Management of Workflows */}
          <Route path="workflows" element={<ContentListPage />} /> {/* Reuses ContentListPage for Admin */}
          <Route path="workflows/new" element={<EditorViewPage />} /> {/* Reuses EditorViewPage for Admin */}
          <Route path="workflows/:itemId" element={<EditorViewPage />} /> {/* Reuses EditorViewPage for Admin */}
          <Route index element={<Navigate to="dashboard" replace />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
