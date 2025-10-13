#!/usr/bin/env python3
"""Analisa checkpoint do daily trader optimizer"""

import pickle
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from genetic_optimizer import Individual
from config import StrategyConfig

def analyze_checkpoint(checkpoint_path: str):
    """Analisa checkpoint"""
    print(f"\n{'='*80}")
    print(f"📊 ANALYZING CHECKPOINT: {checkpoint_path}")
    print(f"{'='*80}\n")
    
    try:
        with open(checkpoint_path, 'rb') as f:
            ckpt = pickle.load(f)
        
        print(f"✅ Checkpoint loaded successfully!")
        print(f"\n📈 Progress:")
        print(f"   Generation: {ckpt['generation']}/{ckpt.get('total_generations', '?')}")
        print(f"   Population size: {len(ckpt['population'])}")
        
        # Sort population by fitness
        population = sorted(ckpt['population'], key=lambda x: x.fitness, reverse=True)
        
        print(f"\n🏆 Top 5 Individuals:")
        print(f"{'─'*80}")
        
        for i, individual in enumerate(population[:5], 1):
            metrics = individual.metrics if hasattr(individual, 'metrics') else {}
            
            print(f"\n{i}. Fitness: {individual.fitness:.2f}")
            
            if metrics:
                print(f"   Trades: {metrics.get('trades', 0)}")
                print(f"   Trades/Year: {metrics.get('trades_per_year', 0):.2f}")
                print(f"   Profit Factor: {metrics.get('profit_factor', 0):.2f}")
                print(f"   Win Rate: {metrics.get('win_rate', 0):.2%}")
                print(f"   Total PnL: ${metrics.get('total_pnl', 0):.2f}")
            
            # Show config
            config = individual.config
            print(f"   Config: variant={config.variant}, dist={config.dist_below_ma_pct:.2f}, "
                  f"tp={config.tp_pct:.2f}, sl={config.sl_pct:.2f}, ma={config.ma_len}, ts={config.time_stop}")
        
        # Statistics
        print(f"\n📊 Population Statistics:")
        print(f"{'─'*80}")
        
        fitness_values = [ind.fitness for ind in population if ind.fitness > -999999]
        if fitness_values:
            print(f"   Valid individuals: {len(fitness_values)}/{len(population)}")
            print(f"   Best fitness: {max(fitness_values):.2f}")
            print(f"   Avg fitness: {sum(fitness_values)/len(fitness_values):.2f}")
            print(f"   Worst fitness: {min(fitness_values):.2f}")
        else:
            print(f"   ⚠️ NO VALID INDIVIDUALS (all penalized for min_trades)")
        
        # Check trades
        trades_count = []
        for ind in population:
            if hasattr(ind, 'metrics') and ind.metrics:
                trades_count.append(ind.metrics.get('trades', 0))
        
        if trades_count:
            print(f"\n📈 Trades Distribution:")
            print(f"   Min trades: {min(trades_count)}")
            print(f"   Max trades: {max(trades_count)}")
            print(f"   Avg trades: {sum(trades_count)/len(trades_count):.1f}")
            print(f"   Zero trades: {trades_count.count(0)}/{len(trades_count)}")
        
        print(f"\n{'='*80}")
        
        if not fitness_values or max(fitness_values) <= 0:
            print("❌ PROBLEM: All individuals have 0 or negative fitness!")
            print("   This means NO trades were generated.")
            print("   Ranges are still too aggressive or there's a bug.")
        elif max([m.get('trades', 0) for ind in population for m in [ind.metrics] if hasattr(ind, 'metrics') and ind.metrics]) == 0:
            print("❌ PROBLEM: All individuals have 0 trades!")
            print("   The parameter ranges are not generating valid entry signals.")
        else:
            print("✅ SUCCESS: Some individuals generated trades!")
            best_trades = max([m.get('trades_per_year', 0) for ind in population for m in [ind.metrics] if hasattr(ind, 'metrics') and ind.metrics])
            print(f"   Best trades/year: {best_trades:.2f}")
            
            # Compare with goal
            goal = 365
            improvement = ((best_trades - 6.87) / 6.87) * 100
            print(f"   Goal: {goal} trades/year")
            print(f"   Improvement vs champion (6.87): +{improvement:.1f}%")
        
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error loading checkpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    checkpoint_path = 'checkpoints/daily_trader_checkpoint_20251013.pkl'
    analyze_checkpoint(checkpoint_path)
