#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimization Utilities
----------------------
Helper functions for optimization operations.
"""

import os
import pandas as pd
from pathlib import Path
from typing import List

from ..config import StrategyConfig, save_params_to_csv
from .types import Individual


def save_optimization_results(
    individuals: List[Individual],
    csv_path: str,
    top_n: int = None
):
    """
    Save optimization results to CSV.
    
    Args:
        individuals: List of individuals (sorted by fitness)
        csv_path: Path to save results
        top_n: If specified, save only top N individuals
    """
    if not individuals:
        raise ValueError("No individuals to save")
    
    # Resolve path
    if not os.path.isabs(csv_path):
        project_root = Path(__file__).parent.parent.parent
        csv_path = str(project_root / "data" / csv_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Prepare data
    if top_n:
        individuals = individuals[:top_n]
    
    rows = []
    for ind in individuals:
        row = {
            'fitness': ind.fitness,
            'generation': ind.generation,
            **ind.config.to_dict()
        }
        if ind.metrics:
            row.update(ind.metrics)
        rows.append(row)
    
    # Save
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(rows)} results to: {csv_path}")


def load_optimization_history(csv_path: str) -> pd.DataFrame:
    """
    Load optimization history from CSV.
    
    Args:
        csv_path: Path to history CSV
    
    Returns:
        DataFrame with history
    """
    if not os.path.isabs(csv_path):
        project_root = Path(__file__).parent.parent.parent
        csv_path = str(project_root / "report" / csv_path)
    
    return pd.read_csv(csv_path)


def save_best_config(individual: Individual, csv_path: str):
    """
    Save best configuration to config folder.
    
    Args:
        individual: Best individual
        csv_path: Filename (saved to config/)
    """
    save_params_to_csv(individual.config, csv_path)
    print(f"Saved best configuration to: config/{csv_path}")


def calculate_diversity(population: List[Individual]) -> float:
    """
    Calculate population diversity.
    
    Measures how different individuals are from each other.
    Higher diversity = more exploration.
    
    Args:
        population: List of individuals
    
    Returns:
        Diversity score (0-1)
    """
    if len(population) < 2:
        return 0.0
    
    # Calculate fitness variance as diversity measure
    fitnesses = [ind.fitness for ind in population if ind.fitness > -999999]
    
    if len(fitnesses) < 2:
        return 0.0
    
    import numpy as np
    return float(np.std(fitnesses) / (np.mean(fitnesses) + 1e-10))


def print_population_summary(population: List[Individual]):
    """
    Print summary statistics of population.
    
    Args:
        population: List of individuals
    """
    fitnesses = [ind.fitness for ind in population if ind.fitness > -999999]
    
    if not fitnesses:
        print("No valid individuals in population")
        return
    
    import numpy as np
    
    print("\nPopulation Summary:")
    print(f"  Size: {len(population)}")
    print(f"  Valid: {len(fitnesses)}")
    print(f"  Best Fitness: {max(fitnesses):.4f}")
    print(f"  Avg Fitness: {np.mean(fitnesses):.4f}")
    print(f"  Worst Fitness: {min(fitnesses):.4f}")
    print(f"  Std Dev: {np.std(fitnesses):.4f}")
    print(f"  Diversity: {calculate_diversity(population):.4f}")
