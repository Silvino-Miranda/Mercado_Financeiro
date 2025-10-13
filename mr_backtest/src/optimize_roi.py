#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimize Trading Strategy for Maximum ROI
------------------------------------------
Uses Genetic Algorithm to optimize all strategy parameters to maximize:
- ROI (Return on Investment)
- Trades per year (more trading opportunities)
- Profit Factor (quality of trades)

This script runs multiple optimization phases:
1. Exploration: Wide parameter ranges, large population
2. Refinement: Narrow ranges around best results
3. Validation: Test best config on full dataset

Usage:
    # Quick test (10 minutes)
    python optimize_roi.py --quick
    
    # Full optimization (1-2 hours)
    python optimize_roi.py --full
    
    # Custom parameters
    python optimize_roi.py --population 100 --generations 50 --objective multi
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Updated imports - using new modular structure
from src.optimization import GeneticOptimizer, OptimizationObjective
from src.config import (
    StrategyConfig, save_params_to_csv, create_default_ranges, 
    create_narrow_ranges, ParamRange
)
from src.backtest import BacktestEngine
from src.backtest.utils import load_ohlc_csv, calculate_metrics


# Compatibility functions to match old API
def backtest(df, params):
    """Compatibility wrapper for old API"""
    engine = BacktestEngine(params)
    result = engine.run(df)
    return result.trades, result.equity_curve


def analyze(trades, equity_curve, df):
    """Compatibility wrapper for old API"""
    return calculate_metrics(trades, equity_curve, df)


def create_roi_focused_ranges() -> dict:
    """
    Create parameter ranges focused on maximizing ROI:
    - More aggressive TP/SL for better risk/reward
    - Wider dist_below_ma to catch more opportunities
    - Shorter time_stop for faster capital rotation
    """
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=0,
            values=['base'],  # BASE is best from grid search
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=180, max_val=230,
            step=5,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.03, max_val=0.12,  # Wider range for more trades
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.08, max_val=0.20,  # Higher TP for better ROI
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.05, max_val=0.12,
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.5, max_val=2.5,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=15, max_val=45,  # Shorter for capital rotation
            step=5,
            param_type='int'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=1,
            values=[False],  # False is better from grid search
            param_type='bool'
        ),
    }


def print_optimization_header(objective: str, population: int, generations: int):
    """Print optimization header"""
    print("\n" + "=" * 80)
    print("🧬 GENETIC ALGORITHM - ROI OPTIMIZATION")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Objective: {objective}")
    print(f"   Population: {population}")
    print(f"   Generations: {generations}")
    print(f"   Estimated time: ~{population * generations * 0.15:.1f} seconds")
    print("\n🎯 Optimization Goals:")
    print("   1. Maximize ROI (PnL / Max Drawdown)")
    print("   2. Increase trades/year (more opportunities)")
    print("   3. Maintain high profit factor (>1.5)")
    print("\n" + "=" * 80 + "\n")


