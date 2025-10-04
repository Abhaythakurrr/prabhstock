# PowerShell Deployment Script for Vercel

# Check if Vercel CLI is installed
if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "Vercel CLI not found. Installing..."
    npm install -g vercel
}

# Ensure environment variables are set in Vercel
Write-Host "Setting up environment variables in Vercel..."
vercel env add OPENROUTER_API_KEY production
vercel env add OPENROUTER_MODEL production
vercel env add RAPID_API_KEY production
vercel env add RAPID_API_HOST production

# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Deploy to Vercel
Write-Host "Deploying to Vercel..."
vercel --prod

Write-Host "Deployment complete!"