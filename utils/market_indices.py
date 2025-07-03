import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

class MarketIndices:
    """Market indices data fetching and analysis"""
    
    def __init__(self):
        self.indices = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK", 
            "SENSEX": "^BSESN",
            "FINNIFTY": "^CNXFIN",
            "NIFTYMID": "^CNXMID",
            "NIFTYSMALL": "^CNXSC"
        }
    
    def get_live_indices(self):
        """
        Fetch live market indices data
        
        Returns:
            DataFrame with current indices information
        """
        try:
            indices_data = []
            
            for name, symbol in self.indices.items():
                try:
                    # Fetch ticker data
                    ticker = yf.Ticker(symbol)
                    
                    # Get recent data (last 2 days to calculate change)
                    data = ticker.history(period="2d", interval="1d")
                    
                    if not data.empty and len(data) >= 1:
                        current_price = data['Close'].iloc[-1]
                        
                        # Calculate change
                        if len(data) >= 2:
                            prev_close = data['Close'].iloc[-2]
                        else:
                            prev_close = current_price
                        
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                        
                        indices_data.append({
                            'Name': name,
                            'Symbol': symbol,
                            'Price': current_price,
                            'Change': change,
                            'Change%': change_percent,
                            'Volume': data['Volume'].iloc[-1] if 'Volume' in data else 0,
                            'Timestamp': datetime.now()
                        })
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching {name}: {e}")
                    continue
            
            return pd.DataFrame(indices_data)
            
        except Exception as e:
            print(f"Error fetching market indices: {e}")
            return pd.DataFrame()
    
    def get_index_data(self, index_name, period="1mo", interval="1d"):
        """
        Get historical data for a specific index
        
        Args:
            index_name: Name of the index (NIFTY, BANKNIFTY, etc.)
            period: Data period
            interval: Data interval
            
        Returns:
            DataFrame with historical index data
        """
        try:
            if index_name not in self.indices:
                raise ValueError(f"Index {index_name} not found")
            
            symbol = self.indices[index_name]
            ticker = yf.Ticker(symbol)
            
            data = ticker.history(period=period, interval=interval)
            
            return data
            
        except Exception as e:
            print(f"Error fetching {index_name} data: {e}")
            return pd.DataFrame()
    
    def calculate_index_momentum(self, index_name, short_period=5, long_period=20):
        """
        Calculate momentum for an index
        
        Args:
            index_name: Name of the index
            short_period: Short term period for momentum
            long_period: Long term period for momentum
            
        Returns:
            Dict with momentum analysis
        """
        try:
            data = self.get_index_data(index_name, period="3mo", interval="1d")
            
            if data.empty or len(data) < long_period:
                return None
            
            # Calculate moving averages
            short_ma = data['Close'].rolling(window=short_period).mean()
            long_ma = data['Close'].rolling(window=long_period).mean()
            
            current_price = data['Close'].iloc[-1]
            current_short_ma = short_ma.iloc[-1]
            current_long_ma = long_ma.iloc[-1]
            
            # Momentum signals
            momentum_signal = "Neutral"
            if current_price > current_short_ma > current_long_ma:
                momentum_signal = "Strong Bullish"
            elif current_price > current_short_ma and current_short_ma < current_long_ma:
                momentum_signal = "Weak Bullish"
            elif current_price < current_short_ma > current_long_ma:
                momentum_signal = "Weak Bearish"
            elif current_price < current_short_ma < current_long_ma:
                momentum_signal = "Strong Bearish"
            
            # Calculate price change over different periods
            price_1d = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) >= 2 else 0
            price_5d = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100 if len(data) >= 6 else 0
            price_20d = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100 if len(data) >= 21 else 0
            
            return {
                'index': index_name,
                'current_price': current_price,
                'momentum_signal': momentum_signal,
                'short_ma': current_short_ma,
                'long_ma': current_long_ma,
                'change_1d': price_1d,
                'change_5d': price_5d,
                'change_20d': price_20d,
                'volume': data['Volume'].iloc[-1] if 'Volume' in data else 0
            }
            
        except Exception as e:
            print(f"Error calculating momentum for {index_name}: {e}")
            return None
    
    def get_sector_performance(self):
        """
        Get performance of major sector indices
        
        Returns:
            DataFrame with sector performance
        """
        try:
            sector_indices = {
                "IT": "^CNXIT",
                "BANK": "^NSEBANK",
                "AUTO": "^CNXAUTO",
                "PHARMA": "^CNXPHARMA",
                "FMCG": "^CNXFMCG",
                "METAL": "^CNXMETAL",
                "REALTY": "^CNXREALTY",
                "ENERGY": "^CNXENERGY"
            }
            
            sector_data = []
            
            for sector, symbol in sector_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="5d", interval="1d")
                    
                    if not data.empty:
                        current_price = data['Close'].iloc[-1]
                        
                        # Calculate changes over different periods
                        change_1d = 0
                        change_5d = 0
                        
                        if len(data) >= 2:
                            change_1d = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                        
                        if len(data) >= 5:
                            change_5d = ((current_price - data['Close'].iloc[-5]) / data['Close'].iloc[-5]) * 100
                        
                        sector_data.append({
                            'Sector': sector,
                            'Price': current_price,
                            'Change_1D%': change_1d,
                            'Change_5D%': change_5d,
                            'Volume': data['Volume'].iloc[-1] if 'Volume' in data else 0
                        })
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching {sector}: {e}")
                    continue
            
            return pd.DataFrame(sector_data)
            
        except Exception as e:
            print(f"Error fetching sector performance: {e}")
            return pd.DataFrame()
    
    def get_market_sentiment(self):
        """
        Calculate overall market sentiment based on major indices
        
        Returns:
            Dict with market sentiment analysis
        """
        try:
            indices_data = self.get_live_indices()
            
            if indices_data.empty:
                return None
            
            # Calculate average change across major indices
            major_indices = indices_data[indices_data['Name'].isin(['NIFTY', 'BANKNIFTY', 'SENSEX'])]
            
            if major_indices.empty:
                return None
            
            avg_change = major_indices['Change%'].mean()
            positive_indices = len(major_indices[major_indices['Change%'] > 0])
            total_indices = len(major_indices)
            
            # Determine sentiment
            if avg_change > 1 and positive_indices >= total_indices * 0.7:
                sentiment = "Very Bullish"
            elif avg_change > 0.5 and positive_indices >= total_indices * 0.6:
                sentiment = "Bullish"
            elif avg_change > -0.5 and positive_indices >= total_indices * 0.4:
                sentiment = "Neutral"
            elif avg_change > -1 and positive_indices >= total_indices * 0.3:
                sentiment = "Bearish"
            else:
                sentiment = "Very Bearish"
            
            return {
                'sentiment': sentiment,
                'avg_change': avg_change,
                'positive_indices': positive_indices,
                'total_indices': total_indices,
                'positive_ratio': positive_indices / total_indices,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
            return None
