#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Module CLI
-------------------
Command-line interface for analyzing backtest results and checkpoints.

Usage:
    python -m src.analysis checkpoint --file checkpoints/checkpoint.pkl
    python -m src.analysis results --csv data/grid_results.csv --top 20
    python -m src.analysis compare --files config1.csv config2.csv
"""

import argparse
import sys
from pathlib import Path

from .checkpoint import CheckpointAnalyzer
from .results import ResultsAnalyzer
from .utils import load_checkpoint, load_grid_results, save_top_configs_to_csv


def cmd_checkpoint(args):
    """Analyze genetic algorithm checkpoint."""
    try:
        # Load checkpoint
        checkpoint = load_checkpoint(args.file)
        
        # Create analyzer
        analyzer = CheckpointAnalyzer(checkpoint)
        
        # Print summary
        analyzer.print_summary()
        
        # Save analysis if requested
        if args.save:
            analysis = analyzer.analyze()
            output_path = args.output or "report/checkpoint_analysis.pkl"
            
            from .utils import save_analysis
            save_analysis(analysis, output_path)
            print(f"\n✓ Analysis saved to: {output_path}")
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error analyzing checkpoint: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_results(args):
    """Analyze grid search or optimization results."""
    try:
        # Load results
        df = load_grid_results(args.csv)
        print(f"✓ Loaded {len(df)} configurations from {args.csv}\n")
        
        # Filter by variant if specified
        if args.variant:
            df = df[df['variant'] == args.variant].copy()
            print(f"✓ Filtered to variant: {args.variant} ({len(df)} configs)\n")
        
        # Create analyzer
        analyzer = ResultsAnalyzer(df)
        
        # Print summary
        analyzer.print_summary(top_n=args.top, min_trades=args.min_trades)
        
        # Detailed analysis if requested
        if args.detailed:
            analysis = analyzer.analyze(
                top_n=args.top,
                min_trades=args.min_trades,
                pf_threshold=args.pf_threshold,
                min_win_rate=args.min_wr
            )
            
            # Print parameter sensitivity
            if analysis.parameter_sensitivity:
                print("\n" + "=" * 80)
                print("📊 PARAMETER SENSITIVITY")
                print("=" * 80)
                
                for param, stats in analysis.parameter_sensitivity.items():
                    print(f"\n{param.upper()}:")
                    if 'pf_mean_by_value' in stats:
                        for value, pf_mean in sorted(stats['pf_mean_by_value'].items()):
                            count = stats['count_by_value'].get(value, 0)
                            print(f"  {value}: PF={pf_mean:.4f} (n={count})")
        
        # Show robust configurations if requested
        if args.robust:
            print("\n" + "=" * 80)
            print(f"🛡️ ROBUST CONFIGURATIONS")
            print(f"   Criteria: PF>={args.pf_threshold}, Trades>={args.min_trades}, WR>={args.min_wr}")
            print("=" * 80)
            
            robust_configs = analyzer.get_robust_configs(
                pf_threshold=args.pf_threshold,
                min_trades=args.min_trades,
                min_win_rate=args.min_wr,
                top_n=args.top
            )
            
            if not robust_configs:
                print("\n⚠️ No configurations meet the robustness criteria")
            else:
                print(f"\n✓ Found {len(robust_configs)} robust configurations\n")
                for i, config in enumerate(robust_configs, 1):
                    print(f"{i}. {config.get('variant', 'N/A').upper()} | "
                          f"PF={config['profit_factor']:.4f}, "
                          f"Score={config['composite_score']:.2f}")
        
        # Save filtered results if requested
        if args.save_filtered:
            output_path = args.output or "data/filtered_results.csv"
            count = analyzer.save_filtered(
                output_path,
                pf_min=args.pf_threshold,
                trades_min=args.min_trades
            )
            print(f"\n✓ Saved {count} filtered configurations to: {output_path}")
        
        # Save top configs if requested
        if args.save_top:
            output_path = args.output or "config/top_configs.csv"
            top_configs = analyzer.get_top_configs(n=args.top, min_trades=args.min_trades)
            save_top_configs_to_csv(top_configs, output_path)
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure the results file exists and path is correct")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error analyzing results: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_compare(args):
    """Compare multiple configuration files."""
    import pandas as pd
    
    print("\n" + "=" * 80)
    print("🔍 CONFIGURATION COMPARISON")
    print("=" * 80)
    
    try:
        # Load all configurations
        all_results = []
        for file_path in args.files:
            df = load_grid_results(file_path)
            df['source_file'] = Path(file_path).name
            all_results.append(df)
            print(f"✓ Loaded {len(df)} configs from {Path(file_path).name}")
        
        # Combine
        combined_df = pd.concat(all_results, ignore_index=True)
        print(f"\n✓ Total: {len(combined_df)} configurations")
        
        # Analyze combined
        analyzer = ResultsAnalyzer(combined_df)
        analyzer.print_summary(top_n=args.top, min_trades=args.min_trades)
        
        # Show best from each file
        print("\n" + "=" * 80)
        print("🏆 BEST FROM EACH FILE")
        print("=" * 80)
        
        for file_path in args.files:
            file_name = Path(file_path).name
            file_df = combined_df[combined_df['source_file'] == file_name]
            
            if len(file_df) == 0:
                continue
            
            valid = file_df[file_df['trades'] >= args.min_trades]
            if len(valid) == 0:
                print(f"\n{file_name}: No valid configurations")
                continue
            
            best = valid.nlargest(1, 'profit_factor').iloc[0]
            print(f"\n{file_name}:")
            print(f"  Best PF: {best['profit_factor']:.4f}")
            print(f"  Win Rate: {best['win_rate']:.2%}")
            print(f"  Total PnL: ${best['total_pnl']:.2f}")
            print(f"  Trades: {int(best['trades'])}")
        
        print("\n" + "=" * 80)
    
    except Exception as e:
        print(f"❌ Error comparing configurations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analysis tools for backtest results and checkpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze checkpoint
  python -m src.analysis checkpoint --file checkpoints/daily_checkpoint.pkl
  
  # Analyze results with top 20 configs
  python -m src.analysis results --csv data/grid_results.csv --top 20
  
  # Show robust configurations
  python -m src.analysis results --csv data/grid_results.csv --robust --pf-threshold 1.8
  
  # Detailed analysis with parameter sensitivity
  python -m src.analysis results --csv data/grid_results.csv --detailed
  
  # Compare multiple result files
  python -m src.analysis compare --files data/results1.csv data/results2.csv --top 10
  
  # Save filtered results
  python -m src.analysis results --csv data/grid_results.csv --save-filtered --output data/best.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Analysis command')
    
    # CHECKPOINT command
    checkpoint_parser = subparsers.add_parser('checkpoint', help='Analyze GA checkpoint')
    checkpoint_parser.add_argument('--file', required=True, help='Path to checkpoint file (.pkl)')
    checkpoint_parser.add_argument('--save', action='store_true', help='Save analysis to file')
    checkpoint_parser.add_argument('--output', help='Output path for analysis')
    checkpoint_parser.set_defaults(func=cmd_checkpoint)
    
    # RESULTS command
    results_parser = subparsers.add_parser('results', help='Analyze grid search / optimization results')
    results_parser.add_argument('--csv', required=True, help='Path to results CSV file')
    results_parser.add_argument('--top', type=int, default=10, help='Number of top configs to show (default: 10)')
    results_parser.add_argument('--min-trades', type=int, default=5, help='Minimum trades for filtering (default: 5)')
    results_parser.add_argument('--variant', help='Filter by specific variant')
    results_parser.add_argument('--detailed', action='store_true', help='Show detailed analysis with parameter sensitivity')
    results_parser.add_argument('--robust', action='store_true', help='Show robust configurations')
    results_parser.add_argument('--pf-threshold', type=float, default=1.5, help='Minimum profit factor for robust filter (default: 1.5)')
    results_parser.add_argument('--min-wr', type=float, default=0.4, help='Minimum win rate for robust filter (default: 0.4)')
    results_parser.add_argument('--save-filtered', action='store_true', help='Save filtered results to CSV')
    results_parser.add_argument('--save-top', action='store_true', help='Save top configs to CSV')
    results_parser.add_argument('--output', help='Output path for saved results')
    results_parser.set_defaults(func=cmd_results)
    
    # COMPARE command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple result files')
    compare_parser.add_argument('--files', nargs='+', required=True, help='Paths to result CSV files')
    compare_parser.add_argument('--top', type=int, default=10, help='Number of top configs to show (default: 10)')
    compare_parser.add_argument('--min-trades', type=int, default=5, help='Minimum trades for filtering (default: 5)')
    compare_parser.set_defaults(func=cmd_compare)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import pandas here (only when needed)
    if args.command == 'compare':
        import pandas as pd
        globals()['pd'] = pd
    
    args.func(args)


if __name__ == "__main__":
    main()
