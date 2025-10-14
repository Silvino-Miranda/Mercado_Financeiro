#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Types for Backtesting
---------------------------
Defines core data structures used throughout the backtesting framework.
"""

from dataclasses import dataclass
from typing import List, Dict
import pandas as pd


@dataclass
class Params:
    """
    Strategy and risk management parameters.
    
    Attributes:
        variant: Strategy variant (base | rsi | reclaim)
        ma_len: Moving average period
        dist_below_ma_pct: Distance below MA for entry signal (e.g., 0.05 = 5%)
        slope_lookback: Bars to lookback for MA slope calculation
        rsi_period: RSI indicator period
        rsi_cross_level: RSI level for cross-up signal
        tp_pct: Take profit percentage
        sl_pct: Stop loss percentage
        atr_mult: ATR multiplier for stop distance
        time_stop: Maximum bars to hold position
        be_trigger_pct: Breakeven trigger percentage
        fees_bps: Trading fees in basis points per side
        slip_bps: Slippage in basis points per side
        capital_per_trade: Capital allocated per trade
        allow_breakeven: Enable breakeven stop adjustment
    """
    variant: str = "base"
    ma_len: int = 200
    dist_below_ma_pct: float = 0.05
    slope_lookback: int = 5
    rsi_period: int = 14
    rsi_cross_level: float = 30.0
    tp_pct: float = 0.10
    sl_pct: float = 0.08
    atr_mult: float = 2.0
    time_stop: int = 30
    be_trigger_pct: float = 0.06
    fees_bps: float = 10.0
    slip_bps: float = 5.0
    capital_per_trade: float = 1000.0
    allow_breakeven: bool = True


@dataclass
class TradeResult:
    """
    Result of a single completed trade.
    
    Attributes:
        entry_date: Trade entry timestamp
        exit_date: Trade exit timestamp
        entry_px: Executed entry price (after fees & slippage)
        exit_px: Executed exit price (after fees & slippage)
        shares: Position size in shares
        pnl: Profit/loss in dollar terms
        pnl_pct: Profit/loss as percentage of entry
        reason: Exit reason (tp, stop, time_stop, etc.)
        bars_held: Number of bars position was held
    """
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_px: float
    exit_px: float
    shares: float
    pnl: float
    pnl_pct: float
    reason: str
    bars_held: int


@dataclass
class BacktestResult:
    """
    Complete backtest results including trades and metrics.
    
    Attributes:
        trades: List of completed trades
        equity_curve: DataFrame with Date index and Equity column
        metrics: Dictionary of performance metrics
        params: Parameters used for the backtest
    """
    trades: List[TradeResult]
    equity_curve: pd.DataFrame
    metrics: Dict[str, float]
    params: Params
