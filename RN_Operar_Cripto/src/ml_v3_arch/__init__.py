"""
ML v3 - Arquitetura SOLID para Trading com Deep Learning

Módulo completamente refatorado usando:
- SOLID Principles
- Clean Architecture
- Domain-Driven Design
- Design Patterns

Coexiste com ml_v2 para permitir migração gradual.
"""

__version__ = "3.0.0"
__author__ = "Silvino Miranda"
__status__ = "Development"

# Public API
from .domain import (
    ModelConfig,
    BacktestConfig,
    TradeDirection,
    TradeStatus,
    MarketDirection,
)

from .factories import ModelFactory

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__status__",
    
    # Domain
    "ModelConfig",
    "BacktestConfig",
    "TradeDirection",
    "TradeStatus",
    "MarketDirection",
    
    # Factories
    "ModelFactory",
]
