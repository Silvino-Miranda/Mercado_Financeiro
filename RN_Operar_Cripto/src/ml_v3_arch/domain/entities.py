"""
Value Objects e Entities do domínio de trading.
Princípios aplicados:
- DDD (Domain-Driven Design): Modelagem do domínio de negócio
- Immutability: Value Objects são imutáveis
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TradeDirection(Enum):
    """Direção do trade."""
    LONG = 1
    SHORT = -1
    NEUTRAL = 0


class TradeStatus(Enum):
    """Status do trade."""
    ENTRY = "Entrada"
    EXIT = "Saida"


class MarketDirection(Enum):
    """Direção do mercado (classificação)."""
    BAIXA = 0
    LATERAL = 1
    ALTA = 2


@dataclass(frozen=True)
class TradeSignal:
    """
    Value Object: Sinal de trading.
    Imutável após criação.
    """
    timestamp: datetime
    direction: TradeDirection
    confidence: float
    price: float
    predicted_price: Optional[float] = None
    
    def __post_init__(self):
        """Validações."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence deve estar entre 0 e 1, got {self.confidence}")
        if self.price <= 0:
            raise ValueError(f"Price deve ser positivo, got {self.price}")


@dataclass
class Trade:
    """
    Entity: Representa um trade executado.
    Mutável (status pode mudar).
    """
    entry_date: datetime
    entry_price: float
    direction: TradeDirection
    quantity: float
    status: TradeStatus = TradeStatus.ENTRY
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    fee: float = 0.0
    slippage: float = 0.0
    
    def close(self, exit_date: datetime, exit_price: float, fee: float = 0.0):
        """Fecha o trade."""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.status = TradeStatus.EXIT
        self.fee += fee
    
    @property
    def gross_return(self) -> Optional[float]:
        """Retorno bruto (sem custos)."""
        if self.exit_price is None:
            return None
        
        price_diff = self.exit_price - self.entry_price
        return price_diff / self.entry_price * self.direction.value
    
    @property
    def net_return(self) -> Optional[float]:
        """Retorno líquido (com custos)."""
        if self.gross_return is None:
            return None
        
        total_fees = self.fee + self.slippage
        return self.gross_return - total_fees
    
    @property
    def profit_loss(self) -> Optional[float]:
        """P&L em dólares."""
        if self.net_return is None:
            return None
        
        return self.quantity * self.entry_price * self.net_return
    
    @property
    def is_closed(self) -> bool:
        """Verifica se o trade está fechado."""
        return self.status == TradeStatus.EXIT


@dataclass
class MarketData:
    """Value Object: Dados de mercado em um timestamp."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __post_init__(self):
        """Validações."""
        if self.high < max(self.open, self.close):
            raise ValueError("High deve ser >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError("Low deve ser <= min(open, close)")
        if any(x <= 0 for x in [self.open, self.high, self.low, self.close]):
            raise ValueError("Preços devem ser positivos")


@dataclass
class ModelConfig:
    """
    Value Object: Configuração de modelo.
    Centraliza hiperparâmetros.
    """
    model_type: str  # 'lstm', 'gru', 'directional'
    lookback: int = 60
    lstm_units: int = 64
    lstm_layers: int = 2
    dropout: float = 0.3
    learning_rate: float = 1e-3
    batch_size: int = 64
    epochs: int = 100
    patience: int = 15
    
    def __post_init__(self):
        """Validações."""
        if self.lookback <= 0:
            raise ValueError("Lookback deve ser > 0")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("Dropout deve estar entre 0 e 1")
        if self.learning_rate <= 0:
            raise ValueError("Learning rate deve ser > 0")
        if self.batch_size <= 0:
            raise ValueError("Batch size deve ser > 0")


@dataclass
class BacktestConfig:
    """Value Object: Configuração de backtest."""
    initial_capital: float = 100000.0
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    position_size: float = 0.95
    min_confidence: float = 0.6
    threshold_bps: float = 20.0
    
    def __post_init__(self):
        """Validações."""
        if self.initial_capital <= 0:
            raise ValueError("Capital inicial deve ser > 0")
        if not 0.0 < self.position_size <= 1.0:
            raise ValueError("Position size deve estar entre 0 e 1")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("Min confidence deve estar entre 0 e 1")


@dataclass
class BacktestMetrics:
    """Value Object: Métricas de backtest."""
    total_return: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    exposure: float
    final_equity: float
    initial_capital: float
    
    @property
    def risk_adjusted_return(self) -> float:
        """Retorno ajustado pelo risco."""
        if self.max_drawdown == 0:
            return 0.0
        return self.total_return / abs(self.max_drawdown)
    
    def to_dict(self) -> dict:
        """Converte para dict."""
        return {
            'total_return': self.total_return,
            'cagr': self.cagr,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'exposure': self.exposure,
            'final_equity': self.final_equity,
            'initial_capital': self.initial_capital,
            'risk_adjusted_return': self.risk_adjusted_return
        }
