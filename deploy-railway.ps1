# Railway Deployment Script for Windows PowerShell
# This script automates the deployment to Railway

Write-Host "🚀 Starting Railway deployment process..." -ForegroundColor Green

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# Login to Railway (if not already logged in)
Write-Host "🔐 Checking Railway authentication..." -ForegroundColor Cyan
railway login

# Set environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
railway variables set OPENROUTER_API_KEY="$env:OPENROUTER_API_KEY"
railway variables set OPENROUTER_MODEL="$env:OPENROUTER_MODEL"
railway variables set RAPID_API_KEY="$env:RAPID_API_KEY"
railway variables set RAPID_API_HOST="$env:RAPID_API_HOST"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Deploy to Railway
Write-Host "🚂 Deploying to Railway..." -ForegroundColor Magenta
railway up

Write-Host "✅ Deployment complete! Check your Railway dashboard for the deployed URL." -ForegroundColor Green