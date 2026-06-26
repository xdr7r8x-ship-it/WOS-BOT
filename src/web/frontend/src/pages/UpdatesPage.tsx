import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../api/client';

export default function UpdatesPage() {
  const { data, refetch } = useQuery({
    queryKey: ['updates'],
    queryFn: () => api.updates.check(),
  });

  const applyMutation = useMutation({
    mutationFn: () => api.updates.apply(),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.updates</h1>
      <div className="card mb-6">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-gray-400">Current Version</p>
            <p className="text-white text-xl">{(data as any)?.current_version || 'Unknown'}</p>
          </div>
          <button onClick={() => refetch()} className="btn btn-primary">Check Updates</button>
        </div>
      </div>
      <div className="card">
        <p className="text-gray-400">
          {(data as any)?.update_available ? `Update ${(data as any)?.latest_version} available` : 'No updates available'}
        </p>
        {(data as any)?.update_available && (
          <button onClick={() => applyMutation.mutate()} disabled={applyMutation.isLoading} className="btn btn-primary mt-4">
            {applyMutation.isLoading ? 'Applying...' : 'Apply Update'}
          </button>
        )}
      </div>
    </div>
  );
}