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

  if (loading) return null;
  if (!insights.length) return (
    <div className="bg-white shadow rounded-lg p-4">
      <div className="text-gray-700">No new insights. Check back after more transactions.</div>
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


