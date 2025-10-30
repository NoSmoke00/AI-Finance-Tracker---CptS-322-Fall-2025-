'use client';

import { useEffect, useState } from 'react';
import { insightsApi } from '@/lib/api';
import InsightCard from './InsightCard';

export default function InsightsSummary() {
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await insightsApi.list();
        setInsights((res || []).slice(0, 3));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return (
    <div className="text-center py-4">
      <p className="text-gray-600">Loading insights...</p>
    </div>
  );
  
  if (!insights.length) return (
    <div className="text-center py-8">
      <p className="text-gray-600 mb-2">No new insights</p>
      <p className="text-sm text-gray-500">Generate insights to get personalized financial recommendations</p>
      <a href="/insights" className="mt-4 inline-block text-sm text-blue-600 hover:text-blue-800 font-medium">
        Generate Insights →
      </a>
    </div>
  );

  return (
    <div className="space-y-3">
      {insights.map((i) => (
        <InsightCard key={i.id} insight={i} />
      ))}
    </div>
  );
}


