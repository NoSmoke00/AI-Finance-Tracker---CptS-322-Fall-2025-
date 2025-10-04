'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { plaidApi } from '@/lib/api';
import { Account } from '@/types';
import PlaidLink from '@/components/PlaidLink';
import AppLayout from '@/components/AppLayout';

export default function AccountsPage() {
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [error, setError] = useState('');
  const [showPlaidLink, setShowPlaidLink] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await plaidApi.getAccounts();
      setAccounts(response.accounts);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError('Failed to load accounts');
      }
    }
  };

  const handleLinkSuccess = () => {
    setShowPlaidLink(false);
    loadAccounts(); // Refresh accounts list
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };


  return (
    <AppLayout>
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Bank Accounts</h1>
              <p className="text-gray-600">Manage your linked bank accounts</p>
            </div>
            <button
              onClick={() => setShowPlaidLink(true)}
              className="btn btn-primary"
            >
              Link New Account
            </button>
          </div>
        </div>

        <main className="p-6">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {showPlaidLink ? (
          <div className="bg-white shadow rounded-lg">
            <PlaidLink
              onSuccess={handleLinkSuccess}
              onExit={() => setShowPlaidLink(false)}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {accounts.length === 0 ? (
              <div className="bg-white shadow rounded-lg">
                <div className="p-6 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No accounts linked</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by linking your first bank account.
                  </p>
                  <div className="mt-6">
                    <button
                      onClick={() => setShowPlaidLink(true)}
                      className="btn btn-primary"
                    >
                      Link Bank Account
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {accounts.map((account) => (
                  <div key={account.id} className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-6">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                            <span className="text-white font-bold text-lg">
                              {account.institution_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4 flex-1">
                          <h3 className="text-lg font-medium text-gray-900">
                            {account.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {account.institution_name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {account.subtype} • ****{account.mask}
                          </p>
                        </div>
                      </div>
                      
                      <div className="mt-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-500">
                            Current Balance
                          </span>
                          <span className="text-lg font-semibold text-gray-900">
                            {formatCurrency(account.balance_current)}
                          </span>
                        </div>
                        
                        {account.balance_available !== account.balance_current && (
                          <div className="flex justify-between items-center mt-2">
                            <span className="text-sm text-gray-500">
                              Available
                            </span>
                            <span className="text-sm font-medium text-gray-900">
                              {formatCurrency(account.balance_available)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        </main>
      </div>
    </AppLayout>
  );
}

