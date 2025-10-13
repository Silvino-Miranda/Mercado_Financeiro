#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager
---------------------
Manages multiple strategy configurations and parameter ranges.
"""

from typing import List, Dict
import pandas as pd

from .types import StrategyConfig, ParamRange


class ConfigManager:
    """
    Manager for multiple strategy configurations and optimization ranges.
    
    Features:
    - Store multiple configurations
    - Load/save from CSV
    - Manage parameter ranges for optimization
    - Extract best configuration from results
    """
    
    def __init__(self):
        """Initialize empty configuration manager."""
        self.configs: List[StrategyConfig] = []
        self.param_ranges: Dict[str, ParamRange] = {}
    
    def add_config(self, config: StrategyConfig):
        """
        Add configuration to manager.
        
        Args:
            config: StrategyConfig to add
        """
        self.configs.append(config)
    
    def add_param_range(self, param_range: ParamRange):
        """
        Define parameter range for optimization.
        
        Args:
            param_range: ParamRange specification
        """
        self.param_ranges[param_range.name] = param_range
    
    def load_from_csv(self, csv_path: str):
        """
        Load configurations from CSV file.
        
        Reads all rows and creates StrategyConfig for each.
        Handles boolean string conversion ('true'/'false').
        
        Args:
            csv_path: Path to CSV file
        """
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            data = row.to_dict()
            
            # Convert boolean strings to actual booleans
            for key, val in data.items():
                if isinstance(val, str):
                    if val.lower() in ['true', 'false']:
                        data[key] = val.lower() == 'true'
            
            config = StrategyConfig.from_dict(data)
            self.add_config(config)
    
    def save_to_csv(self, csv_path: str):
        """
        Save all configurations to CSV file.
        
        Args:
            csv_path: Path to save CSV
            
        Raises:
            ValueError: If no configurations to save
        """
        if not self.configs:
            raise ValueError("No configurations to save")
        
        data = [config.to_dict() for config in self.configs]
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
    
    def get_best_config(self, results: pd.DataFrame, metric: str = 'profit_factor') -> StrategyConfig:
        """
        Extract best configuration from backtest results.
        
        Args:
            results: DataFrame with backtest results
            metric: Metric to optimize (default: profit_factor)
        
        Returns:
            StrategyConfig with best performance
            
        Raises:
            ValueError: If results DataFrame is empty
        """
        if results.empty:
            raise ValueError("No results provided")
        
        best_idx = results[metric].idxmax()
        best_row = results.loc[best_idx]
        
        return StrategyConfig.from_dict(best_row.to_dict())
    
    def clear(self):
        """Clear all configurations and parameter ranges."""
        self.configs.clear()
        self.param_ranges.clear()
    
    def get_config_by_name(self, name: str) -> StrategyConfig:
        """
        Get configuration by name.
        
        Args:
            name: Configuration name
        
        Returns:
            StrategyConfig with matching name
            
        Raises:
            ValueError: If no configuration with that name exists
        """
        for config in self.configs:
            if config.name == name:
                return config
        raise ValueError(f"No configuration found with name: {name}")
    
    def validate_all(self) -> Dict[str, List[str]]:
        """
        Validate all configurations.
        
        Returns:
            Dictionary mapping config names to error messages
        """
        validation_results = {}
        
        for config in self.configs:
            is_valid, errors = config.validate()
            if not is_valid:
                validation_results[config.name] = errors
        
        return validation_results
    
    def __len__(self) -> int:
        """Return number of configurations."""
        return len(self.configs)
    
    def __iter__(self):
        """Iterate over configurations."""
        return iter(self.configs)
