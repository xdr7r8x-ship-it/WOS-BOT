import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../api/client';

export default function AllianceApiPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['alliance-api-health'],
    queryFn: () => api.allianceApi.health(),
  });

  const syncMutation = useMutation({
    mutationFn: () => api.allianceApi.sync(),
  });

  const d = data as any;

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.allianceApi</h1>
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-400">Health Status</p>
            <p className={`text-2xl font-bold ${d?.healthy ? 'text-green-500' : 'text-red-500'}`}>
              {isLoading ? 'Loading...' : d?.status || 'Unknown'}
            </p>
          </div>
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isLoading}
            className="btn btn-primary"
          >
            {syncMutation.isLoading ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>
      </div>
    </div>
  );
}