#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Utilities
-----------------------
Helper functions for configuration management.
"""

import os
from typing import List, Dict
from pathlib import Path
import pandas as pd

from .types import StrategyConfig, ParamRange
from .manager import ConfigManager


def get_project_root() -> Path:
    """
    Get the project root directory (parent of src/).
    
    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent.parent


def resolve_config_path(csv_path: str) -> str:
    """
    Resolve configuration file path.
    
    If path is absolute, returns as-is.
    If path is just a filename, looks in config/ folder.
    Otherwise, treats as relative path.
    
    Args:
        csv_path: Path to config file
    
    Returns:
        Resolved absolute path
    """
    if os.path.isabs(csv_path):
        return csv_path
    
    # If just a filename, look in config/ folder
    if os.sep not in csv_path and '/' not in csv_path:
        project_root = get_project_root()
        return str(project_root / "config" / csv_path)
    
    return csv_path


def load_params_from_csv(csv_path: str) -> StrategyConfig:
    """
    Load parameters from CSV file (first row).
    
    Args:
        csv_path: Path to CSV file. Can be:
            - Absolute path: /full/path/to/params.csv
            - Relative path: ../config/params.csv
            - Filename only: params.csv (looks in config/ folder)
    
    Returns:
        StrategyConfig from first row of CSV
        
    Raises:
        ValueError: If no configurations found in file
    """
    resolved_path = resolve_config_path(csv_path)
    manager = ConfigManager()
    manager.load_from_csv(resolved_path)
    
    if not manager.configs:
        raise ValueError(f"No configurations found in {resolved_path}")
    
    return manager.configs[0]


def load_all_params_from_csv(csv_path: str) -> List[StrategyConfig]:
    """
    Load all parameter sets from CSV file.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        List of StrategyConfig objects (one per row)
    """
    resolved_path = resolve_config_path(csv_path)
    manager = ConfigManager()
    manager.load_from_csv(resolved_path)
    return manager.configs


def save_params_to_csv(config: StrategyConfig, csv_path: str):
    """
    Save parameters to CSV file.
    
    Args:
        config: StrategyConfig to save
        csv_path: Path to save. If filename only, saves to config/ folder.
    """
    resolved_path = resolve_config_path(csv_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    
    df = pd.DataFrame([config.to_dict()])
    df.to_csv(resolved_path, index=False)


def save_multiple_params_to_csv(configs: List[StrategyConfig], csv_path: str):
    """
    Save multiple parameter sets to CSV file.
    
    Args:
        configs: List of StrategyConfig objects
        csv_path: Path to save
    """
    resolved_path = resolve_config_path(csv_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    
    data = [config.to_dict() for config in configs]
    df = pd.DataFrame(data)
    df.to_csv(resolved_path, index=False)


def create_default_ranges() -> Dict[str, ParamRange]:
    """
    Create default parameter ranges for optimization.
    
    Wide ranges suitable for initial exploration.
    
    Returns:
        Dictionary mapping parameter names to ParamRange objects
    """
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=2,
            values=['base', 'rsi', 'reclaim'],
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=150, max_val=250,
            step=10,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.02, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.05, max_val=0.20,
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.04, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.0, max_val=3.0,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=10, max_val=60,
            step=5,
            param_type='int'
        ),
        'be_trigger_pct': ParamRange(
            name='be_trigger_pct',
            min_val=0.03, max_val=0.10,
            step=0.01,
            param_type='float'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=1,
            values=[True, False],
            param_type='bool'
        )
    }


def create_narrow_ranges() -> Dict[str, ParamRange]:
    """
    Create narrow parameter ranges based on best grid search results.
    
    Focused ranges for fine-tuning around known good parameters.
    Based on empirical results showing:
    - BASE variant performs best
    - Breakeven=False is optimal
    - MA200-220 range is effective
    
    Returns:
        Dictionary mapping parameter names to ParamRange objects
    """
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=0,
            values=['base'],  # Only BASE variant
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=200, max_val=230,
            step=5,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.03, max_val=0.10,
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.08, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.06, max_val=0.12,
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.0, max_val=2.5,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=15, max_val=45,
            step=5,
            param_type='int'
        ),
        'be_trigger_pct': ParamRange(
            name='be_trigger_pct',
            min_val=0.05, max_val=0.08,
            step=0.01,
            param_type='float'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=0,
            values=[False],  # Always False (best empirical result)
            param_type='bool'
        )
    }


def create_custom_ranges(params: Dict[str, tuple]) -> Dict[str, ParamRange]:
    """
    Create custom parameter ranges from specification.
    
    Args:
        params: Dictionary with format:
            {
                'param_name': (min_val, max_val, step, type),
                'variant': (['base', 'rsi'], 'str'),  # For discrete values
            }
    
    Returns:
        Dictionary of ParamRange objects
        
    Example:
        ranges = create_custom_ranges({
            'tp_pct': (0.08, 0.15, 0.01, 'float'),
            'sl_pct': (0.06, 0.10, 0.01, 'float'),
            'variant': (['base', 'rsi'], 'str')
        })
    """
    ranges = {}
    
    for name, spec in params.items():
        if isinstance(spec[0], list):
            # Discrete values provided
            values, param_type = spec
            ranges[name] = ParamRange(
                name=name,
                min_val=0,
                max_val=len(values) - 1,
                values=values,
                param_type=param_type
            )
        else:
            # Continuous range
            min_val, max_val, step, param_type = spec
            ranges[name] = ParamRange(
                name=name,
                min_val=min_val,
                max_val=max_val,
                step=step,
                param_type=param_type
            )
    
    return ranges
