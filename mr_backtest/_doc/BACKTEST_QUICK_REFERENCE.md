# Backtest Module - Quick Reference

## 🚀 Quick Start

### Installation
```bash
cd c:\_Dev\Github\Python\Mercado_Financeiro\mr_backtest
# Dependencies already installed via project requirements
```

### Basic Usage
```bash
# Single backtest
python -m src.backtest --csv data/BTCUSDT_daily.csv --variant base

# Grid search
python -m src.backtest --csv data/BTCUSDT_daily.csv --grid

# Custom parameters
python -m src.backtest --csv data/BTCUSDT_daily.csv \
    --variant rsi --tp_pct 0.12 --sl_pct 0.08
```

---

## 📚 API Reference

### Core Classes

#### `BacktestEngine`
```python
from src.backtest import BacktestEngine, Params

params = Params(variant="base", tp_pct=0.10)
engine = BacktestEngine(params)
result = engine.run(df)  # Returns BacktestResult
```

#### `Params` (Dataclass)
```python
from src.backtest import Params

params = Params(
    variant="base",           # "base" | "rsi" | "reclaim"
    ma_len=200,               # Moving average period
    dist_below_ma_pct=0.05,   # Distance below MA for entry (5%)
    tp_pct=0.10,              # Take profit (10%)
    sl_pct=0.08,              # Stop loss (8%)
    atr_mult=2.0,             # ATR multiplier
    time_stop=30,             # Max bars to hold
    be_trigger_pct=0.06,      # Breakeven trigger (6%)
    fees_bps=10.0,            # Fees per side (0.10%)
    slip_bps=5.0,             # Slippage per side (0.05%)
    capital_per_trade=1000.0, # Capital per trade
    allow_breakeven=True      # Enable breakeven logic
)
```

#### `Strategy` (ABC)
```python
from src.backtest.strategies import Strategy, get_strategy

# Get strategy instance
strategy = get_strategy("base", params)  # "base" | "rsi" | "reclaim"

# Or instantiate directly
from src.backtest.strategies import BaseStrategy
strategy = BaseStrategy(params)
```

---

## 🎯 Strategy Variants

### 1. Base Strategy
**Entry:** Price closes below MA by `dist_below_ma_pct` AND MA has positive slope

```python
params = Params(variant="base", dist_below_ma_pct=0.05, ma_len=200)
```

### 2. RSI Strategy
**Entry:** Price closes below MA by `dist_below_ma_pct` AND RSI crosses above 30

```python
params = Params(variant="rsi", dist_below_ma_pct=0.05, rsi_cross_level=30.0)
```

### 3. Reclaim Strategy
**Entry:** Previous close was below MA threshold AND current close reclaims MA

```python
params = Params(variant="reclaim", dist_below_ma_pct=0.05)
```

---

## 📊 Metrics Available

```python
result = engine.run(df)
metrics = result.metrics

# Available metrics:
metrics["trades"]                # Number of trades
metrics["win_rate"]              # Win rate (0.0 to 1.0)
metrics["profit_factor"]         # Profit factor
metrics["expectancy_per_trade"]  # Average expectancy
metrics["avg_win"]               # Average winning trade
metrics["avg_loss"]              # Average losing trade
metrics["max_drawdown"]          # Maximum drawdown
metrics["sharpe_like"]           # Sharpe-like ratio
metrics["sortino_like"]          # Sortino-like ratio
metrics["time_in_market"]        # % of time in position
metrics["trades_per_year"]       # Annualized trade frequency
metrics["total_pnl"]             # Total profit/loss
```

---

## 🔧 Indicators

### Wilder RSI
```python
from src.backtest.indicators import wilder_rsi

rsi = wilder_rsi(df["Close"], period=14)
```

### Wilder ATR
```python
from src.backtest.indicators import wilder_atr

atr = wilder_atr(df["High"], df["Low"], df["Close"], period=14)
```

### Moving Average
```python
from src.backtest.indicators import moving_average

ma = moving_average(df["Close"], window=200)
```

### MA Slope
```python
from src.backtest.indicators import ma_slope

slope_pos = ma_slope(ma_series, lookback=5)  # Returns 1 or 0
```

### RSI Cross Up
```python
from src.backtest.indicators import rsi_cross_up

crosses = rsi_cross_up(rsi_series, level=30.0)  # Returns boolean series
```

---

## 🛠️ Utilities

### Load OHLC CSV
```python
from src.backtest.utils import load_ohlc_csv

df = load_ohlc_csv("data/BTCUSDT_daily.csv")
# Returns DataFrame with: Date, Open, High, Low, Close
```

