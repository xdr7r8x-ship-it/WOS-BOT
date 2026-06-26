import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function AuditLogsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => api.audit.logs({ limit: 100 }),
  });

  const logs = (data as any)?.logs || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.auditLogs</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : logs.length === 0 ? (
          <p className="text-gray-400">No logs</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-100">
                  <th className="pb-3">Actor</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Result</th>
                  <th className="pb-3">Time</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log: any, i: number) => (
                  <tr key={i} className="border-b border-dark-100">
                    <td className="py-3 text-white">{log.actor_id}</td>
                    <td className="py-3 text-gray-300">{log.action}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${log.result === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
                        {log.result}
                      </span>
                    </td>
                    <td className="py-3 text-gray-400 text-sm">{log.created_at}</td>
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