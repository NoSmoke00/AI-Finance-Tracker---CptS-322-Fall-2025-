from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv

from app.database import get_db, engine
from app.models import Base
from app.auth.router import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.plaid_routes import router as plaid_router
from app.api.transactions import router as transactions_router
from app.api.insights import router as insights_router
from app.api.budgets import router as budgets_router
from app.tasks.insight_tasks import start_scheduler
import os

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Finance Tracker API",
    description="Backend API for AI-Finance Tracker application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(plaid_router, prefix="/api/plaid", tags=["plaid"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["transactions"])
app.include_router(insights_router, prefix="/api/insights", tags=["insights"])
app.include_router(budgets_router, prefix="/api/budgets", tags=["budgets"])

@app.get("/")
async def root():
    return {"message": "AI-Finance Tracker API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Start scheduler (guard to avoid multiple in dev reloads)
try:
    start_scheduler()
except Exception:
    pass
