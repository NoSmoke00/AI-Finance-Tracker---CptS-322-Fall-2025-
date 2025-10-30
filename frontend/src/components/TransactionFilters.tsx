'use client';

import { useState, useEffect } from 'react';
import { transactionsApi } from '@/lib/api';

type Preset = '7' | '30' | '90' | 'custom';

interface Props {
  accounts: { id: number; name: string }[];
  categories: string[];
  onChange: (filters: {
    start_date?: string;
    end_date?: string;
    account_id?: number;
    category?: string;
    search?: string;
  }) => void;
  onSync: () => Promise<void>;
}

export default function TransactionFilters({ accounts, categories, onChange, onSync }: Props) {
  const [preset, setPreset] = useState<Preset>('30');
  const [startDate, setStartDate] = useState<string | undefined>();
  const [endDate, setEndDate] = useState<string | undefined>();
  const [accountId, setAccountId] = useState<number | undefined>();
  const [category, setCategory] = useState<string | undefined>();
  const [search, setSearch] = useState<string>('');
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    const today = new Date();
    if (preset !== 'custom') {
      const days = parseInt(preset, 10);
      const start = new Date(today);
      start.setDate(start.getDate() - (days - 1));
      setStartDate(start.toISOString().slice(0, 10));
      setEndDate(today.toISOString().slice(0, 10));
    }
  }, [preset]);

  useEffect(() => {
    onChange({ start_date: startDate, end_date: endDate, account_id: accountId, category, search });
    // intentionally exclude onChange to avoid new reference causing loops
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate, accountId, category, search]);

  const handleSync = async () => {
    try {
      setSyncing(true);
      await onSync();
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-4 text-gray-800">
      <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
        <select value={preset} onChange={(e) => setPreset(e.target.value as Preset)} className="border rounded px-2 py-1 text-gray-800">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 3 months</option>
          <option value="custom">Custom</option>
        </select>

        <input type="date" value={startDate || ''} onChange={(e) => { setPreset('custom'); setStartDate(e.target.value); }} className="border rounded px-2 py-1 text-gray-800" />
        <input type="date" value={endDate || ''} onChange={(e) => { setPreset('custom'); setEndDate(e.target.value); }} className="border rounded px-2 py-1 text-gray-800" />

        <select value={accountId || ''} onChange={(e) => setAccountId(e.target.value ? Number(e.target.value) : undefined)} className="border rounded px-2 py-1 text-gray-800">
          <option value="">All accounts</option>
          {accounts.map((a) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>

        <select value={category || ''} onChange={(e) => setCategory(e.target.value || undefined)} className="border rounded px-2 py-1 text-gray-800">
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <input placeholder="Search merchant/description" value={search} onChange={(e) => setSearch(e.target.value)} className="border rounded px-2 py-1 text-gray-800 placeholder-gray-600" />
      </div>

      <div className="mt-3 flex justify-end">
        <button onClick={handleSync} disabled={syncing} className="px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-50">
          {syncing ? 'Syncing…' : 'Sync Now'}
        </button>
      </div>
    </div>
  );
}