### Apply Trading Costs
```python
from src.backtest.utils import apply_fees_and_slippage

entry_px = apply_fees_and_slippage(price=50000, side="buy", fees_bps=10, slip_bps=5)
exit_px = apply_fees_and_slippage(price=55000, side="sell", fees_bps=10, slip_bps=5)
```

---

## 📝 Complete Example

```python
from src.backtest import BacktestEngine, Params, load_ohlc_csv
import pandas as pd

# 1. Load data
df = load_ohlc_csv("data/BTCUSDT_daily.csv")
print(f"Loaded {len(df)} bars")

# 2. Configure parameters
params = Params(
    variant="rsi",
    ma_len=200,
    dist_below_ma_pct=0.05,
    tp_pct=0.12,
    sl_pct=0.08,
    atr_mult=2.0,
    time_stop=30,
    be_trigger_pct=0.06,
    fees_bps=10.0,
    slip_bps=5.0,
    capital_per_trade=1000.0,
    allow_breakeven=True
)

# 3. Run backtest
engine = BacktestEngine(params)
result = engine.run(df)

# 4. Access results
print(f"\nResults:")
print(f"  Trades: {result.metrics['trades']}")
print(f"  Win Rate: {result.metrics['win_rate']:.2%}")
print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
print(f"  Total PnL: ${result.metrics['total_pnl']:.2f}")
print(f"  Max Drawdown: ${result.metrics['max_drawdown']:.2f}")

# 5. Analyze trades
for trade in result.trades[-5:]:  # Last 5 trades
    print(f"\n  Entry: {trade.entry_date.date()} @ ${trade.entry_px:.2f}")
    print(f"  Exit:  {trade.exit_date.date()} @ ${trade.exit_px:.2f}")
    print(f"  PnL:   ${trade.pnl:.2f} ({trade.pnl_pct:.2%})")
    print(f"  Reason: {trade.reason}")
    print(f"  Bars held: {trade.bars_held}")

# 6. Equity curve
print(f"\nEquity Curve:")
print(result.equity_curve.tail())

# 7. Save results
result.equity_curve.to_csv("equity_curve.csv")
trades_df = pd.DataFrame([vars(t) for t in result.trades])
trades_df.to_csv("trades.csv", index=False)
```

---

## 🎨 Extending the Module

### Adding a New Strategy

1. Create new class in `strategies.py`:
```python
class MyStrategy(Strategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Your signal logic here
        return (df["Close"] < df["MA"]).fillna(False)
```

2. Register in factory:
```python
def get_strategy(variant: str, params: Params) -> Strategy:
    strategies = {
        "base": BaseStrategy,
        "rsi": RSIStrategy,
        "reclaim": ReclaimStrategy,
        "my_strategy": MyStrategy  # Add here
    }
    # ... rest of function
```

### Adding a New Indicator

Add function to `indicators.py`:
```python
def my_indicator(series: pd.Series, period: int = 20) -> pd.Series:
    """
    My custom indicator.
    
    Args:
        series: Price series
        period: Calculation period
    
    Returns:
        Indicator values
    """
    return series.rolling(period).std()  # Example
```

### Adding New Metrics

Extend `_calculate_metrics()` in `engine.py`:
```python
def _calculate_metrics(self, trades, ec, df):
    metrics = {
        # ... existing metrics
        "my_custom_metric": self._calculate_my_metric(trades)
    }
    return metrics
```

---

## 🐛 Common Issues

### Issue: "CSV file not found"
**Solution:** Use absolute path or ensure file exists
```bash
python -m src.backtest --csv "$(pwd)/data/BTCUSDT_daily.csv"
```

### Issue: "0 trades generated"
**Causes:**
- Not enough data (need 200+ bars for MA200)
- Parameters too restrictive
- No valid entry signals in data

**Solution:** Check data length and adjust parameters

### Issue: "Import error"
**Solution:** Run from project root
```bash
cd c:\_Dev\Github\Python\Mercado_Financeiro\mr_backtest
python -m src.backtest ...
```

---

## 📖 Further Reading

- **Full documentation:** `docs/BACKTEST_REFACTORING_DONE.md`
- **Architecture plan:** `BACKTEST_REFACTOR_PLAN.md`
- **Summary:** `docs/BACKTEST_MODULE_SUMMARY.md`

---

## 💬 Support

For issues or questions:
1. Check documentation in `docs/`
2. Review code comments and docstrings
3. Examine test files for usage examples

---

**Last Updated:** October 13, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
