import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
import queue
import os
import pytz

# Import custom modules
from scanners.macd_scanner import MACDScanner
from scanners.range_breakout_scanner import RangeBreakoutScanner
from scanners.resistance_breakout_scanner import ResistanceBreakoutScanner
from scanners.support_level_scanner import SupportLevelScanner
from utils.market_indices import MarketIndices
from utils.data_fetcher import DataFetcher

# Page configuration
st.set_page_config(
    page_title="🚀 NSE Stock Screener Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = None
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = {}
if 'auto_scan_enabled' not in st.session_state:
    st.session_state.auto_scan_enabled = False
if 'scan_interval' not in st.session_state:
    st.session_state.scan_interval = 15  # minutes - FIXED: Default to 15 minutes
if 'active_scanners' not in st.session_state:
    st.session_state.active_scanners = {
        "MACD 15min": True,
        "MACD 4h": True, 
        "MACD 1d": True,
        "Range Breakout 4h": True,
        "Resistance Breakout 4h": True,
        "Support Level 4h": True
    }

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def check_market_hours_ist():
    """Check if NSE market is open in IST"""
    now = get_ist_time()
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
    return is_weekday and market_open <= now <= market_close

def main():
    # Fresh modern UI header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem;">
            🚀 NSE Stock Screener Pro
        </h1>
        <p style="color: #E8F4FD; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Advanced Technical Analysis & Real-time Market Intelligence
        </p>
        <p style="color: #B8D4EA; text-align: center; margin: 0.5rem 0 0 0;">
            IST: {current_time} | Market Status: {market_status}
        </p>
    </div>
    """.format(
        current_time=get_ist_time().strftime('%Y-%m-%d %H:%M:%S'),
        market_status="🟢 OPEN" if check_market_hours_ist() else "🔴 CLOSED"
    ), unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Scanner Configuration")
        
        # Auto-scan settings
        st.markdown("#### 🔄 Auto-Scan Settings")
        auto_scan = st.checkbox("Enable Auto-Scan (15min intervals)", value=st.session_state.auto_scan_enabled)
        
        # FIXED: Force scan interval to 15 minutes as per requirements
        scan_interval = st.selectbox(
            "Scan Interval (minutes)",
            [15, 30, 60],  # Removed 5 and 10 minute options
            index=0,  # Default to 15 minutes
            key="scan_interval_select"
        )
        
        if auto_scan != st.session_state.auto_scan_enabled:
            st.session_state.auto_scan_enabled = auto_scan
            st.session_state.scan_interval = scan_interval
        
        # Manual scan button
        if st.button("🔍 Run Manual Scan", type="primary", use_container_width=True):
            run_all_scanners()
        
        # Scanner selection - PRESERVE EXISTING MACD LOGIC
        st.markdown("#### 📊 Active Scanners")
        
        # MACD Scanners (existing logic preserved)
        st.markdown("**MACD Scanners:**")
        st.session_state.active_scanners["MACD 15min"] = st.checkbox("MACD 15-minute", value=st.session_state.active_scanners["MACD 15min"])
        st.session_state.active_scanners["MACD 4h"] = st.checkbox("MACD 4-hour", value=st.session_state.active_scanners["MACD 4h"])
        st.session_state.active_scanners["MACD 1d"] = st.checkbox("MACD 1-day", value=st.session_state.active_scanners["MACD 1d"])
        
        # New scanners
        st.markdown("**New Advanced Scanners:**")
        st.session_state.active_scanners["Range Breakout 4h"] = st.checkbox("Range Breakout (4h)", value=st.session_state.active_scanners["Range Breakout 4h"])
        st.session_state.active_scanners["Resistance Breakout 4h"] = st.checkbox("Resistance Breakout (4h)", value=st.session_state.active_scanners["Resistance Breakout 4h"])
        st.session_state.active_scanners["Support Level 4h"] = st.checkbox("Support Level (4h)", value=st.session_state.active_scanners["Support Level 4h"])
        
        # Export options
        st.markdown("#### 📊 Export Options")
        if st.button("📥 Export Results", use_container_width=True):
            export_results()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Market indices display
        display_market_indices()
        
        # Scanner results tabs
        display_scanner_results()
    
    with col2:
        # Status and info panel
        display_status_panel()
    
    # Auto-scan logic - FIXED: Use 15-minute intervals
    if st.session_state.auto_scan_enabled:
        handle_auto_scan()

def display_market_indices():
    """Display real-time market indices with fresh UI"""
    st.markdown("### 📊 Live Market Indices")
    
    try:
        market_indices = MarketIndices()
        indices_data = market_indices.get_live_indices()
        
        if not indices_data.empty:
            # Create responsive columns
            cols = st.columns(min(len(indices_data), 4))
            
            for i, (index, row) in enumerate(indices_data.iterrows()):
                with cols[i % 4]:
                    # Fix the LSP error by converting to string
                    name = str(row['Name'])
                    price = float(row['Price'])
                    change = float(row['Change'])
                    change_pct = float(row['Change%'])
                    
                    st.metric(
                        label=name,
                        value=f"₹{price:,.2f}",
                        delta=f"{change:+.2f} ({change_pct:+.2f}%)"
                    )
        else:
            st.warning("📊 Market indices data temporarily unavailable")
    except Exception as e:
        st.error(f"⚠️ Error fetching market indices: {str(e)}")

def display_scanner_results():
    """Display results from all active scanners with fresh UI"""
    st.markdown("### 🎯 Technical Scanner Results")
    
    # Get active scanners from session state
    active_scanners = [name for name, active in st.session_state.active_scanners.items() if active]
    
    if active_scanners:
        tabs = st.tabs(active_scanners)
        
        for i, scanner_name in enumerate(active_scanners):
            with tabs[i]:
                display_individual_scanner_results(scanner_name)
    else:
        st.info("💡 No scanners selected. Please enable scanners from the sidebar.")

def display_individual_scanner_results(scanner_name):
    """Display results for a specific scanner"""
    if scanner_name in st.session_state.scan_results:
        results = st.session_state.scan_results[scanner_name]
        
        if isinstance(results, pd.DataFrame) and not results.empty:
            # Add sorting and filtering options
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                sort_by = st.selectbox(
                    "Sort by",
                    options=results.columns.tolist(),
                    key=f"sort_{scanner_name}"
                )
            
            with col2:
                sort_order = st.selectbox(
                    "Order",
                    ["Descending", "Ascending"],
                    key=f"order_{scanner_name}"
                )
            
            with col3:
                max_results = st.number_input(
                    "Max Results",
                    min_value=10,
                    max_value=100,
                    value=50,
                    key=f"max_{scanner_name}"
                )
            
            # Sort and limit results
            ascending = sort_order == "Ascending"
            sorted_results = results.sort_values(by=sort_by, ascending=ascending).head(max_results)
            
            # Display results table
            st.dataframe(
                sorted_results,
                use_container_width=True,
                hide_index=True
            )
            
            # Display summary stats
            st.write(f"**Total signals found:** {len(results)}")
            st.write(f"**Showing top:** {len(sorted_results)} results")
            
        else:
            st.info(f"No signals found for {scanner_name}")
    else:
        st.info(f"No data available for {scanner_name}. Run a scan to see results.")

def display_status_panel():
    """Display status and information panel with IST times"""
    st.markdown("### 📋 Control Panel")
    
    current_time = get_ist_time()
    
    # Last scan information
    st.markdown("#### ⏱️ Scan Status")
    if st.session_state.last_scan_time:
        st.write(f"**Last Scan:** {st.session_state.last_scan_time.strftime('%H:%M:%S IST')}")
        time_since = current_time - st.session_state.last_scan_time
        minutes_ago = int(time_since.total_seconds() / 60)
        st.write(f"**Time Since:** {minutes_ago} minutes ago")
    else:
        st.write("**Last Scan:** Never")
    
    # Auto-scan status
    if st.session_state.auto_scan_enabled:
        st.success("✅ Auto-scan ENABLED")
        st.write(f"**Interval:** {st.session_state.scan_interval} minutes")
        
        # Next scan countdown
        if st.session_state.last_scan_time:
            # FIXED: Use minimum 15-minute intervals
            actual_interval = max(st.session_state.scan_interval, 15)
            next_scan = st.session_state.last_scan_time + timedelta(minutes=actual_interval)
            time_to_next = next_scan - current_time
            
            if time_to_next.total_seconds() > 0:
                minutes_left = int(time_to_next.total_seconds() / 60)
                seconds_left = int(time_to_next.total_seconds() % 60)
                st.write(f"**Next Scan:** {minutes_left}m {seconds_left}s")
            else:
                st.write("**Next Scan:** ⏰ Due now")
    else:
        st.info("⏸️ Auto-scan DISABLED")
    
    # Market status with IST
    st.markdown("#### 🏛️ NSE Market Status")
    if check_market_hours_ist():
        st.success("🟢 MARKET OPEN")
        st.write(f"**Current Time:** {current_time.strftime('%H:%M:%S IST')}")
    else:
        st.error("🔴 MARKET CLOSED")
        st.write(f"**Current Time:** {current_time.strftime('%H:%M:%S IST')}")
        st.write("**Market Hours:** 09:15 - 15:30 IST")
    
    # Scanner statistics
    st.markdown("#### 📈 Live Statistics")
    total_signals = sum(len(results) if isinstance(results, pd.DataFrame) else 0 
                       for results in st.session_state.scan_results.values())
    st.metric("🎯 Total Active Signals", total_signals)
    
    # Active scanners count
    active_count = sum(1 for active in st.session_state.active_scanners.values() if active)
    st.metric("🔧 Active Scanners", f"{active_count}/6")

def run_all_scanners():
    """Run all enabled scanners - PRESERVE EXISTING MACD LOGIC"""
    with st.spinner("🔄 Running active scanners..."):
        try:
            # Initialize scanners
            macd_scanner = MACDScanner()
            range_scanner = RangeBreakoutScanner()
            resistance_scanner = ResistanceBreakoutScanner()
            support_scanner = SupportLevelScanner()
            
            # PRESERVE EXISTING MACD LOGIC - Run all MACD timeframes if enabled
            if st.session_state.active_scanners["MACD 15min"]:
                st.session_state.scan_results["MACD 15min"] = macd_scanner.scan(timeframe="15m")
            
            if st.session_state.active_scanners["MACD 4h"]:
                st.session_state.scan_results["MACD 4h"] = macd_scanner.scan(timeframe="4h")
            
            if st.session_state.active_scanners["MACD 1d"]:
                st.session_state.scan_results["MACD 1d"] = macd_scanner.scan(timeframe="1d")
            
            # NEW SCANNERS - Run 4-hour intervals as specified
            if st.session_state.active_scanners["Range Breakout 4h"]:
                st.session_state.scan_results["Range Breakout 4h"] = range_scanner.scan(timeframe="4h")
            
            if st.session_state.active_scanners["Resistance Breakout 4h"]:
                st.session_state.scan_results["Resistance Breakout 4h"] = resistance_scanner.scan(timeframe="4h")
            
            if st.session_state.active_scanners["Support Level 4h"]:
                st.session_state.scan_results["Support Level 4h"] = support_scanner.scan(timeframe="4h")
            
            # Update scan time in IST
            st.session_state.last_scan_time = get_ist_time()
            st.success("✅ All active scanners completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error running scanners: {str(e)}")

def handle_auto_scan():
    """Handle automatic scanning based on 15-minute intervals in IST"""
    current_time = get_ist_time()
    
    if st.session_state.last_scan_time is None:
        # Run initial scan
        run_all_scanners()
    else:
        # FIXED: Check if it's time for next scan (ensure 15-minute minimum)
        time_since_last = current_time - st.session_state.last_scan_time
        scan_interval_seconds = max(st.session_state.scan_interval, 15) * 60  # Minimum 15 minutes
        
        if time_since_last.total_seconds() >= scan_interval_seconds:
            run_all_scanners()
            st.rerun()

def export_results():
    """Export scan results to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for scanner_name, results in st.session_state.scan_results.items():
            if isinstance(results, pd.DataFrame) and not results.empty:
                filename = f"{scanner_name.replace(' ', '_')}_{timestamp}.csv"
                results.to_csv(filename, index=False)
                
                # Provide download link
                with open(filename, 'rb') as f:
                    st.download_button(
                        label=f"Download {scanner_name} Results",
                        data=f.read(),
                        file_name=filename,
                        mime='text/csv'
                    )
        
        st.success("✅ Export completed!")
        
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")

if __name__ == "__main__":
    main()
