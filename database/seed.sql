-- Seed data for testing and development
-- This file contains sample data for testing the application

-- Insert test users (passwords are hashed versions of 'password123')
INSERT INTO users (email, hashed_password, first_name, last_name, is_active) VALUES
('john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8Xj4.8L2K2', 'John', 'Doe', TRUE),
('jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8Xj4.8L2K2', 'Jane', 'Smith', TRUE),
('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8Xj4.8L2K2', 'Test', 'User', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Note: Plaid items and accounts will be created through the API when users link their bank accounts
-- This seed file only contains user data for testing authentication

