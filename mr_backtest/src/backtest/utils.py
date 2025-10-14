#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions
-----------------
Helper functions for backtesting operations.
"""

import pandas as pd


def apply_fees_and_slippage(price: float, side: str, fees_bps: float, slip_bps: float) -> float:
    """
    Apply trading fees and slippage to execution price.
    
    For buy orders: Price increases by fees and slippage
    For sell orders: Price decreases by fees and slippage
    
    Args:
        price: Raw price
        side: "buy" or "sell"
        fees_bps: Trading fees in basis points per side
        slip_bps: Slippage in basis points per side
    
    Returns:
        Executed price after fees and slippage
    """
    fee_mult = 1 + (fees_bps / 10000.0)
    slip_mult = 1 + (slip_bps / 10000.0) if side == "buy" else 1 - (slip_bps / 10000.0)
    
    if side == "buy":
        return price * fee_mult * slip_mult
    else:
        # For sells, price received decreases by fees
        return price * slip_mult / fee_mult


def load_ohlc_csv(path: str) -> pd.DataFrame:
    """
    Load OHLC data from CSV file.
    
    Normalizes column names to standard format (Date, Open, High, Low, Close).
    Handles case-insensitive column matching.
    
    Args:
        path: Path to CSV file
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close
        
    Raises:
        ValueError: If required columns are missing
    """
    df = pd.read_csv(path)
    
    # Normalize column names (case-insensitive matching)
    required = ["date", "open", "high", "low", "close"]
    mapping = {}
    
    for req in required:
        matches = [c for c in df.columns if c.lower() == req]
        if not matches:
            raise ValueError(f"CSV must include column '{req}' (case-insensitive).")
        mapping[matches[0]] = req.capitalize() if req != "date" else "Date"
    
    df = df.rename(columns=mapping)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    
    return df[["Date", "Open", "High", "Low", "Close"]]
