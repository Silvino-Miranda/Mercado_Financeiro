#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkpoint Analyzer
-------------------
Analyze genetic algorithm checkpoints.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .types import CheckpointData


class CheckpointAnalyzer:
    """
    Analyze genetic algorithm optimization checkpoints.
    
    Provides detailed analysis of population evolution, fitness distribution,
    and individual performance.
    """
    
    def __init__(self, checkpoint: CheckpointData):
        """
        Initialize analyzer with checkpoint data.
        
        Args:
            checkpoint: CheckpointData instance
        """
        self.checkpoint = checkpoint
        self.population = checkpoint.population
        self.generation = checkpoint.generation
        self.total_generations = checkpoint.total_generations
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive checkpoint analysis.
        
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'generation': self.generation,
            'total_generations': self.total_generations,
            'progress_pct': (self.generation / self.total_generations * 100) if self.total_generations > 0 else 0,
            'population_size': len(self.population),
            'fitness_stats': self._fitness_statistics(),
            'trades_stats': self._trades_statistics(),
            'top_individuals': self._get_top_individuals(5),
            'diversity': self._calculate_diversity(),
            'convergence': self._check_convergence(),
        }
        
        return analysis
    
    def _fitness_statistics(self) -> Dict[str, float]:
        """Calculate fitness statistics."""
        fitness_values = [ind.fitness for ind in self.population if ind.fitness > -999999]
        
        if not fitness_values:
            return {
                'valid_count': 0,
                'invalid_count': len(self.population),
                'best': -999999,
                'worst': -999999,
                'mean': -999999,
                'std': 0,
            }
        
        return {
            'valid_count': len(fitness_values),
            'invalid_count': len(self.population) - len(fitness_values),
            'best': max(fitness_values),
            'worst': min(fitness_values),
            'mean': sum(fitness_values) / len(fitness_values),
            'std': self._std(fitness_values),
        }
    
    def _trades_statistics(self) -> Dict[str, Any]:
        """Calculate trades statistics."""
        trades = []
        trades_per_year = []
        
        for ind in self.population:
            if hasattr(ind, 'metrics') and ind.metrics:
                trades.append(ind.metrics.get('trades', 0))
                trades_per_year.append(ind.metrics.get('trades_per_year', 0))
        
        if not trades:
            return {'available': False}
        
        return {
            'available': True,
            'min_trades': min(trades),
            'max_trades': max(trades),
            'mean_trades': sum(trades) / len(trades),
            'zero_trades_count': trades.count(0),
            'min_tpy': min(trades_per_year) if trades_per_year else 0,
            'max_tpy': max(trades_per_year) if trades_per_year else 0,
            'mean_tpy': sum(trades_per_year) / len(trades_per_year) if trades_per_year else 0,
        }
    
    def _get_top_individuals(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N individuals by fitness."""
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        top = []
        for ind in sorted_pop[:n]:
            config_dict = {
                'variant': ind.config.variant,
                'ma_len': ind.config.ma_len,
                'dist_below_ma_pct': ind.config.dist_below_ma_pct,
                'tp_pct': ind.config.tp_pct,
                'sl_pct': ind.config.sl_pct,
                'atr_mult': ind.config.atr_mult,
                'time_stop': ind.config.time_stop,
                'be_trigger_pct': ind.config.be_trigger_pct,
                'allow_breakeven': ind.config.allow_breakeven,
            }
            
            top.append({
                'fitness': ind.fitness,
                'generation': ind.generation,
                'config': config_dict,
                'metrics': ind.metrics if hasattr(ind, 'metrics') else None,
            })
        
        return top
    
    def _calculate_diversity(self) -> Dict[str, float]:
        """Calculate population diversity."""
        # Count unique configurations
        configs_str = set()
        for ind in self.population:
            config_str = f"{ind.config.variant}_{ind.config.ma_len}_{ind.config.tp_pct}_{ind.config.sl_pct}"
            configs_str.add(config_str)
        
        unique_count = len(configs_str)
        total_count = len(self.population)
        
        # Calculate fitness variance (another diversity measure)
        fitness_values = [ind.fitness for ind in self.population if ind.fitness > -999999]
        fitness_variance = self._variance(fitness_values) if fitness_values else 0
        
        return {
            'unique_configs': unique_count,
            'total_configs': total_count,
            'diversity_ratio': unique_count / total_count if total_count > 0 else 0,
            'fitness_variance': fitness_variance,
        }
    
    def _check_convergence(self) -> Dict[str, Any]:
        """Check if population has converged."""
        fitness_values = [ind.fitness for ind in self.population if ind.fitness > -999999]
        
        if not fitness_values or len(fitness_values) < 2:
            return {
                'converged': False,
                'reason': 'Insufficient valid individuals',
            }
        
        # Calculate coefficient of variation
        mean = sum(fitness_values) / len(fitness_values)
        std = self._std(fitness_values)
        cv = (std / mean * 100) if mean != 0 else 0
        
        # Consider converged if CV < 10%
        converged = cv < 10.0
        
        return {
            'converged': converged,
            'coefficient_of_variation': cv,
            'fitness_range': max(fitness_values) - min(fitness_values),
        }
    
    @staticmethod
    def _std(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    @staticmethod
    def _variance(values: List[float]) -> float:
        """Calculate variance."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    
    def print_summary(self) -> None:
        """Print human-readable summary."""
        analysis = self.analyze()
        
        print("\n" + "=" * 80)
        print(f"📊 CHECKPOINT ANALYSIS")
        print("=" * 80)
        
        print(f"\n📈 Progress:")
        print(f"   Generation: {analysis['generation']}/{analysis['total_generations']} "
              f"({analysis['progress_pct']:.1f}%)")
        print(f"   Population size: {analysis['population_size']}")
        
        # Fitness stats
        fs = analysis['fitness_stats']
        print(f"\n🎯 Fitness Statistics:")
        print(f"   Valid individuals: {fs['valid_count']}/{analysis['population_size']}")
        if fs['valid_count'] > 0:
            print(f"   Best: {fs['best']:.4f}")
            print(f"   Mean: {fs['mean']:.4f}")
            print(f"   Worst: {fs['worst']:.4f}")
            print(f"   Std Dev: {fs['std']:.4f}")
        else:
            print(f"   ⚠️ NO VALID INDIVIDUALS (all penalized)")
        
        # Trades stats
        ts = analysis['trades_stats']
        if ts['available']:
            print(f"\n📊 Trades Statistics:")
            print(f"   Min trades: {ts['min_trades']}")
            print(f"   Max trades: {ts['max_trades']}")
            print(f"   Mean trades: {ts['mean_trades']:.1f}")
            print(f"   Zero trades: {ts['zero_trades_count']}/{analysis['population_size']}")
            if ts['max_tpy'] > 0:
                print(f"   Trades/Year: {ts['min_tpy']:.1f} - {ts['max_tpy']:.1f} (mean: {ts['mean_tpy']:.1f})")
        
        # Top individuals
        print(f"\n🏆 Top 5 Individuals:")
        print("─" * 80)
        for i, ind in enumerate(analysis['top_individuals'], 1):
            print(f"\n{i}. Fitness: {ind['fitness']:.4f} (Gen {ind['generation']})")
            if ind['metrics']:
                m = ind['metrics']
                print(f"   PF: {m.get('profit_factor', 0):.2f}, "
                      f"WR: {m.get('win_rate', 0):.2%}, "
                      f"Trades/Year: {m.get('trades_per_year', 0):.1f}")
            cfg = ind['config']
            print(f"   Config: {cfg['variant']}, dist={cfg['dist_below_ma_pct']:.2f}, "
                  f"tp={cfg['tp_pct']:.2f}, sl={cfg['sl_pct']:.2f}, ma={cfg['ma_len']}")
        
        # Diversity
        div = analysis['diversity']
        print(f"\n🌈 Population Diversity:")
        print(f"   Unique configs: {div['unique_configs']}/{div['total_configs']}")
        print(f"   Diversity ratio: {div['diversity_ratio']:.2%}")
        print(f"   Fitness variance: {div['fitness_variance']:.4f}")
        
        # Convergence
        conv = analysis['convergence']
        print(f"\n🎯 Convergence:")
        if conv['converged']:
            print(f"   ✅ CONVERGED (CV: {conv['coefficient_of_variation']:.2f}%)")
        else:
            print(f"   ⏳ NOT CONVERGED (CV: {conv['coefficient_of_variation']:.2f}%)")
        print(f"   Fitness range: {conv['fitness_range']:.4f}")
        
        print("\n" + "=" * 80)
