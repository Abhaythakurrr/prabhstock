import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator

def perform_technical_analysis(stock_data):
    """
    Perform technical analysis on stock data.
    
    Args:
        stock_data (pandas.DataFrame): Historical stock data with OHLCV columns
    
    Returns:
        dict: Technical analysis results
    """
    if stock_data.empty:
        return {}
    
    # Make a copy to avoid modifying the original data
    df = stock_data.copy()
    
    # Ensure the dataframe has the required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            return {'error': f'Missing required column: {col}'}
    
    # Ensure all data is numeric
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate technical indicators
    try:
        # Moving Averages
        sma_20 = SMAIndicator(close=df['Close'], window=20).sma_indicator()
        sma_50 = SMAIndicator(close=df['Close'], window=50).sma_indicator()
        sma_200 = SMAIndicator(close=df['Close'], window=200).sma_indicator()
        ema_12 = EMAIndicator(close=df['Close'], window=12).ema_indicator()
        ema_26 = EMAIndicator(close=df['Close'], window=26).ema_indicator()
        
        # MACD
        macd = MACD(close=df['Close']).macd()
        macd_signal = MACD(close=df['Close']).macd_signal()
        macd_diff = MACD(close=df['Close']).macd_diff()
        
        # RSI
        rsi = RSIIndicator(close=df['Close']).rsi()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close']).stoch()
        stoch_signal = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close']).stoch_signal()
        
        # Bollinger Bands
        bollinger = BollingerBands(close=df['Close'])
        bollinger_high = bollinger.bollinger_hband()
        bollinger_low = bollinger.bollinger_lband()
        bollinger_pct = bollinger.bollinger_pband()
        
        # On-Balance Volume
        obv = OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
        
        # Get the latest values
        current_close = df['Close'].iloc[-1]
        current_sma_20 = sma_20.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1] if len(sma_200) > 0 else None
        current_ema_12 = ema_12.iloc[-1]
        current_ema_26 = ema_26.iloc[-1]
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_macd_diff = macd_diff.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_stoch = stoch.iloc[-1]
        current_stoch_signal = stoch_signal.iloc[-1]
        current_bollinger_high = bollinger_high.iloc[-1]
        current_bollinger_low = bollinger_low.iloc[-1]
        current_bollinger_pct = bollinger_pct.iloc[-1]
        
        # Calculate trends
        price_above_sma_20 = current_close > current_sma_20
        price_above_sma_50 = current_close > current_sma_50
        price_above_sma_200 = current_close > current_sma_200 if current_sma_200 else None
        sma_20_above_sma_50 = current_sma_20 > current_sma_50
        sma_50_above_sma_200 = current_sma_50 > current_sma_200 if current_sma_200 else None
        macd_above_signal = current_macd > current_macd_signal
        macd_positive = current_macd > 0
        rsi_overbought = current_rsi > 70
        rsi_oversold = current_rsi < 30
        stoch_overbought = current_stoch > 80
        stoch_oversold = current_stoch < 20
        near_bollinger_high = current_close > (current_bollinger_high * 0.95)
        near_bollinger_low = current_close < (current_bollinger_low * 1.05)
        
        # Golden Cross / Death Cross detection
        golden_cross = False
        death_cross = False
        
        if len(sma_50) > 1 and len(sma_200) > 1:
            prev_sma_50_above_sma_200 = sma_50.iloc[-2] > sma_200.iloc[-2] if not pd.isna(sma_50.iloc[-2]) and not pd.isna(sma_200.iloc[-2]) else None
            current_sma_50_above_sma_200 = sma_50.iloc[-1] > sma_200.iloc[-1] if not pd.isna(sma_50.iloc[-1]) and not pd.isna(sma_200.iloc[-1]) else None
            
            if prev_sma_50_above_sma_200 is not None and current_sma_50_above_sma_200 is not None:
                golden_cross = not prev_sma_50_above_sma_200 and current_sma_50_above_sma_200
                death_cross = prev_sma_50_above_sma_200 and not current_sma_50_above_sma_200
        
        # Compile results
        analysis_results = {
            'moving_averages': {
                'sma_20': float(current_sma_20),
                'sma_50': float(current_sma_50),
                'sma_200': float(current_sma_200) if current_sma_200 else None,
                'ema_12': float(current_ema_12),
                'ema_26': float(current_ema_26),
                'price_above_sma_20': bool(price_above_sma_20),
                'price_above_sma_50': bool(price_above_sma_50),
                'price_above_sma_200': bool(price_above_sma_200) if price_above_sma_200 is not None else None,
                'sma_20_above_sma_50': bool(sma_20_above_sma_50),
                'sma_50_above_sma_200': bool(sma_50_above_sma_200) if sma_50_above_sma_200 is not None else None,
                'golden_cross': bool(golden_cross),
                'death_cross': bool(death_cross)
            },
            'macd': {
                'macd': float(current_macd),
                'signal': float(current_macd_signal),
                'histogram': float(current_macd_diff),
                'macd_above_signal': bool(macd_above_signal),
                'macd_positive': bool(macd_positive)
            },
            'rsi': {
                'value': float(current_rsi),
                'overbought': bool(rsi_overbought),
                'oversold': bool(rsi_oversold)
            },
            'stochastic': {
                'k': float(current_stoch),
                'd': float(current_stoch_signal),
                'overbought': bool(stoch_overbought),
                'oversold': bool(stoch_oversold)
            },
            'bollinger_bands': {
                'upper': float(current_bollinger_high),
                'lower': float(current_bollinger_low),
                'percent_b': float(current_bollinger_pct),
                'near_upper': bool(near_bollinger_high),
                'near_lower': bool(near_bollinger_low)
            }
        }
        
        return analysis_results
    
    except Exception as e:
        return {'error': f'Error performing technical analysis: {str(e)}'}

