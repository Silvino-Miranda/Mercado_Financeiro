#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics Calculator
------------------
Calculate performance metrics and composite scores.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def calculate_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate aggregate metrics from results DataFrame.
    
    Args:
        df: Results DataFrame with columns: profit_factor, win_rate, total_pnl, etc.
    
    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}
    
    if len(df) == 0:
        return metrics
    
    # Filter valid results (with trades)
    valid_df = df[df['trades'] > 0].copy()
    
    metrics['total_combinations'] = len(df)
    metrics['valid_combinations'] = len(valid_df)
    metrics['invalid_combinations'] = len(df) - len(valid_df)
    metrics['valid_percentage'] = len(valid_df) / len(df) * 100 if len(df) > 0 else 0
    
    if len(valid_df) == 0:
        return metrics
    
    # Profit factor
    metrics['pf_best'] = valid_df['profit_factor'].max()
    metrics['pf_worst'] = valid_df['profit_factor'].min()
    metrics['pf_mean'] = valid_df['profit_factor'].mean()
    metrics['pf_std'] = valid_df['profit_factor'].std()
    metrics['pf_median'] = valid_df['profit_factor'].median()
    
    # Win rate
    metrics['wr_best'] = valid_df['win_rate'].max()
    metrics['wr_worst'] = valid_df['win_rate'].min()
    metrics['wr_mean'] = valid_df['win_rate'].mean()
    metrics['wr_std'] = valid_df['win_rate'].std()
    metrics['wr_median'] = valid_df['win_rate'].median()
    
    # Total PnL
    metrics['pnl_best'] = valid_df['total_pnl'].max()
    metrics['pnl_worst'] = valid_df['total_pnl'].min()
    metrics['pnl_mean'] = valid_df['total_pnl'].mean()
    metrics['pnl_std'] = valid_df['total_pnl'].std()
    metrics['pnl_median'] = valid_df['total_pnl'].median()
    
    # Max drawdown
    if 'max_drawdown' in valid_df.columns:
        metrics['dd_best'] = valid_df['max_drawdown'].max()  # Least negative
        metrics['dd_worst'] = valid_df['max_drawdown'].min()  # Most negative
        metrics['dd_mean'] = valid_df['max_drawdown'].mean()
        metrics['dd_std'] = valid_df['max_drawdown'].std()
    
    # Trades
    metrics['trades_min'] = valid_df['trades'].min()
    metrics['trades_max'] = valid_df['trades'].max()
    metrics['trades_mean'] = valid_df['trades'].mean()
    
    # Trades per year
    if 'trades_per_year' in valid_df.columns:
        metrics['tpy_min'] = valid_df['trades_per_year'].min()
        metrics['tpy_max'] = valid_df['trades_per_year'].max()
        metrics['tpy_mean'] = valid_df['trades_per_year'].mean()
    
    # Expectancy
    if 'expectancy_per_trade' in valid_df.columns:
        metrics['expectancy_mean'] = valid_df['expectancy_per_trade'].mean()
        metrics['expectancy_median'] = valid_df['expectancy_per_trade'].median()
    
    # Sharpe-like
    if 'sharpe_like' in valid_df.columns:
        metrics['sharpe_mean'] = valid_df['sharpe_like'].mean()
        metrics['sharpe_best'] = valid_df['sharpe_like'].max()
    
    return metrics


