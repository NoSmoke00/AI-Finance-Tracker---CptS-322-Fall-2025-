'use client';

import { useEffect, useMemo, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import TransactionFilters from '@/components/TransactionFilters';
import TransactionList from '@/components/TransactionList';
import { transactionsApi, plaidApi } from '@/lib/api';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<{ id: number; name: string }[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [filters, setFilters] = useState<any>({ limit: 50 });
  const [summary, setSummary] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const accountsById = useMemo(() => {
    const m: Record<number, { name: string }> = {};
    for (const a of accounts) m[a.id] = { name: a.name };
    return m;
  }, [accounts]);

  const load = async () => {
    setLoading(true);
    try {
      const [txs, accRes, sum] = await Promise.all([
        transactionsApi.list(filters),
        plaidApi.getAccounts(),
        transactionsApi.summary('month'),
      ]);
      setTransactions(txs);
      setAccounts(accRes.accounts.map((a: any) => ({ id: a.id, name: a.name })));
      // derive categories from transactions
      const cats = Array.from(new Set((txs || []).map((t: any) => t.primary_category).filter(Boolean)));
      setCategories(cats);
      setSummary(sum);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filters)]);

  const formatCurrency = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n || 0);

  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        <main className="p-6 space-y-4">
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white shadow rounded-lg p-4">
              <div className="text-sm text-gray-700">Total Income</div>
              <div className="text-xl font-semibold text-green-600">{formatCurrency(summary?.total_income || 0)}</div>
            </div>
            <div className="bg-white shadow rounded-lg p-4">
              <div className="text-sm text-gray-700">Total Expenses</div>
              <div className="text-xl font-semibold text-red-600">{formatCurrency(summary?.total_expenses || 0)}</div>
            </div>
            <div className="bg-white shadow rounded-lg p-4">
              <div className="text-sm text-gray-700">Net Savings</div>
              <div className="text-xl font-semibold text-blue-600">{formatCurrency(summary?.net_savings || 0)}</div>
            </div>
            <div className="bg-white shadow rounded-lg p-4">
              <div className="text-sm text-gray-700">Transactions</div>
              <div className="text-xl font-semibold text-gray-800">{summary?.transaction_count || 0}</div>
            </div>
          </div>

          {/* Filters */}
          <TransactionFilters
            accounts={accounts}
            categories={categories}
            onChange={(f) => setFilters((old: any) => ({ ...old, ...f }))}
            onSync={async () => { await transactionsApi.sync(); await load(); }}
          />

          {/* List */}
          {loading ? (
            <div className="bg-white shadow rounded-lg p-6 text-center">Loading…</div>
          ) : (
            <TransactionList transactions={transactions} accountsById={accountsById} />
          )}
        </main>
      </div>
    </AppLayout>
  );
}


