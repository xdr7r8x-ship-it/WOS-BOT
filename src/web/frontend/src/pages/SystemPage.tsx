import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function SystemPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['system-status'],
    queryFn: () => api.system.status(),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.system</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Memory</h2>
          {isLoading ? <p className="text-gray-400">Loading...</p> :
           <div className="space-y-2">
             <p className="text-white">Used: {(data as any)?.memory_used_mb || 0} MB</p>
             <p className="text-white">Total: {(data as any)?.memory_total_mb || 0} MB</p>
           </div>
          }
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Disk</h2>
          {isLoading ? <p className="text-gray-400">Loading...</p> :
           <div className="space-y-2">
             <p className="text-white">Used: {(data as any)?.disk_used_gb || 0} GB</p>
             <p className="text-white">Total: {(data as any)?.disk_total_gb || 0} GB</p>
           </div>
          }
        </div>
      </div>
    </div>
  );
}