import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

export default function ContentPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['content-pages'],
    queryFn: () => api.content.pages(),
  });

  const pages = (data as any)?.pages || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">nav.content</h1>
      <div className="card">
        {isLoading ? <p className="text-gray-400">Loading...</p> : 
         pages.length === 0 ? <p className="text-gray-400">No content pages</p> :
         <div className="space-y-2">
           {pages.map((page: any, i: number) => (
             <div key={i} className="p-3 bg-dark-300 rounded-lg">
               <p className="text-white">{page.key}</p>
             </div>
           ))}
         </div>
        }
      </div>
    </div>
  );
}