import pandas as pd
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.technical_indicators import TechnicalIndicators

class MACDScanner:
    """MACD Scanner with 15-minute intervals for momentum analysis"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.tech_indicators = TechnicalIndicators()
        
    def scan(self, timeframe="15m", lookback_days=30):
        """
        Scan for MACD signals
        
        Args:
            timeframe: Data timeframe (15m, 1h, 4h, 1d)
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with MACD signals
        """
        try:
            # Get NSE stock list
            symbols = self.data_fetcher.get_nse_stock_list()
            results = []
            
            for symbol in symbols[:100]:  # Limit to first 100 for performance
                try:
                    # Fetch data
                    data = self.data_fetcher.get_stock_data(
                        symbol, 
                        period=f"{lookback_days}d",
                        interval=timeframe
                    )
                    
                    if data is None or len(data) < 50:
                        continue
                    
                    # Calculate MACD
                    macd_data = self.tech_indicators.calculate_macd(
                        data['Close'], 
                        fast=12, 
                        slow=26, 
                        signal=9
                    )
                    
                    # Check for MACD signals
                    signal = self.detect_macd_signal(macd_data)
                    
                    if signal['type'] != 'none':
                        # Get current price info
                        current_price = data['Close'].iloc[-1]
                        volume = data['Volume'].iloc[-1] if 'Volume' in data else 0
                        
                        # Calculate additional metrics
                        price_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                        
                        results.append({
                            'Symbol': symbol,
                            'Signal': signal['type'],
                            'MACD': round(macd_data['MACD'].iloc[-1], 4),
                            'Signal_Line': round(macd_data['Signal'].iloc[-1], 4),
                            'Histogram': round(macd_data['Histogram'].iloc[-1], 4),
                            'Current_Price': round(current_price, 2),
                            'Price_Change_%': round(price_change, 2),
                            'Volume': int(volume),
                            'Strength': signal['strength'],
                            'Timeframe': timeframe
                        })
                        
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error in MACD scanner: {e}")
            return pd.DataFrame()
    
    def detect_macd_signal(self, macd_data):
        """
        Detect MACD signals
        
        Args:
            macd_data: DataFrame with MACD, Signal, and Histogram columns
            
        Returns:
            Dict with signal type and strength
        """
        if len(macd_data) < 3:
            return {'type': 'none', 'strength': 0}
        
        macd = macd_data['MACD'].iloc[-1]
        signal_line = macd_data['Signal'].iloc[-1]
        histogram = macd_data['Histogram'].iloc[-1]
        
        prev_histogram = macd_data['Histogram'].iloc[-2]
        prev_macd = macd_data['MACD'].iloc[-2]
        prev_signal = macd_data['Signal'].iloc[-2]
        
        # Bullish signals
        if (macd > signal_line and prev_macd <= prev_signal and 
            histogram > 0 and prev_histogram <= 0):
            strength = min(abs(histogram) * 10, 100)
            return {'type': 'Bullish Crossover', 'strength': round(strength, 1)}
        
        # Bearish signals
        elif (macd < signal_line and prev_macd >= prev_signal and 
              histogram < 0 and prev_histogram >= 0):
            strength = min(abs(histogram) * 10, 100)
            return {'type': 'Bearish Crossover', 'strength': round(strength, 1)}
        
        # Divergence signals
        elif macd > signal_line and histogram > prev_histogram > 0:
            strength = min(abs(histogram - prev_histogram) * 20, 100)
            return {'type': 'Bullish Momentum', 'strength': round(strength, 1)}
        
        elif macd < signal_line and histogram < prev_histogram < 0:
            strength = min(abs(histogram - prev_histogram) * 20, 100)
            return {'type': 'Bearish Momentum', 'strength': round(strength, 1)}
        
        return {'type': 'none', 'strength': 0}