def calculate_composite_score(
    row: pd.Series,
    pf_weight: float = 0.4,
    wr_weight: float = 0.2,
    pnl_weight: float = 0.2,
    dd_weight: float = 0.2,
    pnl_max: float = None,
    dd_min: float = None
) -> float:
    """
    Calculate composite score for a configuration.
    
    Combines multiple metrics into a single score for ranking.
    
    Args:
        row: DataFrame row with metrics
        pf_weight: Weight for profit factor (default: 0.4)
        wr_weight: Weight for win rate (default: 0.2)
        pnl_weight: Weight for PnL (default: 0.2)
        dd_weight: Weight for drawdown (default: 0.2)
        pnl_max: Maximum PnL for normalization (if None, uses row value)
        dd_min: Minimum drawdown for normalization (if None, uses row value)
    
    Returns:
        Composite score (higher is better)
    """
    score = 0.0
    
    # Profit factor component (normalized to 0-100)
    pf = min(row.get('profit_factor', 0), 5.0)  # Cap at 5
    score += pf * 20 * pf_weight  # Scale to 0-100
    
    # Win rate component (already 0-1, scale to 0-100)
    wr = row.get('win_rate', 0)
    score += wr * 100 * wr_weight
    
    # PnL component (normalized to 0-100)
    pnl = row.get('total_pnl', 0)
    if pnl_max and pnl_max > 0:
        score += (pnl / pnl_max) * 100 * pnl_weight
    else:
        score += (pnl / max(pnl, 1)) * 100 * pnl_weight
    
    # Drawdown component (less negative is better, normalized to 0-100)
    dd = row.get('max_drawdown', 0)
    if dd_min and dd_min < 0:
        score += (1 - dd / dd_min) * 100 * dd_weight
    else:
        score += 0  # No drawdown info
    
    return score


def parameter_sensitivity_analysis(df: pd.DataFrame, param_columns: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Analyze sensitivity of results to parameter changes.
    
    Args:
        df: Results DataFrame
        param_columns: List of parameter column names to analyze
    
    Returns:
        Dictionary mapping parameter names to their statistics
    """
    sensitivity = {}
    
    valid_df = df[df['trades'] > 0].copy()
    
    if len(valid_df) == 0:
        return sensitivity
    
    for param in param_columns:
        if param not in valid_df.columns:
            continue
        
        grouped = valid_df.groupby(param).agg({
            'profit_factor': ['mean', 'std', 'max', 'count'],
            'win_rate': 'mean',
            'total_pnl': 'mean'
        })
        
        sensitivity[param] = {
            'pf_mean_by_value': grouped['profit_factor']['mean'].to_dict(),
            'pf_std_by_value': grouped['profit_factor']['std'].to_dict(),
            'pf_max_by_value': grouped['profit_factor']['max'].to_dict(),
            'count_by_value': grouped['profit_factor']['count'].to_dict(),
            'wr_mean_by_value': grouped['win_rate']['mean'].to_dict(),
            'pnl_mean_by_value': grouped['total_pnl']['mean'].to_dict(),
        }
    
    return sensitivity


def variant_comparison(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Compare performance across strategy variants.
    
    Args:
        df: Results DataFrame with 'variant' column
    
    Returns:
        Dictionary mapping variant names to their statistics
    """
    comparison = {}
    
    valid_df = df[df['trades'] > 0].copy()
    
    if len(valid_df) == 0 or 'variant' not in valid_df.columns:
        return comparison
    
    for variant in valid_df['variant'].unique():
        v_data = valid_df[valid_df['variant'] == variant]
        
        comparison[variant] = {
            'count': len(v_data),
            'pf_mean': v_data['profit_factor'].mean(),
            'pf_std': v_data['profit_factor'].std(),
            'pf_max': v_data['profit_factor'].max(),
            'wr_mean': v_data['win_rate'].mean(),
            'wr_std': v_data['win_rate'].std(),
            'pnl_mean': v_data['total_pnl'].mean(),
            'pnl_std': v_data['total_pnl'].std(),
            'trades_mean': v_data['trades'].mean(),
        }
        
        if 'max_drawdown' in v_data.columns:
            comparison[variant]['dd_mean'] = v_data['max_drawdown'].mean()
        
        if 'trades_per_year' in v_data.columns:
            comparison[variant]['tpy_mean'] = v_data['trades_per_year'].mean()
    
    return comparison


def robust_filter(
    df: pd.DataFrame,
    pf_threshold: float = 1.5,
    min_trades: int = 10,
    min_win_rate: float = 0.4
) -> pd.DataFrame:
    """
    Filter for robust configurations.
    
    Args:
        df: Results DataFrame
        pf_threshold: Minimum profit factor
        min_trades: Minimum number of trades
        min_win_rate: Minimum win rate
    
    Returns:
        Filtered DataFrame with robust configurations
    """
    robust = df[
        (df['profit_factor'] >= pf_threshold) &
        (df['trades'] >= min_trades) &
        (df['total_pnl'] > 0) &
        (df['win_rate'] >= min_win_rate)
    ].copy()
    
    return robust
