from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import json

# Import custom modules
from utils.data_fetcher import fetch_stock_data, get_company_info
from utils.technical_analysis import perform_technical_analysis
from models.prediction import predict_stock_movement
from utils.recommendation import generate_recommendation
from utils.rapidapi_client import fetch_realtime_stock_data

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    timeframe = data.get('timeframe', '1y')
    use_realtime = data.get('use_realtime', True)
    use_ai = data.get('use_ai', True)
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        # Fetch historical data with real-time augmentation if requested
        stock_data = fetch_stock_data(symbol, timeframe, use_realtime=use_realtime)
        
        if stock_data.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        response = {'symbol': symbol}
        
        # Get real-time data if requested
        if use_realtime:
            realtime_data = fetch_realtime_stock_data(symbol)
            if realtime_data and 'error' not in realtime_data:
                response['realtime'] = realtime_data
        
        try:
            # Perform technical analysis
            analysis_results = perform_technical_analysis(stock_data)
            response['analysis'] = analysis_results
            
            # Get prediction with AI if requested
            prediction = predict_stock_movement(stock_data, analysis_results, use_ai_prediction=use_ai)
            response['prediction'] = prediction
            
            # Generate recommendation
            recommendation = generate_recommendation(analysis_results, prediction)
            response['recommendation'] = recommendation
        except Exception as e:
            # If analysis fails, provide partial response with error
            response['error'] = str(e)
            response['current_price'] = float(stock_data['Close'].iloc[-1]) if not stock_data.empty else 0
            response['analysis'] = {}
            response['prediction'] = {'direction': 'unknown', 'confidence': 0, 'source': 'error'}
            response['recommendation'] = {'verdict': 'HOLD', 'confidence': 0, 'reasons': ['Analysis error occurred']}
        
        # Add current price to response if not already added
        if 'current_price' not in response:
            response['current_price'] = float(stock_data['Close'].iloc[-1])
        
        # Add data source information
        response['data_source'] = 'RapidAPI (real-time)' if use_realtime else 'Historical'
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/symbols')
def get_symbols():
    # Return a list of popular Indian stocks
    popular_stocks = [
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Ltd.'},
        {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Ltd.'},
        {'symbol': 'INFY.NS', 'name': 'Infosys Ltd.'},
        {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Ltd.'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Ltd.'},
        {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Ltd.'},
        {'symbol': 'SBIN.NS', 'name': 'State Bank of India'},
        {'symbol': 'BAJFINANCE.NS', 'name': 'Bajaj Finance Ltd.'},
        {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Ltd.'},
        {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Ltd.'}
    ]
    return jsonify(popular_stocks)

@app.route('/chart-data', methods=['POST'])
def get_chart_data():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    timeframe = data.get('timeframe', '1y')
    use_realtime = data.get('use_realtime', True)
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        # Fetch historical data with real-time augmentation if requested
        stock_data = fetch_stock_data(symbol, timeframe, use_realtime=use_realtime)
        
        if stock_data.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Format data for charts
        # Convert index to dates safely
        try:
            # Try to convert index to datetime and format as string
            dates = pd.to_datetime(stock_data.index).strftime('%Y-%m-%d').tolist()
        except (AttributeError, ValueError, TypeError):
            # If that fails, convert index to strings directly
            dates = [str(date) for date in stock_data.index.tolist()]
            
        # Filter out any non-date strings (like 'Ticker' or 'Date')
        import re
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        dates = [date for date in dates if date_pattern.match(date)]
            
        chart_data = {
            'dates': dates,
            'prices': {
                'close': stock_data['Close'].tolist(),
                'open': stock_data['Open'].tolist(),
                'high': stock_data['High'].tolist(),
                'low': stock_data['Low'].tolist()
            },
            'volume': stock_data['Volume'].tolist(),
            'technical': {
                'sma_20': stock_data['sma_20'].tolist() if 'sma_20' in stock_data.columns else [],
                'sma_50': stock_data['sma_50'].tolist() if 'sma_50' in stock_data.columns else [],
                'sma_200': stock_data['sma_200'].tolist() if 'sma_200' in stock_data.columns else [],
                'upper_band': stock_data['upper_band'].tolist() if 'upper_band' in stock_data.columns else [],
                'middle_band': stock_data['middle_band'].tolist() if 'middle_band' in stock_data.columns else [],
                'lower_band': stock_data['lower_band'].tolist() if 'lower_band' in stock_data.columns else [],
                'rsi': stock_data['rsi'].tolist() if 'rsi' in stock_data.columns else []
            }
        }
        
        return jsonify(chart_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watchlist', methods=['GET'])
def get_watchlist():
    # In a real app, this would be fetched from a database
    # For now, we'll return a static list of stocks with their latest analysis
    watchlist = [
        {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Ltd.'},
        {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services Ltd.'},
        {'symbol': 'INFY.NS', 'name': 'Infosys Ltd.'},
        {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Ltd.'},
        {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Ltd.'}
    ]
    
    # Enrich with latest data
    for stock in watchlist:
        try:
            # Get real-time data first
            realtime_data = fetch_realtime_stock_data(stock['symbol'])
            if realtime_data and 'error' not in realtime_data:
                # Add real-time data
                stock['current_price'] = realtime_data.get('last_price', 0)
                stock['price_change'] = realtime_data.get('change', 0)
                stock['price_change_pct'] = realtime_data.get('change_percent', 0)
                stock['data_source'] = 'RapidAPI (real-time)'
            else:
                # Fall back to historical data
                stock_data = fetch_stock_data(stock['symbol'], '1mo', use_realtime=False)
                if not stock_data.empty:
                    # Add current price and change
                    stock['current_price'] = float(stock_data['Close'].iloc[-1])
                    # Convert to float before subtraction to avoid string subtraction
                    latest_price = float(stock_data['Close'].iloc[-1])
                    previous_price = float(stock_data['Close'].iloc[-2])
                    stock['price_change'] = latest_price - previous_price
                    stock['price_change_pct'] = (stock['price_change'] / previous_price) * 100
                    stock['data_source'] = 'Historical'
            
            # Get historical data for analysis
            stock_data = fetch_stock_data(stock['symbol'], '1mo', use_realtime=True)
            if not stock_data.empty:
                # Add quick analysis with error handling
                try:
                    analysis = perform_technical_analysis(stock_data)
                    prediction = predict_stock_movement(stock_data, analysis, use_ai_prediction=True)
                    stock['analysis'] = analysis
                    stock['prediction'] = prediction
                except Exception as e:
                    stock['error'] = str(e)
                    stock['analysis'] = {}
                    stock['prediction'] = {'direction': 'unknown', 'confidence': 0, 'source': 'error'}
                # Generate recommendation if analysis and prediction are available
                if 'analysis' in stock and 'prediction' in stock:
                    recommendation = generate_recommendation(stock['analysis'], stock['prediction'])
                    stock['recommendation'] = recommendation['verdict']
                else:
                    stock['recommendation'] = 'HOLD'
        except Exception as e:
            stock['error'] = str(e)
    
    return jsonify(watchlist)

@app.route('/realtime-data', methods=['POST'])
def get_realtime_data():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        # Fetch real-time data
        realtime_data = fetch_realtime_stock_data(symbol)
        
        if not realtime_data or 'error' in realtime_data:
            return jsonify({'error': f'No real-time data found for {symbol}'}), 404
        
        return jsonify(realtime_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/company-info', methods=['POST'])
def get_company_info_route():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    use_realtime = data.get('use_realtime', True)
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        # Fetch company info
        company_info = get_company_info(symbol, use_realtime=use_realtime)
        
        if not company_info:
            return jsonify({'error': f'No company info found for {symbol}'}), 404
        
        return jsonify(company_info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories if they don't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    app.run(debug=True, port=5000)