#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimization Module
-------------------
Strategy parameter optimization using various algorithms.

This module provides:
- Genetic Algorithm optimization
- Grid Search optimization
- Multi-objective optimization
- Parameter evolution tracking
- Results analysis
"""

from .types import Individual, OptimizationObjective
from .genetic import GeneticOptimizer
from .grid import GridSearchOptimizer
from .utils import save_optimization_results, load_optimization_history

__all__ = [
    # Types
    "Individual",
    "OptimizationObjective",
    # Optimizers
    "GeneticOptimizer",
    "GridSearchOptimizer",
    # Utils
    "save_optimization_results",
    "load_optimization_history",
]
