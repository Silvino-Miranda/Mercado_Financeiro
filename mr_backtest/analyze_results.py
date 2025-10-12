#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid Search Results Analyzer
-----------------------------
Analyze and visualize backtest results from grid_results.csv

Features:
- Filter best results by multiple criteria
- Compare strategy variants performance
- Visualize parameter sensitivity
- Identify robust parameter ranges
- Generate reports with top configurations

Usage:
    python analyze_results.py --csv grid_results.csv
    python analyze_results.py --csv grid_results.csv --top 20
    python analyze_results.py --csv grid_results.csv --variant base --plot
"""

import argparse
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


def load_results(csv_path: str) -> pd.DataFrame:
    """Load grid search results"""
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df)} combinations from {csv_path}")
    return df


def basic_stats(df: pd.DataFrame) -> None:
    """Print basic statistics about results"""
    print("\n" + "=" * 70)
    print("BASIC STATISTICS")
    print("=" * 70)
    
    print(f"\nTotal combinations tested: {len(df)}")
    print(f"Variants tested: {df['variant'].unique().tolist()}")
    
    # Combinations with trades
    with_trades = df[df['trades'] > 0]
    print(f"\nCombinations with trades: {len(with_trades)} ({len(with_trades)/len(df)*100:.1f}%)")
    print(f"Combinations without trades: {len(df) - len(with_trades)}")
    
    if len(with_trades) > 0:
        print(f"\n--- Metrics Summary (only combinations with trades) ---")
        print(f"Profit Factor:")
        print(f"  Best: {with_trades['profit_factor'].max():.4f}")
        print(f"  Worst: {with_trades['profit_factor'].min():.4f}")
        print(f"  Average: {with_trades['profit_factor'].mean():.4f}")
        
        print(f"\nWin Rate:")
        print(f"  Best: {with_trades['win_rate'].max():.2%}")
        print(f"  Worst: {with_trades['win_rate'].min():.2%}")
        print(f"  Average: {with_trades['win_rate'].mean():.2%}")
        
        print(f"\nTotal PnL:")
        print(f"  Best: ${with_trades['total_pnl'].max():.2f}")
        print(f"  Worst: ${with_trades['total_pnl'].min():.2f}")
        print(f"  Average: ${with_trades['total_pnl'].mean():.2f}")
        
        print(f"\nMax Drawdown:")
        print(f"  Best (smallest): ${with_trades['max_drawdown'].max():.2f}")
        print(f"  Worst (largest): ${with_trades['max_drawdown'].min():.2f}")
        print(f"  Average: ${with_trades['max_drawdown'].mean():.2f}")


def variant_comparison(df: pd.DataFrame) -> None:
    """Compare performance by variant"""
    print("\n" + "=" * 70)
    print("VARIANT COMPARISON")
    print("=" * 70)
    
    # Filter only combinations with trades
    df_filtered = df[df['trades'] > 0].copy()
    
    if len(df_filtered) == 0:
        print("\nNo variants generated trades.")
        return
    
    for variant in df_filtered['variant'].unique():
        v_data = df_filtered[df_filtered['variant'] == variant]
        print(f"\n--- {variant.upper()} Strategy ---")
        print(f"Combinations tested: {len(v_data)}")
        print(f"Avg Profit Factor: {v_data['profit_factor'].mean():.4f}")
        print(f"Avg Win Rate: {v_data['win_rate'].mean():.2%}")
        print(f"Avg Total PnL: ${v_data['total_pnl'].mean():.2f}")
        print(f"Avg Max Drawdown: ${v_data['max_drawdown'].mean():.2f}")
        print(f"Avg Trades/Year: {v_data['trades_per_year'].mean():.2f}")
        
        # Best configuration for this variant
        best = v_data.nlargest(1, 'profit_factor').iloc[0]
        print(f"\nBest Config: PF={best['profit_factor']:.4f}, " +
              f"WinRate={best['win_rate']:.2%}, " +
              f"PnL=${best['total_pnl']:.2f}")


def top_configurations(df: pd.DataFrame, n: int = 10, min_trades: int = 5) -> pd.DataFrame:
    """Show top N configurations"""
    print("\n" + "=" * 70)
    print(f"TOP {n} CONFIGURATIONS (min {min_trades} trades)")
    print("=" * 70)
    
    # Filter combinations with minimum trades
    df_filtered = df[df['trades'] >= min_trades].copy()
    
    if len(df_filtered) == 0:
        print(f"\nNo configurations with at least {min_trades} trades.")
        return pd.DataFrame()
    
    # Sort by profit factor, then total PnL, then lower drawdown
    top = df_filtered.nlargest(n, 'profit_factor')
    
    # Display columns
    display_cols = ['variant', 'dist', 'tp', 'sl', 'atr_mult', 'time_stop', 'ma', 'breakeven',
                   'trades', 'win_rate', 'profit_factor', 'total_pnl', 'max_drawdown', 
                   'expectancy_per_trade', 'sharpe_like']
    
    print()
    for idx, row in enumerate(top.itertuples(), 1):
        print(f"\n#{idx} - Variant: {row.variant} | PF: {row.profit_factor:.4f} | PnL: ${row.total_pnl:.2f}")
        print(f"    Params: dist={row.dist:.2f}, tp={row.tp:.2f}, sl={row.sl:.2f}, " +
              f"atr={row.atr_mult:.1f}, ts={row.time_stop}, ma={row.ma}, be={row.breakeven}")
        print(f"    Metrics: Trades={int(row.trades)}, WinRate={row.win_rate:.2%}, " +
              f"Expectancy=${row.expectancy_per_trade:.2f}, MaxDD=${row.max_drawdown:.2f}")
    
    return top


def parameter_sensitivity(df: pd.DataFrame) -> None:
    """Analyze parameter sensitivity"""
    print("\n" + "=" * 70)
    print("PARAMETER SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    df_filtered = df[df['trades'] > 0].copy()
    
    if len(df_filtered) == 0:
        print("\nNo data to analyze.")
        return
    
    params = ['dist', 'tp', 'sl', 'atr_mult', 'time_stop', 'ma']
    
    for param in params:
        print(f"\n--- {param.upper()} ---")
        grouped = df_filtered.groupby(param).agg({
            'profit_factor': ['mean', 'std', 'max'],
            'total_pnl': 'mean',
            'win_rate': 'mean',
            'trades': 'count'
        }).round(4)
        print(grouped.to_string())


def robust_configurations(df: pd.DataFrame, pf_threshold: float = 1.5, 
                         min_trades: int = 10, top_n: int = 10) -> pd.DataFrame:
    """Find robust configurations across multiple criteria"""
    print("\n" + "=" * 70)
    print(f"ROBUST CONFIGURATIONS")
    print(f"Criteria: PF >= {pf_threshold}, Trades >= {min_trades}, Positive PnL")
    print("=" * 70)
    
    robust = df[
        (df['profit_factor'] >= pf_threshold) &
        (df['trades'] >= min_trades) &
        (df['total_pnl'] > 0) &
        (df['win_rate'] > 0.4)  # At least 40% win rate
    ].copy()
    
    if len(robust) == 0:
        print("\nNo configurations meet the robustness criteria.")
        return pd.DataFrame()
    
    print(f"\n{len(robust)} configurations meet the criteria")
    
    # Create a composite score
    robust['composite_score'] = (
        robust['profit_factor'] * 0.4 +
        robust['win_rate'] * 100 * 0.2 +
        (robust['total_pnl'] / robust['total_pnl'].max()) * 50 * 0.2 +
        (1 - robust['max_drawdown'] / robust['max_drawdown'].min()) * 20 * 0.2
    )
    
    top_robust = robust.nlargest(top_n, 'composite_score')
    
    print(f"\nTop {min(top_n, len(top_robust))} Robust Configurations:")
    for idx, row in enumerate(top_robust.itertuples(), 1):
        print(f"\n#{idx} - {row.variant.upper()} | Score: {row.composite_score:.2f}")
        print(f"    PF: {row.profit_factor:.4f}, WinRate: {row.win_rate:.2%}, PnL: ${row.total_pnl:.2f}")
        print(f"    Params: dist={row.dist}, tp={row.tp}, sl={row.sl}, ts={row.time_stop}, ma={row.ma}")
    
    return top_robust


def save_filtered_results(df: pd.DataFrame, output_path: str, 
                          pf_min: float = 1.0, trades_min: int = 5) -> None:
    """Save filtered results to CSV"""
    filtered = df[
        (df['profit_factor'] >= pf_min) &
        (df['trades'] >= trades_min)
    ].copy()
    
    filtered = filtered.sort_values('profit_factor', ascending=False)
    filtered.to_csv(output_path, index=False)
    print(f"\n✓ Saved {len(filtered)} filtered results to: {output_path}")


def plot_results(df: pd.DataFrame) -> None:
    """Create visualizations of results"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_style("whitegrid")
    except ImportError:
        print("\n⚠ Matplotlib/Seaborn not installed. Skipping plots.")
        print("  Install with: pip install matplotlib seaborn")
        return
    
    df_filtered = df[df['trades'] > 0].copy()
    
    if len(df_filtered) == 0:
        print("\nNo data to plot.")
        return
    
    print("\n" + "=" * 70)
    print("GENERATING PLOTS")
    print("=" * 70)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Grid Search Results Analysis', fontsize=16, fontweight='bold')
    
    # 1. Profit Factor vs Total PnL
    ax1 = axes[0, 0]
    for variant in df_filtered['variant'].unique():
        v_data = df_filtered[df_filtered['variant'] == variant]
        ax1.scatter(v_data['profit_factor'], v_data['total_pnl'], 
                   label=variant, alpha=0.6, s=50)
    ax1.set_xlabel('Profit Factor')
    ax1.set_ylabel('Total PnL ($)')
    ax1.set_title('Profit Factor vs Total PnL')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Win Rate Distribution
    ax2 = axes[0, 1]
    df_filtered.boxplot(column='win_rate', by='variant', ax=ax2)
    ax2.set_xlabel('Variant')
    ax2.set_ylabel('Win Rate')
    ax2.set_title('Win Rate Distribution by Variant')
    plt.sca(ax2)
    plt.xticks(rotation=0)
    
    # 3. Profit Factor vs Max Drawdown
    ax3 = axes[1, 0]
    scatter = ax3.scatter(df_filtered['max_drawdown'], df_filtered['profit_factor'],
                         c=df_filtered['win_rate'], cmap='RdYlGn', alpha=0.6, s=50)
    ax3.set_xlabel('Max Drawdown ($)')
    ax3.set_ylabel('Profit Factor')
    ax3.set_title('Profit Factor vs Max Drawdown (colored by Win Rate)')
    plt.colorbar(scatter, ax=ax3, label='Win Rate')
    ax3.grid(True, alpha=0.3)
    
    # 4. Trade Count Distribution
    ax4 = axes[1, 1]
    df_filtered['trades'].hist(bins=30, ax=ax4, edgecolor='black', alpha=0.7)
    ax4.set_xlabel('Number of Trades')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Trade Count Distribution')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = 'grid_results_analysis.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved plot to: {plot_path}")
    print("  Opening plot...")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Analyze grid search results')
    parser.add_argument('--csv', default='grid_results.csv', help='Path to grid_results.csv')
    parser.add_argument('--top', type=int, default=10, help='Number of top results to show')
    parser.add_argument('--min-trades', type=int, default=5, help='Minimum trades for filtering')
    parser.add_argument('--variant', help='Filter by specific variant (base, rsi, reclaim)')
    parser.add_argument('--plot', action='store_true', help='Generate visualization plots')
    parser.add_argument('--save-filtered', help='Save filtered results to CSV')
    parser.add_argument('--pf-min', type=float, default=1.0, help='Minimum profit factor for filtering')
    args = parser.parse_args()
    
    # Load results
    try:
        df = load_results(args.csv)
    except FileNotFoundError:
        print(f"❌ Error: File '{args.csv}' not found.")
        print("   Make sure the grid search has completed and generated the results file.")
        return
    
    # Filter by variant if specified
    if args.variant:
        df = df[df['variant'] == args.variant].copy()
        print(f"Filtered to variant: {args.variant} ({len(df)} combinations)")
    
    # Run analyses
    basic_stats(df)
    variant_comparison(df)
    top_configurations(df, n=args.top, min_trades=args.min_trades)
    parameter_sensitivity(df)
    robust_configurations(df, min_trades=args.min_trades)
    
    # Save filtered results if requested
    if args.save_filtered:
        save_filtered_results(df, args.save_filtered, pf_min=args.pf_min, 
                            trades_min=args.min_trades)
    
    # Generate plots if requested
    if args.plot:
        plot_results(df)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
