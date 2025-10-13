#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Results Analyzer
----------------
Analyze grid search and optimization results.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from .types import AnalysisResult
from .metrics import (
    calculate_metrics,
    calculate_composite_score,
    parameter_sensitivity_analysis,
    variant_comparison as variant_comp,
    robust_filter,
)


class ResultsAnalyzer:
    """
    Analyze grid search or optimization results from CSV files.
    
    Provides comprehensive analysis including:
    - Basic statistics
    - Variant comparison
    - Parameter sensitivity
    - Top configurations
    - Robust configuration filtering
    """
    
    def __init__(self, results_df: pd.DataFrame):
        """
        Initialize analyzer with results DataFrame.
        
        Args:
            results_df: DataFrame with backtest results
        """
        self.df = results_df
        self.valid_df = results_df[results_df['trades'] > 0].copy()
    
    def analyze(
        self,
        top_n: int = 10,
        min_trades: int = 5,
        pf_threshold: float = 1.5,
        min_win_rate: float = 0.4
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis.
        
        Args:
            top_n: Number of top configurations to return
            min_trades: Minimum trades for filtering
            pf_threshold: Profit factor threshold for robust filter
            min_win_rate: Minimum win rate for robust filter
        
        Returns:
            AnalysisResult with complete analysis
        """
        # Basic metrics
        metrics = calculate_metrics(self.df)
        
        # Variant comparison
        variant_comparison = variant_comp(self.df)
        
        # Parameter sensitivity
        param_columns = ['dist_below_ma_pct', 'tp_pct', 'sl_pct', 'atr_mult', 'time_stop', 'ma_len']
        param_columns = [col for col in param_columns if col in self.df.columns]
        sensitivity = parameter_sensitivity_analysis(self.df, param_columns)
        
        # Top configurations
        top_configs = self.get_top_configs(n=top_n, min_trades=min_trades)
        
        # Best overall
        best_config = top_configs[0] if top_configs else None
        
        return AnalysisResult(
            total_configs=len(self.df),
            valid_configs=len(self.valid_df),
            invalid_configs=len(self.df) - len(self.valid_df),
            best_config=best_config,
            top_configs=top_configs,
            statistics=metrics,
            parameter_sensitivity=sensitivity,
            variant_comparison=variant_comparison,
        )
    
    def get_top_configs(self, n: int = 10, min_trades: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N configurations by profit factor.
        
        Args:
            n: Number of configurations to return
            min_trades: Minimum trades required
        
        Returns:
            List of configuration dictionaries
        """
        filtered = self.df[self.df['trades'] >= min_trades].copy()
        
        if len(filtered) == 0:
            return []
        
        top = filtered.nlargest(n, 'profit_factor')
        
        configs = []
        for _, row in top.iterrows():
            config = row.to_dict()
            configs.append(config)
        
        return configs
    
    def get_robust_configs(
        self,
        pf_threshold: float = 1.5,
        min_trades: int = 10,
        min_win_rate: float = 0.4,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get robust configurations meeting multiple criteria.
        
        Args:
            pf_threshold: Minimum profit factor
            min_trades: Minimum number of trades
            min_win_rate: Minimum win rate
            top_n: Number of configurations to return
        
        Returns:
            List of robust configuration dictionaries
        """
        robust_df = robust_filter(self.df, pf_threshold, min_trades, min_win_rate)
        
        if len(robust_df) == 0:
            return []
        
        # Calculate composite scores
        pnl_max = robust_df['total_pnl'].max()
        dd_min = robust_df['max_drawdown'].min() if 'max_drawdown' in robust_df.columns else None
        
        robust_df['composite_score'] = robust_df.apply(
            lambda row: calculate_composite_score(row, pnl_max=pnl_max, dd_min=dd_min),
            axis=1
        )
        
        top_robust = robust_df.nlargest(top_n, 'composite_score')
        
        configs = []
        for _, row in top_robust.iterrows():
            config = row.to_dict()
            configs.append(config)
        
        return configs
    
    def filter_by_variant(self, variant: str) -> 'ResultsAnalyzer':
        """
        Create a new analyzer filtered by variant.
        
        Args:
            variant: Variant name to filter by
        
        Returns:
            New ResultsAnalyzer instance with filtered data
        """
        filtered_df = self.df[self.df['variant'] == variant].copy()
        return ResultsAnalyzer(filtered_df)
    
    def print_summary(self, top_n: int = 10, min_trades: int = 5) -> None:
        """
        Print human-readable summary.
        
        Args:
            top_n: Number of top configurations to show
            min_trades: Minimum trades for filtering
        """
        print("\n" + "=" * 80)
        print("📊 RESULTS ANALYSIS")
        print("=" * 80)
        
        print(f"\n📈 Dataset Overview:")
        print(f"   Total combinations: {len(self.df)}")
        print(f"   Valid (with trades): {len(self.valid_df)} ({len(self.valid_df)/len(self.df)*100:.1f}%)")
        print(f"   Invalid (no trades): {len(self.df) - len(self.valid_df)}")
        
        if len(self.valid_df) == 0:
            print("\n⚠️ No valid configurations found (all had 0 trades)")
            print("=" * 80)
            return
        
        # Variants
        if 'variant' in self.df.columns:
            variants = self.df['variant'].unique()
            print(f"   Variants tested: {', '.join(variants)}")
        
        # Metrics summary
        print(f"\n📊 Metrics Summary (valid configurations only):")
        print(f"   Profit Factor:")
        print(f"      Best: {self.valid_df['profit_factor'].max():.4f}")
        print(f"      Mean: {self.valid_df['profit_factor'].mean():.4f}")
        print(f"      Worst: {self.valid_df['profit_factor'].min():.4f}")
        
        print(f"   Win Rate:")
        print(f"      Best: {self.valid_df['win_rate'].max():.2%}")
        print(f"      Mean: {self.valid_df['win_rate'].mean():.2%}")
        print(f"      Worst: {self.valid_df['win_rate'].min():.2%}")
        
        print(f"   Total PnL:")
        print(f"      Best: ${self.valid_df['total_pnl'].max():.2f}")
        print(f"      Mean: ${self.valid_df['total_pnl'].mean():.2f}")
        print(f"      Worst: ${self.valid_df['total_pnl'].min():.2f}")
        
        if 'trades_per_year' in self.valid_df.columns:
            print(f"   Trades/Year:")
            print(f"      Max: {self.valid_df['trades_per_year'].max():.1f}")
            print(f"      Mean: {self.valid_df['trades_per_year'].mean():.1f}")
            print(f"      Min: {self.valid_df['trades_per_year'].min():.1f}")
        
        # Variant comparison
        if 'variant' in self.valid_df.columns and len(self.valid_df['variant'].unique()) > 1:
            print(f"\n🔍 Variant Comparison:")
            for variant in self.valid_df['variant'].unique():
                v_data = self.valid_df[self.valid_df['variant'] == variant]
                print(f"\n   {variant.upper()}:")
                print(f"      Combinations: {len(v_data)}")
                print(f"      Avg PF: {v_data['profit_factor'].mean():.4f}")
                print(f"      Avg WR: {v_data['win_rate'].mean():.2%}")
                print(f"      Avg PnL: ${v_data['total_pnl'].mean():.2f}")
        
        # Top configurations
        top_configs = self.get_top_configs(n=top_n, min_trades=min_trades)
        
        print(f"\n🏆 Top {min(top_n, len(top_configs))} Configurations (min {min_trades} trades):")
        print("─" * 80)
        
        for i, config in enumerate(top_configs[:top_n], 1):
            print(f"\n#{i} - {config.get('variant', 'N/A').upper()} | "
                  f"PF: {config['profit_factor']:.4f} | PnL: ${config['total_pnl']:.2f}")
            
            # Parameters
            params = []
            if 'dist_below_ma_pct' in config:
                params.append(f"dist={config['dist_below_ma_pct']:.2f}")
            if 'tp_pct' in config:
                params.append(f"tp={config['tp_pct']:.2f}")
            if 'sl_pct' in config:
                params.append(f"sl={config['sl_pct']:.2f}")
            if 'atr_mult' in config:
                params.append(f"atr={config['atr_mult']:.1f}")
            if 'time_stop' in config:
                params.append(f"ts={config['time_stop']}")
            if 'ma_len' in config:
                params.append(f"ma={config['ma_len']}")
            
            print(f"    Params: {', '.join(params)}")
            
            # Metrics
            metrics = []
            metrics.append(f"Trades={int(config['trades'])}")
            metrics.append(f"WR={config['win_rate']:.2%}")
            if 'expectancy_per_trade' in config:
                metrics.append(f"Exp=${config['expectancy_per_trade']:.2f}")
            if 'max_drawdown' in config:
                metrics.append(f"DD=${config['max_drawdown']:.2f}")
            
            print(f"    Metrics: {', '.join(metrics)}")
        
        print("\n" + "=" * 80)
    
    def save_filtered(
        self,
        output_path: str,
        pf_min: float = 1.0,
        trades_min: int = 5
    ) -> int:
        """
        Save filtered results to CSV.
        
        Args:
            output_path: Output CSV path
            pf_min: Minimum profit factor
            trades_min: Minimum trades
        
        Returns:
            Number of configurations saved
        """
        filtered = self.df[
            (self.df['profit_factor'] >= pf_min) &
            (self.df['trades'] >= trades_min)
        ].copy()
        
        filtered = filtered.sort_values('profit_factor', ascending=False)
        filtered.to_csv(output_path, index=False)
        
        return len(filtered)
