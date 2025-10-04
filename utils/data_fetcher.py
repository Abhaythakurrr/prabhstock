import pandas as pd
import yfinance as yf
import nsepy
from datetime import datetime, timedelta
import os

# Import RapidAPI client
from utils.rapidapi_client import fetch_realtime_stock_data

def fetch_stock_data(symbol, timeframe='1y', use_realtime=True):
    """
    Fetch historical stock data for the given symbol and timeframe.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE.NS', 'INFY.NS')
        timeframe (str): Time period for data ('1d', '1w', '1m', '3m', '6m', '1y', '2y', '5y')
        use_realtime (bool): Whether to augment with real-time data from RapidAPI
    
    Returns:
        pandas.DataFrame: Historical stock data
    """
    # Map timeframe to period
    timeframe_map = {
        '1d': '1d',
        '1w': '5d',
        '1m': '1mo',
        '3m': '3mo',
        '6m': '6mo',
        '1y': '1y',
        '2y': '2y',
        '5y': '5y'
    }
    
    period = timeframe_map.get(timeframe, '1y')
    
    # Check if we have cached data
    cache_file = os.path.join('data', f"{symbol}_{timeframe}.csv")
    
    # If cache exists and is recent (less than 1 day old), use it
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time < timedelta(days=1):
            # Check if the file has the standard format or the non-standard format with 'Ticker' and 'Date' rows
            with open(cache_file, 'r') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('Price,Close'):
                # Non-standard format - skip the first 3 rows and use the 4th row as header
                return pd.read_csv(cache_file, skiprows=3, header=None, 
                                 names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'],
                                 index_col=0, parse_dates=True)
            else:
                # Standard format
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    
    # Fetch data using yfinance
    try:
        # For NSE stocks, ensure the symbol has .NS suffix
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
            
        data = yf.download(symbol, period=period)
        
        # If data is empty, try using nsepy for Indian stocks
        if data.empty:
            today = datetime.now()
            if timeframe == '1d':
                start_date = today - timedelta(days=1)
            elif timeframe == '1w':
                start_date = today - timedelta(days=7)
            elif timeframe == '1m':
                start_date = today - timedelta(days=30)
            elif timeframe == '3m':
                start_date = today - timedelta(days=90)
            elif timeframe == '6m':
                start_date = today - timedelta(days=180)
            elif timeframe == '1y':
                start_date = today - timedelta(days=365)
            elif timeframe == '2y':
                start_date = today - timedelta(days=730)
            else:  # 5y
                start_date = today - timedelta(days=1825)
            
            # Remove .NS or .BO suffix for nsepy
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            data = nsepy.get_history(symbol=clean_symbol, start=start_date, end=today)
        
        # Save to cache
        if not data.empty:
            os.makedirs('data', exist_ok=True)
            data.to_csv(cache_file)
        
        # Augment with real-time data if requested
        if use_realtime and not data.empty:
            try:
                # Get real-time data
                realtime_data = fetch_realtime_stock_data(symbol)
                
                # If real-time data is available and doesn't have an error, update the latest data point
                if realtime_data and 'error' not in realtime_data:
                    # Create a new row for today's data
                    today = pd.Timestamp.now().strftime('%Y-%m-%d')
                    
                    # Check if today's data already exists
                    if today not in data.index:
                        # Create a new row with real-time data
                        new_row = pd.Series({
                            'Open': realtime_data.get('open', 0),
                            'High': realtime_data.get('high', 0),
                            'Low': realtime_data.get('low', 0),
                            'Close': realtime_data.get('last_price', 0),
                            'Volume': realtime_data.get('volume', 0)
                        }, name=today)
                        
                        # Append to historical data
                        data = data.append(new_row)
                    else:
                        # Update today's data
                        data.loc[today, 'Close'] = realtime_data.get('last_price', data.loc[today, 'Close'])
                        data.loc[today, 'High'] = max(realtime_data.get('high', 0), data.loc[today, 'High'])
                        data.loc[today, 'Low'] = min(realtime_data.get('low', 0), data.loc[today, 'Low'])
                        data.loc[today, 'Volume'] = realtime_data.get('volume', data.loc[today, 'Volume'])
            except Exception as e:
                print(f"Error augmenting with real-time data: {e}")
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def get_company_info(symbol, use_realtime=True):
    """
    Get company information for the given symbol.
    
    Args:
        symbol (str): Stock symbol (e.g., 'RELIANCE.NS', 'INFY.NS')
        use_realtime (bool): Whether to augment with real-time data from RapidAPI
    
    Returns:
        dict: Company information
    """
    try:
        # For NSE stocks, ensure the symbol has .NS suffix
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Extract relevant information
        company_info = {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'website': info.get('website', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A',
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'avg_volume': info.get('averageVolume', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A')
        }
        
        # Augment with real-time data if requested
        if use_realtime:
            try:
                realtime_data = fetch_realtime_stock_data(symbol)
                if realtime_data and 'error' not in realtime_data:
                    # Update with real-time price information
                    company_info['current_price'] = realtime_data.get('last_price', 'N/A')
                    company_info['price_change'] = realtime_data.get('change', 'N/A')
                    company_info['price_change_percent'] = realtime_data.get('change_percent', 'N/A')
                    company_info['day_high'] = realtime_data.get('high', 'N/A')
                    company_info['day_low'] = realtime_data.get('low', 'N/A')
                    company_info['volume'] = realtime_data.get('volume', 'N/A')
                    company_info['data_source'] = 'RapidAPI (real-time)'
            except Exception as e:
                print(f"Error augmenting with real-time data: {e}")
        
        return company_info
    
    except Exception as e:
        print(f"Error fetching company info for {symbol}: {e}")
        return {}