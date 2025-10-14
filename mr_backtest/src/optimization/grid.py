#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid Search Optimizer
----------------------
Exhaustive grid search over parameter combinations.
"""

import os
import pandas as pd
from typing import Dict, List
from pathlib import Path
from itertools import product
from tqdm import tqdm

from ..config import StrategyConfig, ParamRange, create_default_ranges
from ..backtest import BacktestEngine, load_ohlc_csv


class GridSearchOptimizer:
    """
    Grid search optimizer for trading strategies.
    
    Performs exhaustive search over all parameter combinations.
    
    Parameters:
        csv_data_path: Path to OHLC CSV data
        param_ranges: Parameter ranges (None = use default ranges)
        min_trades: Minimum trades required for valid solution
    """
    
    def __init__(
        self,
        csv_data_path: str,
        param_ranges: Dict[str, ParamRange] = None,
        min_trades: int = 5
    ):
        # Resolve data path
        if not os.path.isabs(csv_data_path):
            project_root = Path(__file__).parent.parent.parent
            csv_data_path = str(project_root / "data" / csv_data_path)
        
        self.csv_data_path = csv_data_path
        self.param_ranges = param_ranges or create_default_ranges()
        self.min_trades = min_trades
        
        # Load data
        self.df = load_ohlc_csv(csv_data_path)
        
        # Results
        self.results: List[Dict] = []
        self.best_config: StrategyConfig = None
        self.best_metrics: Dict = None
    
    def _generate_combinations(self) -> List[Dict]:
        """
        Generate all parameter combinations.
        
        Returns:
            List of parameter dictionaries
        """
        param_names = list(self.param_ranges.keys())
        param_values = [self.param_ranges[name].get_values() for name in param_names]
        
        combinations = []
        for values in product(*param_values):
            combo = dict(zip(param_names, values))
            combinations.append(combo)
        
        return combinations
    
    def run(self, sort_by: str = 'profit_factor') -> StrategyConfig:
        """
        Run grid search optimization.
        
        Args:
            sort_by: Metric to sort results by
        
        Returns:
            Best configuration found
        """
        # Generate all combinations
        combinations = self._generate_combinations()
        total_combinations = len(combinations)
        
        print("=" * 70)
        print("GRID SEARCH OPTIMIZATION")
        print("=" * 70)
        print(f"Total combinations: {total_combinations:,}")
        print(f"Parameters: {len(self.param_ranges)}")
        print(f"Estimated time: ~{total_combinations * 0.1:.1f} seconds")
        print("=" * 70)
        
        # Test each combination
        for combo in tqdm(combinations, desc="Grid Search"):
            # Create config with this combination
            config_dict = combo.copy()
            
            # Fill missing params with defaults
            default_config = StrategyConfig()
            for field_name in default_config.__dataclass_fields__:
                if field_name not in config_dict:
                    config_dict[field_name] = getattr(default_config, field_name)
            
            config = StrategyConfig.from_dict(config_dict)
            
            # Run backtest
            try:
                params = config.to_params()
                engine = BacktestEngine(params)
                result = engine.run(self.df)
                
                # Filter by minimum trades
                if result.metrics['trades'] >= self.min_trades:
                    # Store results
                    row = {
                        **combo,  # Parameter values
                        **result.metrics  # Metrics
                    }
                    self.results.append(row)
            
            except Exception as e:
                # Skip invalid configurations
                continue
        
        # Convert to DataFrame and sort
        if not self.results:
            raise RuntimeError("No valid configurations found")
        
        df_results = pd.DataFrame(self.results)
        df_results = df_results.sort_values(
            by=[sort_by, "total_pnl", "max_drawdown"],
            ascending=[False, False, True]
        )
        
        # Get best config
        best_row = df_results.iloc[0]
        self.best_config = StrategyConfig.from_dict(best_row.to_dict())
        self.best_metrics = best_row.to_dict()
        
        # Print results
        print("\n" + "=" * 70)
        print("GRID SEARCH COMPLETE")
        print("=" * 70)
        print(f"\nTested: {len(self.results)} valid configurations")
        print(f"Best configuration (by {sort_by}):")
        print(f"\nMetrics:")
        print(f"  Profit Factor: {best_row['profit_factor']:.4f}")
        print(f"  Win Rate: {best_row['win_rate']:.2%}")
        print(f"  Trades/Year: {best_row['trades_per_year']:.2f}")
        print(f"  Total PnL: ${best_row['total_pnl']:.2f}")
        print(f"  Max Drawdown: ${best_row['max_drawdown']:.2f}")
        
        print("\nParameters:")
        for key in self.param_ranges.keys():
            print(f"  {key}: {best_row[key]}")
        
        return self.best_config
    
    def save_results(self, csv_path: str):
        """
        Save all results to CSV.
        
        Args:
            csv_path: Path to save (relative paths resolve to data/ folder)
        """
        if not self.results:
            raise RuntimeError("No results to save. Run optimization first.")
        
        if not os.path.isabs(csv_path):
            project_root = Path(__file__).parent.parent.parent
            csv_path = str(project_root / "data" / csv_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        df = pd.DataFrame(self.results)
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(self.results)} results to: {csv_path}")
    
    def get_top_n(self, n: int = 10, sort_by: str = 'profit_factor') -> pd.DataFrame:
        """
        Get top N configurations.
        
        Args:
            n: Number of configurations to return
            sort_by: Metric to sort by
        
        Returns:
            DataFrame with top configurations
        """
        if not self.results:
            raise RuntimeError("No results available. Run optimization first.")
        
        df = pd.DataFrame(self.results)
        df = df.sort_values(
            by=[sort_by, "total_pnl"],
            ascending=[False, False]
        )
        return df.head(n)
