#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Module
--------------------
Parameter configuration management for trading strategies.

This module provides:
- Strategy configuration (StrategyConfig dataclass)
- Parameter ranges for optimization (ParamRange)
- Configuration manager (ConfigManager)
- CSV import/export functionality
- Parameter validation
"""

from .types import StrategyConfig, ParamRange
from .manager import ConfigManager
from .utils import (
    load_params_from_csv,
    load_all_params_from_csv,
    save_params_to_csv,
    create_default_ranges,
    create_narrow_ranges,
    resolve_config_path,
    get_project_root
)

__all__ = [
    # Types
    "StrategyConfig",
    "ParamRange",
    # Manager
    "ConfigManager",
    # Utils
    "load_params_from_csv",
    "load_all_params_from_csv",
    "save_params_to_csv",
    "create_default_ranges",
    "create_narrow_ranges",
    "resolve_config_path",
    "get_project_root",
]
