// Type definitions for the AI-Finance Tracker application

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface Account {
  id: number;
  account_id: string;
  name: string;
  official_name?: string;
  type: string;
  subtype?: string;
  mask?: string;
  balance_current: number;
  balance_available: number;
  currency_code: string;
  institution_name: string;
}

export interface Transaction {
  transaction_id: string;
  account_id: string;
  amount: number;
  date: string;
  name: string;
  merchant_name?: string;
  category?: string[];
  account_name: string;
}

export interface DashboardSummary {
  user: {
    name: string;
    email: string;
  };
  summary: {
    total_balance: number;
    checking_balance: number;
    savings_balance: number;
    credit_balance: number;
    total_accounts: number;
  };
  accounts: Account[];
}

export interface PlaidLinkTokenResponse {
  link_token: string;
  expiration: string;
}

export interface PlaidExchangeResponse {
  message: string;
  item_id: string;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

