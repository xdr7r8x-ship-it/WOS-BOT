import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function RemindersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['reminders'],
    queryFn: () => api.reminders.list({ limit: 50 }),
  });

  const reminders = (data as any)?.reminders || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.reminders</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : reminders.length === 0 ? (
          <p className="text-gray-400">No reminders found</p>
        ) : (
          <div className="space-y-3">
            {reminders.map((reminder: any, i: number) => (
              <div key={i} className="p-4 bg-dark-300 rounded-lg">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-white font-medium">{reminder.event_name}</p>
                    <p className="text-gray-400 text-sm">{reminder.event_time}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${reminder.status === 'active' ? 'bg-green-600' : 'bg-gray-600'}`}>
                    {reminder.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}