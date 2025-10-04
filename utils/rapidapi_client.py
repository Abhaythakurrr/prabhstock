import http.client
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RapidAPI credentials from environment variables
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")

def fetch_realtime_stock_data(symbol):
    """
    Fetch real-time stock data from Indian Stock Exchange API.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE', 'INFY')
        
    Returns:
        dict: Real-time stock data
    """
    try:
        # Remove any exchange suffixes (.NS, .BO)
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        # Create connection
        conn = http.client.HTTPSConnection("indianstockexchange.p.rapidapi.com")
        
        # Set headers
        headers = {
            'x-rapidapi-key': RAPID_API_KEY,
            'x-rapidapi-host': "indian-stock-exchange.p.rapidapi.com"
        }
        
        # Make request
        conn.request("GET", f"/index.php?id={clean_symbol}", headers=headers)
        
        # Get response
        res = conn.getresponse()
        data = res.read()
        
        # Parse response
        response_data = json.loads(data.decode("utf-8"))
        
        # Check if response contains data
        if not response_data:
            return {
                "error": f"No data found for symbol: {symbol}"
            }
        
        # Format response
        return {
            "symbol": symbol,
            "last_price": response_data.get("lastPrice", 0),
            "change": response_data.get("change", 0),
            "change_percent": response_data.get("pChange", 0),
            "open": response_data.get("open", 0),
            "high": response_data.get("dayHigh", 0),
            "low": response_data.get("dayLow", 0),
            "close": response_data.get("previousClose", 0),
            "volume": response_data.get("totalTradedVolume", 0),
            "market_cap": response_data.get("marketCap", 0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "rapidapi"
        }
        
    except Exception as e:
        return {
            "error": f"Error fetching data: {str(e)}"
        }

def fetch_historical_data(symbol, timeframe='1mo'):
    """
    Fetch historical data for the given symbol using RapidAPI.
    This is a placeholder function as the current RapidAPI endpoint doesn't support historical data.
    We'll use the existing yfinance/nsepy data and augment it with real-time data.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE.NS', 'INFY.NS')
        timeframe (str): Time period for data ('1d', '1w', '1m', '3m', '6m', '1y', '2y', '5y')
    
    Returns:
        pandas.DataFrame: Historical stock data
    """
    # For now, we'll use the existing data fetcher and update the latest data point
    # with real-time data from RapidAPI
    from utils.data_fetcher import fetch_stock_data
    
    # Get historical data from existing source
    historical_data = fetch_stock_data(symbol, timeframe)
    
    if historical_data.empty:
        return historical_data
    
    # Get real-time data
    realtime_data = fetch_realtime_stock_data(symbol)
    
    # If real-time data is available and doesn't have an error, update the latest data point
    if realtime_data and 'error' not in realtime_data:
        # Create a new row for today's data
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if today's data already exists
        if today not in historical_data.index:
            # Create a new row with real-time data
            new_row = pd.Series({
                'Open': realtime_data.get('open', 0),
                'High': realtime_data.get('high', 0),
                'Low': realtime_data.get('low', 0),
                'Close': realtime_data.get('last_price', 0),
                'Volume': realtime_data.get('volume', 0)
            }, name=today)
            
            # Append to historical data
            historical_data = historical_data.append(new_row)
    
    return historical_data