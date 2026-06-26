import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Activity, Users, Gift, Clock, Database } from 'lucide-react';

export default function OverviewPage() {
  const { data: liveData, isLoading } = useQuery({
    queryKey: ['dashboard-live'],
    queryFn: () => api.dashboard.live(),
    refetchInterval: 30000,
  });

  const d = liveData as any;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  const stats = [
    { label: 'botStatus', value: d?.bot_status === 'online' ? 'online' : 'offline', icon: Activity, color: d?.bot_status === 'online' ? 'text-green-500' : 'text-red-500' },
    { label: 'uptime', value: d?.uptime || 'N/A', icon: Clock, color: 'text-blue-500' },
    { label: 'playersCount', value: d?.players_count || 0, icon: Users, color: 'text-purple-500' },
    { label: 'activePlayers', value: d?.active_players || 0, icon: Users, color: 'text-green-500' },
    { label: 'queueSize', value: d?.queue_size || 0, icon: Gift, color: 'text-yellow-500' },
    { label: 'memory', value: `${d?.memory_percent || 0}%`, icon: Database, color: 'text-orange-500' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">{stat.label}</p>
                  <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-dark-300 ${stat.color}`}>
                  <Icon size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">codeStats</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Processed</span>
              <span className="text-white">{d?.code_stats?.processed || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Success</span>
              <span className="text-green-500">{d?.code_stats?.success || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Failed</span>
              <span className="text-red-500">{d?.code_stats?.failed || 0}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">reminderStats</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Active</span>
              <span className="text-white">{d?.reminder_stats?.active || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Delivered</span>
              <span className="text-green-500">{d?.reminder_stats?.delivered || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}