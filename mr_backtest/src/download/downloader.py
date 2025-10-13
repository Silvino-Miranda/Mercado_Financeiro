"""
Data downloader for cryptocurrency OHLC data from exchanges.

Supports:
- Binance (spot, futures)
- Configurable timeframes
- Date range filtering
- CSV export
"""

import datetime as dt
import time
from pathlib import Path
from typing import Optional, List, Tuple
import requests
import pandas as pd


class DataDownloader:
    """
    Download OHLC data from cryptocurrency exchanges.
    
    Example:
        >>> downloader = DataDownloader(exchange='binance')
        >>> downloader.download(
        ...     symbol='BTCUSDT',
        ...     interval='1d',
        ...     start_date='2020-01-01',
        ...     end_date='2025-10-01',
        ...     output_path='data/raw/BTCUSDT_daily.csv'
        ... )
    """
    
    BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
    
    VALID_INTERVALS = {
        '1m', '3m', '5m', '15m', '30m',  # Minutes
        '1h', '2h', '4h', '6h', '8h', '12h',  # Hours
        '1d', '3d',  # Days
        '1w',  # Week
        '1M'   # Month
    }
    
    def __init__(self, exchange: str = 'binance'):
        """
        Initialize downloader.
        
        Args:
            exchange: Exchange name (default: 'binance')
        """
        self.exchange = exchange.lower()
        if self.exchange != 'binance':
            raise ValueError(f"Exchange '{exchange}' not supported. Only 'binance' is available.")
    
    def download(
        self,
        symbol: str,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_path: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Download OHLC data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1d', '1h', '15m')
            start_date: Start date in YYYY-MM-DD format (inclusive)
            end_date: End date in YYYY-MM-DD format (inclusive)
            output_path: Path to save CSV file (optional)
            limit: Max candles per request (max 1000 for Binance)
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close
        """
        # Validate inputs
        if interval not in self.VALID_INTERVALS:
            raise ValueError(f"Invalid interval '{interval}'. Must be one of: {self.VALID_INTERVALS}")
        
        # Convert dates to timestamps
        start_ts = self._date_to_ms(start_date) if start_date else None
        end_ts = self._date_to_ms(end_date) if end_date else None
        
        print(f"\n{'='*80}")
        print(f"📥 Downloading {symbol} {interval} data")
        print(f"{'='*80}")
        print(f"Exchange: {self.exchange.upper()}")
        print(f"Period: {start_date or 'earliest'} to {end_date or 'latest'}")
        print(f"Interval: {interval}")
        print(f"{'='*80}\n")
        
        # Fetch data
        candles = self._fetch_all_candles(symbol, interval, start_ts, end_ts, limit)
        
        # Convert to DataFrame
        df = self._candles_to_dataframe(candles)
        
        print(f"\n✅ Downloaded {len(df):,} candles")
        print(f"   Period: {df['Date'].min()} to {df['Date'].max()}")
        
        # Save if output path provided
        if output_path:
            self._save_csv(df, output_path)
        
        return df
    
    def _fetch_all_candles(
        self,
        symbol: str,
        interval: str,
        start_ts: Optional[int],
        end_ts: Optional[int],
        limit: int
    ) -> List[List]:
        """Fetch all candles in date range (handles pagination)."""
        all_candles = []
        current_start = start_ts
        
        while True:
            # Fetch batch
            candles = self._fetch_klines_batch(
                symbol, interval, current_start, end_ts, limit
            )
            
            if not candles:
                break
            
            all_candles.extend(candles)
            print(f"\r   Fetched {len(all_candles):,} candles...", end='', flush=True)
            
            # Check if we got less than limit (last batch)
            if len(candles) < limit:
                break
            
            # Update start timestamp for next batch
            last_candle_time = int(candles[-1][0])
            current_start = last_candle_time + 1
            
            # Be gentle with API
            time.sleep(0.2)
        
        print()  # New line after progress
        return all_candles
    
    def _fetch_klines_batch(
        self,
        symbol: str,
        interval: str,
        start_ts: Optional[int],
        end_ts: Optional[int],
        limit: int
    ) -> List[List]:
        """Fetch a single batch of klines from Binance API."""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_ts is not None:
            params['startTime'] = start_ts
        if end_ts is not None:
            params['endTime'] = end_ts
        
        try:
            response = requests.get(self.BINANCE_KLINES_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from Binance: {e}")
    
    def _candles_to_dataframe(self, candles: List[List]) -> pd.DataFrame:
        """Convert raw candles to DataFrame."""
        data = []
        for candle in candles:
            open_time = int(candle[0])
            data.append({
                'Date': self._ms_to_date(open_time),
                'Open': float(candle[1]),
                'High': float(candle[2]),
                'Low': float(candle[3]),
                'Close': float(candle[4])
            })
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def _save_csv(self, df: pd.DataFrame, output_path: str):
        """Save DataFrame to CSV."""
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        df.to_csv(output_file, index=False)
        print(f"💾 Saved to: {output_file.absolute()}\n")
    
    @staticmethod
    def _date_to_ms(date_str: str) -> int:
        """Convert YYYY-MM-DD to milliseconds timestamp."""
        return int(
            dt.datetime.fromisoformat(date_str)
            .replace(tzinfo=dt.timezone.utc)
            .timestamp() * 1000
        )
    
    @staticmethod
    def _ms_to_date(ms: int) -> str:
        """Convert milliseconds timestamp to YYYY-MM-DD."""
        return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime('%Y-%m-%d')
