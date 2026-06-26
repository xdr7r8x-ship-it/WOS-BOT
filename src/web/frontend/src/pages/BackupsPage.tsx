import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export default function BackupsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['backups'],
    queryFn: () => api.backups.list(),
  });

  const createMutation = useMutation({
    mutationFn: () => api.backups.create(),
    onSuccess: () => queryClient.invalidateQueries(['backups']),
  });

  const backups = (data as any)?.backups || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.backups</h1>
      <div className="card mb-6">
        <button onClick={() => createMutation.mutate()} disabled={createMutation.isLoading} className="btn btn-primary">
          {createMutation.isLoading ? 'Creating...' : 'Create Backup'}
        </button>
      </div>
      <div className="card">
        {isLoading ? <p className="text-gray-400">Loading...</p> :
         backups.length === 0 ? <p className="text-gray-400">No backups</p> :
         <div className="space-y-2">
           {backups.map((backup: any, i: number) => (
             <div key={i} className="p-3 bg-dark-300 rounded-lg flex justify-between items-center">
               <div>
                 <p className="text-white">{backup.name}</p>
                 <p className="text-gray-400 text-sm">{backup.created_at}</p>
               </div>
             </div>
           ))}
         </div>
        }
      </div>
    </div>
  );
}