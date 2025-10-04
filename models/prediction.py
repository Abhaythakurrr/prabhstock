import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime

# Import OpenRouter API for AI predictions
from utils.openrouter_api import generate_prediction

def prepare_features(stock_data):
    """
    Prepare features for the prediction model.
    
    Args:
        stock_data (pandas.DataFrame): Historical stock data
    
    Returns:
        pandas.DataFrame: DataFrame with features
    """
    df = stock_data.copy()
    
    # Calculate returns
    df['return'] = pd.to_numeric(df['Close'], errors='coerce').pct_change()
    df['return_1d'] = df['return'].shift(1)
    df['return_2d'] = df['return'].shift(2)
    df['return_3d'] = df['return'].shift(3)
    df['return_5d'] = df['return'].shift(5)
    df['return_10d'] = df['return'].shift(10)
    
    # Calculate moving averages
    df['sma_5'] = pd.to_numeric(df['Close'], errors='coerce').rolling(window=5).mean()
    df['sma_10'] = pd.to_numeric(df['Close'], errors='coerce').rolling(window=10).mean()
    df['sma_20'] = pd.to_numeric(df['Close'], errors='coerce').rolling(window=20).mean()
    df['sma_50'] = pd.to_numeric(df['Close'], errors='coerce').rolling(window=50).mean()
    
    # Calculate price relative to moving averages
    # Handle potential division by zero or NaN values
    # Ensure values are converted to float before division and handle infinity values
    close_numeric = pd.to_numeric(df['Close'], errors='coerce')
    sma5_numeric = pd.to_numeric(df['sma_5'], errors='coerce')
    sma10_numeric = pd.to_numeric(df['sma_10'], errors='coerce')
    sma20_numeric = pd.to_numeric(df['sma_20'], errors='coerce')
    sma50_numeric = pd.to_numeric(df['sma_50'], errors='coerce')
    
    # Replace zeros with NaN to avoid division by zero
    sma5_numeric = sma5_numeric.replace(0, np.nan)
    sma10_numeric = sma10_numeric.replace(0, np.nan)
    sma20_numeric = sma20_numeric.replace(0, np.nan)
    sma50_numeric = sma50_numeric.replace(0, np.nan)
    
    df['price_sma_5_ratio'] = close_numeric.div(sma5_numeric).replace([np.inf, -np.inf], np.nan)
    df['price_sma_10_ratio'] = close_numeric.div(sma10_numeric).replace([np.inf, -np.inf], np.nan)
    df['price_sma_20_ratio'] = close_numeric.div(sma20_numeric).replace([np.inf, -np.inf], np.nan)
    df['price_sma_50_ratio'] = close_numeric.div(sma50_numeric).replace([np.inf, -np.inf], np.nan)
    
    # Calculate volatility
    df['volatility_5d'] = df['return'].rolling(window=5).std()
    df['volatility_10d'] = df['return'].rolling(window=10).std()
    df['volatility_20d'] = df['return'].rolling(window=20).std()
    
    # Calculate volume features
    volume_numeric = pd.to_numeric(df['Volume'], errors='coerce')
    df['volume_change'] = volume_numeric.pct_change()
    df['volume_sma_5'] = volume_numeric.rolling(window=5).mean()
    df['volume_sma_10'] = volume_numeric.rolling(window=10).mean()
    
    # Replace zeros with NaN to avoid division by zero
    volume_sma5 = pd.to_numeric(df['volume_sma_5'], errors='coerce').replace(0, np.nan)
    volume_sma10 = pd.to_numeric(df['volume_sma_10'], errors='coerce').replace(0, np.nan)
    
    df['volume_ratio_5'] = volume_numeric.div(volume_sma5).replace([np.inf, -np.inf], np.nan)
    df['volume_ratio_10'] = volume_numeric.div(volume_sma10).replace([np.inf, -np.inf], np.nan)
    
    # Calculate price momentum
    df['momentum_5d'] = pd.to_numeric(df['Close'], errors='coerce') - pd.to_numeric(df['Close'], errors='coerce').shift(5)
    df['momentum_10d'] = pd.to_numeric(df['Close'], errors='coerce') - pd.to_numeric(df['Close'], errors='coerce').shift(10)
    df['momentum_20d'] = pd.to_numeric(df['Close'], errors='coerce') - pd.to_numeric(df['Close'], errors='coerce').shift(20)
    
    # Calculate target variable (next day return)
    df['target_return'] = df['return'].shift(-1)
    df['target_direction'] = np.where(df['target_return'] > 0, 1, 0)
    
    # Fill NaN values with appropriate defaults instead of dropping
    # This helps prevent data loss while still handling infinity and NaN values
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Fill NaN values with appropriate defaults
    # For ratio columns, use 1.0 (neutral value)
    ratio_columns = ['price_sma_5_ratio', 'price_sma_10_ratio', 'price_sma_20_ratio', 'price_sma_50_ratio',
                     'volume_ratio_5', 'volume_ratio_10']
    for col in ratio_columns:
        if col in df.columns:
            df[col] = df[col].fillna(1.0)
    
    # For return columns, use 0.0 (no change)
    return_columns = ['return', 'return_1d', 'return_2d', 'return_3d', 'return_5d', 'return_10d', 'target_return']
    for col in return_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)
    
    # For volatility columns, use the mean or a small default value
    volatility_columns = ['volatility_5d', 'volatility_10d', 'volatility_20d']
    for col in volatility_columns:
        if col in df.columns:
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val if not np.isnan(mean_val) else 0.01)
    
    # For momentum columns, use 0.0 (no momentum)
    momentum_columns = ['momentum_5d', 'momentum_10d', 'momentum_20d']
    for col in momentum_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)
    
    # For target direction, use the most common value or 0
    if 'target_direction' in df.columns:
        most_common = df['target_direction'].mode().iloc[0] if not df['target_direction'].empty else 0
        df['target_direction'] = df['target_direction'].fillna(most_common)
    
    # Finally, drop any remaining NaN values as a safety measure
    df = df.dropna()
    
    return df

