import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime, timedelta
import pytz

class MACDScannerOriginal:
    """MACD Scanner with exact logic from user's original file"""
    
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        
    def get_ist_time(self):
        """Get current IST time"""
        return datetime.now(self.ist)
    
    @staticmethod
    def calculate_ema(data, period):
        """Calculate Exponential Moving Average exactly like Google Apps Script"""
        k = 2 / (period + 1)
        ema_array = [data[0]]

        for i in range(1, len(data)):
            ema_value = data[i] * k + ema_array[i - 1] * (1 - k)
            ema_array.append(ema_value)

        return ema_array

    @staticmethod
    def calculate_macd(close_prices):
        """Calculate MACD exactly like the Google Apps Script reference"""
        if len(close_prices) < 30:
            return None

        # Calculate EMAs using the exact same logic as Google Apps Script
        fast_ema = MACDScannerOriginal.calculate_ema(close_prices, 12)
        slow_ema = MACDScannerOriginal.calculate_ema(close_prices, 26)

        # MACD line
        macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(fast_ema))]

        # Signal line (9-period EMA of MACD line)
        signal_line = MACDScannerOriginal.calculate_ema(macd_line, 9)

        # Histogram (latest values)
        histogram = macd_line[-1] - signal_line[-1]

        # Generate signals using exact same logic as Google Apps Script
        signals = []
        for i in range(len(macd_line)):
            macd_val = macd_line[i]
            signal_val = signal_line[i]

            if macd_val > signal_val and macd_val > 0 and signal_val > 0:
                signals.append("STRONG BUY")
            elif macd_val < signal_val and macd_val < 0 and signal_val < 0:
                signals.append("STRONG SELL")
            elif macd_val > signal_val and macd_val < 0:
                signals.append("WEAK BUY")
            elif macd_val < signal_val and macd_val > 0:
                signals.append("WEAK SELL")
            elif macd_val > signal_val:
                signals.append("BUY")
            elif macd_val < signal_val:
                signals.append("SELL")
            else:
                signals.append("NO SIGNAL")

        return {
            'macd': macd_line[-1],
            'signal': signal_line[-1],
            'histogram': histogram,
            'signals': signals
        }
    
    def scan_crossovers(self, stock_symbols, timeframe='1d'):
        """Scan for MACD crossovers focusing on bearish to bullish transitions"""
        crossovers = []

        for symbol in stock_symbols:
            try:
                stock = yf.Ticker(symbol)

                # Get data based on timeframe
                if timeframe == '4h':
                    hist = stock.history(period="60d", interval="1h")
                    # Resample to 4-hour intervals
                    hist = hist.resample('4h').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()
                else:
                    hist = stock.history(period="3mo", interval="1d")

                if hist.empty or len(hist) < 30:
                    continue

                prices = hist['Close'].tolist()
                macd_data = self.calculate_macd(prices)

                if not macd_data:
                    continue

                current_signal = macd_data['signals'][-1] if macd_data['signals'] else "NO SIGNAL"
                prev_signal = macd_data['signals'][-2] if len(macd_data['signals']) > 1 else "NO SIGNAL"

                # Focus on bearish to bullish transitions
                bearish_signals = ["SELL", "WEAK SELL", "STRONG SELL"]
                bullish_signals = ["BUY", "WEAK BUY", "STRONG BUY"]

                # Check for signal change from bearish to bullish
                if (prev_signal in bearish_signals and current_signal in bullish_signals):
                    crossover_type = "bullish"

                    crossovers.append({
                        'symbol': symbol.replace('.NS', ''),
                        'type': crossover_type,
                        'previous_type': prev_signal,
                        'current_signal': current_signal,
                        'timestamp': self.get_ist_time(),
                        'macd': macd_data['macd'],
                        'signal': macd_data['signal'],
                        'histogram': macd_data['histogram'],
                        'price': prices[-1],
                        'timeframe': timeframe,
                        'signal_strength': self._calculate_signal_strength(current_signal)
                    })

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                continue

        return crossovers
    
    def _calculate_signal_strength(self, signal):
        """Calculate signal strength based on signal type"""
        strength_map = {
            "STRONG BUY": 5,
            "BUY": 4, 
            "WEAK BUY": 3,
            "NO SIGNAL": 2,
            "WEAK SELL": 1,
            "SELL": 0,
            "STRONG SELL": -1
        }
        return strength_map.get(signal, 2)
    
    def scan(self, timeframe="15m", lookback_days=30):
        """
        Scan for MACD signals using original logic
        
        Args:
            timeframe: Data timeframe (15m, 4h, 1d)
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with MACD signals
        """
        from utils.data_fetcher import DataFetcher
        
        data_fetcher = DataFetcher()
        stock_symbols = data_fetcher.get_nse_stock_list()
        
        # Map timeframes for scanning
        if timeframe == "15m":
            scan_timeframe = "1d"  # Use daily for 15m analysis
        else:
            scan_timeframe = timeframe
            
        crossovers = self.scan_crossovers(stock_symbols, scan_timeframe)
        
        if not crossovers:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(crossovers)
        
        # Add additional columns for compatibility
        df['signal_type'] = 'MACD Crossover'
        df['confidence'] = df['signal_strength'] / 5.0  # Normalize to 0-1
        
        return df