def get_support_resistance_levels(stock_data, window=20):
    """
    Calculate support and resistance levels.
    
    Args:
        stock_data (pandas.DataFrame): Historical stock data
        window (int): Window size for calculating pivots
    
    Returns:
        dict: Support and resistance levels
    """
    df = stock_data.copy()
    
    # Find pivot highs and lows
    df['pivot_high'] = df['High'].rolling(window=window, center=True).apply(lambda x: x[window//2] == max(x), raw=True)
    df['pivot_low'] = df['Low'].rolling(window=window, center=True).apply(lambda x: x[window//2] == min(x), raw=True)
    
    # Get pivot points
    pivot_highs = df[df['pivot_high'] == 1]['High'].tolist()
    pivot_lows = df[df['pivot_low'] == 1]['Low'].tolist()
    
    # Find clusters of pivot points (resistance and support zones)
    def find_clusters(points, threshold=0.02):
        if not points:
            return []
        
        # Sort points
        sorted_points = sorted(points)
        
        # Initialize clusters
        clusters = [[sorted_points[0]]]
        
        # Group points into clusters
        for point in sorted_points[1:]:
            last_cluster = clusters[-1][-1]
            if point <= last_cluster * (1 + threshold) and point >= last_cluster * (1 - threshold):
                clusters[-1].append(point)
            else:
                clusters.append([point])
        
        # Calculate average of each cluster
        return [sum(cluster) / len(cluster) for cluster in clusters]
    
    resistance_levels = find_clusters(pivot_highs)
    support_levels = find_clusters(pivot_lows)
    
    # Get current price
    current_price = df['Close'].iloc[-1]
    
    # Filter levels near current price
    nearby_resistance = [level for level in resistance_levels if level > current_price]
    nearby_support = [level for level in support_levels if level < current_price]
    
    # Sort by distance from current price
    nearby_resistance.sort()
    nearby_support.sort(reverse=True)
    
    return {
        'resistance_levels': [float(level) for level in nearby_resistance[:3]],
        'support_levels': [float(level) for level in nearby_support[:3]]
    }