def train_prediction_model(stock_data, symbol):
    """
    Train a prediction model for the given stock.
    
    Args:
        stock_data (pandas.DataFrame): Historical stock data
        symbol (str): Stock symbol
    
    Returns:
        dict: Training results
    """
    # Prepare features
    df = prepare_features(stock_data)
    
    if len(df) < 100:
        return {'error': 'Insufficient data for training'}
    
    # Define features and target
    feature_columns = [
        'return_1d', 'return_2d', 'return_3d', 'return_5d', 'return_10d',
        'price_sma_5_ratio', 'price_sma_10_ratio', 'price_sma_20_ratio', 'price_sma_50_ratio',
        'volatility_5d', 'volatility_10d', 'volatility_20d',
        'volume_change', 'volume_ratio_5', 'volume_ratio_10',
        'momentum_5d', 'momentum_10d', 'momentum_20d'
    ]
    
    X = df[feature_columns]
    y_direction = df['target_direction']
    y_return = df['target_return']
    
    # Split data
    X_train, X_test, y_dir_train, y_dir_test, y_ret_train, y_ret_test = train_test_split(
        X, y_direction, y_return, test_size=0.2, shuffle=False
    )
    
    # Scale features
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train direction model (classification)
    dir_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dir_model.fit(X_train_scaled, y_dir_train)
    
    # Train return model (regression)
    ret_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    ret_model.fit(X_train_scaled, y_ret_train)
    
    # Evaluate models
    dir_accuracy = dir_model.score(X_test_scaled, y_dir_test)
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(dir_model, f'models/{symbol}_direction_model.joblib')
    joblib.dump(ret_model, f'models/{symbol}_return_model.joblib')
    joblib.dump(scaler, f'models/{symbol}_scaler.joblib')
    
    # Save feature list
    with open(f'models/{symbol}_features.txt', 'w') as f:
        f.write('\n'.join(feature_columns))
    
    return {
        'direction_accuracy': dir_accuracy,
        'training_date': datetime.now().strftime('%Y-%m-%d'),
        'data_points': len(df),
        'features': feature_columns
    }

