# Stock Analysis Application

A comprehensive stock analysis application that provides real-time stock data, technical analysis, AI-powered predictions, and investment recommendations for Indian stocks.

## Features

- **Real-time Stock Data**: Integration with RapidAPI Indian Stock Exchange API
- **AI-Powered Predictions**: Using OpenRouter API with NVIDIA Nemotron Nano model
- **Technical Analysis**: Comprehensive technical indicators and charting
- **Investment Recommendations**: Smart recommendations based on analysis
- **Interactive Dashboard**: User-friendly web interface
- **Watchlist Management**: Track multiple stocks

## Prerequisites

- Python 3.9+
- Railway CLI (for deployment)
- API Keys:
  - OpenRouter API Key
  - RapidAPI Key (Indian Stock Exchange)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd stock-analysis-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with your API keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
RAPID_API_KEY=your_rapidapi_key
RAPID_API_HOST=indian-stock-exchange.p.rapidapi.com
```

## Local Development

Run the application locally:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment to Railway

Railway is a modern cloud platform that makes deployment simple and offers a generous free tier. Here's how to deploy your application:

### Prerequisites for Railway
- Railway account (free)
- Railway CLI installed

### Automatic Deployment (Recommended)

#### For Windows (PowerShell):
```powershell
.\deploy-railway.ps1
```

#### For Linux/Mac (Bash):
```bash
chmod +x deploy-railway.sh
./deploy-railway.sh
```

### Manual Deployment

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Login to Railway**:
```bash
railway login
```

3. **Create a new Railway project**:
```bash
railway init
```

4. **Set environment variables**:
```bash
railway variables set OPENROUTER_API_KEY="your_openrouter_api_key"
railway variables set OPENROUTER_MODEL="nvidia/nemotron-nano-9b-v2:free"
railway variables set RAPID_API_KEY="your_rapidapi_key"
railway variables set RAPID_API_HOST="indian-stock-exchange.p.rapidapi.com"
```

5. **Deploy to Railway**:
```bash
railway up
```

6. **Open your deployed app**:
```bash
railway open
```

### Railway Configuration Files

The following files are configured for Railway deployment:
- `railway.json` - Railway deployment configuration
- `Procfile` - Process definition for Railway
- `runtime.txt` - Python version specification

### Railway Benefits
- **Free tier**: 500 hours/month (enough for continuous deployment)
- **Auto-scaling**: Scales based on traffic
- **Built-in databases**: Easy PostgreSQL, Redis, etc.
- **GitHub integration**: Auto-deploy on push
- **Custom domains**: Free SSL certificates
- **Environment variables**: Secure management

### Monitoring
Railway provides built-in monitoring:
- Application logs
- Resource usage
- Error tracking
- Performance metrics

## Alternative: Deployment to Vercel

If you prefer Vercel, the configuration is also available:

### Automatic Deployment (Vercel)

#### For Windows (PowerShell):
```powershell
.\deploy.ps1
```

#### For Linux/Mac (Bash):
```bash
chmod +x deploy.sh
./deploy.sh
```

## API Endpoints

- `GET /` - Home page
- `GET /dashboard` - Dashboard page
- `GET /health` - Health check (for monitoring)
- `POST /analyze` - Analyze stock data
- `POST /chart-data` - Get chart data
- `GET /symbols` - Get available stock symbols
- `GET /watchlist` - Get watchlist data
- `POST /realtime-data` - Get real-time stock data
- `POST /company-info` - Get company information

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | OpenRouter model to use |
| `RAPID_API_KEY` | Your RapidAPI key |
| `RAPID_API_HOST` | RapidAPI host URL |

## Important Notes

- **API Limits**: Be aware of your API usage limits on both OpenRouter and RapidAPI
- **Security**: Never commit your `.env` file with real API keys
- **Performance**: The free tier may have limitations on concurrent requests
- **Caching**: Consider implementing caching for better performance

## License

This project is licensed under the MIT License.