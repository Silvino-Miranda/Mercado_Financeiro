"""
Utility functions for download module.
"""

import datetime as dt
from typing import Tuple


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start = dt.datetime.fromisoformat(start_date)
        end = dt.datetime.fromisoformat(end_date)
        
        if start > end:
            return False, "Start date must be before end date"
        
        if end > dt.datetime.now():
            return False, "End date cannot be in the future"
        
        return True, ""
    
    except ValueError as e:
        return False, f"Invalid date format: {e}"


def format_timestamp(timestamp: int, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Format Unix timestamp (milliseconds) to human-readable string.
    
    Args:
        timestamp: Unix timestamp in milliseconds
        format_str: strftime format string
        
    Returns:
        Formatted datetime string
    """
    return dt.datetime.fromtimestamp(
        timestamp / 1000, 
        tz=dt.timezone.utc
    ).strftime(format_str)


def calculate_expected_candles(
    start_date: str,
    end_date: str,
    interval: str
) -> int:
    """
    Calculate expected number of candles for date range and interval.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        interval: Timeframe (e.g., '1d', '1h', '15m')
        
    Returns:
        Expected number of candles
    """
    start = dt.datetime.fromisoformat(start_date)
    end = dt.datetime.fromisoformat(end_date)
    delta = end - start
    
    # Map interval to hours
    interval_hours = {
        '1m': 1/60, '3m': 3/60, '5m': 5/60, '15m': 15/60, '30m': 30/60,
        '1h': 1, '2h': 2, '4h': 4, '6h': 6, '8h': 8, '12h': 12,
        '1d': 24, '3d': 72,
        '1w': 168,
        '1M': 720  # Approximate
    }
    
    hours_per_candle = interval_hours.get(interval, 24)
    total_hours = delta.total_seconds() / 3600
    
    return int(total_hours / hours_per_candle)