def run_optimization_phase(
    phase_name: str,
    csv_path: str,
    population: int,
    generations: int,
    objective: OptimizationObjective,
    param_ranges: dict,
    min_trades: int = 10
):
    """Run one optimization phase"""
    print(f"\n{'─' * 80}")
    print(f"🔬 PHASE: {phase_name}")
    print(f"{'─' * 80}\n")
    
    optimizer = GeneticOptimizer(
        csv_data_path=csv_path,
        population_size=population,
        generations=generations,
        objective=objective,
        param_ranges=param_ranges,
        mutation_rate=0.25,  # Higher mutation for exploration
        crossover_rate=0.7,
        elitism_rate=0.15,  # Keep top 15%
        min_trades=min_trades
    )
    
    best_config = optimizer.run()
    
    # Save results
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save best config
    config_name = f"optimized_{phase_name.lower().replace(' ', '_')}_{timestamp}.csv"
    save_params_to_csv(best_config, config_name)
    print(f"\n✅ Saved best config to: config/{config_name}")
    
    # Save history
    history_name = f"optimization_history_{phase_name.lower().replace(' ', '_')}_{timestamp}.csv"
    optimizer.save_history(history_name)
    print(f"✅ Saved evolution history to: report/{history_name}")
    
    # Print top 5 results
    print(f"\n{'─' * 80}")
    print(f"🏆 TOP 5 CONFIGURATIONS FROM {phase_name}")
    print(f"{'─' * 80}\n")
    
    top5 = optimizer.get_top_n(5)
    for i, ind in enumerate(top5, 1):
        m = ind.metrics
        c = ind.config
        roi = m['total_pnl'] / abs(m['max_drawdown']) if m['max_drawdown'] != 0 else 0
        
        print(f"#{i} - Fitness: {ind.fitness:.2f}")
        print(f"   ROI: {roi:.2f} | Trades/Year: {m['trades_per_year']:.1f} | PF: {m['profit_factor']:.2f}")
        print(f"   PnL: ${m['total_pnl']:.2f} | WR: {m['win_rate']:.1%} | DD: ${m['max_drawdown']:.2f}")
        print(f"   Params: MA={c.ma_len}, dist={c.dist_below_ma_pct:.2f}, TP={c.tp_pct:.2f}, SL={c.sl_pct:.2f}")
        print()
    
    return best_config, optimizer


def validate_config(config: StrategyConfig, csv_path: str):
    """Validate configuration on full dataset"""
    print(f"\n{'─' * 80}")
    print("🔍 VALIDATION - Full Dataset Backtest")
    print(f"{'─' * 80}\n")
    
    df = load_ohlc_csv(csv_path)
    params = config.to_params()
    trades, ec = backtest(df, params)
    metrics = analyze(trades, ec, df)
    
    roi = metrics['total_pnl'] / abs(metrics['max_drawdown']) if metrics['max_drawdown'] != 0 else 0
    
    print("📊 Final Metrics:")
    print(f"   Trades: {metrics['trades']}")
    print(f"   Trades/Year: {metrics['trades_per_year']:.2f}")
    print(f"   Win Rate: {metrics['win_rate']:.2%}")
    print(f"   Profit Factor: {metrics['profit_factor']:.4f}")
    print(f"   Total PnL: ${metrics['total_pnl']:.2f}")
    print(f"   Max Drawdown: ${metrics['max_drawdown']:.2f}")
    print(f"   ROI: {roi:.2f}")
    print(f"   Sharpe-like: {metrics['sharpe_like']:.4f}")
    print(f"   Time in Market: {metrics['time_in_market']:.2%}")
    print(f"\n   Avg Win: ${metrics['avg_win']:.2f}")
    print(f"   Avg Loss: ${metrics['avg_loss']:.2f}")
    print(f"   Expectancy: ${metrics['expectancy_per_trade']:.2f}")
    
    return metrics


