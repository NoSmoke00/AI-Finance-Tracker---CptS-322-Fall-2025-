# AI-Finance Tracker

## Getting Started

### Prerequisites

- **VS Code** (or any code editor)
- **Docker Desktop** installed and running
- **Git** for version control

cp shared/env.example .env
```

### 2. Configure Environment

Edit the `.env` file in the project root and add your Plaid credentials:

```env
# Get these from your Plaid dashboard (sandbox mode)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret_key
```

### 3. Start the Application

```bash
# Start all services (database, backend, frontend)
docker compose up --build
```

Wait for all containers to start up (about 1-2 minutes).

### 4. Access the App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

### VS Code Setup

1. **Open the project** in VS Code
2. **Install recommended extensions**:
   - Docker
   - Python
   - TypeScript and JavaScript Language Features
   - Tailwind CSS IntelliSense

### Making Changes

```bash
# View logs while developing
docker compose logs -f

# Restart specific service after changes
docker compose restart backend
docker compose restart frontend
```

### Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

