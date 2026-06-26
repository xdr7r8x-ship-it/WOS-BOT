import React from 'react';
import { useAuth } from '../auth/AuthProvider';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.settings</h1>
      <div className="card">
        <div className="space-y-4">
          <div>
            <label className="label">User ID</label>
            <p className="text-white">{user?.user_id}</p>
          </div>
          <div>
            <label className="label">Role</label>
            <p className="text-white">{user?.role}</p>
          </div>
          <div>
            <label className="label">Permissions</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {user?.permissions?.map((perm, i) => (
                <span key={i} className="px-2 py-1 bg-dark-300 text-gray-300 text-xs rounded">{perm}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}