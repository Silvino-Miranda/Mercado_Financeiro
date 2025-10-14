#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Data Types
------------------------
Data structures for strategy configuration and parameter ranges.
"""

from dataclasses import dataclass, asdict, fields
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class StrategyConfig:
    """
    Configuration for trading strategy parameters.
    
    Attributes:
        variant: Strategy variant (base | rsi | reclaim)
        ma_len: Moving average period
        rsi_period: RSI indicator period
        slope_lookback: Bars for MA slope calculation
        dist_below_ma_pct: Distance below MA for entry
        rsi_cross_level: RSI level for cross-up signal
        tp_pct: Take profit percentage
        sl_pct: Stop loss percentage
        atr_mult: ATR multiplier for stop distance
        time_stop: Maximum bars to hold position
        be_trigger_pct: Breakeven trigger percentage
        allow_breakeven: Enable breakeven stop adjustment
        fees_bps: Trading fees in basis points per side
        slip_bps: Slippage in basis points per side
        capital_per_trade: Capital allocated per trade
        name: Configuration name
        description: Configuration description
    """
    
    # Strategy selection
    variant: str = "base"
    
    # Technical indicators
    ma_len: int = 200
    rsi_period: int = 14
    slope_lookback: int = 5
    
    # Entry conditions
    dist_below_ma_pct: float = 0.05
    rsi_cross_level: float = 30.0
    
    # Exit management
    tp_pct: float = 0.10
    sl_pct: float = 0.08
    atr_mult: float = 2.0
    time_stop: int = 30
    
    # Risk management
    be_trigger_pct: float = 0.06
    allow_breakeven: bool = True
    
    # Trading costs
    fees_bps: float = 10.0
    slip_bps: float = 5.0
    
    # Position sizing
    capital_per_trade: float = 1000.0
    
    # Metadata
    name: str = "default"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def to_params(self):
        """
        Convert to Params dataclass for backtesting.
        
        Returns:
            Params object compatible with BacktestEngine
        """
        from ..backtest import Params
        return Params(
            variant=self.variant,
            ma_len=self.ma_len,
            dist_below_ma_pct=self.dist_below_ma_pct,
            slope_lookback=self.slope_lookback,
            rsi_period=self.rsi_period,
            rsi_cross_level=self.rsi_cross_level,
            tp_pct=self.tp_pct,
            sl_pct=self.sl_pct,
            atr_mult=self.atr_mult,
            time_stop=self.time_stop,
            be_trigger_pct=self.be_trigger_pct,
            fees_bps=self.fees_bps,
            slip_bps=self.slip_bps,
            capital_per_trade=self.capital_per_trade,
            allow_breakeven=self.allow_breakeven
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyConfig':
        """
        Create StrategyConfig from dictionary.
        
        Args:
            data: Dictionary with parameter values
        
        Returns:
            StrategyConfig instance
        """
        # Filter only valid fields
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate parameter values.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Variant check
        if self.variant not in ['base', 'rsi', 'reclaim']:
            errors.append(f"Invalid variant: {self.variant}. Must be 'base', 'rsi', or 'reclaim'")
        
        # Positive integers
        if self.ma_len <= 0:
            errors.append(f"ma_len must be > 0, got: {self.ma_len}")
        if self.rsi_period <= 0:
            errors.append(f"rsi_period must be > 0, got: {self.rsi_period}")
        if self.slope_lookback <= 0:
            errors.append(f"slope_lookback must be > 0, got: {self.slope_lookback}")
        if self.time_stop <= 0:
            errors.append(f"time_stop must be > 0, got: {self.time_stop}")
        
        # Percentages (0-1 range)
        if not 0 < self.dist_below_ma_pct < 1:
            errors.append(f"dist_below_ma_pct must be in (0, 1), got: {self.dist_below_ma_pct}")
        if not 0 < self.tp_pct < 1:
            errors.append(f"tp_pct must be in (0, 1), got: {self.tp_pct}")
        if not 0 < self.sl_pct < 1:
            errors.append(f"sl_pct must be in (0, 1), got: {self.sl_pct}")
        if not 0 < self.be_trigger_pct < 1:
            errors.append(f"be_trigger_pct must be in (0, 1), got: {self.be_trigger_pct}")
        
        # RSI level
        if not 0 < self.rsi_cross_level < 100:
            errors.append(f"rsi_cross_level must be in (0, 100), got: {self.rsi_cross_level}")
        
        # Positive values
        if self.atr_mult <= 0:
            errors.append(f"atr_mult must be > 0, got: {self.atr_mult}")
        if self.capital_per_trade <= 0:
            errors.append(f"capital_per_trade must be > 0, got: {self.capital_per_trade}")
        if self.fees_bps < 0:
            errors.append(f"fees_bps must be >= 0, got: {self.fees_bps}")
        if self.slip_bps < 0:
            errors.append(f"slip_bps must be >= 0, got: {self.slip_bps}")
        
        return len(errors) == 0, errors


@dataclass
class ParamRange:
    """
    Define parameter range for optimization.
    
    Attributes:
        name: Parameter name
        min_val: Minimum value
        max_val: Maximum value
        step: Step size for numeric ranges
        values: Explicit list of values (for discrete parameters)
        param_type: Parameter type (float | int | str | bool)
    """
    name: str
    min_val: float
    max_val: float
    step: Optional[float] = None
    values: Optional[List[Any]] = None
    param_type: str = "float"
    
    def get_values(self) -> List[Any]:
        """
        Get list of possible parameter values.
        
        Returns:
            List of values based on range specification
        """
        # Use explicit values if provided
        if self.values is not None:
            return self.values
        
        # Generate values for integers
        if self.param_type == "int":
            if self.step:
                return list(range(int(self.min_val), int(self.max_val) + 1, int(self.step)))
            return list(range(int(self.min_val), int(self.max_val) + 1))
        
        # Generate values for floats
        if self.param_type == "float":
            if self.step:
                import numpy as np
                return np.arange(self.min_val, self.max_val + self.step, self.step).tolist()
            return [self.min_val, self.max_val]
        
        # Boolean or string types should use explicit values
        return []
    
    def __len__(self) -> int:
        """Return number of possible values."""
        return len(self.get_values())
