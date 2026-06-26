import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function AdminsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['admins'],
    queryFn: () => api.admins.list(),
  });

  const admins = (data as any)?.admins || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.admins</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : admins.length === 0 ? (
          <p className="text-gray-400">No admins</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-100">
                  <th className="pb-3">User ID</th>
                  <th className="pb-3">Role</th>
                </tr>
              </thead>
              <tbody>
                {admins.map((admin: any, i: number) => (
                  <tr key={i} className="border-b border-dark-100">
                    <td className="py-3 text-white">{admin.user_id}</td>
                    <td className="py-3 text-gray-300">{admin.role}</td>
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