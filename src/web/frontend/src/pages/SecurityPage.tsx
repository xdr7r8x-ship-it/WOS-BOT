import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function SecurityPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['security-incidents'],
    queryFn: () => api.security.incidents(50),
  });

  const incidents = (data as any)?.incidents || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.security</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : incidents.length === 0 ? (
          <p className="text-gray-400">No incidents</p>
        ) : (
          <div className="space-y-2">
            {incidents.map((incident: any, i: number) => (
              <div key={i} className="p-3 bg-dark-300 rounded-lg">
                <p className="text-white">{incident.type}</p>
                <p className="text-gray-400 text-sm">{incident.created_at}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}