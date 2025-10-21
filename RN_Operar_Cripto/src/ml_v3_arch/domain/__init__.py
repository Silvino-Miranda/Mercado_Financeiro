"""
Módulo de domínio com Value Objects e Entities.
Representa o core business do sistema de trading.
"""
from .entities import (
    TradeDirection,
    TradeStatus,
    MarketDirection,
    TradeSignal,
    Trade,
    MarketData,
    ModelConfig,
    BacktestConfig,
    BacktestMetrics,
)

__all__ = [
    "TradeDirection",
    "TradeStatus",
    "MarketDirection",
    "TradeSignal",
    "Trade",
    "MarketData",
    "ModelConfig",
    "BacktestConfig",
    "BacktestMetrics",
]
