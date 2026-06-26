import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export default function PlayersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  
  const { data: playersData, isLoading } = useQuery({
    queryKey: ['players', search],
    queryFn: () => api.players.list({ search: search || undefined, limit: 50 }),
  });

  const disableMutation = useMutation({
    mutationFn: (playerId: string) => api.players.disable(playerId),
    onSuccess: () => queryClient.invalidateQueries(['players']),
  });

  const players = (playersData as any)?.players || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.players</h1>
      
      <div className="card mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search players..."
          className="input"
        />
      </div>

      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : players.length === 0 ? (
          <p className="text-gray-400">No players found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-100">
                  <th className="pb-3">ID</th>
                  <th className="pb-3">Nickname</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player: any, i: number) => (
                  <tr key={i} className="border-b border-dark-100">
                    <td className="py-3 text-white">{player.player_id}</td>
                    <td className="py-3 text-gray-300">{player.nickname || '-'}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${player.disabled ? 'bg-red-600' : 'bg-green-600'}`}>
                        {player.disabled ? 'Disabled' : 'Active'}
                      </span>
                    </td>
                    <td className="py-3">
                      <button
                        onClick={() => disableMutation.mutate(player.player_id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        {player.disabled ? 'Enable' : 'Disable'}
                      </button>
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