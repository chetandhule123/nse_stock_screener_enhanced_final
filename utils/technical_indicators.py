import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Technical indicators calculations for stock analysis"""
    
    @staticmethod
    def calculate_macd(price_series, fast=12, slow=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            price_series: Pandas Series of prices (usually Close)
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            DataFrame with MACD, Signal, and Histogram columns
        """
        try:
            # Calculate EMAs
            ema_fast = price_series.ewm(span=fast).mean()
            ema_slow = price_series.ewm(span=slow).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate Signal line
            signal_line = macd_line.ewm(span=signal).mean()
            
            # Calculate Histogram
            histogram = macd_line - signal_line
            
            return pd.DataFrame({
                'MACD': macd_line,
                'Signal': signal_line,
                'Histogram': histogram
            })
            
        except Exception as e:
            print(f"Error calculating MACD: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_atr(data, period=14):
        """
        Calculate Average True Range (ATR)
        
        Args:
            data: OHLC DataFrame
            period: ATR calculation period
            
        Returns:
            Pandas Series with ATR values
        """
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            # Calculate True Range components
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            # True Range is the maximum of the three
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate ATR as rolling mean of True Range
            atr = true_range.rolling(window=period).mean()
            
            return atr
            
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return pd.Series()
    
    @staticmethod
    def calculate_sma(price_series, period):
        """
        Calculate Simple Moving Average
        
        Args:
            price_series: Pandas Series of prices
            period: SMA period
            
        Returns:
            Pandas Series with SMA values
        """
        try:
            return price_series.rolling(window=period).mean()
        except Exception as e:
            print(f"Error calculating SMA: {e}")
            return pd.Series()
    
    @staticmethod
    def calculate_ema(price_series, period):
        """
        Calculate Exponential Moving Average
        
        Args:
            price_series: Pandas Series of prices
            period: EMA period
            
        Returns:
            Pandas Series with EMA values
        """
        try:
            return price_series.ewm(span=period).mean()
        except Exception as e:
            print(f"Error calculating EMA: {e}")
            return pd.Series()
    
    @staticmethod
    def calculate_rsi(price_series, period=14):
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            price_series: Pandas Series of prices
            period: RSI calculation period
            
        Returns:
            Pandas Series with RSI values
        """
        try:
            delta = price_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            return pd.Series()
    
    @staticmethod
    def calculate_bollinger_bands(price_series, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Args:
            price_series: Pandas Series of prices
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            DataFrame with Upper, Middle, and Lower bands
        """
        try:
            middle_band = price_series.rolling(window=period).mean()
            std = price_series.rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return pd.DataFrame({
                'Upper': upper_band,
                'Middle': middle_band,
                'Lower': lower_band
            })
            
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_stochastic(data, k_period=14, d_period=3):
        """
        Calculate Stochastic Oscillator
        
        Args:
            data: OHLC DataFrame
            k_period: %K calculation period
            d_period: %D smoothing period
            
        Returns:
            DataFrame with %K and %D values
        """
        try:
            low_min = data['Low'].rolling(window=k_period).min()
            high_max = data['High'].rolling(window=k_period).max()
            
            k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return pd.DataFrame({
                '%K': k_percent,
                '%D': d_percent
            })
            
        except Exception as e:
            print(f"Error calculating Stochastic: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_volume_sma(volume_series, period):
        """
        Calculate Volume Simple Moving Average
        
        Args:
            volume_series: Pandas Series of volume data
            period: SMA period
            
        Returns:
            Pandas Series with Volume SMA values
        """
        try:
            return volume_series.rolling(window=period).mean()
        except Exception as e:
            print(f"Error calculating Volume SMA: {e}")
            return pd.Series()
    
    @staticmethod
    def detect_support_resistance(data, window=20, min_touches=2):
        """
        Detect support and resistance levels
        
        Args:
            data: OHLC DataFrame
            window: Rolling window for local extrema detection
            min_touches: Minimum touches to confirm level
            
        Returns:
            Dict with support and resistance levels
        """
        try:
            # Find local maxima and minima
            highs = data['High'].rolling(window=window, center=True).max()
            lows = data['Low'].rolling(window=window, center=True).min()
            
            resistance_points = data['High'] == highs
            support_points = data['Low'] == lows
            
            # Extract levels
            resistance_levels = data.loc[resistance_points, 'High'].values
            support_levels = data.loc[support_points, 'Low'].values
            
            return {
                'resistance': resistance_levels,
                'support': support_levels
            }
            
        except Exception as e:
            print(f"Error detecting support/resistance: {e}")
            return {'resistance': [], 'support': []}
