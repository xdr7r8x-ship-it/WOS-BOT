import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function PlayerPanelPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['player-panel-status'],
    queryFn: () => api.playerPanel.status(),
  });

  const d = data as any;

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.playerPanel</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Status</span>
              <span className={`px-2 py-1 rounded text-xs ${d?.enabled ? 'bg-green-600' : 'bg-red-600'}`}>
                {d?.enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Register Channel</span>
              <span className="text-white">{d?.register_channel || 'Not set'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Registered Count</span>
              <span className="text-white">{d?.registered_count || 0}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}