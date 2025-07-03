import pandas as pd
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.technical_indicators import TechnicalIndicators

class SupportLevelScanner:
    """Support Level Scanner showing support & resistance levels on 4-hour intervals"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.tech_indicators = TechnicalIndicators()
        
    def scan(self, timeframe="4h", lookback_days=90):
        """
        Scan for support level signals
        
        Args:
            timeframe: Data timeframe (4h recommended)
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with support level signals
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
                    
                    # Identify support and resistance levels
                    support_levels = self.identify_support_levels(data)
                    resistance_levels = self.identify_resistance_levels(data)
                    
                    # Analyze current position relative to levels
                    analysis = self.analyze_current_position(data, support_levels, resistance_levels)
                    
                    if analysis['signal'] != 'none':
                        current_price = data['Close'].iloc[-1]
                        volume = data['Volume'].iloc[-1] if 'Volume' in data else 0
                        
                        results.append({
                            'Symbol': symbol,
                            'Signal': analysis['signal'],
                            'Current_Price': round(current_price, 2),
                            'Nearest_Support': round(analysis['nearest_support'], 2) if analysis['nearest_support'] else None,
                            'Nearest_Resistance': round(analysis['nearest_resistance'], 2) if analysis['nearest_resistance'] else None,
                            'Distance_to_Support_%': round(analysis['distance_to_support'], 2) if analysis['distance_to_support'] else None,
                            'Distance_to_Resistance_%': round(analysis['distance_to_resistance'], 2) if analysis['distance_to_resistance'] else None,
                            'Support_Strength': analysis['support_strength'],
                            'Resistance_Strength': analysis['resistance_strength'],
                            'Risk_Reward_Ratio': analysis['risk_reward'],
                            'Volume': int(volume),
                            'Timeframe': timeframe
                        })
                        
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error in Support Level scanner: {e}")
            return pd.DataFrame()
    
    def identify_support_levels(self, data, window=20, min_touches=2):
        """
        Identify support levels from price data
        
        Args:
            data: OHLCV DataFrame
            window: Rolling window for trough detection
            min_touches: Minimum number of touches to confirm support
            
        Returns:
            List of support levels with metadata
        """
        try:
            # Find local troughs (support candidates)
            lows = data['Low'].rolling(window=window, center=True).min()
            troughs = data['Low'] == lows
            
            support_levels = []
            tolerance = 0.025  # 2.5% tolerance for level matching
            
            # Extract trough prices and indices
            trough_prices = data.loc[troughs, 'Low'].values
            trough_indices = data.loc[troughs].index.values
            
            for i, trough_price in enumerate(trough_prices):
                # Count touches within tolerance
                touches = []
                touch_indices = []
                
                for j, test_price in enumerate(data['Low']):
                    if abs(test_price - trough_price) / trough_price <= tolerance:
                        touches.append(test_price)
                        touch_indices.append(j)
                
                # Confirm as support if enough touches
                if len(touches) >= min_touches:
                    # Calculate average level
                    avg_level = np.mean(touches)
                    
                    # Find most recent touch
                    last_touch_idx = max(touch_indices)
                    
                    # Calculate strength based on touches and recency
                    strength = len(touches) * (1 + (len(data) - last_touch_idx) / len(data))
                    
                    support_levels.append({
                        'level': avg_level,
                        'touches': len(touches),
                        'last_touch': last_touch_idx,
                        'first_touch': min(touch_indices),
                        'strength': strength
                    })
            
            # Sort by strength
            support_levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return support_levels[:10]  # Return top 10 levels
            
        except Exception as e:
            print(f"Error in support level identification: {e}")
            return []
    
    def identify_resistance_levels(self, data, window=20, min_touches=2):
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
            tolerance = 0.025  # 2.5% tolerance for level matching
            
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
                    
                    # Calculate strength
                    strength = len(touches) * (1 + (len(data) - last_touch_idx) / len(data))
                    
                    resistance_levels.append({
                        'level': avg_level,
                        'touches': len(touches),
                        'last_touch': last_touch_idx,
                        'first_touch': min(touch_indices),
                        'strength': strength
                    })
            
            # Sort by strength
            resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
            
            return resistance_levels[:10]  # Return top 10 levels
            
        except Exception as e:
            print(f"Error in resistance level identification: {e}")
            return []
    
    def analyze_current_position(self, data, support_levels, resistance_levels):
        """
        Analyze current price position relative to support and resistance levels
        
        Args:
            data: OHLCV DataFrame
            support_levels: List of support levels
            resistance_levels: List of resistance levels
            
        Returns:
            Dict with analysis results
        """
        try:
            current_price = data['Close'].iloc[-1]
            
            # Find nearest support and resistance
            nearest_support = None
            nearest_resistance = None
            
            # Find nearest support below current price
            for support in support_levels:
                if support['level'] < current_price:
                    nearest_support = support
                    break
            
            # Find nearest resistance above current price
            for resistance in resistance_levels:
                if resistance['level'] > current_price:
                    nearest_resistance = resistance
                    break
            
            # Calculate distances
            distance_to_support = None
            distance_to_resistance = None
            
            if nearest_support:
                distance_to_support = ((current_price - nearest_support['level']) / 
                                     current_price) * 100
            
            if nearest_resistance:
                distance_to_resistance = ((nearest_resistance['level'] - current_price) / 
                                        current_price) * 100
            
            # Determine signal based on position and distances
            signal = self.determine_signal(
                current_price, 
                nearest_support, 
                nearest_resistance,
                distance_to_support,
                distance_to_resistance
            )
            
            # Calculate risk-reward ratio
            risk_reward = None
            if nearest_support and nearest_resistance:
                risk = current_price - nearest_support['level']
                reward = nearest_resistance['level'] - current_price
                if risk > 0:
                    risk_reward = round(reward / risk, 2)
            
            return {
                'signal': signal,
                'nearest_support': nearest_support['level'] if nearest_support else None,
                'nearest_resistance': nearest_resistance['level'] if nearest_resistance else None,
                'distance_to_support': distance_to_support,
                'distance_to_resistance': distance_to_resistance,
                'support_strength': nearest_support['strength'] if nearest_support else 0,
                'resistance_strength': nearest_resistance['strength'] if nearest_resistance else 0,
                'risk_reward': risk_reward
            }
            
        except Exception as e:
            print(f"Error in position analysis: {e}")
            return {'signal': 'none'}
    
    def determine_signal(self, current_price, nearest_support, nearest_resistance, 
                        dist_to_support, dist_to_resistance):
        """
        Determine trading signal based on position relative to support/resistance
        
        Args:
            current_price: Current stock price
            nearest_support: Nearest support level data
            nearest_resistance: Nearest resistance level data
            dist_to_support: Distance to support as percentage
            dist_to_resistance: Distance to resistance as percentage
            
        Returns:
            String indicating the signal type
        """
        try:
            # Near strong support (potential bounce)
            if (nearest_support and dist_to_support is not None and 
                dist_to_support <= 3 and nearest_support['strength'] >= 5):
                return 'Near Strong Support'
            
            # Near strong resistance (potential rejection)
            elif (nearest_resistance and dist_to_resistance is not None and 
                  dist_to_resistance <= 3 and nearest_resistance['strength'] >= 5):
                return 'Near Strong Resistance'
            
            # Good risk-reward setup
            elif (nearest_support and nearest_resistance and 
                  dist_to_support is not None and dist_to_resistance is not None):
                
                risk = dist_to_support
                reward = dist_to_resistance
                
                if reward / risk >= 2 and risk <= 5:  # R:R >= 2:1 with max 5% risk
                    return 'Good Risk-Reward Setup'
            
            # Breaking above resistance
            elif (nearest_resistance and dist_to_resistance is not None and 
                  dist_to_resistance < 0):  # Price above resistance
                return 'Above Resistance'
            
            # Breaking below support
            elif (nearest_support and dist_to_support is not None and 
                  dist_to_support < 0):  # Price below support
                return 'Below Support'
            
            # In middle zone
            elif (nearest_support and nearest_resistance and 
                  dist_to_support and dist_to_resistance and
                  dist_to_support > 10 and dist_to_resistance > 10):
                return 'Middle Zone'
            
            return 'none'
            
        except Exception as e:
            print(f"Error in signal determination: {e}")
            return 'none'
