#!/bin/bash

# AI-Finance Tracker Setup Script
# This script helps set up the development environment

echo " Setting up AI-Finance Tracker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (support both v1 and v2)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp shared/env.example .env
    echo "⚠️  Please update the .env file with your actual values before running the application."
fi

# Create .env files for frontend and backend
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local..."
    cp shared/env.example frontend/.env.local
fi

if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env..."
    cp shared/env.example backend/.env
fi

echo "✅ Environment files created. Please update them with your actual values."

# Make sure the script is executable
chmod +x shared/scripts/setup.sh

echo "🎉 Setup complete! Next steps:"
echo "1. Update the .env files with your actual values"
echo "2. Get your Plaid API credentials from https://dashboard.plaid.com/"
echo "3. Run 'docker-compose up' to start the application"
echo ""
echo "📚 For more information, see the README.md file"
