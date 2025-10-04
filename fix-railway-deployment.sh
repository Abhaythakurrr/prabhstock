#!/bin/bash

# Railway Deployment Fix Script
# This script fixes common Railway deployment issues

echo "🔧 Fixing Railway deployment issues..."

# 1. Ensure all files are committed
echo "📁 Checking git status..."
git add .
git commit -m "Railway deployment fix" || echo "No changes to commit"

# 2. Set proper environment variables
echo "⚙️ Setting environment variables..."
railway variables set PORT=8080
railway variables set PYTHON_VERSION=3.9

# 3. Update Railway configuration
echo "📝 Updating Railway configuration..."
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt",
    "startCommand": "gunicorn main:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
EOF

# 4. Deploy with verbose output
echo "🚂 Deploying to Railway with verbose output..."
railway up --verbose

echo "✅ Fix deployment complete!"
echo "📊 Check Railway logs with: railway logs"