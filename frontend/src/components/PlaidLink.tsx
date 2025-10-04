'use client';

import { useState, useEffect } from 'react';
import { plaidApi } from '@/lib/api';

declare global {
  interface Window {
    Plaid: any;
  }
}

interface PlaidLinkProps {
  onSuccess: () => void;
  onExit?: () => void;
}

export default function PlaidLink({ onSuccess, onExit }: PlaidLinkProps) {
  const [linkToken, setLinkToken] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPlaidScript = async () => {
      try {
        // Load Plaid Link script
        const script = document.createElement('script');
        script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
        script.onload = () => {
          initializePlaid();
        };
        document.head.appendChild(script);
      } catch (err) {
        setError('Failed to load Plaid Link');
        setLoading(false);
      }
    };

    const initializePlaid = async () => {
      try {
        const response = await plaidApi.createLinkToken();
        setLinkToken(response.link_token);
        setLoading(false);
      } catch (err: any) {
        // Handle different error formats
        let errorMessage = 'Failed to create link token';
        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.data?.message) {
          errorMessage = err.response.data.message;
        } else if (typeof err.message === 'string') {
          errorMessage = err.message;
        }
        setError(errorMessage);
        setLoading(false);
      }
    };

    loadPlaidScript();
  }, []);

  const handlePlaidLink = () => {
    if (!linkToken || !window.Plaid) return;

    const handler = window.Plaid.create({
      token: linkToken,
      onSuccess: async (public_token: string) => {
        try {
          await plaidApi.exchangeToken(public_token);
          onSuccess();
        } catch (err: any) {
          // Handle different error formats
          let errorMessage = 'Failed to link account';
          if (err.response?.data?.detail) {
            errorMessage = err.response.data.detail;
          } else if (err.response?.data?.message) {
            errorMessage = err.response.data.message;
          } else if (typeof err.message === 'string') {
            errorMessage = err.message;
          }
          setError(errorMessage);
        }
      },
      onExit: (err: any, metadata: any) => {
        if (err) {
          setError('Link was cancelled or failed');
        }
        if (onExit) onExit();
      },
      onEvent: (eventName: string, metadata: any) => {
        console.log('Plaid Link Event:', eventName, metadata);
      },
    });

    handler.open();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading Plaid Link...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-600">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-2 btn btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Link Your Bank Account
      </h3>
      <p className="text-gray-600 mb-6">
        Connect your bank account to start tracking your finances. We use Plaid to securely connect to your bank.
      </p>
      
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Sandbox Mode
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>This is a test environment. Use these credentials:</p>
              <ul className="list-disc list-inside mt-1">
                <li>Username: user_good</li>
                <li>Password: pass_good</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={handlePlaidLink}
        className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        Connect Bank Account
      </button>
    </div>
  );
}
