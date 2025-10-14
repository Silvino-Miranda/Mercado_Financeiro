# 🔬 Plano de Refatoração: Módulo Backtest

## 📊 Arquivo Atual: `mr_backtest.py` (600+ linhas)

### Problemas:
- ❌ Tudo em um único arquivo monolítico
- ❌ Indicadores misturados com lógica de backtest
- ❌ Estratégias hardcoded
- ❌ Difícil de testar e manter

## ✅ Estrutura Nova

```
src/backtest/
├── __init__.py           # Exports principais
├── __main__.py           # CLI: python -m src.backtest
├── engine.py             # BacktestEngine class
├── strategies.py         # Strategy classes (Base, RSI, Reclaim)
├── indicators.py         # Technical indicators
├── types.py              # Dataclasses (Params, Trade, etc)
└── utils.py              # Helper functions
```

## 📋 Divisão de Responsabilidades

### 1. `types.py` - Dataclasses e Types
```python
@dataclass
class Params:
    """Strategy parameters"""
    variant: str
    ma_len: int
    dist_below_ma_pct: float
    tp_pct: float
    sl_pct: float
    # ... rest

@dataclass
class Trade:
    """Individual trade record"""
    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    pnl: float
    exit_reason: str

@dataclass
class BacktestResult:
    """Backtest results container"""
    trades: List[Trade]
    metrics: Dict[str, float]
    equity_curve: List[float]
```

### 2. `indicators.py` - Technical Indicators
```python
def wilder_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI using Wilder's smoothing"""
    pass

def wilder_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using Wilder's smoothing"""
    pass

def moving_average(prices: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average"""
    pass

def ma_slope(ma: pd.Series, lookback: int = 5) -> pd.Series:
    """MA slope calculation"""
    pass
```

### 3. `strategies.py` - Strategy Classes
```python
class Strategy(ABC):
    """Base strategy class"""
    
    @abstractmethod
    def should_enter(self, df: pd.DataFrame, i: int, params: Params) -> bool:
        """Check if should enter trade"""
        pass
    
    @abstractmethod
    def calculate_stops(self, entry_price: float, params: Params, df: pd.DataFrame, i: int) -> Tuple[float, float]:
        """Calculate TP and SL levels"""
        pass

class BaseStrategy(Strategy):
    """Original BASE strategy"""
    
    def should_enter(self, df: pd.DataFrame, i: int, params: Params) -> bool:
        price = df.loc[i, 'Close']
        ma = df.loc[i, 'MA']
        slope = df.loc[i, 'MA_Slope']
        
        threshold = ma * (1.0 - params.dist_below_ma_pct)
        return price < threshold and slope > 0
    
    def calculate_stops(self, entry_price: float, params: Params, df: pd.DataFrame, i: int) -> Tuple[float, float]:
        tp = entry_price * (1.0 + params.tp_pct)
        sl = entry_price * (1.0 - params.sl_pct)
        return tp, sl

class RSIStrategy(Strategy):
    """RSI-based strategy"""
    pass

class ReclaimStrategy(Strategy):
    """Reclaim-based strategy"""
    pass

# Strategy factory
def get_strategy(variant: str) -> Strategy:
    strategies = {
        'base': BaseStrategy(),
        'rsi': RSIStrategy(),
        'reclaim': ReclaimStrategy()
    }
    return strategies[variant]
```

### 4. `engine.py` - Backtest Engine
```python
class BacktestEngine:
    """
    Core backtesting engine.
    
    Example:
        >>> engine = BacktestEngine(df, params)
        >>> result = engine.run()
        >>> print(result.metrics)
    """
    
    def __init__(self, df: pd.DataFrame, params: Params):
        self.df = df.copy()
        self.params = params
        self.strategy = get_strategy(params.variant)
        self._prepare_dataframe()
    
    def _prepare_dataframe(self):
        """Add indicators to dataframe"""
        # Add MA
        self.df['MA'] = moving_average(self.df['Close'], self.params.ma_len)
        
        # Add MA slope
        self.df['MA_Slope'] = ma_slope(self.df['MA'], self.params.slope_lookback)
        
        # Add RSI if needed
        if self.params.variant == 'rsi':
            self.df['RSI'] = wilder_rsi(self.df['Close'], self.params.rsi_period)
        
        # Add ATR
        self.df['ATR'] = wilder_atr(
            self.df['High'],
            self.df['Low'],
            self.df['Close'],
            period=14
        )
    
    def run(self) -> BacktestResult:
        """Execute backtest"""
        trades = []
        position = None
        equity_curve = []
        
        for i in range(self.params.ma_len, len(self.df)):
            # Exit logic
            if position:
                exit_info = self._check_exit(position, i)
                if exit_info:
                    trade = self._close_position(position, exit_info)
                    trades.append(trade)
                    position = None
            
            # Entry logic
            if not position and self.strategy.should_enter(self.df, i, self.params):
                position = self._open_position(i)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades)
        
        return BacktestResult(
            trades=trades,
            metrics=metrics,
            equity_curve=equity_curve
        )
    
    def _open_position(self, i: int) -> Dict:
        """Open new position"""
        pass
    
    def _close_position(self, position: Dict, exit_info: Dict) -> Trade:
        """Close position and create Trade object"""
        pass
    
    def _check_exit(self, position: Dict, i: int) -> Optional[Dict]:
        """Check if should exit position"""
        pass
    
    def _calculate_metrics(self, trades: List[Trade]) -> Dict[str, float]:
        """Calculate performance metrics"""
        pass
```

### 5. `__main__.py` - CLI Interface
```python
def main():
    parser = argparse.ArgumentParser(description='Run backtest')
    
    parser.add_argument('--csv', required=True, help='Path to OHLC CSV')
    parser.add_argument('--config', help='Path to config CSV')
    parser.add_argument('--variant', default='base', choices=['base', 'rsi', 'reclaim'])
    parser.add_argument('--ma-len', type=int, default=220)
    parser.add_argument('--tp-pct', type=float, default=0.10)
    parser.add_argument('--sl-pct', type=float, default=0.10)
    # ... more args
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.csv)
    
    # Create params
    params = Params(...)
    
    # Run backtest
    engine = BacktestEngine(df, params)
    result = engine.run()
    
    # Print results
    print_results(result)

if __name__ == '__main__':
    main()
```

## ✅ Benefícios

1. **Separação de Responsabilidades**: Cada arquivo tem um propósito claro
2. **Testabilidade**: Fácil testar cada componente isoladamente
3. **Extensibilidade**: Adicionar novas estratégias = nova classe
4. **Reutilização**: Indicadores podem ser usados em outros módulos
5. **Manutenibilidade**: Código mais limpo e organizado

## 🚀 Migração

### Ordem de Implementação:
1. ✅ Criar `types.py` (dataclasses)
2. ✅ Migrar indicadores para `indicators.py`
3. ✅ Criar `strategies.py` (Base class + 3 variants)
4. ✅ Criar `engine.py` (BacktestEngine)
5. ✅ Criar `utils.py` (helpers)
6. ✅ Criar `__main__.py` (CLI)
7. ✅ Atualizar `__init__.py` (exports)

**Tempo estimado**: 30-45 minutos

**Quer prosseguir com esta estrutura?**
