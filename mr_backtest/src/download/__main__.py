#!/usr/bin/env python3
"""
Download module CLI interface.

Usage:
    python -m src.download BTCUSDT --interval 1d --start 2020-01-01
    python -m src.download ETHUSDT --interval 1h --start 2024-01-01 --output custom_path.csv
"""

import argparse
import sys
from pathlib import Path

from .downloader import DataDownloader


def main():
    parser = argparse.ArgumentParser(
        description='Download cryptocurrency OHLC data from exchanges',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download BTC daily data from 2020
  python -m src.download BTCUSDT --interval 1d --start 2020-01-01
  
  # Download ETH 1h data with custom output
  python -m src.download ETHUSDT --interval 1h --start 2024-01-01 --output data/raw/ETH_1h.csv
  
  # Download recent BTC 15min data
  python -m src.download BTCUSDT --interval 15m --start 2025-10-01
        """
    )
    
    parser.add_argument(
        'symbol',
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    parser.add_argument(
        '--interval',
        default='1d',
        choices=['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'],
        help='Timeframe interval (default: 1d)'
    )
    parser.add_argument(
        '--start',
        default='2020-01-01',
        help='Start date YYYY-MM-DD (default: 2020-01-01)'
    )
    parser.add_argument(
        '--end',
        default=None,
        help='End date YYYY-MM-DD (default: today)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output CSV path (default: data/raw/{SYMBOL}_{INTERVAL}.csv)'
    )
    parser.add_argument(
        '--exchange',
        default='binance',
        help='Exchange name (default: binance)'
    )
    
    args = parser.parse_args()
    
    # Default output path
    if args.output is None:
        # Get project root (2 levels up from src/download)
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / 'data' / 'raw'
        output_dir.mkdir(parents=True, exist_ok=True)
        args.output = str(output_dir / f"{args.symbol}_{args.interval}.csv")
    
    # Download
    try:
        downloader = DataDownloader(exchange=args.exchange)
        downloader.download(
            symbol=args.symbol,
            interval=args.interval,
            start_date=args.start,
            end_date=args.end,
            output_path=args.output
        )
        
        print("✅ Download completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
