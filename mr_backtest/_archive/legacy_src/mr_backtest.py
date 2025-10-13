
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mean-Reversion Backtester (BTCUSDT Daily)
-----------------------------------------
Implements three strategy variants proposed by the user with strict risk management:

Variants:
1) MR-Base (slope filter)
2) MR-RSI (RSI(14) crosses up 30)
3) MR-Reclaim (close reclaims MA200 after prior day <= 0.95*MA200)

Assumptions
- Signals are evaluated on close of day t; entries execute at next day open (t+1).
- Only 1 position at a time.
- Costs: fees (bps) each side + slippage (bps) each side.
- Intrabar hit order: if both TP and SL touch within same bar, SL is hit first (conservative).
- Time stop exits at the close of the time-stop bar.
- Breakeven: when price advances BE_trigger_pct from entry, stop is raised to entry.

CSV requirements
- Columns: Date, Open, High, Low, Close (case-insensitive). Date parseable to pandas datetime.
- Daily timeframe.

Usage
-----
python mr_backtest.py --csv path/to/BTCUSDT_1d.csv --variant base \
  --capital_per_trade 1000 --fees_bps 10 --slip_bps 5 \
  --tp_pct 0.10 --sl_pct 0.08 --atr_mult 2.0 --time_stop 30 \
  --be_trigger_pct 0.06 --ma_len 200 --dist_below_ma_pct 0.05

Run a grid (recommended):
python mr_backtest.py --csv path/to/BTCUSDT_1d.csv --grid

