#!/bin/bash

# Railway Deployment Script
# This script automates the deployment to Railway

echo "🚀 Starting Railway deployment process..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
railway variables set OPENROUTER_MODEL="$OPENROUTER_MODEL"
railway variables set RAPID_API_KEY="$RAPID_API_KEY"
railway variables set RAPID_API_HOST="$RAPID_API_HOST"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Deploy to Railway
echo "🚂 Deploying to Railway..."
railway up

echo "✅ Deployment complete! Check your Railway dashboard for the deployed URL."