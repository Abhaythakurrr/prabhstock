import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

def generate_prediction(stock_symbol, historical_data, technical_analysis):
    """
    Generate AI prediction for stock movement using OpenRouter API.
    
    Args:
        stock_symbol (str): Stock symbol (e.g., 'RELIANCE.NS')
        historical_data (dict): Historical price data
        technical_analysis (dict): Technical analysis results
        
    Returns:
        dict: AI prediction results
    """
    try:
        # Prepare the prompt with stock data and technical analysis
        prompt = f"""Based on the following data for {stock_symbol}, predict whether the stock price will go up or down in the next trading day, and provide a confidence level (0-100%) and reasoning:

Historical Data (Last 5 days):
"""
        
        # Add last 5 days of price data
        dates = historical_data.get('dates', [])[-5:]
        prices = historical_data.get('prices', {}).get('close', [])[-5:]
        
        for i in range(len(dates)):
            if i < len(prices):
                prompt += f"\n{dates[i]}: {prices[i]}"
        
        # Add technical indicators
        prompt += "\n\nTechnical Indicators:"
        
        # Add moving averages
        ma = technical_analysis.get('moving_averages', {})
        prompt += f"\nPrice above 20-day MA: {ma.get('price_above_sma_20', 'Unknown')}"
        prompt += f"\nPrice above 50-day MA: {ma.get('price_above_sma_50', 'Unknown')}"
        prompt += f"\nPrice above 200-day MA: {ma.get('price_above_sma_200', 'Unknown')}"
        prompt += f"\nGolden Cross: {ma.get('golden_cross', 'Unknown')}"
        prompt += f"\nDeath Cross: {ma.get('death_cross', 'Unknown')}"
        
        # Add RSI
        rsi = technical_analysis.get('rsi', {})
        prompt += f"\nRSI: {rsi.get('value', 'Unknown')}"
        prompt += f"\nRSI Overbought: {rsi.get('overbought', 'Unknown')}"
        prompt += f"\nRSI Oversold: {rsi.get('oversold', 'Unknown')}"
        
        # Add MACD
        macd = technical_analysis.get('macd', {})
        prompt += f"\nMACD above Signal: {macd.get('macd_above_signal', 'Unknown')}"
        prompt += f"\nMACD Positive: {macd.get('macd_positive', 'Unknown')}"
        
        # Request prediction
        prompt += "\n\nBased on this data, predict the stock movement (UP or DOWN), confidence level (0-100%), and provide a brief explanation."
        
        # Make API request to OpenRouter
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        
        if response.status_code != 200:
            return {
                "direction": "unknown",
                "confidence": 0,
                "explanation": f"API Error: {response.status_code}",
                "source": "ai"
            }
        
        # Parse the response
        result = response.json()
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Extract prediction from AI response
        direction = "unknown"
        confidence = 0
        explanation = "No clear prediction"
        
        # Simple parsing of the AI response
        ai_response_lower = ai_response.lower()
        if "up" in ai_response_lower or "increase" in ai_response_lower or "rise" in ai_response_lower:
            direction = "up"
        elif "down" in ai_response_lower or "decrease" in ai_response_lower or "fall" in ai_response_lower:
            direction = "down"
        
        # Try to extract confidence percentage
        import re
        confidence_matches = re.findall(r'(\d+)\s*%', ai_response)
        if confidence_matches:
            try:
                confidence = int(confidence_matches[0]) / 100  # Convert percentage to decimal
            except ValueError:
                confidence = 0.5  # Default if parsing fails
        
        # Extract explanation (use the whole response as explanation if we can't parse it)
        explanation = ai_response
        
        return {
            "direction": direction,
            "confidence": confidence,
            "explanation": explanation,
            "source": "ai"
        }
        
    except Exception as e:
        return {
            "direction": "unknown",
            "confidence": 0,
            "explanation": f"Error: {str(e)}",
            "source": "ai"
        }