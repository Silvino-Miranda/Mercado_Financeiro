#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Module CLI
------------------------
Command-line interface for managing strategy configurations.

Usage:
    python -m src.config create --name champion --variant base --tp_pct 0.10
    python -m src.config validate config/my_params.csv
    python -m src.config list config/my_params.csv
    python -m src.config show-ranges --type narrow
"""

import argparse
import json
import sys
from pathlib import Path

from .types import StrategyConfig, ParamRange
from .manager import ConfigManager
from .utils import (
    load_params_from_csv,
    load_all_params_from_csv,
    save_params_to_csv,
    save_multiple_params_to_csv,
    create_default_ranges,
    create_narrow_ranges,
    get_project_root
)


def cmd_create(args):
    """Create a new configuration."""
    config = StrategyConfig(
        variant=args.variant,
        ma_len=args.ma_len,
        dist_below_ma_pct=args.dist_below_ma_pct,
        tp_pct=args.tp_pct,
        sl_pct=args.sl_pct,
        atr_mult=args.atr_mult,
        time_stop=args.time_stop,
        be_trigger_pct=args.be_trigger_pct,
        allow_breakeven=args.allow_breakeven,
        fees_bps=args.fees_bps,
        slip_bps=args.slip_bps,
        capital_per_trade=args.capital_per_trade,
        name=args.name,
        description=args.description
    )
    
    # Validate
    is_valid, errors = config.validate()
    if not is_valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    # Save
    output_file = args.output if args.output else f"config/{args.name}.csv"
    save_params_to_csv(config, output_file)
    
    print(f"✅ Configuration created successfully!")
    print(f"   Name: {config.name}")
    print(f"   Variant: {config.variant}")
    print(f"   Saved to: {output_file}")


def cmd_validate(args):
    """Validate configuration file."""
    try:
        configs = load_all_params_from_csv(args.file)
        
        print(f"\n{'='*60}")
        print(f"Validating: {args.file}")
        print(f"{'='*60}\n")
        
        all_valid = True
        for i, config in enumerate(configs, 1):
            is_valid, errors = config.validate()
            
            if is_valid:
                print(f"✅ Config {i} ({config.name}): VALID")
            else:
                print(f"❌ Config {i} ({config.name}): INVALID")
                for error in errors:
                    print(f"   - {error}")
                all_valid = False
        
        print(f"\n{'='*60}")
        if all_valid:
            print(f"✅ All {len(configs)} configuration(s) are valid!")
        else:
            print(f"❌ Some configurations have errors")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)


def cmd_list(args):
    """List all configurations in a file."""
    try:
        configs = load_all_params_from_csv(args.file)
        
        print(f"\n{'='*60}")
        print(f"Configurations in: {args.file}")
        print(f"{'='*60}\n")
        
        for i, config in enumerate(configs, 1):
            print(f"{i}. {config.name}")
            print(f"   Variant: {config.variant}")
            print(f"   MA Length: {config.ma_len}")
            print(f"   Dist below MA: {config.dist_below_ma_pct:.2%}")
            print(f"   TP: {config.tp_pct:.2%} | SL: {config.sl_pct:.2%}")
            print(f"   ATR Mult: {config.atr_mult} | Time Stop: {config.time_stop} bars")
            print(f"   Breakeven: {config.allow_breakeven}")
            if config.description:
                print(f"   Description: {config.description}")
            print()
        
        print(f"Total: {len(configs)} configuration(s)")
        print(f"{'='*60}\n")
    
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)


def cmd_show(args):
    """Show detailed configuration."""
    try:
        configs = load_all_params_from_csv(args.file)
        
        # Find config by index or name
        if args.index is not None:
            if args.index < 1 or args.index > len(configs):
                print(f"❌ Invalid index: {args.index}. File has {len(configs)} configs.")
                sys.exit(1)
            config = configs[args.index - 1]
        elif args.name:
            manager = ConfigManager()
            for c in configs:
                manager.add_config(c)
            try:
                config = manager.get_config_by_name(args.name)
            except ValueError as e:
                print(f"❌ {e}")
                sys.exit(1)
        else:
            config = configs[0]  # Default to first
        
        # Display
        print(f"\n{'='*60}")
        print(f"Configuration: {config.name}")
        print(f"{'='*60}\n")
        
        config_dict = config.to_dict()
        for key, value in config_dict.items():
            if isinstance(value, float):
                if key.endswith('_pct'):
                    print(f"  {key:25s}: {value:.4f} ({value:.2%})")
                else:
                    print(f"  {key:25s}: {value:.4f}")
            else:
                print(f"  {key:25s}: {value}")
        
        print(f"\n{'='*60}\n")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cmd_show_ranges(args):
    """Show parameter ranges for optimization."""
    if args.type == 'default':
        ranges = create_default_ranges()
        title = "Default Parameter Ranges (Wide)"
    elif args.type == 'narrow':
        ranges = create_narrow_ranges()
        title = "Narrow Parameter Ranges (Fine-tuning)"
    else:
        print(f"❌ Unknown range type: {args.type}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(title)
    print(f"{'='*60}\n")
    
    total_combinations = 1
    for name, param_range in ranges.items():
        values = param_range.get_values()
        count = len(values)
        total_combinations *= count
        
        print(f"{name:20s}:")
        print(f"  Type: {param_range.param_type}")
        print(f"  Range: {param_range.min_val} to {param_range.max_val}")
        if param_range.step:
            print(f"  Step: {param_range.step}")
        print(f"  Values: {count}")
        
        # Show first few values
        if count <= 10:
            print(f"  → {values}")
        else:
            print(f"  → {values[:5]} ... {values[-2:]}")
        print()
    
    print(f"{'='*60}")
    print(f"Total combinations: {total_combinations:,}")
    print(f"{'='*60}\n")


def cmd_convert(args):
    """Convert configuration to different formats."""
    try:
        config = load_params_from_csv(args.file)
        
        if args.format == 'json':
            output = json.dumps(config.to_dict(), indent=2)
            print(output)
        elif args.format == 'params':
            params = config.to_params()
            print(f"Params object for backtesting:")
            print(params)
        else:
            print(f"❌ Unknown format: {args.format}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Configuration Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new configuration
  python -m src.config create --name my_strategy --variant base --tp_pct 0.12
  
  # Validate configuration file
  python -m src.config validate config/my_params.csv
  
  # List all configurations in file
  python -m src.config list config/my_params.csv
  
  # Show specific configuration
  python -m src.config show config/my_params.csv --index 1
  
  # Show optimization ranges
  python -m src.config show-ranges --type narrow
  
  # Convert to JSON
  python -m src.config convert config/my_params.csv --format json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # CREATE command
    create_parser = subparsers.add_parser('create', help='Create new configuration')
    create_parser.add_argument('--name', required=True, help='Configuration name')
    create_parser.add_argument('--variant', choices=['base', 'rsi', 'reclaim'], default='base')
    create_parser.add_argument('--ma_len', type=int, default=200)
    create_parser.add_argument('--dist_below_ma_pct', type=float, default=0.05)
    create_parser.add_argument('--tp_pct', type=float, default=0.10)
    create_parser.add_argument('--sl_pct', type=float, default=0.08)
    create_parser.add_argument('--atr_mult', type=float, default=2.0)
    create_parser.add_argument('--time_stop', type=int, default=30)
    create_parser.add_argument('--be_trigger_pct', type=float, default=0.06)
    create_parser.add_argument('--allow_breakeven', type=bool, default=True)
    create_parser.add_argument('--fees_bps', type=float, default=10.0)
    create_parser.add_argument('--slip_bps', type=float, default=5.0)
    create_parser.add_argument('--capital_per_trade', type=float, default=1000.0)
    create_parser.add_argument('--description', default='')
    create_parser.add_argument('--output', help='Output file path')
    create_parser.set_defaults(func=cmd_create)
    
    # VALIDATE command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('file', help='Configuration CSV file')
    validate_parser.set_defaults(func=cmd_validate)
    
    # LIST command
    list_parser = subparsers.add_parser('list', help='List configurations')
    list_parser.add_argument('file', help='Configuration CSV file')
    list_parser.set_defaults(func=cmd_list)
    
    # SHOW command
    show_parser = subparsers.add_parser('show', help='Show configuration details')
    show_parser.add_argument('file', help='Configuration CSV file')
    show_parser.add_argument('--index', type=int, help='Configuration index (1-based)')
    show_parser.add_argument('--name', help='Configuration name')
    show_parser.set_defaults(func=cmd_show)
    
    # SHOW-RANGES command
    ranges_parser = subparsers.add_parser('show-ranges', help='Show parameter ranges')
    ranges_parser.add_argument('--type', choices=['default', 'narrow'], default='default')
    ranges_parser.set_defaults(func=cmd_show_ranges)
    
    # CONVERT command
    convert_parser = subparsers.add_parser('convert', help='Convert configuration format')
    convert_parser.add_argument('file', help='Configuration CSV file')
    convert_parser.add_argument('--format', choices=['json', 'params'], default='json')
    convert_parser.set_defaults(func=cmd_convert)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
