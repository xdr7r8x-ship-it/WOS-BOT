import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function AlliancesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['alliances'],
    queryFn: () => api.alliances.list(),
  });

  const alliances = (data as any)?.alliances || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.alliances</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : alliances.length === 0 ? (
          <p className="text-gray-400">No alliances found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-100">
                  <th className="pb-3">Name</th>
                  <th className="pb-3">Tag</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {alliances.map((alliance: any, i: number) => (
                  <tr key={i} className="border-b border-dark-100">
                    <td className="py-3 text-white">{alliance.name}</td>
                    <td className="py-3 text-gray-300">[{alliance.tag}]</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${alliance.disabled ? 'bg-red-600' : 'bg-green-600'}`}>
                        {alliance.disabled ? 'Disabled' : 'Active'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}