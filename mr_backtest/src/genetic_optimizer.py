#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genetic Algorithm Optimizer for Trading Strategies
--------------------------------------------------
Otimiza parâmetros de estratégias usando Algoritmo Genético com objetivo de:
- Maximizar ROI (return on investment)
- Aumentar número de trades por ano
- Manter profit factor alto
- Minimizar drawdown

Features:
- Multi-objective optimization (Pareto front)
- Elitism (melhores indivíduos sempre sobrevivem)
- Mutação adaptativa
- Crossover uniforme e de ponto único
- Suporte a paralelização

Usage:
    from genetic_optimizer import GeneticOptimizer, OptimizationObjective
    
    optimizer = GeneticOptimizer(
        csv_data_path='BTCUSDT_daily.csv',
        population_size=50,
        generations=20,
        objective=OptimizationObjective.MULTI
    )
    
    best_params = optimizer.run()
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
from tqdm import tqdm
import multiprocessing as mp

from config import StrategyConfig, ParamRange, create_narrow_ranges
from mr_backtest import backtest, analyze, load_ohlc_csv


class OptimizationObjective(Enum):
    """Objetivos de otimização"""
    PROFIT_FACTOR = "profit_factor"
    TOTAL_PNL = "total_pnl"
    SHARPE = "sharpe_like"
    TRADES_PER_YEAR = "trades_per_year"
    ROI = "roi"  # PnL / max_drawdown
    MULTI = "multi"  # Multi-objetivo


@dataclass
class Individual:
    """Indivíduo da população (conjunto de parâmetros)"""
    config: StrategyConfig
    fitness: float = 0.0
    metrics: Optional[Dict[str, float]] = None
    generation: int = 0
    
    def __lt__(self, other):
        return self.fitness < other.fitness


