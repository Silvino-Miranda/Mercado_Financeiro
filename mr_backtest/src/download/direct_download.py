#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct CSV Download - Bypasses pandas DataFrame creation issues
"""

import csv
import datetime as dt
import time
import requests
from pathlib import Path


def download_btcusdt_incremental(
    start_year: int = 2015,
    end_year: int = 2025,
    interval: str = '30m',
    output_file: str = 'data/raw/BTCUSDT_30m_full.csv'
):
    """
    Download BTCUSDT data year-by-year and save directly to CSV.
    
    This bypasses all pandas DataFrame issues by writing directly to CSV.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Direct CSV Download: BTCUSDT {interval}")
    print(f"Period: {start_year} to {end_year}")
    print(f"Output: {output_file}")
    print("="*80)
    
    # Open CSV for writing
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close'])
        
        total_candles = 0
        
        for year in range(start_year, end_year + 1):
            print(f"\n📆 Year {year}...")
            
            # Define year boundaries
            year_start = dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc)
            year_end = dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc)
            
            # Adjust for first/last year
            if year == start_year and start_year == 2015:
                year_start = dt.datetime(2015, 8, 17, tzinfo=dt.timezone.utc)
            if year == end_year:
                year_end = dt.datetime.now(dt.timezone.utc)
            
            start_ts = int(year_start.timestamp() * 1000)
            end_ts = int(year_end.timestamp() * 1000)
            
            # Fetch all candles for this year
            year_candles = 0
            current_start = start_ts
            
            while current_start < end_ts:
                # Fetch batch
                params = {
                    'symbol': 'BTCUSDT',
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': end_ts,
                    'limit': 1000
                }
                
                try:
                    response = requests.get(
                        'https://api.binance.com/api/v3/klines',
                        params=params,
                        timeout=30
                    )
                    response.raise_for_status()
                    candles = response.json()
                    
                    if not candles:
                        break
                    
                    # Write candles directly to CSV
                    for candle in candles:
                        open_time = int(candle[0])
                        date_str = dt.datetime.fromtimestamp(
                            open_time / 1000,
                            tz=dt.timezone.utc
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        
                        writer.writerow([
                            date_str,
                            float(candle[1]),  # Open
                            float(candle[2]),  # High
                            float(candle[3]),  # Low
                            float(candle[4])   # Close
                        ])
                        year_candles += 1
                        total_candles += 1
                    
                    # Progress
                    progress = ((current_start - start_ts) / (end_ts - start_ts)) * 100
                    print(f"\r   {year_candles:,} candles ({progress:.1f}%)...", end='', flush=True)
                    
                    # Check if last batch
                    if len(candles) < 1000:
                        break
                    
                    # Update for next batch
                    last_time = int(candles[-1][0])
                    current_start = last_time + 1
                    
                    # Rate limiting
                    time.sleep(0.25)
                    
                except Exception as e:
                    print(f"\n   ⚠️  Error: {e}")
                    print(f"   Retrying in 2s...")
                    time.sleep(2)
                    continue
            
            print(f"\r   ✅ {year_candles:,} candles (100.0%)")
    
    print(f"\n{'='*80}")
    print(f"✅ Download complete!")
    print(f"   Total: {total_candles:,} candles")
    print(f"   Saved to: {output_path}")
    print(f"{'='*80}")


if __name__ == '__main__':
    download_btcusdt_incremental(
        start_year=2015,
        end_year=2025,
        interval='30m',
        output_file='data/raw/BTCUSDT_30m_full.csv'
    )
