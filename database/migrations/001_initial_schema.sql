-- Migration: 001_initial_schema.sql
-- Description: Initial database schema creation
-- Date: 2024-01-01

-- This migration creates the initial database schema for the AI-Finance Tracker

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Plaid items table (stores bank connections)
CREATE TABLE IF NOT EXISTS plaid_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token VARCHAR(255) NOT NULL,
    item_id VARCHAR(255) UNIQUE NOT NULL,
    institution_id VARCHAR(255) NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table (stores individual bank accounts)
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plaid_item_id INTEGER NOT NULL REFERENCES plaid_items(id) ON DELETE CASCADE,
    account_id VARCHAR(255) NOT NULL, -- Plaid account ID
    name VARCHAR(255) NOT NULL,
    official_name VARCHAR(255),
    type VARCHAR(50) NOT NULL, -- e.g., 'depository', 'credit'
    subtype VARCHAR(50), -- e.g., 'checking', 'savings'
    mask VARCHAR(10), -- Last 4 digits
    balance_current DECIMAL(15,2),
    balance_available DECIMAL(15,2),
    currency_code VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

