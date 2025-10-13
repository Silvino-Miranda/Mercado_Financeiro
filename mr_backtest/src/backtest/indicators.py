#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technical Indicators
--------------------
Implementation of technical indicators for trading strategies.
"""

import numpy as np
import pandas as pd


def wilder_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Wilder's Relative Strength Index (RSI).
    
    Uses Wilder's smoothing method (exponential moving average with alpha=1/period).
    
    Args:
        series: Price series (typically Close prices)
        period: RSI period (default: 14)
    
    Returns:
        Series with RSI values (0-100 scale)
    """
    close = series.astype(float)
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    # Wilder's smoothing (RMA - Running Moving Average)
    gain = up.ewm(alpha=1/period, adjust=False).mean()
    loss = down.ewm(alpha=1/period, adjust=False).mean()

    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # Neutral value for early bars


def wilder_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Wilder's Average True Range (ATR).
    
    Measures market volatility using True Range smoothed with Wilder's method.
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period (default: 14)
    
    Returns:
        Series with ATR values
    """
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr


def moving_average(series: pd.Series, window: int = 200) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        series: Price series
        window: MA period (default: 200)
    
    Returns:
        Series with moving average values
    """
    return series.astype(float).rolling(window=window, min_periods=window).mean()


def ma_slope(ma_series: pd.Series, lookback: int = 5) -> pd.Series:
    """
    Calculate whether moving average has positive slope.
    
    Compares current MA value to MA value 'lookback' bars ago.
    
    Args:
        ma_series: Moving average series
        lookback: Number of bars to look back (default: 5)
    
    Returns:
        Series with 1 (positive slope) or 0 (flat/negative slope)
    """
    return (ma_series > ma_series.shift(lookback)).astype(int)


def rsi_cross_up(series: pd.Series, level: float) -> pd.Series:
    """
    Detect RSI crossing above a level.
    
    Identifies bars where RSI was below the level and crosses above it.
    
    Args:
        series: RSI series
        level: Level to detect crossings (e.g., 30.0)
    
    Returns:
        Boolean series (True where cross-up occurred)
    """
    prev = series.shift(1)
    return (prev < level) & (series >= level)
