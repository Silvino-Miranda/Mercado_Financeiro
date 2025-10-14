#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimization Module CLI
-----------------------
Command-line interface for strategy optimization.

Usage:
    python -m src.optimization genetic --csv data.csv --generations 20
    python -m src.optimization grid --csv data.csv
"""

import argparse
import sys
from pathlib import Path

from .genetic import GeneticOptimizer
from .grid import GridSearchOptimizer
from .types import OptimizationObjective
from ..config import create_default_ranges, create_narrow_ranges, save_params_to_csv


def cmd_genetic(args):
    """Run genetic algorithm optimization."""
    # Determine param ranges
    if args.ranges == 'default':
        param_ranges = create_default_ranges()
    elif args.ranges == 'narrow':
        param_ranges = create_narrow_ranges()
    else:
        param_ranges = create_narrow_ranges()  # Default to narrow
    
    # Determine objective
    objective_map = {
        'profit_factor': OptimizationObjective.PROFIT_FACTOR,
        'total_pnl': OptimizationObjective.TOTAL_PNL,
        'sharpe': OptimizationObjective.SHARPE,
        'trades_per_year': OptimizationObjective.TRADES_PER_YEAR,
        'roi': OptimizationObjective.ROI,
        'multi': OptimizationObjective.MULTI,
    }
    objective = objective_map[args.objective]
    
    # Create optimizer
    optimizer = GeneticOptimizer(
        csv_data_path=args.csv,
        population_size=args.population,
        generations=args.generations,
        objective=objective,
        param_ranges=param_ranges,
        mutation_rate=args.mutation_rate,
        crossover_rate=args.crossover_rate,
        elitism_rate=args.elitism_rate,
        min_trades=args.min_trades,
        parallel=False
    )
    
    # Run optimization
    try:
        best_config = optimizer.run()
        
        # Save results
        if args.save_best:
            output_name = args.output or f"ga_best_{args.objective}.csv"
            save_params_to_csv(best_config, output_name)
            print(f"\n✅ Best configuration saved to: config/{output_name}")
        
        if args.save_history:
            history_name = args.history_output or "ga_history.csv"
            optimizer.save_history(history_name)
        
        # Show top N
        if args.show_top:
            print(f"\n{'='*70}")
            print(f"Top {args.show_top} Individuals:")
            print(f"{'='*70}")
            
            top_individuals = optimizer.get_top_n(args.show_top)
            for i, ind in enumerate(top_individuals, 1):
                print(f"\n{i}. Fitness: {ind.fitness:.4f} (Gen {ind.generation})")
                if ind.metrics:
                    print(f"   PF: {ind.metrics['profit_factor']:.2f}, "
                          f"WR: {ind.metrics['win_rate']:.2%}, "
                          f"Trades/Year: {ind.metrics['trades_per_year']:.1f}")
    
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        sys.exit(1)


def cmd_grid(args):
    """Run grid search optimization."""
    # Determine param ranges
    if args.ranges == 'default':
        param_ranges = create_default_ranges()
    elif args.ranges == 'narrow':
        param_ranges = create_narrow_ranges()
    else:
        param_ranges = create_narrow_ranges()
    
    # Create optimizer
    optimizer = GridSearchOptimizer(
        csv_data_path=args.csv,
        param_ranges=param_ranges,
        min_trades=args.min_trades
    )
    
    # Run optimization
    try:
        best_config = optimizer.run(sort_by=args.sort_by)
        
        # Save results
        if args.save_all:
            output_name = args.output or "grid_search_results.csv"
            optimizer.save_results(output_name)
        
        if args.save_best:
            best_name = args.best_output or f"grid_best_{args.sort_by}.csv"
            save_params_to_csv(best_config, best_name)
            print(f"\n✅ Best configuration saved to: config/{best_name}")
        
        # Show top N
        if args.show_top:
            print(f"\n{'='*70}")
            print(f"Top {args.show_top} Configurations:")
            print(f"{'='*70}\n")
            
            top_df = optimizer.get_top_n(args.show_top, sort_by=args.sort_by)
            print(top_df[['variant', 'ma_len', 'tp_pct', 'sl_pct', 
                         'profit_factor', 'win_rate', 'trades_per_year', 'total_pnl']].to_string(index=False))
    
    except Exception as e:
        print(f"\n❌ Grid search failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Strategy Parameter Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Genetic algorithm with multi-objective
  python -m src.optimization genetic --csv data/BTCUSDT_daily.csv --generations 20 --objective multi
  
  # Grid search over narrow ranges
  python -m src.optimization grid --csv data/BTCUSDT_daily.csv --ranges narrow
  
  # GA with custom parameters
  python -m src.optimization genetic --csv data.csv --population 100 --generations 50 --mutation_rate 0.3
  
  # Grid search sorted by Sharpe
  python -m src.optimization grid --csv data.csv --sort_by sharpe_like --show_top 20
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Optimization method')
    
    # GENETIC command
    genetic_parser = subparsers.add_parser('genetic', help='Genetic algorithm optimization')
    genetic_parser.add_argument('--csv', required=True, help='Path to OHLC CSV data')
    genetic_parser.add_argument('--population', type=int, default=50, help='Population size (default: 50)')
    genetic_parser.add_argument('--generations', type=int, default=20, help='Number of generations (default: 20)')
    genetic_parser.add_argument('--objective', choices=['profit_factor', 'total_pnl', 'sharpe', 'trades_per_year', 'roi', 'multi'], 
                               default='multi', help='Optimization objective (default: multi)')
    genetic_parser.add_argument('--ranges', choices=['default', 'narrow'], default='narrow', 
                               help='Parameter ranges (default: narrow)')
    genetic_parser.add_argument('--mutation_rate', type=float, default=0.2, help='Mutation rate (default: 0.2)')
    genetic_parser.add_argument('--crossover_rate', type=float, default=0.7, help='Crossover rate (default: 0.7)')
    genetic_parser.add_argument('--elitism_rate', type=float, default=0.1, help='Elitism rate (default: 0.1)')
    genetic_parser.add_argument('--min_trades', type=int, default=5, help='Minimum trades required (default: 5)')
    genetic_parser.add_argument('--save_best', action='store_true', help='Save best configuration')
    genetic_parser.add_argument('--save_history', action='store_true', help='Save evolution history')
    genetic_parser.add_argument('--output', help='Output filename for best config')
    genetic_parser.add_argument('--history_output', help='Output filename for history')
    genetic_parser.add_argument('--show_top', type=int, help='Show top N individuals')
    genetic_parser.set_defaults(func=cmd_genetic)
    
    # GRID command
    grid_parser = subparsers.add_parser('grid', help='Grid search optimization')
    grid_parser.add_argument('--csv', required=True, help='Path to OHLC CSV data')
    grid_parser.add_argument('--ranges', choices=['default', 'narrow'], default='narrow',
                            help='Parameter ranges (default: narrow)')
    grid_parser.add_argument('--min_trades', type=int, default=5, help='Minimum trades required (default: 5)')
    grid_parser.add_argument('--sort_by', default='profit_factor', 
                            help='Metric to sort by (default: profit_factor)')
    grid_parser.add_argument('--save_all', action='store_true', help='Save all results to CSV')
    grid_parser.add_argument('--save_best', action='store_true', help='Save best configuration')
    grid_parser.add_argument('--output', help='Output filename for all results')
    grid_parser.add_argument('--best_output', help='Output filename for best config')
    grid_parser.add_argument('--show_top', type=int, help='Show top N configurations')
    grid_parser.set_defaults(func=cmd_grid)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
