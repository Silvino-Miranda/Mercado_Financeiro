"""
Interfaces abstratas para garantir DIP e ISP.
Todos os módulos devem depender destas abstrações, não de implementações concretas.
"""
from .base_model import BaseModel, Trainable, Predictable, Evaluable
from .base_preprocessor import BasePreprocessor, DataTransformer, DataScaler
from .base_backtester import BaseBacktester, TradingStrategy
from .base_evaluator import BaseEvaluator, MetricsCalculator

__all__ = [
    # Model interfaces
    "BaseModel",
    "Trainable",
    "Predictable",
    "Evaluable",
    
    # Preprocessor interfaces
    "BasePreprocessor",
    "DataTransformer",
    "DataScaler",
    
    # Backtester interfaces
    "BaseBacktester",
    "TradingStrategy",
    
    # Evaluator interfaces
    "BaseEvaluator",
    "MetricsCalculator",
]
