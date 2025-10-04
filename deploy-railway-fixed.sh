#!/bin/bash

# Railway Deployment Script - Fixed Version
# This script properly deploys to Railway with correct configuration

echo "🚀 Starting Railway deployment process..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Check if we're in a Railway project
if [ ! -f "railway.json" ]; then
    echo "📝 Creating new Railway project..."
    railway init --name prabhstock --template nixpacks
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
railway variables set OPENROUTER_MODEL="$OPENROUTER_MODEL"
railway variables set RAPID_API_KEY="$RAPID_API_KEY"
railway variables set RAPID_API_HOST="$RAPID_API_HOST"

# Deploy to Railway
echo "🚂 Deploying to Railway..."
railway up --detach

echo "✅ Deployment complete! Check your Railway dashboard for the deployed URL."
echo "🌐 Run 'railway open' to open your deployed application"