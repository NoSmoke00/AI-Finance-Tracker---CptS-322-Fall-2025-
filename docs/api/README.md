# API Documentation

## Overview

The AI-Finance Tracker API is built with FastAPI and provides endpoints for user authentication, bank account management, and financial data retrieval.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST `/api/auth/login`
Authenticate a user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET `/api/auth/me`
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Dashboard

#### GET `/api/dashboard/summary`
Get dashboard summary data.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "name": "John Doe",
    "email": "user@example.com"
  },
  "summary": {
    "total_balance": 5000.00,
    "checking_balance": 3000.00,
    "savings_balance": 2000.00,
    "credit_balance": -500.00,
    "total_accounts": 3
  },
  "accounts": [
    {
      "id": 1,
      "name": "Chase Total Checking",
      "type": "depository",
      "subtype": "checking",
      "balance": 3000.00,
      "currency": "USD",
      "institution": "Chase"
    }
  ]
}
```

### Plaid Integration

#### POST `/api/plaid/link_token`
Create a Plaid link token for bank account linking.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "link_token": "link-sandbox-xxx-xxx-xxx",
  "expiration": "2024-01-01T01:00:00Z"
}
```

#### POST `/api/plaid/exchange_token`
Exchange public token for access token.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "public_token": "public-sandbox-xxx-xxx-xxx"
}
```

**Response:**
```json
{
  "message": "Successfully linked bank account",
  "item_id": "item-xxx-xxx-xxx"
}
```

#### GET `/api/plaid/accounts`
Get all linked accounts.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "accounts": [
    {
      "id": 1,
      "account_id": "account-xxx-xxx-xxx",
      "name": "Chase Total Checking",
      "official_name": "Chase Total Checking - 1234",
      "type": "depository",
      "subtype": "checking",
      "mask": "1234",
      "balance_current": 3000.00,
      "balance_available": 3000.00,
      "currency_code": "USD",
      "institution_name": "Chase"
    }
  ]
}
```

#### GET `/api/plaid/transactions`
Get recent transactions.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "txn-xxx-xxx-xxx",
      "account_id": "account-xxx-xxx-xxx",
      "amount": -50.00,
      "date": "2024-01-01",
      "name": "Coffee Shop",
      "merchant_name": "Coffee Shop",
      "category": ["Food and Drink", "Restaurants"],
      "account_name": "Chase Total Checking"
    }
  ]
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error message description"
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