Outputs
- Prints a summary for single run.
- With --grid, writes grid_results.csv next to the script and prints top rows.
"""

import argparse
import math
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------- Indicators ----------------------

def wilder_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    close = series.astype(float)
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    # Wilder's smoothing (RMA)
    gain = up.ewm(alpha=1/period, adjust=False).mean()
    loss = down.ewm(alpha=1/period, adjust=False).mean()

    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # neutral for early bars


def wilder_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr


def moving_average(series: pd.Series, window: int = 200) -> pd.Series:
    return series.astype(float).rolling(window=window, min_periods=window).mean()


# ---------------------- Strategy Logic ----------------------

@dataclass
class Params:
    variant: str = "base"                      # base | rsi | reclaim
    ma_len: int = 200
    dist_below_ma_pct: float = 0.05            # 5%
    slope_lookback: int = 5                    # MA200 today > MA200 5d ago
    rsi_period: int = 14
    rsi_cross_level: float = 30.0
    tp_pct: float = 0.10                        # 10%
    sl_pct: float = 0.08                        # 8%
    atr_mult: float = 2.0                       # stop = min(sl_pct, atr_mult*ATR/entry)
    time_stop: int = 30                         # bars
    be_trigger_pct: float = 0.06                # move stop to entry past this
    fees_bps: float = 10.0                      # 0.10% per side
    slip_bps: float = 5.0                       # 0.05% per side
    capital_per_trade: float = 1000.0
    allow_breakeven: bool = True


@dataclass
class TradeResult:
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_px: float
    exit_px: float
    shares: float
    pnl: float
    pnl_pct: float
    reason: str
    bars_held: int


def compute_indicators(df: pd.DataFrame, ma_len=200, rsi_period=14, slope_lookback=5) -> pd.DataFrame:
    out = df.copy()
    out["MA"] = moving_average(out["Close"], ma_len)
    out["ATR"] = wilder_atr(out["High"], out["Low"], out["Close"], 14)
    out["RSI"] = wilder_rsi(out["Close"], rsi_period)
    out["MA_slope_pos"] = (out["MA"] > out["MA"].shift(slope_lookback)).astype(int)
    return out


def rsi_cross_up(series: pd.Series, level: float) -> pd.Series:
    prev = series.shift(1)
    return (prev < level) & (series >= level)


def generate_signal_rows(df: pd.DataFrame, p: Params) -> pd.Series:
    ma_cond = df["Close"] <= (1 - p.dist_below_ma_pct) * df["MA"]
    if p.variant == "base":
        cond = ma_cond & (df["MA_slope_pos"] == 1)
    elif p.variant == "rsi":
        cond = ma_cond & rsi_cross_up(df["RSI"], p.rsi_cross_level)
    elif p.variant == "reclaim":
        cond = (df["Close"].shift(1) <= (1 - p.dist_below_ma_pct) * df["MA"].shift(1)) & (df["Close"] >= df["MA"])
    else:
        raise ValueError("Unknown variant")
    return cond.fillna(False)


def apply_fees_and_slippage(price: float, side: str, fees_bps: float, slip_bps: float) -> float:
    fee_mult = 1 + (fees_bps / 10000.0)
    slip_mult = 1 + (slip_bps / 10000.0) if side == "buy" else 1 - (slip_bps / 10000.0)
    if side == "buy":
        return price * fee_mult * slip_mult
    else:
        # For sells we charge fee as well; price received decreases by fees
        return price * slip_mult / fee_mult


def backtest(df: pd.DataFrame, p: Params) -> Tuple[List[TradeResult], pd.DataFrame]:
    df = df.copy().reset_index(drop=True)
    df = compute_indicators(df, ma_len=p.ma_len, rsi_period=p.rsi_period, slope_lookback=p.slope_lookback)

    signal_rows = generate_signal_rows(df, p)
    in_pos = False
    entry_idx = None
    entry_px_raw = None
    entry_px_exec = None
    shares = 0.0
    be_active = False

    trades: List[TradeResult] = []
    equity_curve = []  # (date, equity)

    # Running equity (sum of realized PnL only, since capital is separate per trade)
    equity = 0.0

    n = len(df)
    i = 0
    while i < n - 1:  # ensure we have i+1 for next open entries
        row = df.iloc[i]
        next_row = df.iloc[i+1]

        if not in_pos:
            # Check signal on close of day i -> enter at next day's open (i+1)
            if signal_rows.iloc[i] and not np.isnan(next_row["Open"]):
                entry_idx = i + 1
                entry_px_raw = float(next_row["Open"])
                entry_px_exec = apply_fees_and_slippage(entry_px_raw, "buy", p.fees_bps, p.slip_bps)
                shares = p.capital_per_trade / entry_px_exec
                be_active = False
                in_pos = True
                i += 1
                continue
            else:
                i += 1
                continue
        else:
            # Manage position starting at bar entry_idx
            bars_held = i - entry_idx + 1
            # Determine stop distance at entry (ATR and pct are computed at entry bar)
            atr_entry = float(df.iloc[entry_idx]["ATR"])
            pct_stop_dist = p.sl_pct * df.iloc[entry_idx]["Close"]  # approximate; use entry_px_exec * sl_pct
            # Use entry price for pct stop distance to be precise
            pct_stop_dist = p.sl_pct * entry_px_exec
            atr_stop_dist = p.atr_mult * atr_entry
            stop_dist = min(pct_stop_dist, atr_stop_dist)

            target_px = entry_px_exec * (1 + p.tp_pct)
            stop_px_initial = entry_px_exec - stop_dist
            stop_px = stop_px_initial

            # Breakeven activation check using current bar's High
            # We'll iterate bar-by-bar within this state machine
            # Since we check day by day, compute outcomes on day i
            cur = df.iloc[i]
            o, h, l, c = float(cur["Open"]), float(cur["High"]), float(cur["Low"]), float(cur["Close"])

            # Compute conservative intrabar event ordering
            # If gap through levels occurs at open, prioritize that.
            # Buy position exit rules:
            # 1) If time stop reached, exit at close.
            # 2) Else if open <= stop -> exit at open (gap down through stop).
            # 3) Else if open >= target -> exit at open (gap up to TP).
            # 4) Else if both high >= target and low <= stop during bar -> assume SL first.
            # 5) Else if low <= stop -> exit at stop.
            # 6) Else if high >= target -> exit at target.
            # 7) Else hold and possibly activate BE if high >= be_trigger.
            reason = None
            exit_px_exec = None

            # Time stop check first: if this is the time-stop bar, exit at close
            if bars_held >= p.time_stop:
                # exit at close with fees+slippage for sell
                exit_px_exec = apply_fees_and_slippage(c, "sell", p.fees_bps, p.slip_bps)
                reason = "time_stop"
            else:
                # Breakeven activation
                if p.allow_breakeven and (not be_active):
                    if h >= entry_px_exec * (1 + p.be_trigger_pct):
                        be_active = True
                        stop_px = max(stop_px, entry_px_exec)

                # Recompute stop if BE active
                if be_active:
                    stop_px = max(stop_px, entry_px_exec)

                # Gap exits at open
                if o <= stop_px:
                    exit_px_exec = apply_fees_and_slippage(o, "sell", p.fees_bps, p.slip_bps)
                    reason = "stop_gap"
                elif o >= target_px:
                    exit_px_exec = apply_fees_and_slippage(o, "sell", p.fees_bps, p.slip_bps)
                    reason = "tp_gap"
                else:
                    # Intrabar both levels?
                    both_hit = (h >= target_px) and (l <= stop_px)
                    if both_hit:
                        exit_px_exec = apply_fees_and_slippage(stop_px, "sell", p.fees_bps, p.slip_bps)
                        reason = "stop_then_tp_same_bar"
                    elif l <= stop_px:
                        exit_px_exec = apply_fees_and_slippage(stop_px, "sell", p.fees_bps, p.slip_bps)
                        reason = "stop"
                    elif h >= target_px:
                        exit_px_exec = apply_fees_and_slippage(target_px, "sell", p.fees_bps, p.slip_bps)
                        reason = "tp"

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
                in_pos = False
                entry_idx = None
                entry_px_raw = None
                entry_px_exec = None
                shares = 0.0
                be_active = False
                i += 1
                continue
            else:
                # Still in position; go to next bar
                i += 1
                continue

    # If still in position at the end, force exit at last close
    if in_pos:
        last = df.iloc[-1]
        exit_px_exec = apply_fees_and_slippage(float(last["Close"]), "sell", p.fees_bps, p.slip_bps)
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

    ec_df = pd.DataFrame(equity_curve, columns=["Date", "Equity"]).set_index("Date")
    return trades, ec_df


# ---------------------- Metrics ----------------------

def max_drawdown(equity_series: pd.Series) -> float:
    if equity_series.empty:
        return 0.0
    roll_max = equity_series.cummax()
    dd = equity_series - roll_max
    return float(dd.min())  # negative number


def profit_factor(trades: List[TradeResult]) -> float:
    gains = sum(max(t.pnl, 0.0) for t in trades)
    losses = -sum(min(t.pnl, 0.0) for t in trades)
    if losses == 0:
        return float('inf') if gains > 0 else 0.0
    return gains / losses


def sharpe_sortino_from_equity(ec: pd.DataFrame) -> Tuple[float, float]:
    if ec.empty or len(ec) < 2:
        return 0.0, 0.0
    # Use daily diffs as "returns" on the separated equity (not annualized here)
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


def analyze(trades: List[TradeResult], ec: pd.DataFrame, df: pd.DataFrame) -> Dict[str, float]:
    n_trades = len(trades)
    wins = sum(1 for t in trades if t.pnl > 0)
    losses = sum(1 for t in trades if t.pnl <= 0)
    win_rate = wins / n_trades if n_trades else 0.0
    pf = profit_factor(trades)

    avg_win = np.mean([t.pnl for t in trades if t.pnl > 0]) if wins else 0.0
    avg_loss = np.mean([-t.pnl for t in trades if t.pnl <= 0]) if losses else 0.0
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    mdd = max_drawdown(ec["Equity"] if not ec.empty else pd.Series(dtype=float))
    sharpe, sortino = sharpe_sortino_from_equity(ec)

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
        "profit_factor": pf,
        "expectancy_per_trade": expectancy,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "max_drawdown": mdd,
        "sharpe_like": sharpe,
        "sortino_like": sortino,
        "time_in_market": time_in_mkt,
        "trades_per_year": tpy,
        "total_pnl": total_pnl
    }


def print_summary(metrics: Dict[str, float], p: Params):
    print("Strategy Summary")
    for k, v in asdict(p).items():
        print(f"  {k}: {v}")
    print("-" * 40)
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")


# ---------------------- Grid Search ----------------------

def grid_search(df: pd.DataFrame) -> pd.DataFrame:
    try:
        from tqdm import tqdm
    except ImportError:
        print("Warning: tqdm not installed. Install with 'pip install tqdm' for progress bar.")
        tqdm = None
    
    rows = []
    variants = ["base", "rsi", "reclaim"]
    dist_list = [0.03, 0.05, 0.07, 0.10]
    tp_list = [0.08, 0.10, 0.12]
    sl_list = [0.06, 0.08, 0.10]
    atr_mult_list = [1.5, 2.0]
    time_stop_list = [20, 30, 45]
    ma_list = [180, 200, 220]
    be_list = [True, False]

    # Calculate total combinations
    total = (len(variants) * len(dist_list) * len(tp_list) * len(sl_list) * 
             len(atr_mult_list) * len(time_stop_list) * len(ma_list) * len(be_list))
    
    print(f"Total combinations to test: {total}")
    print(f"Estimated time: ~{total * 0.1:.1f} seconds (assuming ~0.1s per backtest)")
    
    # Create progress bar if tqdm is available
    pbar = tqdm(total=total, desc="Grid Search Progress", unit="run") if tqdm else None

    for variant in variants:
        for dist in dist_list:
            for tp in tp_list:
                for sl in sl_list:
                    for atrm in atr_mult_list:
                        for ts in time_stop_list:
                            for ma in ma_list:
                                for be in be_list:
                                    p = Params(
                                        variant=variant,
                                        dist_below_ma_pct=dist,
                                        tp_pct=tp,
                                        sl_pct=sl,
                                        atr_mult=atrm,
                                        time_stop=ts,
                                        ma_len=ma,
                                        allow_breakeven=be
                                    )
                                    trades, ec = backtest(df, p)
                                    metrics = analyze(trades, ec, df)
                                    row = {
                                        "variant": variant,
                                        "dist": dist,
                                        "tp": tp,
                                        "sl": sl,
                                        "atr_mult": atrm,
                                        "time_stop": ts,
                                        "ma": ma,
                                        "breakeven": be,
                                        **metrics
                                    }
                                    rows.append(row)
                                    if pbar:
                                        pbar.update(1)
    
    if pbar:
        pbar.close()
    
    res = pd.DataFrame(rows)
    # Sort by Profit Factor then Total PnL then lower Max DD
    res = res.sort_values(by=["profit_factor", "total_pnl", "max_drawdown"], ascending=[False, False, True])
    return res


# ---------------------- I/O Helpers ----------------------

def load_ohlc_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize column names
    cols = {c.lower(): c for c in df.columns}
    required = ["date", "open", "high", "low", "close"]
    # Map in a case-insensitive way
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


def get_project_root() -> str:
    """Get the project root directory (parent of src/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Path to daily OHLC CSV for BTCUSDT (default: data/BTCUSDT_daily.csv)")
    parser.add_argument("--config", help="Path to config CSV file (loads params from config/)")
    parser.add_argument("--variant", choices=["base", "rsi", "reclaim"], default="base")
    parser.add_argument("--capital_per_trade", type=float, default=1000.0)
    parser.add_argument("--fees_bps", type=float, default=10.0)
    parser.add_argument("--slip_bps", type=float, default=5.0)
    parser.add_argument("--tp_pct", type=float, default=0.10)
    parser.add_argument("--sl_pct", type=float, default=0.08)
    parser.add_argument("--atr_mult", type=float, default=2.0)
    parser.add_argument("--time_stop", type=int, default=30)
    parser.add_argument("--be_trigger_pct", type=float, default=0.06)
    parser.add_argument("--ma_len", type=int, default=200)
    parser.add_argument("--dist_below_ma_pct", type=float, default=0.05)
    parser.add_argument("--grid", action="store_true", help="Run the recommended parameter sweep")
    parser.add_argument("--no_breakeven", action="store_true", help="Disable breakeven move")
    args = parser.parse_args()

    # Determine project root and default paths
    project_root = get_project_root()
    
    # Default CSV path if not provided
    if not args.csv:
        args.csv = os.path.join(project_root, "data", "BTCUSDT_daily.csv")
    
    # Load CSV data
    df = load_ohlc_csv(args.csv)

    # Load params from config if specified
    if args.config:
        try:
            from config import load_params_from_csv
            config_path = args.config if os.path.isabs(args.config) else os.path.join(project_root, "config", args.config)
            config = load_params_from_csv(config_path)
            p = config.to_params()
            print(f"Loaded parameters from: {config_path}")
        except Exception as e:
            print(f"Error loading config: {e}")
            return
    else:
        # Use command-line arguments
        p = Params(
            variant=args.variant,
            capital_per_trade=args.capital_per_trade,
            fees_bps=args.fees_bps,
            slip_bps=args.slip_bps,
            tp_pct=args.tp_pct,
            sl_pct=args.sl_pct,
            atr_mult=args.atr_mult,
            time_stop=args.time_stop,
            be_trigger_pct=args.be_trigger_pct,
            ma_len=args.ma_len,
            dist_below_ma_pct=args.dist_below_ma_pct,
            allow_breakeven=(not args.no_breakeven)
        )

    if args.grid:
        print("Running grid search... (this can take a while)")
        res = grid_search(df)
        out_path = os.path.join(project_root, "data", "grid_results.csv")
        res.to_csv(out_path, index=False)
        print(f"Grid complete. Saved: {out_path}")
        print("Top 10 rows:")
        print(res.head(10).to_string(index=False))
        return

    trades, ec = backtest(df, p)
    metrics = analyze(trades, ec, df)
    print_summary(metrics, p)

    # Also dump individual trades
    if trades:
        td = pd.DataFrame([{
            "entry_date": t.entry_date,
            "exit_date": t.exit_date,
            "entry_px": t.entry_px,
            "exit_px": t.exit_px,
            "shares": t.shares,
            "pnl": t.pnl,
            "pnl_pct": t.pnl_pct,
            "reason": t.reason,
            "bars_held": t.bars_held
        } for t in trades])
        out_path = os.path.join(project_root, "data", "trades.csv")
        td.to_csv(out_path, index=False)
        print(f"Saved individual trades to: {out_path}")


if __name__ == "__main__":
    main()
