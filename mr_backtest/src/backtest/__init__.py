#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest Module
---------------
Mean-reversion backtesting framework for cryptocurrency trading strategies.

This module provides:
- Strategy implementations (Base, RSI, Reclaim variants)
- Backtesting engine with realistic order execution
- Technical indicators (RSI, ATR, Moving Averages)
- Performance metrics and analysis
"""

from .types import Params, TradeResult, BacktestResult
from .indicators import wilder_rsi, wilder_atr, moving_average, ma_slope
from .strategies import Strategy, BaseStrategy, RSIStrategy, ReclaimStrategy
from .engine import BacktestEngine
from .utils import load_ohlc_csv, apply_fees_and_slippage

__all__ = [
    # Types
    "Params",
    "TradeResult",
    "BacktestResult",
    # Indicators
    "wilder_rsi",
    "wilder_atr",
    "moving_average",
    "ma_slope",
    # Strategies
    "Strategy",
    "BaseStrategy",
    "RSIStrategy",
    "ReclaimStrategy",
    # Engine
    "BacktestEngine",
    # Utils
    "load_ohlc_csv",
    "apply_fees_and_slippage",
]
