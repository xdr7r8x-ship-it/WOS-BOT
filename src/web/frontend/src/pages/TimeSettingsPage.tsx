import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function TimeSettingsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['time-settings'],
    queryFn: () => api.reminders.timeSettings(),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.timeSettings</h1>
      <div className="card">
        {isLoading ? <p className="text-gray-400">Loading...</p> :
         <div className="space-y-4">
           <div className="flex justify-between">
             <span className="text-gray-400">Game Timezone</span>
             <span className="text-white">{(data as any)?.game_timezone || 'UTC'}</span>
           </div>
           <div className="flex justify-between">
             <span className="text-gray-400">Real Timezone</span>
             <span className="text-white">{(data as any)?.real_timezone || 'UTC'}</span>
           </div>
         </div>
        }
      </div>
    </div>
  );
}