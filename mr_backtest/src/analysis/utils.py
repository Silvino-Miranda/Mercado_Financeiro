#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Utilities
------------------
Helper functions for loading and saving analysis data.
"""

import pickle
from pathlib import Path
from typing import Any, Dict
import pandas as pd

from .types import CheckpointData


def load_checkpoint(checkpoint_path: str) -> CheckpointData:
    """
    Load checkpoint from pickle file.
    
    Args:
        checkpoint_path: Path to checkpoint file
    
    Returns:
        CheckpointData instance
    
    Raises:
        FileNotFoundError: If checkpoint file doesn't exist
        ValueError: If checkpoint format is invalid
    """
    path = Path(checkpoint_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    with open(path, 'rb') as f:
        ckpt_dict = pickle.load(f)
    
    # Validate required fields
    if 'population' not in ckpt_dict:
        raise ValueError("Invalid checkpoint: missing 'population' field")
    
    if 'generation' not in ckpt_dict:
        raise ValueError("Invalid checkpoint: missing 'generation' field")
    
    # Extract data
    population = ckpt_dict['population']
    generation = ckpt_dict['generation']
    total_generations = ckpt_dict.get('total_generations', generation)
    
    # Find best individual
    valid_individuals = [ind for ind in population if ind.fitness > -999999]
    best_individual = max(valid_individuals, key=lambda x: x.fitness) if valid_individuals else None
    
    # Extract metadata
    metadata = {k: v for k, v in ckpt_dict.items() 
                if k not in ['population', 'generation', 'total_generations']}
    
    return CheckpointData(
        generation=generation,
        total_generations=total_generations,
        population=population,
        best_individual=best_individual,
        metadata=metadata
    )


def save_analysis(analysis_dict: Dict[str, Any], output_path: str) -> None:
    """
    Save analysis results to file.
    
    Args:
        analysis_dict: Analysis results dictionary
        output_path: Output file path (.pkl or .json)
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix == '.pkl':
        with open(path, 'wb') as f:
            pickle.dump(analysis_dict, f)
    elif path.suffix == '.json':
        import json
        with open(path, 'w') as f:
            json.dump(analysis_dict, f, indent=2, default=str)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix} (use .pkl or .json)")


def load_grid_results(csv_path: str) -> pd.DataFrame:
    """
    Load grid search results from CSV.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        DataFrame with results
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    path = Path(csv_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {csv_path}")
    
    df = pd.read_csv(path)
    
    return df


def resolve_path(path: str, base_dir: str = None) -> Path:
    """
    Resolve relative path to absolute path.
    
    Args:
        path: File path (relative or absolute)
        base_dir: Base directory for relative paths (default: current working directory)
    
    Returns:
        Absolute Path object
    """
    p = Path(path)
    
    if p.is_absolute():
        return p
    
    if base_dir:
        return Path(base_dir) / p
    
    return p.resolve()


def save_top_configs_to_csv(configs: list, output_path: str) -> None:
    """
    Save top configurations to CSV file.
    
    Args:
        configs: List of configuration dictionaries
        output_path: Output CSV path
    """
    if not configs:
        print(f"⚠️ No configurations to save")
        return
    
    df = pd.DataFrame(configs)
    
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(path, index=False)
    print(f"✓ Saved {len(configs)} configurations to: {output_path}")
