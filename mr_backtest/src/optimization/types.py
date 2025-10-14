#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimization Data Types
-----------------------
Data structures for optimization algorithms.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import StrategyConfig


class OptimizationObjective(Enum):
    """
    Optimization objectives for strategy parameter tuning.
    
    Values:
        PROFIT_FACTOR: Maximize profit factor (gains/losses)
        TOTAL_PNL: Maximize total profit/loss
        SHARPE: Maximize Sharpe ratio
        TRADES_PER_YEAR: Maximize trade frequency (balanced with quality)
        ROI: Maximize return on investment (PnL / drawdown)
        MULTI: Multi-objective optimization (combined metrics)
    """
    PROFIT_FACTOR = "profit_factor"
    TOTAL_PNL = "total_pnl"
    SHARPE = "sharpe_like"
    TRADES_PER_YEAR = "trades_per_year"
    ROI = "roi"
    MULTI = "multi"


@dataclass
class Individual:
    """
    Individual in genetic algorithm population.
    
    Represents a candidate solution (parameter set) with its fitness score.
    
    Attributes:
        config: Strategy configuration (parameter values)
        fitness: Fitness score (higher is better)
        metrics: Backtest performance metrics
        generation: Generation number when created/evaluated
    """
    config: 'StrategyConfig'  # Forward reference to avoid circular import
    fitness: float = 0.0
    metrics: Optional[Dict[str, float]] = None
    generation: int = 0
    
    def __lt__(self, other):
        """Enable sorting by fitness."""
        return self.fitness < other.fitness
    
    def __repr__(self):
        """String representation."""
        return f"Individual(fitness={self.fitness:.4f}, gen={self.generation})"
