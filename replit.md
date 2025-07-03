# NSE Stock Screener - Enhanced Technical Analysis Platform

## Overview

This is a comprehensive real-time NSE (National Stock Exchange) stock screener application built with Streamlit. The application provides automated technical analysis scanning capabilities for Indian stock markets, featuring multiple scanning strategies based on popular technical indicators like MACD, range breakouts, resistance levels, and support analysis.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Visualization**: Plotly for interactive charts and graphs
- **Layout**: Wide layout with expandable sidebar for configuration
- **Real-time Updates**: Auto-refresh capabilities with configurable intervals (5-60 minutes)

### Backend Architecture
- **Modular Scanner System**: Independent scanner modules for different technical strategies
- **Data Pipeline**: Yahoo Finance API integration through yfinance library
- **Threading Support**: Background scanning with queue-based result handling
- **Session Management**: Streamlit session state for persistent data across interactions

### Scanner Modules
1. **MACD Scanner**: 15-minute interval momentum analysis
2. **Range Breakout Scanner**: 4-hour interval range detection and breakout signals
3. **Resistance Breakout Scanner**: 4-hour interval resistance level analysis
4. **Support Level Scanner**: 4-hour interval support/resistance level identification

## Key Components

### Core Application (`app.py`)
- Main Streamlit application entry point
- Session state management for scan results and configuration
- Auto-scan functionality with configurable intervals
- Real-time market indices display
- Interactive dashboard with filtering and sorting capabilities

### Scanner Framework (`/scanners/`)
- **MACDScanner**: Implements MACD crossover and momentum signals
- **RangeBreakoutScanner**: Based on Pine Script range detection logic
- **ResistanceBreakoutScanner**: Breakout and retracement pattern detection
- **SupportLevelScanner**: Multi-level support and resistance analysis

### Utility Framework (`/utils/`)
- **DataFetcher**: Yahoo Finance API wrapper with NSE stock list management
- **TechnicalIndicators**: Mathematical calculations for technical analysis
- **MarketIndices**: Real-time market indices monitoring (NIFTY, BANKNIFTY, SENSEX, etc.)

### Data Management
- **Stock Universe**: Curated list of 100+ major NSE stocks
- **Timeframe Support**: Multiple intervals (15m, 1h, 4h, 1d)
- **Historical Data**: Configurable lookback periods (30-90 days)
- **Caching Strategy**: Session-based result caching for performance optimization

## Data Flow

1. **Data Acquisition**: Yahoo Finance API → DataFetcher → Individual Scanners
2. **Signal Processing**: Raw price data → Technical Indicators → Signal Detection
3. **Result Aggregation**: Scanner results → Session State → Dashboard Display
4. **Auto-refresh Cycle**: Timer-based scanning → Background processing → UI updates

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualization
- **yfinance**: Yahoo Finance API client

### Technical Analysis
- Custom technical indicator implementations
- MACD, ATR, and other momentum indicators
- Support/resistance level detection algorithms
- Range breakout pattern recognition

### Market Data Sources
- **Primary**: Yahoo Finance API for NSE stock data
- **Coverage**: 100+ major NSE stocks including NIFTY constituents
- **Indices**: NIFTY, BANKNIFTY, SENSEX, FINNIFTY, NIFTYMID, NIFTYSMALL

## Deployment Strategy

### Development Environment
- **Platform**: Streamlit Cloud or local development server
- **Requirements**: Python dependencies managed through requirements.txt
- **Configuration**: Environment-based settings for API limits and intervals

### Production Considerations
- **Performance**: Limited to 100 stocks per scan for optimal response times
- **Rate Limiting**: Built-in delays and error handling for API calls
- **Scalability**: Modular architecture allows for easy scanner addition
- **Monitoring**: Error logging and scan result tracking

### Security & Compliance
- **Data Source**: Public market data through Yahoo Finance
- **No Authentication**: Read-only market data access
- **Rate Limiting**: Respectful API usage with appropriate delays

## Changelog

```
Changelog:
- July 03, 2025. Initial setup
- July 03, 2025. Enhanced with fresh UI, fixed 15-minute scan intervals, added IST timezone, preserved existing MACD logic, added new Pine Script range detection scanner
- July 03, 2025. Updated with user's exact stock symbols and MACD calculation logic from original file, integrated MACDScannerOriginal module
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

### Technical Notes for Development
- The application uses a modular scanner architecture that can be easily extended
- Each scanner implements consistent interfaces for data fetching and signal detection
- Threading support is built-in but may need queue management implementation
- The current stock list focuses on major NSE stocks but can be expanded
- All scanners use configurable timeframes and lookback periods for flexibility
- Error handling is implemented at multiple levels to ensure application stability