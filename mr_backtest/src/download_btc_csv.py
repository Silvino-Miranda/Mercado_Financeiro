#!/usr/bin/env python3
"""Download BTCUSDT daily OHLC CSV from Binance public API.

This script fetches klines (candles) from Binance (spot) for BTCUSDT on the daily interval
and writes a CSV compatible with `mr_backtest.py` (`Date, Open, High, Low, Close`).

Usage examples:
    python download_btc_csv.py --out BTCUSDT_daily.csv --start 2020-01-01 --end 2025-10-01

Options:
    --symbol SYMBOL   (default: BTCUSDT)
    --interval INT    (default: 1d)
    --start DATE      (YYYY-MM-DD) inclusive
    --end DATE        (YYYY-MM-DD) inclusive
    --limit N         (max candles per request, Binance allows up to 1000)
    --out PATH        Output CSV path

References:
- Binance API: https://api.binance.com/api/v3/klines
"""
import argparse
import datetime as dt
import os
import time
from typing import Optional

import requests
import pandas as pd

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"


def iso_to_ms(d: str) -> int:
    # parse YYYY-MM-DD
    return int(dt.datetime.fromisoformat(d).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def ms_to_iso(ms: int) -> str:
    return dt.datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d')


def fetch_klines(symbol: str, interval: str, start_ts: Optional[int], end_ts: Optional[int], limit: int = 1000):
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    if start_ts is not None:
        params['startTime'] = start_ts
    if end_ts is not None:
        params['endTime'] = end_ts

    resp = requests.get(BINANCE_KLINES, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_range(symbol: str, interval: str, start: Optional[str], end: Optional[str], out_path: str, limit: int = 1000):
    # Convert to ms
    start_ms = iso_to_ms(start) if start else None
    end_ms = iso_to_ms(end) if end else None

    rows = []
    cur_start = start_ms
    while True:
        klines = fetch_klines(symbol, interval, cur_start, end_ms, limit=limit)
        if not klines:
            break
        for k in klines:
            open_time = int(k[0])
            open_px = k[1]
            high = k[2]
            low = k[3]
            close = k[4]
            rows.append((ms_to_iso(open_time), open_px, high, low, close))

        # if returned less than limit, we're done
        if len(klines) < limit:
            break

        # advance to last open_time + 1 ms
        last_open = int(klines[-1][0])
        cur_start = last_open + 1
        time.sleep(0.2)  # be gentle on API

    # Save to CSV
    df = pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close'])
    df.to_csv(out_path, index=False)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', default='BTCUSDT')
    p.add_argument('--interval', default='1d')
    p.add_argument('--start', default='2020-01-01')
    p.add_argument('--end', default=None)
    p.add_argument('--limit', type=int, default=1000)
    p.add_argument('--out', default='BTCUSDT_daily.csv', help='Output CSV filename (saves to data/ folder)')
    args = p.parse_args()

    # Resolve output path to data/ folder
    out_path = args.out
    if not os.path.isabs(out_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_path = os.path.join(project_root, "data", out_path)
    
    out = download_range(args.symbol, args.interval, args.start, args.end, out_path, limit=args.limit)
    print(f"Saved OHLC CSV to: {out}")


if __name__ == '__main__':
    main()
