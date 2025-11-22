from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import yfinance as yf

logger = logging.getLogger(__name__)


def get_stock_data(symbol: str) -> Optional[Dict]:
    """
    Fetch real stock data using yfinance.
    
    Returns:
        Dict with keys:
        - current_price: float
        - previous_close: float
        - day_change: float
        - day_change_percent: float
        - week_52_high: float
        - week_52_low: float
        - volume: int
        - series: List[Dict] with dateLabel and price
        - open: float
        - high: float
        - low: float
    """
    if not symbol or not isinstance(symbol, str):
        return None
    
    symbol = symbol.strip().upper()
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current price and previous close
        fast_info = ticker.fast_info
        current_price = fast_info.get('lastPrice') or fast_info.get('regularMarketPrice')
        previous_close = fast_info.get('previousClose')
        
        if current_price is None:
            logger.warning(f"No price data available for {symbol}")
            return None
        
        # Calculate day change
        if previous_close:
            day_change = current_price - previous_close
            day_change_percent = (day_change / previous_close) * 100 if previous_close != 0 else 0
        else:
            day_change = 0
            day_change_percent = 0
        
        # Get 52-week range
        info = ticker.info
        week_52_high = info.get('fiftyTwoWeekHigh') or info.get('52WeekHigh')
        week_52_low = info.get('fiftyTwoWeekLow') or info.get('52WeekLow')
        
        # Get today's OHLC data
        today_data = ticker.history(period='1d', interval='1d')
        if not today_data.empty:
            open_price = float(today_data['Open'].iloc[-1])
            high_price = float(today_data['High'].iloc[-1])
            low_price = float(today_data['Low'].iloc[-1])
            volume = int(today_data['Volume'].iloc[-1])
        else:
            # Fallback to fast_info if history is not available
            open_price = fast_info.get('open') or current_price
            high_price = fast_info.get('dayHigh') or current_price
            low_price = fast_info.get('dayLow') or current_price
            volume = fast_info.get('volume') or 0
        
        # Get historical data for chart (3 months)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)  # Get ~100 days to ensure we have ~60-65 trading days (3 months)
        hist = ticker.history(start=start_date, end=end_date, interval='1d')
        
        series: List[Dict[str, any]] = []  # type: ignore
        chart_data: List[Dict[str, any]] = []  # type: ignore
        if not hist.empty:
            # Use all available data points (should be around 60-65 trading days for 3 months)
            hist_slice = hist
            for date, row in hist_slice.iterrows():
                date_obj = date if isinstance(date, datetime) else datetime.fromisoformat(str(date))
                date_label = date_obj.strftime('%b %d')
                date_iso = date_obj.strftime('%Y-%m-%d')  # Format for lightweight-charts
                
                # For sparkline (backward compatibility)
                series.append({
                    'dateLabel': date_label,
                    'price': float(row['Close'])
                })
                
                # For lightweight-charts (time, value format)
                chart_data.append({
                    'time': date_iso,
                    'value': float(row['Close'])
                })
        else:
            # Fallback: create a simple series with current price
            for i in range(16):
                date = end_date - timedelta(days=15 - i)
                date_iso = date.strftime('%Y-%m-%d')
                series.append({
                    'dateLabel': date.strftime('%b %d'),
                    'price': float(current_price)
                })
                chart_data.append({
                    'time': date_iso,
                    'value': float(current_price)
                })
        
        return {
            'current_price': float(current_price),
            'previous_close': float(previous_close) if previous_close else None,
            'day_change': float(day_change),
            'day_change_percent': float(day_change_percent),
            'week_52_high': float(week_52_high) if week_52_high else None,
            'week_52_low': float(week_52_low) if week_52_low else None,
            'volume': volume,
            'open': float(open_price),
            'high': float(high_price),
            'low': float(low_price),
            'series': series,  # For backward compatibility
            'chart_data': chart_data,  # For lightweight-charts
        }
        
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error fetching stock data for '{symbol}': {error_str}")
        
        # Handle rate limiting
        if '429' in error_str or 'Too Many Requests' in error_str:
            logger.warning(f"Rate limit hit while fetching data for '{symbol}'.")
            return None
        
        return None

