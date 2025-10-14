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
        print("\n📊 Converting candles to DataFrame...")
        df = self._candles_to_dataframe(candles)
        
        print(f"\n✅ Downloaded {len(df):,} candles")
        print(f"   Period: {df['Date'].min()} to {df['Date'].max()}")
        
        # Save if output path provided
        if output_path:
            print(f"💾 Saving to: {output_path}")
            self._save_csv(df, output_path)
            print(f"✅ File saved successfully!")
        
        return df
    
    def _fetch_all_candles(
        self,
        symbol: str,
        interval: str,
        start_ts: Optional[int],
        end_ts: Optional[int],
        limit: int
    ) -> List[List]:
        """
        Fetch all candles in date range (handles pagination with retry).
        
        Features:
        - Automatic retry on network errors
        - Progress display with percentage
        - Estimated total calculation
        """
        all_candles = []
        current_start = start_ts
        batch_count = 0
        
        while True:
            # Fetch batch with retry
            candles = self._fetch_klines_batch(
                symbol, interval, current_start, end_ts, limit
            )
            
            if not candles:
                break
            
            all_candles.extend(candles)
            batch_count += 1
            
            # Calculate progress
            if start_ts and end_ts and all_candles:
                current_time = int(candles[-1][0])
                progress = ((current_time - start_ts) / (end_ts - start_ts)) * 100
                print(f"\r   Fetched {len(all_candles):,} candles... ({progress:.1f}% complete)", end='', flush=True)
            else:
                print(f"\r   Fetched {len(all_candles):,} candles...", end='', flush=True)
            
            # Check if we got less than limit (last batch)
            if len(candles) < limit:
                break
            
            # Update start timestamp for next batch
            last_candle_time = int(candles[-1][0])
            current_start = last_candle_time + 1
            
            # Be gentle with API (rate limiting)
            time.sleep(0.25)
        
        print()  # New line after progress
        return all_candles
    
    def _fetch_klines_batch(
        self,
        symbol: str,
        interval: str,
        start_ts: Optional[int],
        end_ts: Optional[int],
        limit: int,
        max_retries: int = 5
    ) -> List[List]:
        """
        Fetch a single batch of klines from Binance API with automatic retry.
        
        Implements exponential backoff retry logic:
        - Retry on network errors, timeouts, SSL errors
        - Wait time increases: 1s, 2s, 4s, 8s, 16s
        - Max 5 retries by default
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_ts is not None:
            params['startTime'] = start_ts
        if end_ts is not None:
            params['endTime'] = end_ts
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.get(self.BINANCE_KLINES_URL, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                last_error = e
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                    wait_time = 2 ** attempt
                    print(f"\n⚠️  Connection error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # Last attempt failed
                    print(f"\n❌ All {max_retries} retry attempts failed")
        
        raise RuntimeError(f"Failed to fetch data from Binance after {max_retries} attempts: {last_error}")
    
    def _candles_to_dataframe(self, candles: List[List]) -> pd.DataFrame:
        """Convert raw candles to DataFrame."""
        # Build separate lists (avoids pandas nested object issues)
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        
        for candle in candles:
            # Force conversion to native Python types
            open_time = int(float(str(candle[0])))
            dates.append(dt.datetime.fromtimestamp(open_time / 1000, tz=dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
            opens.append(float(str(candle[1])))
            highs.append(float(str(candle[2])))
            lows.append(float(str(candle[3])))
            closes.append(float(str(candle[4])))
        
        # Create DataFrame from separate lists
        df = pd.DataFrame()
        df['Date'] = dates
        df['Open'] = opens
        df['High'] = highs
        df['Low'] = lows
        df['Close'] = closes
        
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
