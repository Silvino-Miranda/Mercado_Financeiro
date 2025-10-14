#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest Module CLI
-------------------
Command-line interface for running backtests.

Usage:
    python -m src.backtest --csv data/BTCUSDT_daily.csv --variant base
    python -m src.backtest --csv data/BTCUSDT_daily.csv --grid
    python -m src.backtest --config config/best_params.csv
"""

import argparse
import os
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .types import Params
from .engine import BacktestEngine
from .utils import load_ohlc_csv


def get_project_root() -> Path:
    """Get the project root directory (parent of src/)."""
    return Path(__file__).parent.parent.parent


def print_summary(result, show_trades: bool = False):
    """Print backtest summary."""
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    
    print("\nStrategy Parameters:")
    print("-" * 60)
    for k, v in asdict(result.params).items():
        print(f"  {k:20s}: {v}")
    
    print("\nPerformance Metrics:")
    print("-" * 60)
    for k, v in result.metrics.items():
        if isinstance(v, float):
            if k in ['win_rate', 'time_in_market']:
                print(f"  {k:20s}: {v:>8.2%}")
            elif k == 'total_pnl':
                print(f"  {k:20s}: ${v:>10.2f}")
            else:
                print(f"  {k:20s}: {v:>10.4f}")
        else:
            print(f"  {k:20s}: {v:>10}")
    
    if show_trades and result.trades:
        print("\nRecent Trades (last 10):")
        print("-" * 60)
        for trade in result.trades[-10:]:
            print(f"  {trade.entry_date.date()} → {trade.exit_date.date()}: "
                  f"${trade.pnl:>8.2f} ({trade.pnl_pct:>6.2%}) [{trade.reason}]")
    
    print("=" * 60 + "\n")


def run_single_backtest(args):
    """Run a single backtest with specified parameters."""
    # Load data
    df = load_ohlc_csv(args.csv)
    print(f"Loaded {len(df)} bars from {args.csv}")
    
    # Create parameters
    if args.config:
        # Load from config file
        try:
            from ..config import load_params_from_csv
            config = load_params_from_csv(args.config)
            params = config.to_params()
            print(f"Loaded parameters from: {args.config}")
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    else:
        # Use command-line arguments
        params = Params(
            variant=args.variant,
            capital_per_trade=args.capital_per_trade,
            fees_bps=args.fees_bps,
            slip_bps=args.slip_bps,
            tp_pct=args.tp_pct,
            sl_pct=args.sl_pct,
            atr_mult=args.atr_mult,
            time_stop=args.time_stop,
            be_trigger_pct=args.be_trigger_pct,
            ma_len=args.ma_len,
            dist_below_ma_pct=args.dist_below_ma_pct,
            allow_breakeven=(not args.no_breakeven)
        )
    
    # Run backtest
    print(f"\nRunning backtest with {params.variant} strategy...")
    engine = BacktestEngine(params)
    result = engine.run(df)
    
    # Print results
    print_summary(result, show_trades=True)
    
    # Save trades to CSV
    if result.trades:
        project_root = get_project_root()
        output_dir = project_root / "data"
        output_dir.mkdir(exist_ok=True)
        
        trades_path = output_dir / "trades.csv"
        trades_df = pd.DataFrame([{
            "entry_date": t.entry_date,
            "exit_date": t.exit_date,
            "entry_px": t.entry_px,
            "exit_px": t.exit_px,
            "shares": t.shares,
            "pnl": t.pnl,
            "pnl_pct": t.pnl_pct,
            "reason": t.reason,
            "bars_held": t.bars_held
        } for t in result.trades])
        trades_df.to_csv(trades_path, index=False)
        print(f"Saved {len(result.trades)} trades to: {trades_path}")


def run_grid_search(args):
    """Run grid search over parameter combinations."""
    try:
        from tqdm import tqdm
    except ImportError:
        print("Warning: tqdm not installed. Install with 'pip install tqdm' for progress bar.")
        tqdm = None
    
    # Load data
    df = load_ohlc_csv(args.csv)
    print(f"Loaded {len(df)} bars from {args.csv}")
    
    # Define grid parameters
    variants = ["base", "rsi", "reclaim"]
    dist_list = [0.03, 0.05, 0.07, 0.10]
    tp_list = [0.08, 0.10, 0.12]
    sl_list = [0.06, 0.08, 0.10]
    atr_mult_list = [1.5, 2.0]
    time_stop_list = [20, 30, 45]
    ma_list = [180, 200, 220]
    be_list = [True, False]
    
    total = (len(variants) * len(dist_list) * len(tp_list) * len(sl_list) * 
             len(atr_mult_list) * len(time_stop_list) * len(ma_list) * len(be_list))
    
    print(f"\nGrid Search Configuration:")
    print(f"  Total combinations: {total}")
    print(f"  Estimated time: ~{total * 0.1:.1f} seconds")
    print("\nRunning grid search...\n")
    
    pbar = tqdm(total=total, desc="Grid Search", unit="run") if tqdm else None
    
    rows = []
    for variant in variants:
        for dist in dist_list:
            for tp in tp_list:
                for sl in sl_list:
                    for atrm in atr_mult_list:
                        for ts in time_stop_list:
                            for ma in ma_list:
                                for be in be_list:
                                    params = Params(
                                        variant=variant,
                                        dist_below_ma_pct=dist,
                                        tp_pct=tp,
                                        sl_pct=sl,
                                        atr_mult=atrm,
                                        time_stop=ts,
                                        ma_len=ma,
                                        allow_breakeven=be
                                    )
                                    
                                    engine = BacktestEngine(params)
                                    result = engine.run(df)
                                    
                                    row = {
                                        "variant": variant,
                                        "dist": dist,
                                        "tp": tp,
                                        "sl": sl,
                                        "atr_mult": atrm,
                                        "time_stop": ts,
                                        "ma": ma,
                                        "breakeven": be,
                                        **result.metrics
                                    }
                                    rows.append(row)
                                    
                                    if pbar:
                                        pbar.update(1)
    
    if pbar:
        pbar.close()
    
    # Create results DataFrame
    results_df = pd.DataFrame(rows)
    results_df = results_df.sort_values(
        by=["profit_factor", "total_pnl", "max_drawdown"], 
        ascending=[False, False, True]
    )
    
    # Save results
    project_root = get_project_root()
    output_dir = project_root / "data"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "grid_results.csv"
    results_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Grid search complete!")
    print(f"Saved results to: {output_path}")
    print("\nTop 10 Results:")
    print("=" * 120)
    
    display_cols = ["variant", "dist", "tp", "sl", "trades", "win_rate", "profit_factor", "total_pnl"]
    print(results_df[display_cols].head(10).to_string(index=False))
    print("=" * 120)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mean-Reversion Backtesting Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single backtest with base strategy
  python -m src.backtest --csv data/BTCUSDT_daily.csv --variant base
  
  # Run with custom parameters
  python -m src.backtest --csv data/BTCUSDT_daily.csv --variant rsi \\
      --tp_pct 0.12 --sl_pct 0.08 --dist_below_ma_pct 0.07
  
  # Run grid search
  python -m src.backtest --csv data/BTCUSDT_daily.csv --grid
  
  # Load parameters from config file
  python -m src.backtest --csv data/BTCUSDT_daily.csv --config config/best_params.csv
        """
    )
    
    # Data input
    parser.add_argument(
        "--csv",
        help="Path to daily OHLC CSV (default: data/BTCUSDT_daily.csv)",
        default=None
    )
    
    # Mode selection
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Run grid search over parameter combinations"
    )
    
    parser.add_argument(
        "--config",
        help="Path to config CSV file (loads params from config/)"
    )
    
    # Strategy parameters
    parser.add_argument(
        "--variant",
        choices=["base", "rsi", "reclaim"],
        default="base",
        help="Strategy variant (default: base)"
    )
    
    parser.add_argument(
        "--capital_per_trade",
        type=float,
        default=1000.0,
        help="Capital per trade (default: 1000.0)"
    )
    
    parser.add_argument(
        "--fees_bps",
        type=float,
        default=10.0,
        help="Trading fees in basis points per side (default: 10.0)"
    )
    
    parser.add_argument(
        "--slip_bps",
        type=float,
        default=5.0,
        help="Slippage in basis points per side (default: 5.0)"
    )
    
    parser.add_argument(
        "--tp_pct",
        type=float,
        default=0.10,
        help="Take profit percentage (default: 0.10)"
    )
    
    parser.add_argument(
        "--sl_pct",
        type=float,
        default=0.08,
        help="Stop loss percentage (default: 0.08)"
    )
    
    parser.add_argument(
        "--atr_mult",
        type=float,
        default=2.0,
        help="ATR multiplier for stop distance (default: 2.0)"
    )
    
    parser.add_argument(
        "--time_stop",
        type=int,
        default=30,
        help="Maximum bars to hold position (default: 30)"
    )
    
    parser.add_argument(
        "--be_trigger_pct",
        type=float,
        default=0.06,
        help="Breakeven trigger percentage (default: 0.06)"
    )
    
    parser.add_argument(
        "--ma_len",
        type=int,
        default=200,
        help="Moving average period (default: 200)"
    )
    
    parser.add_argument(
        "--dist_below_ma_pct",
        type=float,
        default=0.05,
        help="Distance below MA for entry (default: 0.05)"
    )
    
    parser.add_argument(
        "--no_breakeven",
        action="store_true",
        help="Disable breakeven stop adjustment"
    )
    
    args = parser.parse_args()
    
    # Determine CSV path
    if not args.csv:
        project_root = get_project_root()
        args.csv = str(project_root / "data" / "BTCUSDT_daily.csv")
    
    # Check if CSV exists
    if not os.path.exists(args.csv):
        print(f"Error: CSV file not found: {args.csv}")
        sys.exit(1)
    
    # Run appropriate mode
    if args.grid:
        run_grid_search(args)
    else:
        run_single_backtest(args)


if __name__ == "__main__":
    main()
