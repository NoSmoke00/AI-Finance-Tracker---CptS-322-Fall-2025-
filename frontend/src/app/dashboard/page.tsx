'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { dashboardApi, transactionsApi, plaidApi } from '@/lib/api';
import { DashboardSummary, Account, Transaction } from '@/types';
import AppLayout from '@/components/AppLayout';
import InsightsSummary from '@/components/InsightsSummary';

export default function DashboardPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<{ id: number; name: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const [summaryData, transactionsData, accountsData] = await Promise.all([
          dashboardApi.getSummary(),
          transactionsApi.list({ limit: 10 }),
          plaidApi.getAccounts(),
        ]);
        
        setSummary(summaryData);
        setTransactions(transactionsData);
        setAccounts(accountsData.accounts.map((a: { id: number; name: string }) => ({ id: a.id, name: a.name })));
      } catch (err: any) {
        if (err.response?.status === 401) {
          router.push('/login');
        } else {
          setError('Failed to load dashboard data');
        }
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [router]);


  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const accountsById: Record<number, { name: string }> = (accounts || []).reduce(
    (acc: Record<number, { name: string }>, a: { id: number; name: string }) => {
      acc[a.id] = { name: a.name };
      return acc;
    },
    {}
  );

  if (loading) {
    return (
      <AppLayout>
        <div className="flex-1 overflow-auto">
          <main className="p-6">
          {/* Loading Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gray-300 rounded-full animate-pulse"></div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <div className="h-4 bg-gray-300 rounded w-24 mb-2 animate-pulse"></div>
                      <div className="h-6 bg-gray-300 rounded w-16 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Loading Accounts */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Accounts
                </h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="h-4 bg-gray-300 rounded w-32 mb-2 animate-pulse"></div>
                        <div className="h-3 bg-gray-300 rounded w-48 animate-pulse"></div>
                      </div>
                      <div className="h-4 bg-gray-300 rounded w-20 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Loading Transactions */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Recent Transactions
                </h3>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex justify-between items-center py-2 border-b last:border-b-0">
                      <div>
                        <div className="h-4 bg-gray-300 rounded w-32 mb-1 animate-pulse"></div>
                        <div className="h-3 bg-gray-300 rounded w-24 animate-pulse"></div>
                      </div>
                      <div className="h-4 bg-gray-300 rounded w-16 animate-pulse"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
        </div>
        </main>
      </div>
    </AppLayout>
  );
}

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        <main className="p-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">$</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Balance
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(summary?.summary.total_balance || 0)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">C</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Checking
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(summary?.summary.checking_balance || 0)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">S</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Savings
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(summary?.summary.savings_balance || 0)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">CC</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Credit Cards
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatCurrency(summary?.summary.credit_balance || 0)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Transactions - 2 columns */}
            <div className="lg:col-span-2 bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Recent Transactions
                </h3>
                <div className="space-y-4">
                  {transactions.slice(0, 10).map((transaction: any) => (
                    <div key={transaction.id} className="flex justify-between items-center py-2 border-b last:border-b-0">
                      <div>
                        <p className="font-medium text-gray-900">
                          {transaction.merchant_name || transaction.name}
                        </p>
                        <p className="text-sm text-gray-900">
                          {accountsById[transaction.account_id]?.name || 'Account'} • {formatDate(transaction.date)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`font-medium ${
                          transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {transaction.amount > 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                        </p>
                      </div>
                    </div>
                  ))}
                  {transactions.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-500">No transactions found</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - AI Insights & Accounts */}
            <div className="space-y-6">
              {/* AI Insights */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                      AI Insights
                    </h3>
                    <a href="/insights" className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                      View All →
                    </a>
                  </div>
                  <InsightsSummary />
                </div>
              </div>

              {/* Accounts - 1 column */}
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Accounts ({summary?.summary.total_accounts || 0})
                    </h3>
                    <a href="/accounts" className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                      View All →
                    </a>
                  </div>
                  <div className="space-y-3">
                    {summary?.accounts.slice(0, 4).map((account: Account) => (
                      <div key={account.id} className="border rounded-lg p-3">
                        <div className="flex justify-between items-start">
                          <div className="min-w-0 flex-1">
                            <h4 className="font-medium text-gray-900 truncate">{account.name}</h4>
                            <p className="text-xs text-gray-500 truncate">
                              {account.institution_name} • {account.subtype}
                            </p>
                          </div>
                          <div className="text-right ml-2 flex-shrink-0">
                            <p className="font-medium text-gray-900 text-sm">
                              {formatCurrency(account.balance_current)}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                    {(!summary?.accounts || summary.accounts.length === 0) && (
                      <div className="text-center py-4">
                        <p className="text-sm text-gray-500 mb-2">No accounts linked yet</p>
                        <a href="/accounts" className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                          Link Account →
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </AppLayout>
  );
}
