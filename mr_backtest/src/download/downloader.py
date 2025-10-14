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
    
    def download_incremental(
        self,
        symbol: str,
        interval: str = '1d',
        start_date: str = '2017-08-17',
        end_date: Optional[str] = None,
        output_path: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Download large datasets incrementally (year by year) to avoid memory issues.
        
        This method:
        1. Splits date range into yearly chunks
        2. Downloads each year separately
        3. Saves temporary files
        4. Concatenates all years into final file
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1d', '1h', '30m')
            start_date: Start date in YYYY-MM-DD format (default: 2017-08-17)
            end_date: End date in YYYY-MM-DD format (default: today)
            output_path: Path to save final CSV file
            limit: Max candles per request (max 1000 for Binance)
            
        Returns:
            DataFrame with all data concatenated
        """
        if end_date is None:
            end_date = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
        
        print(f"\n{'='*80}")
        print(f"📥 Incremental Download: {symbol} {interval}")
        print(f"{'='*80}")
        print(f"Exchange: {self.exchange.upper()}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Interval: {interval}")
        print(f"Strategy: Year-by-year download + concatenation")
        print(f"{'='*80}\n")
        
        # Parse dates
        start_dt = dt.datetime.fromisoformat(start_date).replace(tzinfo=dt.timezone.utc)
        end_dt = dt.datetime.fromisoformat(end_date).replace(tzinfo=dt.timezone.utc)
        
        # Split into yearly chunks
        all_dfs = []
        current_year = start_dt.year
        end_year = end_dt.year
        
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for year in range(current_year, end_year + 1):
            # Define year boundaries
            year_start = dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc)
            year_end = dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc)
            
            # Adjust for first and last year
            if year == current_year:
                year_start = start_dt
            if year == end_year:
                year_end = end_dt
            
            print(f"\n📆 Downloading year {year}...")
            print(f"   Range: {year_start.strftime('%Y-%m-%d')} to {year_end.strftime('%Y-%m-%d')}")
            
            # Download this year
            try:
                df_year = self.download(
                    symbol=symbol,
                    interval=interval,
                    start_date=year_start.strftime('%Y-%m-%d'),
                    end_date=year_end.strftime('%Y-%m-%d'),
                    output_path=None,  # Don't save yet
                    limit=limit
                )
                
                # Save temporary file
                temp_file = temp_dir / f"{symbol}_{interval}_{year}.csv"
                df_year.to_csv(temp_file, index=False)
                print(f"   ✅ Saved: {temp_file} ({len(df_year):,} candles)")
                
                all_dfs.append(df_year)
                
            except Exception as e:
                print(f"   ⚠️  Warning: Failed to download year {year}: {e}")
                print(f"   Continuing with remaining years...")
                continue
        
        # Concatenate all years
        if not all_dfs:
            raise RuntimeError("No data was downloaded successfully")
        
        print(f"\n🔗 Concatenating {len(all_dfs)} year(s)...")
        df_final = pd.concat(all_dfs, ignore_index=True)
        df_final = df_final.sort_values('Date').reset_index(drop=True)
        
        print(f"\n✅ Total downloaded: {len(df_final):,} candles")
        print(f"   Period: {df_final['Date'].min()} to {df_final['Date'].max()}")
        
        # Save final file
        if output_path:
            self._save_csv(df_final, output_path)
            
            # Cleanup temp files
            print(f"\n🧹 Cleaning up temporary files...")
            for year_file in temp_dir.glob(f"{symbol}_{interval}_*.csv"):
                year_file.unlink()
                print(f"   Deleted: {year_file.name}")
        
        return df_final
    
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
        """Convert raw candles to DataFrame - Bypass pandas constructor bugs by writing to CSV first."""
        import csv
        import tempfile
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as tmp:
            writer = csv.writer(tmp)
            # Write header
            writer.writerow(['Date', 'Open', 'High', 'Low', 'Close'])
            
            # Write data
            for candle in candles:
                open_time = int(candle[0])
                date_str = dt.datetime.fromtimestamp(open_time / 1000, tz=dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([
                    date_str,
                    float(candle[1]),
                    float(candle[2]),
                    float(candle[3]),
                    float(candle[4])
                ])
            
            tmp_path = tmp.name
        
        # Read back with pandas (avoids constructor bugs)
        df = pd.read_csv(tmp_path)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
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
