#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimize for Daily Trading Strategy - 1 Trade Per Day
------------------------------------------------------
META ESPECÍFICA:
- 1 trade por dia (~365 trades/ano vs atual 6-7)
- 2-3% de lucro líquido por trade (após custos)
- Maximizar frequência mantendo qualidade

Features:
- População de 100 indivíduos (alta diversidade)
- Checkpoint automático a cada geração
- Retomar otimização de onde parou
- Objetivo focado em alta frequência + ROI

Usage:
    # Iniciar nova otimização
    python optimize_daily_trader.py --new
    
    # Retomar otimização anterior
    python optimize_daily_trader.py --resume
    
    # Quick test (10 gen)
    python optimize_daily_trader.py --quick
"""

import argparse
import os
import sys
import json
import pickle
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Updated imports - using new modular structure
from src.optimization import GeneticOptimizer, OptimizationObjective
from src.config import StrategyConfig, save_params_to_csv, ParamRange
from src.backtest import BacktestEngine
from src.backtest.utils import load_ohlc_csv


def create_daily_trader_ranges() -> dict:
    """
    Ranges agressivos para trading diário:
    - Alta frequência de sinais (dist_below_ma maior)
    - TP/SL menores para saídas rápidas
    - Time stop curto para rotação rápida
    - Foco em capturar movimentos pequenos frequentes
    """
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=0,
            values=['base'],  # BASE é melhor
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=150, max_val=220,  # MA mais reativa
            step=10,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.05, max_val=0.20,  # AMPLO: 5-20% (0.10=10% funciona bem no grid)
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.05, max_val=0.15,  # TP: 5-15% (0.10=10% funciona bem no grid)
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.05, max_val=0.15,  # SL: 5-15% (0.10=10% funciona bem no grid)
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.0, max_val=2.0,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=5, max_val=20,  # TIME STOP CURTO - 5-20 dias para rotação
            step=5,
            param_type='int'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=1,
            values=[False],
            param_type='bool'
        ),
    }


class DailyTraderOptimizer:
    """
    Otimizador com checkpoint/resume para trading diário
    """
    
    def __init__(
        self,
        csv_data_path: str,
        population_size: int = 100,
        generations: int = 80,
        checkpoint_dir: str = "checkpoints",
        min_trades_per_year: int = 200  # Meta: ~365/ano, mínimo 200
    ):
        self.csv_data_path = csv_data_path
        self.population_size = population_size
        self.generations = generations
        self.min_trades_per_year = min_trades_per_year
        
        # Setup checkpoint directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.checkpoint_dir = os.path.join(project_root, checkpoint_dir)
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        self.checkpoint_file = os.path.join(
            self.checkpoint_dir, 
            f"daily_trader_checkpoint_{datetime.now().strftime('%Y%m%d')}.pkl"
        )
        
        self.optimizer: Optional[GeneticOptimizer] = None
        self.current_generation = 0
        self.best_configs_history: List[Dict] = []
        
    def create_optimizer(self) -> GeneticOptimizer:
        """Create new optimizer instance"""
        # Custom fitness function for daily trading
        # Heavily weight trades_per_year (goal: 365)
        objective = OptimizationObjective.MULTI
        
        optimizer = GeneticOptimizer(
            csv_data_path=self.csv_data_path,
            population_size=self.population_size,
            generations=self.generations,
            objective=objective,
            param_ranges=create_daily_trader_ranges(),
            mutation_rate=0.30,  # Higher mutation for exploration
            crossover_rate=0.75,
            elitism_rate=0.10,  # Keep top 10%
            min_trades=5  # Mínimo de 5 trades (mais realista que 200/ano)
        )
        
        return optimizer
    
    def save_checkpoint(self, generation: int):
        """Save checkpoint after each generation"""
        checkpoint_data = {
            'generation': generation,
            'population': self.optimizer.population,
            'best_individual': self.optimizer.best_individual,
            'history': self.optimizer.history,
            'best_configs_history': self.best_configs_history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Also save JSON summary for readability
        summary_file = self.checkpoint_file.replace('.pkl', '_summary.json')
        summary = {
            'generation': generation,
            'total_generations': self.generations,
            'progress_pct': (generation / self.generations) * 100,
            'best_fitness': self.optimizer.best_individual.fitness if self.optimizer.best_individual else 0,
            'best_trades_per_year': self.optimizer.best_individual.metrics['trades_per_year'] if self.optimizer.best_individual else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Checkpoint saved: {os.path.basename(self.checkpoint_file)}")
        print(f"   Generation: {generation}/{self.generations} ({summary['progress_pct']:.1f}%)")
    
    def load_checkpoint(self) -> bool:
        """Load checkpoint if exists"""
        if not os.path.exists(self.checkpoint_file):
            return False
        
        try:
            with open(self.checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            print(f"\n✅ Checkpoint found: {os.path.basename(self.checkpoint_file)}")
            print(f"   Generation: {checkpoint_data['generation']}/{self.generations}")
            print(f"   Timestamp: {checkpoint_data['timestamp']}")
            
            # Restore optimizer state
            self.optimizer = self.create_optimizer()
            self.optimizer.population = checkpoint_data['population']
            self.optimizer.best_individual = checkpoint_data['best_individual']
            self.optimizer.history = checkpoint_data['history']
            self.optimizer.generation = checkpoint_data['generation']
            self.current_generation = checkpoint_data['generation']
            self.best_configs_history = checkpoint_data.get('best_configs_history', [])
            
            return True
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
            return False
    
    def run_with_checkpoints(self, resume: bool = False):
        """Run optimization with checkpoint at each generation"""
        
        # Try to resume if requested
        if resume:
            if self.load_checkpoint():
                print("\n🔄 Resuming from checkpoint...")
                start_gen = self.current_generation + 1
            else:
                print("\n⚠️ No checkpoint found, starting fresh...")
                self.optimizer = self.create_optimizer()
                start_gen = 0
        else:
            print("\n🆕 Starting new optimization...")
            self.optimizer = self.create_optimizer()
            start_gen = 0
        
        print("\n" + "=" * 80)
        print("🎯 DAILY TRADER OPTIMIZATION")
        print("=" * 80)
        print(f"\n📊 Configuration:")
        print(f"   Population: {self.population_size}")
        print(f"   Generations: {self.generations}")
        print(f"   Min Trades/Year: {self.min_trades_per_year}")
        print(f"   Starting from: Generation {start_gen}")
        print(f"\n🎯 Goal: 1 trade/day (~365/year) with 2-3% profit per trade")
        print(f"   Current champion: 6.87 trades/year")
        print(f"   Target improvement: +5,200% trades frequency! 🚀")
        print("\n" + "=" * 80)
        
        # Initialize population if starting fresh
        if start_gen == 0:
            print("\nInitializing population...")
            self.optimizer._initialize_population()
        
        # Run generations with checkpoints
        from tqdm import tqdm
        
        for gen in range(start_gen, self.generations):
            print(f"\n{'─' * 80}")
            print(f"Generation {gen + 1}/{self.generations}")
            print(f"{'─' * 80}")
            
            # Evolve one generation
            self.optimizer._evolve_generation()
            
            # Track best config
            if self.optimizer.best_individual:
                best_config = {
                    'generation': gen + 1,
                    'fitness': self.optimizer.best_individual.fitness,
                    'trades_per_year': self.optimizer.best_individual.metrics['trades_per_year'],
                    'profit_factor': self.optimizer.best_individual.metrics['profit_factor'],
                    'win_rate': self.optimizer.best_individual.metrics['win_rate'],
                    'total_pnl': self.optimizer.best_individual.metrics['total_pnl'],
                    'config': self.optimizer.best_individual.config.to_dict()
                }
                self.best_configs_history.append(best_config)
            
            # Save checkpoint
            self.save_checkpoint(gen + 1)
            
            # Print progress
            if self.optimizer.best_individual:
                m = self.optimizer.best_individual.metrics
                print(f"\n📈 Best so far:")
                print(f"   Fitness: {self.optimizer.best_individual.fitness:.2f}")
                print(f"   Trades/Year: {m['trades_per_year']:.2f} (goal: 365)")
                print(f"   PF: {m['profit_factor']:.2f}, WR: {m['win_rate']:.1%}")
                print(f"   PnL: ${m['total_pnl']:.2f}")
                
                # Calculate profit per trade
                if m['trades'] > 0:
                    profit_per_trade_pct = (m['total_pnl'] / (m['trades'] * 1000)) * 100
                    print(f"   Profit/Trade: {profit_per_trade_pct:.2f}% (goal: 2-3%)")
        
        print("\n" + "=" * 80)
        print("✅ OPTIMIZATION COMPLETE")
        print("=" * 80)
        
        return self.optimizer.best_individual.config if self.optimizer.best_individual else None
    
    def analyze_results(self):
        """Analyze and save final results"""
        if not self.optimizer or not self.optimizer.best_individual:
            print("❌ No results to analyze")
            return
        
        best_config = self.optimizer.best_individual.config
        best_metrics = self.optimizer.best_individual.metrics
        
        print("\n" + "=" * 80)
        print("📊 FINAL ANALYSIS")
        print("=" * 80)
        
        # Compare with goal
        print(f"\n🎯 Goal Achievement:")
        print(f"   Target Trades/Year: 365")
        print(f"   Achieved: {best_metrics['trades_per_year']:.2f}")
        print(f"   Achievement: {(best_metrics['trades_per_year'] / 365) * 100:.1f}%")
        
        print(f"\n   Target Profit/Trade: 2-3%")
        if best_metrics['trades'] > 0:
            profit_per_trade_pct = (best_metrics['total_pnl'] / (best_metrics['trades'] * 1000)) * 100
            print(f"   Achieved: {profit_per_trade_pct:.2f}%")
            if 2.0 <= profit_per_trade_pct <= 3.0:
                print(f"   Achievement: ✅ WITHIN TARGET!")
            else:
                print(f"   Achievement: ⚠️ Outside target range")
        
        # Compare with champion
        print(f"\n📈 Comparison with Champion:")
        print(f"   Champion Trades/Year: 6.87")
        print(f"   Optimized Trades/Year: {best_metrics['trades_per_year']:.2f}")
        improvement = ((best_metrics['trades_per_year'] - 6.87) / 6.87) * 100
        print(f"   Improvement: {improvement:+.1f}%")
        
        # Save best config
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        config_file = f"daily_trader_best_{timestamp}.csv"
        save_params_to_csv(best_config, config_file)
        print(f"\n💾 Saved best config: config/{config_file}")
        
        # Save evolution history
        history_file = os.path.join(
            project_root, 
            "report", 
            f"daily_trader_evolution_{timestamp}.json"
        )
        with open(history_file, 'w') as f:
            json.dump(self.best_configs_history, f, indent=2, default=str)
        print(f"💾 Saved evolution history: report/daily_trader_evolution_{timestamp}.json")
        
        # Save detailed metrics
        metrics_file = os.path.join(
            project_root,
            "report",
            f"daily_trader_metrics_{timestamp}.json"
        )
        detailed_metrics = {
            'goal': {
                'trades_per_year': 365,
                'profit_per_trade_pct': '2-3%'
            },
            'achieved': {
                'trades_per_year': best_metrics['trades_per_year'],
                'profit_per_trade_pct': profit_per_trade_pct if best_metrics['trades'] > 0 else 0,
                'profit_factor': best_metrics['profit_factor'],
                'win_rate': best_metrics['win_rate'],
                'total_pnl': best_metrics['total_pnl'],
                'max_drawdown': best_metrics['max_drawdown']
            },
            'config': best_config.to_dict(),
            'comparison_with_champion': {
                'champion_trades_per_year': 6.87,
                'improvement_pct': improvement
            }
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(detailed_metrics, f, indent=2)
        print(f"💾 Saved detailed metrics: report/daily_trader_metrics_{timestamp}.json")
        
        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description='Optimize for daily trading (1 trade/day, 2-3% profit)')
    parser.add_argument('--new', action='store_true', help='Start new optimization')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--quick', action='store_true', help='Quick test (100 pop, 10 gen)')
    parser.add_argument('--csv', default='BTCUSDT_daily.csv', help='Data file')
    parser.add_argument('--population', type=int, default=100, help='Population size')
    parser.add_argument('--generations', type=int, default=80, help='Number of generations')
    args = parser.parse_args()
    
    # Resolve data path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_root, "data", args.csv)
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Data file not found: {csv_path}")
        return
    
    # Determine mode
    if args.quick:
        population, generations = 100, 10
        print("\n🚀 QUICK TEST MODE (100 pop, 10 gen)")
    else:
        population = args.population
        generations = args.generations
        print(f"\n⚙️ CUSTOM MODE ({population} pop, {generations} gen)")
    
    # Create optimizer
    optimizer = DailyTraderOptimizer(
        csv_data_path=csv_path,
        population_size=population,
        generations=generations,
        min_trades_per_year=200  # Minimum threshold
    )
    
    # Run optimization
    resume = args.resume and not args.new
    best_config = optimizer.run_with_checkpoints(resume=resume)
    
    if best_config:
        optimizer.analyze_results()
        
        print("\n" + "=" * 80)
        print("🚀 NEXT STEPS")
        print("=" * 80)
        print("\n1. Test optimized config:")
        print("   python src/mr_backtest.py --config daily_trader_best_*.csv")
        print("\n2. Resume optimization if needed:")
        print("   python src/optimize_daily_trader.py --resume")
        print("\n3. View evolution:")
        print("   cat report/daily_trader_evolution_*.json")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