def predict_stock_movement(stock_data, analysis_results=None, use_ai_prediction=True):
    """
    Predict stock movement using trained models or create a new model if none exists.
    Can also use AI prediction from OpenRouter API if requested.
    
    Args:
        stock_data (pandas.DataFrame): Historical stock data
        analysis_results (dict, optional): Technical analysis results
        use_ai_prediction (bool): Whether to use AI prediction from OpenRouter
    
    Returns:
        dict: Prediction results
    """
    if stock_data.empty:
        return {
            'direction': 'unknown',
            'confidence': 0,
            'predicted_return': 0,
            'error': 'No data available'
        }
    
    # Extract symbol from the first row index if available
    symbol = None
    if hasattr(stock_data.index, 'name') and stock_data.index.name == 'Symbol':
        symbol = stock_data.index[0]
    else:
        # Use a default symbol name
        symbol = 'STOCK'
    
    # Check if models exist
    dir_model_path = f'models/{symbol}_direction_model.joblib'
    ret_model_path = f'models/{symbol}_return_model.joblib'
    scaler_path = f'models/{symbol}_scaler.joblib'
    features_path = f'models/{symbol}_features.txt'
    
    # Train new models if they don't exist
    if not (os.path.exists(dir_model_path) and 
            os.path.exists(ret_model_path) and 
            os.path.exists(scaler_path) and 
            os.path.exists(features_path)):
        train_result = train_prediction_model(stock_data, symbol)
        if 'error' in train_result:
            return {
                'direction': 'unknown',
                'confidence': 0,
                'predicted_return': 0,
                'error': train_result['error']
            }
    
    try:
        # Load models and scaler
        dir_model = joblib.load(dir_model_path)
        ret_model = joblib.load(ret_model_path)
        scaler = joblib.load(scaler_path)
        
        # Load feature list
        with open(features_path, 'r') as f:
            feature_columns = f.read().splitlines()
        
        # Prepare features for prediction
        df = prepare_features(stock_data)
        
        if df.empty:
            return {
                'direction': 'unknown',
                'confidence': 0,
                'predicted_return': 0,
                'error': 'Failed to prepare features'
            }
        
        # Get the latest data point
        latest_data = df.iloc[-1:][feature_columns]
        
        # Scale features with error handling
        try:
            # Handle any potential infinity or NaN values
            latest_data = latest_data.replace([np.inf, -np.inf], np.nan)
            
            # Fill any NaN values with appropriate defaults
            for col in latest_data.columns:
                if 'ratio' in col:
                    latest_data[col] = latest_data[col].fillna(1.0)
                elif 'return' in col:
                    latest_data[col] = latest_data[col].fillna(0.0)
                elif 'volatility' in col:
                    latest_data[col] = latest_data[col].fillna(0.01)
                elif 'momentum' in col:
                    latest_data[col] = latest_data[col].fillna(0.0)
                else:
                    # For any other columns, use column mean or 0
                    col_mean = latest_data[col].mean()
                    latest_data[col] = latest_data[col].fillna(0 if np.isnan(col_mean) else col_mean)
            
            latest_data_scaled = scaler.transform(latest_data)
            
            # Make predictions
            direction_prob = dir_model.predict_proba(latest_data_scaled)[0]
            predicted_return = ret_model.predict(latest_data_scaled)[0]
        except Exception as e:
            return {
                'direction': 'unknown',
                'confidence': 0,
                'predicted_return': 0,
                'error': f'Error during prediction scaling: {str(e)}'
            }
        
        # Determine direction and confidence
        if direction_prob[1] > 0.5:  # Probability of upward movement
            direction = 'up'
            confidence = direction_prob[1]
        else:
            direction = 'down'
            confidence = direction_prob[0]
        
        # Incorporate technical analysis if available
        if analysis_results and not isinstance(analysis_results, str) and 'error' not in analysis_results:
            # Adjust confidence based on technical indicators
            ma = analysis_results.get('moving_averages', {})
            rsi = analysis_results.get('rsi', {})
            macd = analysis_results.get('macd', {})
            
            # Adjust for strong technical signals
            if direction == 'up':
                if ma.get('golden_cross'):
                    confidence = min(confidence + 0.1, 0.95)
                if rsi.get('oversold'):
                    confidence = min(confidence + 0.05, 0.95)
                if macd.get('macd_above_signal') and macd.get('macd_positive'):
                    confidence = min(confidence + 0.05, 0.95)
            else:  # direction == 'down'
                if ma.get('death_cross'):
                    confidence = min(confidence + 0.1, 0.95)
                if rsi.get('overbought'):
                    confidence = min(confidence + 0.05, 0.95)
                if not macd.get('macd_above_signal') and not macd.get('macd_positive'):
                    confidence = min(confidence + 0.05, 0.95)
        
        # Create the prediction result
        prediction_result = {
            'direction': direction,
            'confidence': round(confidence, 2),
            'predicted_return': round(predicted_return * 100, 2),  # Convert to percentage
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'model'
        }
        
        # If AI prediction is requested, get it and combine with model prediction
        if use_ai_prediction:
            try:
                # Extract symbol from stock data if available
                symbol = None
                if hasattr(stock_data.index, 'name') and stock_data.index.name == 'Symbol':
                    symbol = stock_data.index[0]
                else:
                    # Try to extract from the first row
                    symbol = 'STOCK'
                
                # Prepare chart data for AI prediction
                chart_data = {
                    'dates': pd.to_datetime(stock_data.index).strftime('%Y-%m-%d').tolist(),
                    'prices': {
                        'close': stock_data['Close'].tolist(),
                        'open': stock_data['Open'].tolist(),
                        'high': stock_data['High'].tolist(),
                        'low': stock_data['Low'].tolist()
                    },
                    'volume': stock_data['Volume'].tolist()
                }
                
                # Get AI prediction
                ai_prediction = generate_prediction(symbol, chart_data, analysis_results)
                
                # If AI prediction is successful, add it to the result
                if ai_prediction and 'direction' in ai_prediction and ai_prediction['direction'] != 'unknown':
                    # Add AI prediction to the result
                    prediction_result['ai_direction'] = ai_prediction['direction']
                    prediction_result['ai_confidence'] = ai_prediction['confidence']
                    prediction_result['ai_explanation'] = ai_prediction['explanation']
                    
                    # Combine model and AI predictions
                    # If they agree, increase confidence
                    if prediction_result['direction'] == ai_prediction['direction']:
                        prediction_result['combined_confidence'] = min(0.95, prediction_result['confidence'] + 0.1)
                        prediction_result['combined_direction'] = prediction_result['direction']
                    else:
                        # If they disagree, use the one with higher confidence
                        if prediction_result['confidence'] >= ai_prediction['confidence']:
                            prediction_result['combined_confidence'] = prediction_result['confidence']
                            prediction_result['combined_direction'] = prediction_result['direction']
                        else:
                            prediction_result['combined_confidence'] = ai_prediction['confidence']
                            prediction_result['combined_direction'] = ai_prediction['direction']
                    
                    # Add AI as a source
                    prediction_result['sources'] = ['model', 'ai']
            except Exception as e:
                # If AI prediction fails, just use the model prediction
                prediction_result['ai_error'] = str(e)
        
        return prediction_result
    
    except Exception as e:
        error_result = {
            'direction': 'unknown',
            'confidence': 0,
            'predicted_return': 0,
            'error': f'Prediction error: {str(e)}',
            'source': 'model'
        }
        
        # If model prediction fails but AI prediction is requested, try using only AI
        if use_ai_prediction:
            try:
                # Extract symbol from stock data if available
                symbol = None
                if hasattr(stock_data.index, 'name') and stock_data.index.name == 'Symbol':
                    symbol = stock_data.index[0]
                else:
                    # Try to extract from the first row
                    symbol = 'STOCK'
                
                # Prepare chart data for AI prediction
                chart_data = {
                    'dates': pd.to_datetime(stock_data.index).strftime('%Y-%m-%d').tolist(),
                    'prices': {
                        'close': stock_data['Close'].tolist(),
                        'open': stock_data['Open'].tolist(),
                        'high': stock_data['High'].tolist(),
                        'low': stock_data['Low'].tolist()
                    },
                    'volume': stock_data['Volume'].tolist()
                }
                
                # Get AI prediction
                ai_prediction = generate_prediction(symbol, chart_data, analysis_results)
                
                # If AI prediction is successful, use it as the result
                if ai_prediction and 'direction' in ai_prediction and ai_prediction['direction'] != 'unknown':
                    error_result['ai_direction'] = ai_prediction['direction']
                    error_result['ai_confidence'] = ai_prediction['confidence']
                    error_result['ai_explanation'] = ai_prediction['explanation']
                    error_result['combined_direction'] = ai_prediction['direction']
                    error_result['combined_confidence'] = ai_prediction['confidence']
                    error_result['sources'] = ['ai']
            except Exception as ai_error:
                error_result['ai_error'] = str(ai_error)
        
        return error_result