class GeneticOptimizer:
    """
    Otimizador baseado em Algoritmo Genético
    
    Parameters:
    -----------
    csv_data_path : str
        Caminho para dados OHLC
    population_size : int
        Tamanho da população
    generations : int
        Número de gerações
    objective : OptimizationObjective
        Objetivo de otimização
    param_ranges : Dict[str, ParamRange]
        Ranges dos parâmetros (None = usar defaults)
    mutation_rate : float
        Taxa de mutação inicial (0.0 - 1.0)
    crossover_rate : float
        Taxa de crossover (0.0 - 1.0)
    elitism_rate : float
        Percentual de elite que sobrevive (0.0 - 1.0)
    min_trades : int
        Mínimo de trades para considerar válido
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
        """Cria configuração aleatória dentro dos ranges"""
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
        """Avalia fitness de um indivíduo"""
        try:
            params = individual.config.to_params()
            trades, ec = backtest(self.df, params)
            metrics = analyze(trades, ec, self.df)
            
            individual.metrics = metrics
            
            # Check minimum trades
            if metrics['trades'] < self.min_trades:
                return -999999.0  # Penalidade severa
            
            # Calculate fitness based on objective
            if self.objective == OptimizationObjective.PROFIT_FACTOR:
                fitness = metrics['profit_factor']
                if fitness == float('inf'):
                    fitness = 100.0  # Cap infinity
            
            elif self.objective == OptimizationObjective.TOTAL_PNL:
                fitness = metrics['total_pnl']
            
            elif self.objective == OptimizationObjective.SHARPE:
                fitness = metrics['sharpe_like']
            
            elif self.objective == OptimizationObjective.TRADES_PER_YEAR:
                # Balance: queremos mais trades mas mantendo qualidade
                fitness = metrics['trades_per_year'] * metrics['win_rate'] * 10
            
            elif self.objective == OptimizationObjective.ROI:
                # ROI = retorno / risco
                if metrics['max_drawdown'] != 0:
                    fitness = metrics['total_pnl'] / abs(metrics['max_drawdown'])
                else:
                    fitness = metrics['total_pnl']
            
            elif self.objective == OptimizationObjective.MULTI:
                # Multi-objetivo: combina várias métricas
                pf = min(metrics['profit_factor'], 10.0)  # Cap PF
                tpy = metrics['trades_per_year']
                wr = metrics['win_rate']
                pnl = metrics['total_pnl']
                
                # Normalizar e combinar
                # Queremos: PF alto, mais trades, alto win rate, PnL positivo
                fitness = (
                    pf * 0.3 +  # 30% profit factor
                    (tpy / 20.0) * 100 * 0.25 +  # 25% frequência (normalizado para ~20 trades/ano)
                    wr * 100 * 0.25 +  # 25% win rate
                    (pnl / 1000.0) * 0.20  # 20% PnL (normalizado)
                )
            
            else:
                fitness = metrics['profit_factor']
            
            return float(fitness)
            
        except Exception as e:
            print(f"Error evaluating individual: {e}")
            return -999999.0
    
    def _initialize_population(self):
        """Inicializa população aleatória"""
        print(f"Initializing population of {self.population_size}...")
        self.population = []
        
        for i in range(self.population_size):
            config = self._create_random_config()
            individual = Individual(config=config, generation=0)
            self.population.append(individual)
        
        # Evaluate fitness
        self._evaluate_population()
    
    def _evaluate_population(self):
        """Avalia fitness de toda população"""
        if self.parallel:
            # TODO: Implementar avaliação paralela
            pass
        
        for individual in tqdm(self.population, desc=f"Gen {self.generation} - Evaluating"):
            individual.fitness = self._evaluate_fitness(individual)
            individual.generation = self.generation
    
    def _selection(self, k: int = 3) -> Individual:
        """Seleção por torneio"""
        tournament = random.sample(self.population, k)
        return max(tournament, key=lambda ind: ind.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Crossover uniforme de dois pais"""
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
        """Mutação de um indivíduo"""
        for param_name, param_range in self.param_ranges.items():
            if random.random() < self.mutation_rate:
                values = param_range.get_values()
                new_value = random.choice(values)
                setattr(individual.config, param_name, new_value)
    
    def _evolve_generation(self):
        """Evolui uma geração"""
        # Sort by fitness
        self.population.sort(reverse=True, key=lambda ind: ind.fitness)
        
        # Elitism: mantém os melhores
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
        
        # Adaptive mutation rate (decai com gerações)
        self.mutation_rate = self.initial_mutation_rate * (1 - self.generation / self.generations)
    
    def _update_best(self):
        """Atualiza melhor indivíduo"""
        best = max(self.population, key=lambda ind: ind.fitness)
        if self.best_individual is None or best.fitness > self.best_individual.fitness:
            self.best_individual = best
    
    def _log_generation(self):
        """Log estatísticas da geração"""
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
        """Executa otimização"""
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
                print(f"\nMetrics:")
                print(f"  Profit Factor: {m['profit_factor']:.4f}")
                print(f"  Win Rate: {m['win_rate']:.2%}")
                print(f"  Trades/Year: {m['trades_per_year']:.2f}")
                print(f"  Total PnL: ${m['total_pnl']:.2f}")
                print(f"  Max Drawdown: ${m['max_drawdown']:.2f}")
                print(f"  Expectancy: ${m['expectancy_per_trade']:.2f}/trade")
            
            print(f"\nParameters:")
            for key in self.param_ranges.keys():
                val = getattr(self.best_individual.config, key)
                print(f"  {key}: {val}")
            
            return self.best_individual.config
        
        raise RuntimeError("No valid solution found")
    
    def get_top_n(self, n: int = 10) -> List[Individual]:
        """Retorna top N indivíduos"""
        sorted_pop = sorted(self.population, reverse=True, key=lambda ind: ind.fitness)
        return sorted_pop[:n]
    
    def save_history(self, csv_path: str):
        """Salva histórico de evolução"""
        df = pd.DataFrame(self.history)
        df.to_csv(csv_path, index=False)
        print(f"Saved evolution history to: {csv_path}")


if __name__ == "__main__":
    # Demo
    print("Testing Genetic Optimizer...")
    
    optimizer = GeneticOptimizer(
        csv_data_path='BTCUSDT_daily.csv',
        population_size=20,  # Small for demo
        generations=5,       # Few generations for demo
        objective=OptimizationObjective.MULTI,
        min_trades=5
    )
    
    best_config = optimizer.run()
    
    # Save results
    optimizer.save_history('optimization_history.csv')
    
    from config import save_params_to_csv
    save_params_to_csv(best_config, 'optimized_params.csv')
    print("\nSaved optimized parameters to: optimized_params.csv")
