#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genetic Algorithm Optimizer
----------------------------
Optimizes trading strategy parameters using genetic algorithms.
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import random
from tqdm import tqdm
from pathlib import Path

from ..config import StrategyConfig, ParamRange, create_narrow_ranges
from ..backtest import BacktestEngine, load_ohlc_csv
from .types import Individual, OptimizationObjective


class GeneticOptimizer:
    """
    Genetic Algorithm optimizer for trading strategies.
    
    Features:
    - Multi-objective optimization
    - Elitism (best individuals always survive)
    - Adaptive mutation rate
    - Tournament selection
    - Uniform crossover
    
    Parameters:
        csv_data_path: Path to OHLC CSV data
        population_size: Number of individuals in population
        generations: Number of generations to evolve
        objective: Optimization objective
        param_ranges: Parameter ranges (None = use narrow ranges)
        mutation_rate: Initial mutation probability
        crossover_rate: Crossover probability
        elitism_rate: Fraction of population preserved as elite
        min_trades: Minimum trades required for valid solution
        parallel: Enable parallel evaluation (not implemented)
    """
    
    def __init__(
        self,
        csv_data_path: str,
        population_size: int = 50,
        generations: int = 20,
        objective: OptimizationObjective = OptimizationObjective.MULTI,
        param_ranges: Optional[Dict[str, ParamRange]] = None,
        mutation_rate: float = 0.2,
        crossover_rate: float = 0.7,
        elitism_rate: float = 0.1,
        min_trades: int = 5,
        parallel: bool = False
    ):
        # Resolve data path
        if not os.path.isabs(csv_data_path):
            project_root = Path(__file__).parent.parent.parent
            csv_data_path = str(project_root / "data" / csv_data_path)
        
        self.csv_data_path = csv_data_path
        self.population_size = population_size
        self.generations = generations
        self.objective = objective
        self.param_ranges = param_ranges or create_narrow_ranges()
        self.mutation_rate = mutation_rate
        self.initial_mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        self.min_trades = min_trades
        self.parallel = parallel
        
        # Load data
        self.df = load_ohlc_csv(csv_data_path)
        
        # Population
        self.population: List[Individual] = []
        self.best_individual: Optional[Individual] = None
        self.history: List[Dict] = []
        
        # Stats
        self.generation = 0
    
    def _create_random_config(self) -> StrategyConfig:
        """Create random configuration within parameter ranges."""
        config_dict = {}
        
        for param_name, param_range in self.param_ranges.items():
            values = param_range.get_values()
            config_dict[param_name] = random.choice(values)
        
        # Fill missing params with defaults
        default_config = StrategyConfig()
        for field_name in default_config.__dataclass_fields__:
            if field_name not in config_dict:
                config_dict[field_name] = getattr(default_config, field_name)
        
        return StrategyConfig.from_dict(config_dict)
    
    def _evaluate_fitness(self, individual: Individual) -> float:
        """
        Evaluate fitness of an individual.
        
        Args:
            individual: Individual to evaluate
        
        Returns:
            Fitness score (higher is better)
        """
        try:
            # Run backtest
            params = individual.config.to_params()
            engine = BacktestEngine(params)
            result = engine.run(self.df)
            
            individual.metrics = result.metrics
            
            # Check minimum trades requirement
            if result.metrics['trades'] < self.min_trades:
                return -999999.0  # Severe penalty
            
            # Calculate fitness based on objective
            if self.objective == OptimizationObjective.PROFIT_FACTOR:
                fitness = result.metrics['profit_factor']
                if fitness == float('inf'):
                    fitness = 100.0  # Cap infinity
            
            elif self.objective == OptimizationObjective.TOTAL_PNL:
                fitness = result.metrics['total_pnl']
            
            elif self.objective == OptimizationObjective.SHARPE:
                fitness = result.metrics['sharpe_like']
            
            elif self.objective == OptimizationObjective.TRADES_PER_YEAR:
                # Balance: want more trades but maintaining quality
                fitness = result.metrics['trades_per_year'] * result.metrics['win_rate'] * 10
            
            elif self.objective == OptimizationObjective.ROI:
                # ROI = return / risk
                if result.metrics['max_drawdown'] != 0:
                    fitness = result.metrics['total_pnl'] / abs(result.metrics['max_drawdown'])
                else:
                    fitness = result.metrics['total_pnl']
            
            elif self.objective == OptimizationObjective.MULTI:
                # Multi-objective: combine multiple metrics
                pf = min(result.metrics['profit_factor'], 10.0)  # Cap PF
                tpy = result.metrics['trades_per_year']
                wr = result.metrics['win_rate']
                pnl = result.metrics['total_pnl']
                
                # Normalize and combine
                fitness = (
                    pf * 0.3 +  # 30% profit factor
                    (tpy / 20.0) * 100 * 0.25 +  # 25% frequency (normalized to ~20 trades/year)
                    wr * 100 * 0.25 +  # 25% win rate
                    (pnl / 1000.0) * 0.20  # 20% PnL (normalized)
                )
            
            else:
                fitness = result.metrics['profit_factor']
            
            return float(fitness)
            
        except Exception as e:
            print(f"Error evaluating individual: {e}")
            return -999999.0
    
    def _initialize_population(self):
        """Initialize random population."""
        print(f"Initializing population of {self.population_size}...")
        self.population = []
        
        for _ in range(self.population_size):
            config = self._create_random_config()
            individual = Individual(config=config, generation=0)
            self.population.append(individual)
        
        # Evaluate fitness
        self._evaluate_population()
    
    def _evaluate_population(self):
        """Evaluate fitness of entire population."""
        if self.parallel:
            # TODO: Implement parallel evaluation
            pass
        
        for individual in tqdm(self.population, desc=f"Gen {self.generation} - Evaluating"):
            individual.fitness = self._evaluate_fitness(individual)
            individual.generation = self.generation
    
    def _selection(self, k: int = 3) -> Individual:
        """
        Tournament selection.
        
        Args:
            k: Tournament size
        
        Returns:
            Selected individual
        """
        tournament = random.sample(self.population, k)
        return max(tournament, key=lambda ind: ind.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Uniform crossover of two parents.
        
        Args:
            parent1: First parent
            parent2: Second parent
        
        Returns:
            Tuple of two offspring
        """
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        child1_dict = {}
        child2_dict = {}
        
        for param_name in self.param_ranges.keys():
            val1 = getattr(parent1.config, param_name)
            val2 = getattr(parent2.config, param_name)
            
            if random.random() < 0.5:
                child1_dict[param_name] = val1
                child2_dict[param_name] = val2
            else:
                child1_dict[param_name] = val2
                child2_dict[param_name] = val1
        
        # Fill missing params
        for field_name in parent1.config.__dataclass_fields__:
            if field_name not in child1_dict:
                child1_dict[field_name] = getattr(parent1.config, field_name)
                child2_dict[field_name] = getattr(parent2.config, field_name)
        
        config1 = StrategyConfig.from_dict(child1_dict)
        config2 = StrategyConfig.from_dict(child2_dict)
        
        return Individual(config=config1), Individual(config=config2)
    
    def _mutate(self, individual: Individual):
        """
        Mutate an individual.
        
        Args:
            individual: Individual to mutate (modified in place)
        """
        for param_name, param_range in self.param_ranges.items():
            if random.random() < self.mutation_rate:
                values = param_range.get_values()
                new_value = random.choice(values)
                setattr(individual.config, param_name, new_value)
    
    def _evolve_generation(self):
        """Evolve one generation."""
        # Sort by fitness
        self.population.sort(reverse=True, key=lambda ind: ind.fitness)
        
        # Elitism: preserve best individuals
        elite_size = int(self.population_size * self.elitism_rate)
        new_population = self.population[:elite_size].copy()
        
        # Generate offspring
        while len(new_population) < self.population_size:
            parent1 = self._selection()
            parent2 = self._selection()
            
            child1, child2 = self._crossover(parent1, parent2)
            
            self._mutate(child1)
            self._mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        self.population = new_population[:self.population_size]
        
        # Adaptive mutation rate (decays with generations)
        self.mutation_rate = self.initial_mutation_rate * (1 - self.generation / self.generations)
    
    def _update_best(self):
        """Update best individual found so far."""
        best = max(self.population, key=lambda ind: ind.fitness)
        if self.best_individual is None or best.fitness > self.best_individual.fitness:
            self.best_individual = best
    
    def _log_generation(self):
        """Log generation statistics."""
        fitnesses = [ind.fitness for ind in self.population if ind.fitness > -999999]
        
        if not fitnesses:
            return
        
        stats = {
            'generation': self.generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'worst_fitness': min(fitnesses),
            'std_fitness': np.std(fitnesses),
            'mutation_rate': self.mutation_rate
        }
        
        self.history.append(stats)
        
        print(f"\nGeneration {self.generation}:")
        print(f"  Best Fitness: {stats['best_fitness']:.4f}")
        print(f"  Avg Fitness:  {stats['avg_fitness']:.4f}")
        print(f"  Mutation Rate: {self.mutation_rate:.4f}")
        
        if self.best_individual and self.best_individual.metrics:
            m = self.best_individual.metrics
            print(f"  Best Individual:")
            print(f"    PF: {m['profit_factor']:.4f}, WR: {m['win_rate']:.2%}, "
                  f"Trades/Year: {m['trades_per_year']:.2f}, PnL: ${m['total_pnl']:.2f}")
    
    def run(self) -> StrategyConfig:
        """
        Run genetic algorithm optimization.
        
        Returns:
            Best configuration found
            
        Raises:
            RuntimeError: If no valid solution found
        """
        print("=" * 70)
        print("GENETIC ALGORITHM OPTIMIZATION")
        print("=" * 70)
        print(f"Population: {self.population_size}")
        print(f"Generations: {self.generations}")
        print(f"Objective: {self.objective.value}")
        print(f"Parameters to optimize: {len(self.param_ranges)}")
        print("=" * 70)
        
        # Initialize
        self._initialize_population()
        self._update_best()
        self._log_generation()
        
        # Evolve
        for gen in range(1, self.generations + 1):
            self.generation = gen
            self._evolve_generation()
            self._evaluate_population()
            self._update_best()
            self._log_generation()
        
        # Final report
        print("\n" + "=" * 70)
        print("OPTIMIZATION COMPLETE")
        print("=" * 70)
        
        if self.best_individual:
            print("\nBest Configuration Found:")
            print(f"  Generation: {self.best_individual.generation}")
            print(f"  Fitness: {self.best_individual.fitness:.4f}")
            
            if self.best_individual.metrics:
                m = self.best_individual.metrics
                print("\nMetrics:")
                print(f"  Profit Factor: {m['profit_factor']:.4f}")
                print(f"  Win Rate: {m['win_rate']:.2%}")
                print(f"  Trades/Year: {m['trades_per_year']:.2f}")
                print(f"  Total PnL: ${m['total_pnl']:.2f}")
                print(f"  Max Drawdown: ${m['max_drawdown']:.2f}")
                print(f"  Expectancy: ${m['expectancy_per_trade']:.2f}/trade")
            
            print("\nParameters:")
            for key in self.param_ranges.keys():
                val = getattr(self.best_individual.config, key)
                print(f"  {key}: {val}")
            
            return self.best_individual.config
        
        raise RuntimeError("No valid solution found")
    
    def get_top_n(self, n: int = 10) -> List[Individual]:
        """
        Get top N individuals by fitness.
        
        Args:
            n: Number of individuals to return
        
        Returns:
            List of top individuals
        """
        sorted_pop = sorted(self.population, reverse=True, key=lambda ind: ind.fitness)
        return sorted_pop[:n]
    
    def save_history(self, csv_path: str):
        """
        Save evolution history to CSV.
        
        Args:
            csv_path: Path to save (relative paths resolve to report/ folder)
        """
        if not os.path.isabs(csv_path):
            project_root = Path(__file__).parent.parent.parent
            csv_path = str(project_root / "report" / csv_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        df = pd.DataFrame(self.history)
        df.to_csv(csv_path, index=False)
        print(f"Saved evolution history to: {csv_path}")
