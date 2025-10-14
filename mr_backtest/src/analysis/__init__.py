#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Module
---------------
Analyze backtest results, checkpoints, and optimization outputs.

Public API:
    # Types
    CheckpointData, AnalysisResult, ComparisonResult
    
    # Metrics
    calculate_metrics, calculate_composite_score
    
    # Checkpoint Analysis
    CheckpointAnalyzer
    
    # Results Analysis
    ResultsAnalyzer
    
    # Utilities
    load_checkpoint, save_analysis, load_grid_results
"""

from .types import CheckpointData, AnalysisResult, ComparisonResult
from .metrics import calculate_metrics, calculate_composite_score
from .checkpoint import CheckpointAnalyzer
from .results import ResultsAnalyzer
from .utils import load_checkpoint, save_analysis, load_grid_results

__all__ = [
    # Types
    'CheckpointData',
    'AnalysisResult',
    'ComparisonResult',
    
    # Metrics
    'calculate_metrics',
    'calculate_composite_score',
    
    # Analyzers
    'CheckpointAnalyzer',
    'ResultsAnalyzer',
    
    # Utilities
    'load_checkpoint',
    'save_analysis',
    'load_grid_results',
]
