import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export default function GiftCodesPage() {
  const queryClient = useQueryClient();
  const [codeInput, setCodeInput] = useState('');
  
  const { data: codesData, isLoading } = useQuery({
    queryKey: ['gift-codes'],
    queryFn: () => api.giftCodes.list({ limit: 50 }),
  });

  const redeemMutation = useMutation({
    mutationFn: (code: string) => api.giftCodes.redeem(code),
    onSuccess: () => {
      queryClient.invalidateQueries(['gift-codes']);
      setCodeInput('');
    },
  });

  const handleRedeem = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    if (codeInput.trim()) {
      redeemMutation.mutate(codeInput.trim());
    }
  };

  const codes = (codesData as any)?.codes || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.giftCodes</h1>
      
      <div className="card mb-6">
        <form onSubmit={handleRedeem} className="flex gap-4">
          <input
            type="text"
            value={codeInput}
            onChange={(e) => setCodeInput(e.target.value)}
            placeholder="Enter gift code..."
            className="input flex-1"
          />
          <button
            type="submit"
            disabled={redeemMutation.isLoading}
            className="btn btn-primary"
          >
            {redeemMutation.isLoading ? 'Processing...' : 'Redeem'}
          </button>
        </form>
        {redeemMutation.isError && (
          <p className="text-red-500 mt-2">Failed to redeem code</p>
        )}
        {redeemMutation.isSuccess && (
          <p className="text-green-500 mt-2">Code submitted successfully</p>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">giftCodes.queue</h2>
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : codes.length === 0 ? (
          <p className="text-gray-400">No codes found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-dark-100">
                  <th className="pb-3">Code</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Submitted</th>
                </tr>
              </thead>
              <tbody>
                {codes.map((code: any, i: number) => (
                  <tr key={i} className="border-b border-dark-100">
                    <td className="py-3 text-white">{code.code_hash}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs ${
                        code.status === 'completed' ? 'bg-green-600' :
                        code.status === 'failed' ? 'bg-red-600' :
                        'bg-yellow-600'
                      }`}>
                        {code.status}
                      </span>
                    </td>
                    <td className="py-3 text-gray-400">{code.submitted_at}</td>
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