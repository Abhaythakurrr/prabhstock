import numpy as np

def generate_recommendation(analysis_results, prediction):
    """
    Generate buy/sell/hold recommendation based on technical analysis and AI prediction.
    
    Args:
        analysis_results (dict): Technical analysis results
        prediction (dict): AI prediction results
    
    Returns:
        dict: Recommendation with verdict and confidence score
    """
    if not analysis_results or 'error' in analysis_results:
        return {
            'verdict': 'HOLD',
            'confidence': 0,
            'reasons': ['Insufficient data for analysis']
        }
    
    # Initialize scores and reasons
    buy_score = 0
    sell_score = 0
    hold_score = 0
    reasons = []
    
    # Check moving averages
    ma = analysis_results.get('moving_averages', {})
    if ma:
        # Price above key moving averages (bullish)
        if ma.get('price_above_sma_20'):
            buy_score += 1
            reasons.append('Price is above 20-day SMA (bullish)')
        else:
            sell_score += 1
            reasons.append('Price is below 20-day SMA (bearish)')
            
        if ma.get('price_above_sma_50'):
            buy_score += 1
            reasons.append('Price is above 50-day SMA (bullish)')
        else:
            sell_score += 1
            reasons.append('Price is below 50-day SMA (bearish)')
            
        if ma.get('price_above_sma_200') is not None:
            if ma.get('price_above_sma_200'):
                buy_score += 2
                reasons.append('Price is above 200-day SMA (strongly bullish)')
            else:
                sell_score += 2
                reasons.append('Price is below 200-day SMA (strongly bearish)')
        
        # Moving average crossovers
        if ma.get('sma_20_above_sma_50'):
            buy_score += 1
            reasons.append('20-day SMA is above 50-day SMA (bullish)')
        else:
            sell_score += 1
            reasons.append('20-day SMA is below 50-day SMA (bearish)')
            
        if ma.get('sma_50_above_sma_200') is not None:
            if ma.get('sma_50_above_sma_200'):
                buy_score += 2
                reasons.append('50-day SMA is above 200-day SMA (strongly bullish)')
            else:
                sell_score += 2
                reasons.append('50-day SMA is below 200-day SMA (strongly bearish)')
        
        # Golden Cross / Death Cross (very significant signals)
        if ma.get('golden_cross'):
            buy_score += 3
            reasons.append('Golden Cross detected (very bullish)')
        
        if ma.get('death_cross'):
            sell_score += 3
            reasons.append('Death Cross detected (very bearish)')
    
    # Check MACD
    macd_data = analysis_results.get('macd', {})
    if macd_data:
        if macd_data.get('macd_above_signal'):
            buy_score += 2
            reasons.append('MACD is above signal line (bullish)')
        else:
            sell_score += 2
            reasons.append('MACD is below signal line (bearish)')
            
        if macd_data.get('macd_positive'):
            buy_score += 1
            reasons.append('MACD is positive (bullish)')
        else:
            sell_score += 1
            reasons.append('MACD is negative (bearish)')
    
    # Check RSI
    rsi_data = analysis_results.get('rsi', {})
    if rsi_data:
        rsi_value = rsi_data.get('value')
        
        if rsi_data.get('overbought'):
            sell_score += 3
            reasons.append(f'RSI is overbought at {rsi_value:.2f} (strongly bearish)')
        elif rsi_data.get('oversold'):
            buy_score += 3
            reasons.append(f'RSI is oversold at {rsi_value:.2f} (strongly bullish)')
        elif rsi_value > 50:
            buy_score += 1
            reasons.append(f'RSI is bullish at {rsi_value:.2f}')
        else:
            sell_score += 1
            reasons.append(f'RSI is bearish at {rsi_value:.2f}')
    
    # Check Stochastic Oscillator
    stoch_data = analysis_results.get('stochastic', {})
    if stoch_data:
        if stoch_data.get('overbought'):
            sell_score += 2
            reasons.append('Stochastic Oscillator is overbought (bearish)')
        elif stoch_data.get('oversold'):
            buy_score += 2
            reasons.append('Stochastic Oscillator is oversold (bullish)')
    
    # Check Bollinger Bands
    bb_data = analysis_results.get('bollinger_bands', {})
    if bb_data:
        if bb_data.get('near_upper'):
            sell_score += 2
            reasons.append('Price is near upper Bollinger Band (potential reversal)')
        elif bb_data.get('near_lower'):
            buy_score += 2
            reasons.append('Price is near lower Bollinger Band (potential reversal)')
    
    # Consider AI prediction
    if prediction:
        pred_direction = prediction.get('direction')
        pred_confidence = prediction.get('confidence', 0)
        
        if pred_direction == 'up' and pred_confidence > 0.6:
            buy_score += int(pred_confidence * 5)  # Scale by confidence
            reasons.append(f'AI predicts upward movement with {pred_confidence:.2f} confidence')
        elif pred_direction == 'down' and pred_confidence > 0.6:
            sell_score += int(pred_confidence * 5)  # Scale by confidence
            reasons.append(f'AI predicts downward movement with {pred_confidence:.2f} confidence')
        else:
            hold_score += 2
            reasons.append('AI prediction is uncertain')
    
    # Calculate total scores
    total_score = buy_score + sell_score + hold_score
    if total_score == 0:
        total_score = 1  # Avoid division by zero
    
    buy_confidence = buy_score / total_score
    sell_confidence = sell_score / total_score
    hold_confidence = hold_score / total_score
    
    # Determine verdict
    if buy_confidence > sell_confidence and buy_confidence > hold_confidence:
        if buy_confidence > 0.7:
            verdict = 'STRONG BUY'
        else:
            verdict = 'BUY'
        confidence = buy_confidence
    elif sell_confidence > buy_confidence and sell_confidence > hold_confidence:
        if sell_confidence > 0.7:
            verdict = 'STRONG SELL'
        else:
            verdict = 'SELL'
        confidence = sell_confidence
    else:
        verdict = 'HOLD'
        confidence = max(hold_confidence, 0.5)  # Minimum 0.5 confidence for HOLD
    
    # Limit reasons to top 5 most significant
    if len(reasons) > 5:
        # Sort reasons by significance (length is a simple proxy for significance)
        reasons.sort(key=len, reverse=True)
        reasons = reasons[:5]
    
    return {
        'verdict': verdict,
        'confidence': round(confidence * 100),  # Convert to percentage
        'reasons': reasons
    }