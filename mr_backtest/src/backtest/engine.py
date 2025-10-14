#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtesting Engine
------------------
Core backtesting engine with realistic order execution simulation.
"""

from typing import List, Tuple
import pandas as pd
import numpy as np

from .types import Params, TradeResult, BacktestResult
from .strategies import get_strategy
from .utils import apply_fees_and_slippage


class BacktestEngine:
    """
    Backtesting engine for mean-reversion strategies.
    
    Features:
    - Realistic order execution (signals on close, entry at next open)
    - Conservative intrabar exit logic (stop hit before target)
    - Breakeven stop adjustment
    - Time-based stops
    - Trading costs (fees and slippage)
    """
    
    def __init__(self, params: Params):
        """
        Initialize backtest engine.
        
        Args:
            params: Strategy and risk management parameters
        """
        self.params = params
        self.strategy = get_strategy(params.variant, params)
    
    def run(self, df: pd.DataFrame) -> BacktestResult:
        """
        Execute backtest on OHLC data.
        
        Args:
            df: DataFrame with Date, Open, High, Low, Close columns
        
        Returns:
            BacktestResult with trades, equity curve, and metrics
        """
        df = df.copy().reset_index(drop=True)
        
        # Compute indicators
        df = self.strategy.compute_indicators(df)
        
        # Generate entry signals
        signal_rows = self.strategy.generate_signals(df)
        
        # Run backtest simulation
        trades, equity_curve = self._simulate_trades(df, signal_rows)
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(trades, equity_curve, df)
        
        return BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            metrics=metrics,
            params=self.params
        )
    
    def _simulate_trades(self, df: pd.DataFrame, signal_rows: pd.Series) -> Tuple[List[TradeResult], pd.DataFrame]:
        """
        Simulate trade execution with realistic order fills.
        
        Args:
            df: DataFrame with OHLC and indicators
            signal_rows: Boolean series indicating entry signals
        
        Returns:
            Tuple of (trades list, equity curve DataFrame)
        """
        in_pos = False
        entry_idx = None
        entry_px_exec = None
        shares = 0.0
        be_active = False
        
        trades: List[TradeResult] = []
        equity_curve = []
        equity = 0.0
        
        n = len(df)
        i = 0
        
        while i < n - 1:
            next_row = df.iloc[i + 1]
            
            if not in_pos:
                # Check for entry signal
                if signal_rows.iloc[i] and not np.isnan(next_row["Open"]):
                    entry_idx = i + 1
                    entry_px_raw = float(next_row["Open"])
                    entry_px_exec = apply_fees_and_slippage(
                        entry_px_raw, "buy", self.params.fees_bps, self.params.slip_bps
                    )
                    shares = self.params.capital_per_trade / entry_px_exec
                    be_active = False
                    in_pos = True
                    i += 1
                    continue
                else:
                    i += 1
                    continue
            else:
                # Manage existing position
                bars_held = i - entry_idx + 1
                
                # Calculate stop distance (use ATR and percentage)
                atr_entry = float(df.iloc[entry_idx]["ATR"])
                pct_stop_dist = self.params.sl_pct * entry_px_exec
                atr_stop_dist = self.params.atr_mult * atr_entry
                stop_dist = min(pct_stop_dist, atr_stop_dist)
                
                # Calculate target and stop prices
                target_px = entry_px_exec * (1 + self.params.tp_pct)
                stop_px = entry_px_exec - stop_dist
                
                # Current bar OHLC
                cur = df.iloc[i]
                open_px = float(cur["Open"])
                high_px = float(cur["High"])
                low_px = float(cur["Low"])
                close_px = float(cur["Close"])
                
                reason = None
                exit_px_exec = None
                
                # Check time stop first
                if bars_held >= self.params.time_stop:
                    exit_px_exec = apply_fees_and_slippage(close_px, "sell", self.params.fees_bps, self.params.slip_bps)
                    reason = "time_stop"
                else:
                    # Check breakeven trigger
                    if self.params.allow_breakeven and (not be_active):
                        if high_px >= entry_px_exec * (1 + self.params.be_trigger_pct):
                            be_active = True
                            stop_px = max(stop_px, entry_px_exec)
                    
                    # Update stop if breakeven is active
                    if be_active:
                        stop_px = max(stop_px, entry_px_exec)
                    
                    # Check for exits (conservative intrabar logic)
                    if open_px <= stop_px:
                        # Gap down through stop
                        exit_px_exec = apply_fees_and_slippage(open_px, "sell", self.params.fees_bps, self.params.slip_bps)
                        reason = "stop_gap"
                    elif open_px >= target_px:
                        # Gap up to target
                        exit_px_exec = apply_fees_and_slippage(open_px, "sell", self.params.fees_bps, self.params.slip_bps)
                        reason = "tp_gap"
                    else:
                        # Check if both levels hit in same bar
                        both_hit = (high_px >= target_px) and (low_px <= stop_px)
                        if both_hit:
                            # Conservative: assume stop hit first
                            exit_px_exec = apply_fees_and_slippage(stop_px, "sell", self.params.fees_bps, self.params.slip_bps)
                            reason = "stop_then_tp_same_bar"
                        elif low_px <= stop_px:
                            # Stop hit
                            exit_px_exec = apply_fees_and_slippage(stop_px, "sell", self.params.fees_bps, self.params.slip_bps)
                            reason = "stop"
                        elif high_px >= target_px:
                            # Target hit
                            exit_px_exec = apply_fees_and_slippage(target_px, "sell", self.params.fees_bps, self.params.slip_bps)
                            reason = "tp"
                
                # If exit occurred, record trade
                if exit_px_exec is not None:
                    pnl = (exit_px_exec - entry_px_exec) * shares
                    pnl_pct = (exit_px_exec / entry_px_exec) - 1.0
                    
                    trades.append(TradeResult(
                        entry_date=pd.to_datetime(df.iloc[entry_idx]["Date"]),
                        exit_date=pd.to_datetime(df.iloc[i]["Date"]),
                        entry_px=entry_px_exec,
                        exit_px=exit_px_exec,
                        shares=shares,
                        pnl=pnl,
                        pnl_pct=pnl_pct,
                        reason=reason,
                        bars_held=bars_held
                    ))
                    
                    equity += pnl
                    equity_curve.append((pd.to_datetime(df.iloc[i]["Date"]), equity))
                    
                    # Reset position state
                    in_pos = False
                    entry_idx = None
                    entry_px_exec = None
                    shares = 0.0
                    be_active = False
                
                i += 1
        
        # Force exit if still in position at end
        if in_pos:
            last = df.iloc[-1]
            exit_px_exec = apply_fees_and_slippage(float(last["Close"]), "sell", self.params.fees_bps, self.params.slip_bps)
            pnl = (exit_px_exec - entry_px_exec) * shares
            pnl_pct = (exit_px_exec / entry_px_exec) - 1.0
            
            trades.append(TradeResult(
                entry_date=pd.to_datetime(df.iloc[entry_idx]["Date"]),
                exit_date=pd.to_datetime(last["Date"]),
                entry_px=entry_px_exec,
                exit_px=exit_px_exec,
                shares=shares,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason="forced_exit_end",
                bars_held=(len(df) - entry_idx)
            ))
            
            equity += pnl
            equity_curve.append((pd.to_datetime(last["Date"]), equity))
        
        # Create equity curve DataFrame
        ec_df = pd.DataFrame(equity_curve, columns=["Date", "Equity"]).set_index("Date")
        
        return trades, ec_df
    
    def _calculate_metrics(self, trades: List[TradeResult], ec: pd.DataFrame, df: pd.DataFrame) -> dict:
        """
        Calculate performance metrics.
        
        Args:
            trades: List of completed trades
            ec: Equity curve DataFrame
            df: Original OHLC DataFrame
        
        Returns:
            Dictionary of performance metrics
        """
        n_trades = len(trades)
        
        if n_trades == 0:
            return {
                "trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "expectancy_per_trade": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "max_drawdown": 0.0,
                "sharpe_like": 0.0,
                "sortino_like": 0.0,
                "time_in_market": 0.0,
                "trades_per_year": 0.0,
                "total_pnl": 0.0
            }
        
        # Win/loss statistics
        wins = sum(1 for t in trades if t.pnl > 0)
        losses = sum(1 for t in trades if t.pnl <= 0)
        win_rate = wins / n_trades
        
        # Profit factor
        gains = sum(max(t.pnl, 0.0) for t in trades)
        loss_sum = -sum(min(t.pnl, 0.0) for t in trades)
        profit_factor = gains / loss_sum if loss_sum > 0 else (float('inf') if gains > 0 else 0.0)
        
        # Average win/loss
        avg_win = np.mean([t.pnl for t in trades if t.pnl > 0]) if wins else 0.0
        avg_loss = np.mean([-t.pnl for t in trades if t.pnl <= 0]) if losses else 0.0
        
        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        # Drawdown
        if not ec.empty:
            roll_max = ec["Equity"].cummax()
            dd = ec["Equity"] - roll_max
            max_dd = float(dd.min())
        else:
            max_dd = 0.0
        
        # Sharpe/Sortino (simplified)
        sharpe, sortino = self._calculate_sharpe_sortino(ec)
        
        # Time in market
        held_days = sum(t.bars_held for t in trades)
        total_days = len(df)
        time_in_mkt = held_days / total_days if total_days else 0.0
        
        # Trades per year
        if total_days:
            date_range_years = (pd.to_datetime(df["Date"].iloc[-1]) - pd.to_datetime(df["Date"].iloc[0])).days / 365.25
            tpy = n_trades / date_range_years if date_range_years > 0 else 0.0
        else:
            tpy = 0.0
        
        total_pnl = sum(t.pnl for t in trades)
        
        return {
            "trades": n_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "expectancy_per_trade": expectancy,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "max_drawdown": max_dd,
            "sharpe_like": sharpe,
            "sortino_like": sortino,
            "time_in_market": time_in_mkt,
            "trades_per_year": tpy,
            "total_pnl": total_pnl
        }
    
    def _calculate_sharpe_sortino(self, ec: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate Sharpe and Sortino ratios.
        
        Args:
            ec: Equity curve DataFrame
        
        Returns:
            Tuple of (sharpe_ratio, sortino_ratio)
        """
        if ec.empty or len(ec) < 2:
            return 0.0, 0.0
        
        rets = ec["Equity"].diff().dropna()
        
        if rets.std(ddof=1) == 0:
            sharpe = 0.0
        else:
            sharpe = rets.mean() / rets.std(ddof=1)
        
        downside = rets.copy()
        downside[downside > 0] = 0
        
        if downside.std(ddof=1) == 0:
            sortino = 0.0
        else:
            sortino = rets.mean() / downside.std(ddof=1)
        
        return float(sharpe), float(sortino)
