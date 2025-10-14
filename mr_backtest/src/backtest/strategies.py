#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Strategies
------------------
Mean-reversion strategy implementations using the Strategy pattern.
"""

from abc import ABC, abstractmethod
import pandas as pd
from .types import Params
from .indicators import wilder_rsi, wilder_atr, moving_average, ma_slope, rsi_cross_up


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategy variants must implement the generate_signals method.
    """
    
    def __init__(self, params: Params):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Strategy parameters
        """
        self.params = params
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate entry signals for the strategy.
        
        Args:
            df: DataFrame with OHLC data and computed indicators
        
        Returns:
            Boolean series where True indicates entry signal
        """
        pass
    
    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute technical indicators needed by strategies.
        
        Args:
            df: DataFrame with OHLC data (Date, Open, High, Low, Close)
        
        Returns:
            DataFrame with added indicator columns (MA, ATR, RSI, MA_slope_pos)
        """
        out = df.copy()
        out["MA"] = moving_average(out["Close"], self.params.ma_len)
        out["ATR"] = wilder_atr(out["High"], out["Low"], out["Close"], 14)
        out["RSI"] = wilder_rsi(out["Close"], self.params.rsi_period)
        out["MA_slope_pos"] = ma_slope(out["MA"], self.params.slope_lookback)
        return out


class BaseStrategy(Strategy):
    """
    MR-Base Strategy: Mean reversion with slope filter.
    
    Entry conditions:
    1. Price closes below MA by dist_below_ma_pct
    2. MA has positive slope over slope_lookback period
    """
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate signals for Base strategy.
        
        Signals when:
        - Close <= (1 - dist_below_ma_pct) * MA
        - MA slope is positive (MA_slope_pos == 1)
        """
        ma_cond = df["Close"] <= (1 - self.params.dist_below_ma_pct) * df["MA"]
        slope_cond = df["MA_slope_pos"] == 1
        return (ma_cond & slope_cond).fillna(False)


class RSIStrategy(Strategy):
    """
    MR-RSI Strategy: Mean reversion with RSI confirmation.
    
    Entry conditions:
    1. Price closes below MA by dist_below_ma_pct
    2. RSI crosses above rsi_cross_level (typically 30)
    """
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate signals for RSI strategy.
        
        Signals when:
        - Close <= (1 - dist_below_ma_pct) * MA
        - RSI crosses up through rsi_cross_level
        """
        ma_cond = df["Close"] <= (1 - self.params.dist_below_ma_pct) * df["MA"]
        rsi_cond = rsi_cross_up(df["RSI"], self.params.rsi_cross_level)
        return (ma_cond & rsi_cond).fillna(False)


class ReclaimStrategy(Strategy):
    """
    MR-Reclaim Strategy: Price reclaiming the moving average.
    
    Entry conditions:
    1. Previous day: Close was <= (1 - dist_below_ma_pct) * MA
    2. Current day: Close reclaims MA (closes >= MA)
    """
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate signals for Reclaim strategy.
        
        Signals when:
        - Previous close was below MA threshold
        - Current close reclaims MA (>= MA)
        """
        prev_below = df["Close"].shift(1) <= (1 - self.params.dist_below_ma_pct) * df["MA"].shift(1)
        curr_reclaim = df["Close"] >= df["MA"]
        return (prev_below & curr_reclaim).fillna(False)


def get_strategy(variant: str, params: Params) -> Strategy:
    """
    Factory function to create strategy instances.
    
    Args:
        variant: Strategy variant name ("base", "rsi", or "reclaim")
        params: Strategy parameters
    
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If variant is unknown
    """
    strategies = {
        "base": BaseStrategy,
        "rsi": RSIStrategy,
        "reclaim": ReclaimStrategy
    }
    
    if variant not in strategies:
        raise ValueError(f"Unknown strategy variant: {variant}. Choose from: {list(strategies.keys())}")
    
    return strategies[variant](params)
