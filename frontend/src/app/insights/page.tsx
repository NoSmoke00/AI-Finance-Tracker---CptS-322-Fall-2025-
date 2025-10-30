'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import InsightCard from '@/components/InsightCard';
import { insightsApi } from '@/lib/api';

export default function InsightsPage() {
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [active, setActive] = useState<'alert'|'warning'|'info'|'success'|'tip'>('alert');

  const load = async () => {
    setLoading(true);
    try {
      const res = await insightsApi.list();
      setInsights(res || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      await insightsApi.generate();
      await load();
    } finally {
      setGenerating(false);
    }
  };

  const onDismiss = async (id: number) => {
    await insightsApi.dismiss(id);
    await load();
  };

  const onAction = (i: any) => {
    if ((i.action || '').toLowerCase().includes('transaction')) {
      window.location.href = '/transactions';
    }
  };

  const groups: Record<string, any[]> = { alert: [], warning: [], info: [], success: [], tip: [] };
  for (const i of insights) {
    (groups[i.type] ||= []).push(i);
  }

  const tabs: { key: 'alert'|'warning'|'info'|'success'|'tip'; label: string; color: string }[] = [
    { key: 'alert', label: 'Alerts', color: 'text-red-600' },
    { key: 'warning', label: 'Warnings', color: 'text-yellow-600' },
    { key: 'info', label: 'Info', color: 'text-blue-600' },
    { key: 'success', label: 'Success', color: 'text-green-600' },
    { key: 'tip', label: 'Tips', color: 'text-purple-600' },
  ];

  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        <main className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">AI Insights</h1>
            <button onClick={handleGenerate} disabled={generating} className="px-4 py-2 rounded-full bg-purple-600 text-white disabled:opacity-50 shadow-sm hover:bg-purple-700">
              {generating ? 'Generating…' : 'Generate New Insights'}
            </button>
          </div>

          {loading ? (
            <div className="bg-white shadow rounded-lg p-6 text-center">Loading…</div>
          ) : (
            <>
              <div className="bg-white shadow rounded-xl p-2 flex flex-wrap gap-2">
                {tabs.map((t) => (
                  <button
                    key={t.key}
                    onClick={() => setActive(t.key)}
                    className={`px-3 py-1.5 rounded-full text-sm ${active === t.key ? `${t.color} bg-gray-100` : 'text-gray-700 hover:bg-gray-50'}`}
                  >
                    {t.label} <span className="ml-1 text-xs text-gray-500">({groups[t.key]?.length || 0})</span>
                  </button>
                ))}
              </div>

              <div className="mt-4 space-y-3">
                {(groups[active] || []).length ? (
                  groups[active].map((i) => (
                    <InsightCard key={i.id} insight={i} onDismiss={onDismiss} onAction={onAction} />
                  ))
                ) : (
                  <div className="bg-white shadow rounded-lg p-6 text-center text-gray-600">No {tabs.find(t => t.key === active)?.label.toLowerCase()}.</div>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </AppLayout>
  );
}


