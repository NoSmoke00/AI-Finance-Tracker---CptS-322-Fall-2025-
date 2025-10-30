import axios, { AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  DashboardSummary,
  Account,
  Transaction,
  PlaidLinkTokenResponse,
  PlaidExchangeResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      Cookies.remove('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/api/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/api/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/api/auth/me');
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const response: AxiosResponse<DashboardSummary> = await api.get('/api/dashboard/summary');
    return response.data;
  },
};

// Plaid API
export const plaidApi = {
  createLinkToken: async (): Promise<PlaidLinkTokenResponse> => {
    const response: AxiosResponse<PlaidLinkTokenResponse> = await api.post('/api/plaid/link_token');
    return response.data;
  },

  exchangeToken: async (publicToken: string): Promise<PlaidExchangeResponse> => {
    const response: AxiosResponse<PlaidExchangeResponse> = await api.post('/api/plaid/exchange_token', {
      public_token: publicToken,
    });
    return response.data;
  },

  getAccounts: async (): Promise<{ accounts: Account[] }> => {
    const response: AxiosResponse<{ accounts: Account[] }> = await api.get('/api/plaid/accounts');
    return response.data;
  },

  getTransactions: async (): Promise<{ transactions: Transaction[] }> => {
    const response: AxiosResponse<{ transactions: Transaction[] }> = await api.get('/api/plaid/transactions');
    return response.data;
  },
};

export default api;

// Transactions API
export const transactionsApi = {
  list: async (params: {
    skip?: number;
    limit?: number;
    account_id?: number;
    start_date?: string;
    end_date?: string;
    category?: string;
    search?: string;
  }) => {
    const response: AxiosResponse<any[]> = await api.get('/api/transactions', { params });
    return response.data;
  },

  detail: async (id: number) => {
    const response: AxiosResponse<any> = await api.get(`/api/transactions/${id}`);
    return response.data;
  },

  sync: async () => {
    const response: AxiosResponse<{ message: string; created: number; updated: number }> = await api.post('/api/transactions/sync');
    return response.data;
  },

  summary: async (period: 'day' | 'week' | 'month' | 'quarter' | 'year' = 'month') => {
    const response: AxiosResponse<any> = await api.get('/api/transactions/summary', { params: { period } });
    return response.data;
  },
};

// Insights API
export const insightsApi = {
  list: async () => {
    const response: AxiosResponse<any[]> = await api.get('/api/insights');
    return response.data;
  },
  generate: async () => {
    const response: AxiosResponse<any[]> = await api.post('/api/insights/generate');
    return response.data;
  },
  dismiss: async (id: number) => {
    const response: AxiosResponse<any> = await api.patch(`/api/insights/${id}/dismiss`);
    return response.data;
  },
  view: async (id: number) => {
    const response: AxiosResponse<any> = await api.patch(`/api/insights/${id}/view`);
    return response.data;
  },
  remove: async (id: number) => {
    const response: AxiosResponse<any> = await api.delete(`/api/insights/${id}`);
    return response.data;
  },
};

