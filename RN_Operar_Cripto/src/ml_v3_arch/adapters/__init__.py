"""
Adapters - Padrão Adapter para compatibilidade entre v2 e v3.

Permite que código existente da v2 use a arquitetura v3 sem modificações.
Segue o Princípio Open/Closed: extensível sem modificar v2.
"""
from .preprocessor_adapter import DataPreprocessorAdapter
from .model_adapter import ModelBuilderAdapter
from .backtest_adapter import BacktestAdapter

__all__ = [
    'DataPreprocessorAdapter',
    'ModelBuilderAdapter',
    'BacktestAdapter',
]
