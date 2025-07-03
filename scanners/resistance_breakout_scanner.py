import pandas as pd
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.technical_indicators import TechnicalIndicators

class ResistanceBreakoutScanner:
    """Resistance Breakout Scanner with 4-hour intervals for breakout + retracement detection"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.tech_indicators = TechnicalIndicators()
        
    def scan(self, timeframe="4h", lookback_days=90):
        """
        Scan for resistance breakout signals
        
        Args:
            timeframe: Data timeframe (4h recommended)
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with resistance breakout signals
        """
        try:
            symbols = self.data_fetcher.get_nse_stock_list()
            results = []
            
            for symbol in symbols[:100]:  # Limit for performance
                try:
                    # Fetch data
                    data = self.data_fetcher.get_stock_data(
                        symbol, 
                        period=f"{lookback_days}d",
                        interval=timeframe
                    )
                    
                    if data is None or len(data) < 100:
                        continue
                    
                    # Identify resistance levels
                    resistance_levels = self.identify_resistance_levels(data)
                    
                    if resistance_levels:
                        # Check for breakouts and retracements
                        signal = self.detect_resistance_breakout(data, resistance_levels)
                        
                        if signal['type'] != 'none':
                            current_price = data['Close'].iloc[-1]
                            volume = data['Volume'].iloc[-1] if 'Volume' in data else 0
                            
                            # Get the relevant resistance level
                            resistance_level = signal['resistance_level']
                            distance_to_resistance = ((current_price - resistance_level) / resistance_level) * 100
                            
                            results.append({
                                'Symbol': symbol,
                                'Signal_Type': signal['type'],
                                'Current_Price': round(current_price, 2),
                                'Resistance_Level': round(resistance_level, 2),
                                'Distance_to_Resistance_%': round(distance_to_resistance, 2),
                                'Breakout_Strength': signal['strength'],
                                'Volume': int(volume),
                                'Resistance_Touches': signal['touches'],
                                'Days_Since_Breakout': signal.get('days_since_breakout', 0),
                                'Timeframe': timeframe
                            })
                            
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error in Resistance Breakout scanner: {e}")
            return pd.DataFrame()
    
    def identify_resistance_levels(self, data, window=20, min_touches=3):
        """
        Identify resistance levels from price data
        
        Args:
            data: OHLCV DataFrame
            window: Rolling window for peak detection
            min_touches: Minimum number of touches to confirm resistance
            
        Returns:
            List of resistance levels with metadata
        """
        try:
            # Find local peaks (resistance candidates)
            highs = data['High'].rolling(window=window, center=True).max()
            peaks = data['High'] == highs
            
            resistance_levels = []
            tolerance = 0.02  # 2% tolerance for level matching
            
            # Extract peak prices and indices
            peak_prices = data.loc[peaks, 'High'].values
            peak_indices = data.loc[peaks].index.values
            
            for i, peak_price in enumerate(peak_prices):
                # Count touches within tolerance
                touches = []
                touch_indices = []
                
                for j, test_price in enumerate(data['High']):
                    if abs(test_price - peak_price) / peak_price <= tolerance:
                        touches.append(test_price)
                        touch_indices.append(j)
                
                # Confirm as resistance if enough touches
                if len(touches) >= min_touches:
                    # Calculate average level
                    avg_level = np.mean(touches)
                    
                    # Find most recent touch
                    last_touch_idx = max(touch_indices)
                    
                    resistance_levels.append({
                        'level': avg_level,
                        'touches': len(touches),
                        'last_touch': last_touch_idx,
                        'first_touch': min(touch_indices),
                        'strength': len(touches) * (1 + (len(data) - last_touch_idx) / len(data))
                    })
            
            # Sort by strength (most recent and frequently tested levels first)
            resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return resistance_levels[:10]  # Return top 10 levels
            
        except Exception as e:
            print(f"Error in resistance level identification: {e}")
            return []
    
    def detect_resistance_breakout(self, data, resistance_levels):
        """
        Detect resistance breakout and retracement patterns
        
        Args:
            data: OHLCV DataFrame
            resistance_levels: List of resistance levels
            
        Returns:
            Dict with signal information
        """
        try:
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            
            for resistance in resistance_levels:
                level = resistance['level']
                tolerance = level * 0.01  # 1% tolerance
                
                # Fresh breakout detection
                if (current_price > level + tolerance and 
                    previous_price <= level + tolerance):
                    
                    # Calculate breakout strength
                    breakout_distance = current_price - level
                    volume_avg = data['Volume'].tail(20).mean() if 'Volume' in data else 1
                    current_volume = data['Volume'].iloc[-1] if 'Volume' in data else 1
                    volume_surge = current_volume / volume_avg if volume_avg > 0 else 1
                    
                    strength = min((breakout_distance / level * 100) * volume_surge, 100)
                    
                    return {
                        'type': 'Fresh Breakout',
                        'resistance_level': level,
                        'strength': round(strength, 1),
                        'touches': resistance['touches'],
                        'volume_surge': round(volume_surge, 2)
                    }
                
                # Retracement after breakout
                elif current_price > level:
                    # Check if there was a recent breakout followed by retracement
                    lookback = min(20, len(data))
                    recent_data = data.tail(lookback)
                    
                    # Find if price went significantly above resistance and came back
                    max_price_recent = recent_data['High'].max()
                    breakout_height = max_price_recent - level
                    
                    if (breakout_height > level * 0.03 and  # At least 3% breakout
                        current_price < max_price_recent * 0.95 and  # Retraced at least 5%
                        current_price > level * 1.005):  # Still above resistance
                        
                        retracement_pct = ((max_price_recent - current_price) / 
                                         (max_price_recent - level)) * 100
                        
                        # Look for retracement patterns
                        if 30 <= retracement_pct <= 70:  # Healthy retracement
                            strength = 100 - retracement_pct  # Stronger if less retraced
                            
                            return {
                                'type': 'Retracement Entry',
                                'resistance_level': level,
                                'strength': round(strength, 1),
                                'touches': resistance['touches'],
                                'retracement_%': round(retracement_pct, 1),
                                'max_breakout_price': round(max_price_recent, 2)
                            }
                
                # Failed breakout (false breakout)
                elif (previous_price > level and current_price <= level):
                    # Check if this was a recent breakout that failed
                    lookback = min(10, len(data))
                    recent_highs = data['High'].tail(lookback)
                    
                    if any(high > level * 1.02 for high in recent_highs):  # Had broken out by 2%
                        strength = ((level - current_price) / level) * 100
                        
                        return {
                            'type': 'Failed Breakout',
                            'resistance_level': level,
                            'strength': round(abs(strength), 1),
                            'touches': resistance['touches']
                        }
            
            return {'type': 'none', 'strength': 0}
            
        except Exception as e:
            print(f"Error in resistance breakout detection: {e}")
            return {'type': 'none', 'strength': 0}
