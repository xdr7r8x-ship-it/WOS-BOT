import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthProvider';
import DashboardLayout from './layout/DashboardLayout';
import LoginPage from './pages/LoginPage';
import OverviewPage from './pages/OverviewPage';
import GiftCodesPage from './pages/GiftCodesPage';
import PlayersPage from './pages/PlayersPage';
import PlayerPanelPage from './pages/PlayerPanelPage';
import AlliancesPage from './pages/AlliancesPage';
import AllianceApiPage from './pages/AllianceApiPage';
import RemindersPage from './pages/RemindersPage';
import TimeSettingsPage from './pages/TimeSettingsPage';
import ContentPage from './pages/ContentPage';
import AdminsPage from './pages/AdminsPage';
import SecurityPage from './pages/SecurityPage';
import SystemPage from './pages/SystemPage';
import BackupsPage from './pages/BackupsPage';
import UpdatesPage from './pages/UpdatesPage';
import AuditLogsPage from './pages/AuditLogsPage';
import SettingsPage from './pages/SettingsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-400 flex items-center justify-center">
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <LoginPage />;
  }
  
  return <DashboardLayout>{children}</DashboardLayout>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<ProtectedRoute><OverviewPage /></ProtectedRoute>} />
      <Route path="/gift-codes" element={<ProtectedRoute><GiftCodesPage /></ProtectedRoute>} />
      <Route path="/players" element={<ProtectedRoute><PlayersPage /></ProtectedRoute>} />
      <Route path="/player-panel" element={<ProtectedRoute><PlayerPanelPage /></ProtectedRoute>} />
      <Route path="/alliances" element={<ProtectedRoute><AlliancesPage /></ProtectedRoute>} />
      <Route path="/alliance-api" element={<ProtectedRoute><AllianceApiPage /></ProtectedRoute>} />
      <Route path="/reminders" element={<ProtectedRoute><RemindersPage /></ProtectedRoute>} />
      <Route path="/time-settings" element={<ProtectedRoute><TimeSettingsPage /></ProtectedRoute>} />
      <Route path="/content" element={<ProtectedRoute><ContentPage /></ProtectedRoute>} />
      <Route path="/admins" element={<ProtectedRoute><AdminsPage /></ProtectedRoute>} />
      <Route path="/security" element={<ProtectedRoute><SecurityPage /></ProtectedRoute>} />
      <Route path="/system" element={<ProtectedRoute><SystemPage /></ProtectedRoute>} />
      <Route path="/backups" element={<ProtectedRoute><BackupsPage /></ProtectedRoute>} />
      <Route path="/updates" element={<ProtectedRoute><UpdatesPage /></ProtectedRoute>} />
      <Route path="/audit-logs" element={<ProtectedRoute><AuditLogsPage /></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
