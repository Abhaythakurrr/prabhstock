# Stock Analysis Application

A Flask-based web application for analyzing Indian stock market data with AI-powered predictions.

## Features

- Historical stock data analysis
- Real-time stock data from Indian Stock Exchange
- Technical analysis with multiple indicators
- AI-powered stock movement predictions
- Interactive charts and dashboards

## Setup

### Prerequisites

- Python 3.9+
- Node.js and npm (for Vercel CLI)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables by creating a `.env` file with:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
   RAPID_API_KEY=your_rapidapi_key
   RAPID_API_HOST=indianstockexchange.p.rapidapi.com
   ```

## Local Development

Run the application locally:

```
python app.py
```

The application will be available at http://127.0.0.1:5000

## Deployment to Vercel

### Automatic Deployment

#### Windows

Run the PowerShell deployment script:

```
.\deploy.ps1
```

#### Linux/Mac

Run the bash deployment script:

```
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Set up environment variables in Vercel:
   ```
   vercel env add OPENROUTER_API_KEY
   vercel env add OPENROUTER_MODEL
   vercel env add RAPID_API_KEY
   vercel env add RAPID_API_HOST
   ```

3. Deploy to Vercel:
   ```
   vercel --prod
   ```

## API Endpoints

- `/` - Home page
- `/dashboard` - Dashboard with stock analysis
- `/analyze` - Analyze a specific stock
- `/chart-data` - Get chart data for a stock
- `/symbols` - Get available stock symbols
- `/watchlist` - Get watchlist data
- `/realtime-data` - Get real-time stock data
- `/company-info` - Get company information

## License

MIT