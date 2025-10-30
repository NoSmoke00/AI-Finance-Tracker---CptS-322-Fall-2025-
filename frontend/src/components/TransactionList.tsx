'use client';

import { useMemo } from 'react';

interface Transaction {
  id: number;
  date: string;
  name: string;
  merchant_name?: string;
  primary_category?: string;
  category?: string[];
  amount: number;
  pending?: boolean;
  account_id: number;
  account_name?: string;
}

interface Props {
  transactions: Transaction[];
  accountsById: Record<number, { name: string }>;
}

export default function TransactionList({ transactions, accountsById }: Props) {
  const groups = useMemo(() => {
    const m: Record<string, Transaction[]> = {};
    for (const t of transactions) {
      (m[t.date] ||= []).push(t);
    }
    const ordered = Object.entries(m).sort((a, b) => (a[0] < b[0] ? 1 : -1));
    return ordered.map(([date, list]) => ({ date, list }));
  }, [transactions]);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const formatDate = (s: string) =>
    new Date(s).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });

  return (
    <div className="space-y-6">
      {groups.map((g) => {
        const dailyTotal = g.list.reduce((sum, t) => sum + t.amount, 0);
        return (
          <div key={g.date} className="bg-white shadow rounded-lg">
            <div className="px-4 py-3 border-b flex items-center justify-between">
              <div className="font-medium text-gray-900">{formatDate(g.date)}</div>
              <div className={`font-semibold ${dailyTotal >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(dailyTotal)}
              </div>
            </div>
            <div className="divide-y">
              {g.list.map((t) => (
                <div key={t.id} className="px-4 py-3 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900">
                      {t.merchant_name || t.name}{' '}
                      {t.pending ? (
                        <span className="ml-2 text-xs px-2 py-0.5 rounded bg-yellow-100 text-yellow-800">Pending</span>
                      ) : null}
                    </div>
                    <div className="text-sm text-gray-700">
                      {accountsById[t.account_id]?.name || 'Account'} • {(t.primary_category || (t.category && t.category[0]) || 'Uncategorized')}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Full: {t.category ? JSON.stringify(t.category) : '[]'}
                    </div>
                  </div>
                  <div className={`font-medium ${t.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {t.amount > 0 ? '+' : ''}{formatCurrency(t.amount)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}