def compare_with_champion(optimized_metrics: dict):
    """Compare optimized results with champion from grid search"""
    print(f"\n{'=' * 80}")
    print("📈 COMPARISON: Optimized vs Champion (Grid Search)")
    print(f"{'=' * 80}\n")
    
    # Champion metrics from grid search
    champion = {
        'trades': 22,
        'trades_per_year': 6.87,
        'win_rate': 0.7273,
        'profit_factor': 2.6318,
        'total_pnl': 3589.97,
        'max_drawdown': -498.88,
        'roi': 7.20
    }
    
    opt_roi = optimized_metrics['total_pnl'] / abs(optimized_metrics['max_drawdown']) \
        if optimized_metrics['max_drawdown'] != 0 else 0
    
    print(f"{'Metric':<20} {'Champion':<20} {'Optimized':<20} {'Improvement':<20}")
    print("─" * 80)
    
    metrics_to_compare = [
        ('Trades/Year', champion['trades_per_year'], optimized_metrics['trades_per_year']),
        ('Profit Factor', champion['profit_factor'], optimized_metrics['profit_factor']),
        ('Win Rate', champion['win_rate'] * 100, optimized_metrics['win_rate'] * 100),
        ('Total PnL', champion['total_pnl'], optimized_metrics['total_pnl']),
        ('Max Drawdown', champion['max_drawdown'], optimized_metrics['max_drawdown']),
        ('ROI', champion['roi'], opt_roi),
    ]
    
    for name, champ_val, opt_val in metrics_to_compare:
        if 'Drawdown' in name:
            improvement = ((opt_val - champ_val) / champ_val * 100) if champ_val != 0 else 0
            improvement_str = f"{improvement:+.1f}% {'✅' if improvement > 0 else '❌'}"
        else:
            improvement = ((opt_val - champ_val) / champ_val * 100) if champ_val != 0 else 0
            improvement_str = f"{improvement:+.1f}% {'✅' if improvement > 0 else '❌'}"
        
        if 'Rate' in name or 'Win' in name:
            print(f"{name:<20} {champ_val:<19.2f}% {opt_val:<19.2f}% {improvement_str}")
        else:
            print(f"{name:<20} {champ_val:<20.2f} {opt_val:<20.2f} {improvement_str}")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description='Optimize trading strategy for maximum ROI')
    parser.add_argument('--csv', default='BTCUSDT_daily.csv', help='CSV data file')
    parser.add_argument('--quick', action='store_true', help='Quick test (20 pop, 10 gen)')
    parser.add_argument('--full', action='store_true', help='Full optimization (80 pop, 40 gen)')
    parser.add_argument('--population', type=int, default=50, help='Population size')
    parser.add_argument('--generations', type=int, default=30, help='Number of generations')
    parser.add_argument('--objective', choices=['multi', 'roi', 'trades_per_year', 'profit_factor'],
                       default='multi', help='Optimization objective')
    parser.add_argument('--min-trades', type=int, default=10, help='Minimum trades required')
    args = parser.parse_args()
    
    # Resolve data path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_root, "data", args.csv)
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Data file not found: {csv_path}")
        print("   Please download data first: python src/download_btc_csv.py")
        return
    
    # Determine configuration
    if args.quick:
        population, generations = 20, 10
        print("\n🚀 QUICK TEST MODE")
    elif args.full:
        population, generations = 80, 40
        print("\n🔥 FULL OPTIMIZATION MODE")
    else:
        population, generations = args.population, args.generations
        print("\n⚙️ CUSTOM OPTIMIZATION MODE")
    
    # Map objective string to enum
    objective_map = {
        'multi': OptimizationObjective.MULTI,
        'roi': OptimizationObjective.ROI,
        'trades_per_year': OptimizationObjective.TRADES_PER_YEAR,
        'profit_factor': OptimizationObjective.PROFIT_FACTOR
    }
    objective = objective_map[args.objective]
    
    print_optimization_header(args.objective.upper(), population, generations)
    
    # Phase 1: Exploration with wide ranges
    print("\n🌍 Starting optimization with ROI-focused ranges...")
    best_config, optimizer = run_optimization_phase(
        phase_name="ROI_Optimization",
        csv_path=csv_path,
        population=population,
        generations=generations,
        objective=objective,
        param_ranges=create_roi_focused_ranges(),
        min_trades=args.min_trades
    )
    
    # Validate best configuration
    metrics = validate_config(best_config, csv_path)
    
    # Compare with champion
    compare_with_champion(metrics)
    
    # Save final best config with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_name = f"best_roi_config_{timestamp}.csv"
    save_params_to_csv(best_config, final_name)
    
    print(f"\n{'=' * 80}")
    print("✅ OPTIMIZATION COMPLETE!")
    print(f"{'=' * 80}")
    print(f"\n📁 Final best configuration saved to: config/{final_name}")
    print("\n🚀 Next steps:")
    print("   1. Review optimized parameters in config/ folder")
    print("   2. Backtest with: python src/mr_backtest.py --config " + final_name)
    print("   3. Compare with champion: python report/analyze_results.py")
    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    main()
