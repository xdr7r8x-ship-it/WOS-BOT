import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
import { Menu, X, LayoutDashboard, Gift, Users, Shield, Settings, LogOut } from 'lucide-react';

const navItems = [
  { path: '/', label: 'nav.overview', icon: LayoutDashboard },
  { path: '/gift-codes', label: 'nav.giftCodes', icon: Gift },
  { path: '/players', label: 'nav.players', icon: Users },
  { path: '/alliances', label: 'nav.alliances', icon: Users },
  { path: '/reminders', label: 'nav.reminders', icon: Settings },
  { path: '/admins', label: 'nav.admins', icon: Shield },
  { path: '/security', label: 'nav.security', icon: Shield },
  { path: '/system', label: 'nav.system', icon: Settings },
  { path: '/backups', label: 'nav.backups', icon: Settings },
  { path: '/updates', label: 'nav.updates', icon: Settings },
  { path: '/audit-logs', label: 'nav.auditLogs', icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-dark-400 flex">
      <aside className={`fixed inset-y-0 right-0 z-50 w-64 bg-dark-300 transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-dark-100">
            <h1 className="text-xl font-bold text-white">WOS-BOT</h1>
            <p className="text-sm text-gray-400 mt-1">Dashboard</p>
          </div>
          
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-300 hover:bg-dark-200 hover:text-white'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
          
          <div className="p-4 border-t border-dark-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
                <span className="text-white font-medium">{user?.user_id?.slice(0, 2) || '??'}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user?.user_id || 'Unknown'}</p>
                <p className="text-xs text-gray-400">{user?.role || 'Unknown'}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <LogOut size={18} />
              <span>auth.logout</span>
            </button>
          </div>
        </div>
      </aside>

      <div className="flex-1 lg:mr-64">
        <header className="sticky top-0 z-40 bg-dark-300 border-b border-dark-100 px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              className="lg:hidden p-2 text-gray-400 hover:text-white"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="flex-1" />
          </div>
        </header>
        
        <main className="p-6">
          {children}
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
