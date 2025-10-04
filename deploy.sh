#!/bin/bash

# Deployment script for Vercel

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Ensure environment variables are set in Vercel
echo "Setting up environment variables in Vercel..."
vercel env add OPENROUTER_API_KEY production
vercel env add OPENROUTER_MODEL production
vercel env add RAPID_API_KEY production
vercel env add RAPID_API_HOST production

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Deploy to Vercel
echo "Deploying to Vercel..."
vercel --prod

echo "Deployment complete!"