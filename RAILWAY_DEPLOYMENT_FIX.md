# Railway Deployment Fix Guide

## Problem Analysis
The deployment is failing because Railway is looking for a `main` module that doesn't exist. Here are the fixes applied:

## Fixes Applied

### 1. Created `main.py`
Created a `main.py` file that imports the Flask app from `app.py`:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 2. Updated Configuration Files
- **Procfile**: Changed from `app:app` to `main:app`
- **railway.json**: Updated start command to use `main:app`
- **requirements.txt**: Added Werkzeug dependency

### 3. Alternative Files Created
- **application.py**: Alternative entry point using `application` as the Flask app name
- **Procfile.web**: Alternative Procfile using `application:application`

## Quick Fix Steps

### Option 1: Use the Fixed Scripts
```bash
# Make the fix script executable
chmod +x fix-railway-deployment.sh

# Run the fix script
./fix-railway-deployment.sh
```

### Option 2: Manual Fix
```bash
# Set environment variables
railway variables set PORT=8080
railway variables set PYTHON_VERSION=3.9

# Deploy with the fixed configuration
railway up
```

### Option 3: Use Alternative Entry Point
```bash
# Rename the alternative Procfile
mv Procfile.web Procfile

# Deploy
railway up
```

## Verification Steps

1. **Check deployment logs**:
   ```bash
   railway logs
   ```

2. **Test the health endpoint**:
   ```bash
   curl https://your-app-url.railway.app/health
   ```

3. **Check Railway dashboard**:
   - Go to Railway dashboard
   - Check if the deployment shows "Success"
   - Verify environment variables are set correctly

## Common Issues and Solutions

### Issue: ModuleNotFoundError
**Solution**: Ensure all dependencies are in `requirements.txt` and the entry point file exists.

### Issue: Port Binding Error
**Solution**: Railway automatically sets the PORT environment variable. Use `os.environ.get('PORT', 8080)` in your code.

### Issue: Timeout Errors
**Solution**: Increase Gunicorn timeout with `--timeout 120` flag.

### Issue: Health Check Failing
**Solution**: Ensure the `/health` endpoint is accessible and returns a 200 status code.

## Environment Variables Required
Make sure these are set in Railway:
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `RAPID_API_KEY`
- `RAPID_API_HOST`
- `PORT` (automatically set by Railway)

## Support
If issues persist, check Railway's official documentation or contact their support team.