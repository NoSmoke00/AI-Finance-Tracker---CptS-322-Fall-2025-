# Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Plaid API credentials (sandbox for testing)
- PostgreSQL database (or use Docker)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd AI-Finance-Tracker---CptS-322-Fall-2025-
chmod +x shared/scripts/setup.sh
./shared/scripts/setup.sh
```

### 2. Configure Environment Variables

Update the `.env` file with your actual values:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_tracker

# JWT Secret Key (change this!)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Plaid Configuration
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox
```

### 3. Get Plaid API Credentials

1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com/)
2. Create a new application
3. Get your `client_id` and `secret` from the dashboard
4. Use sandbox environment for testing

### 4. Start the Application

```bash
# Start all services with Docker Compose
docker-compose up

# Or start services individually
docker-compose up postgres    # Database only
docker-compose up backend     # Backend only
docker-compose up frontend    # Frontend only
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Workflow

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Management

```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d finance_tracker

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec postgres psql -U postgres -d finance_tracker -f /docker-entrypoint-initdb.d/02-seed.sql
```

## Testing with Plaid Sandbox

1. Use the sandbox environment credentials:
   - Username: `user_good`
   - Password: `pass_good`

2. Test different scenarios:
   - `user_good` / `pass_good` - Successful connection
   - `user_bad` / `pass_good` - Invalid credentials
   - `user_good` / `pass_bad` - Invalid credentials

## Production Deployment

### Environment Setup

1. Set up a production PostgreSQL database
2. Configure production Plaid credentials
3. Set secure JWT secret key
4. Configure CORS for your domain

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **JWT Secret**: Use a strong, random secret key
3. **Database**: Use strong passwords and limit access
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS properly for your domain

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Health Checks

- Backend: `GET /health`
- Database: Check container status
- Frontend: Check if accessible

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check if PostgreSQL container is running
   - Verify database URL in environment variables

2. **Plaid Integration Issues**
   - Verify API credentials
   - Check if using correct environment (sandbox/development/production)

3. **Frontend Not Loading**
   - Check if backend is running on port 8000
   - Verify API URL in frontend environment variables

4. **Authentication Issues**
   - Check JWT secret key configuration
   - Verify token expiration settings

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

## Support

For issues and questions:
1. Check the API documentation: `/docs/api/README.md`
2. Review the logs: `docker-compose logs`
3. Check environment configuration
4. Verify all prerequisites are met

