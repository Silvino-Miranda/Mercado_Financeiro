"""
Interfaces para backtesting e estratégias de trading.
Princípios aplicados:
- Strategy Pattern: Diferentes estratégias de trading
- OCP (Open/Closed): Extensível sem modificar código existente
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Protocol
import numpy as np
import pandas as pd


class TradingStrategy(Protocol):
    """
    Interface para estratégias de trading.
    
    Permite diferentes implementações:
    - RegressionStrategy: Baseada em predições de preço
    - DirectionalStrategy: Baseada em classificação direcional
    - CustomStrategy: Estratégias personalizadas
    """
    
    def generate_signals(
        self, 
        predictions: np.ndarray, 
        prices: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        """
        Gera sinais de trading baseado nas predições.
        
        Args:
            predictions: Predições do modelo
            prices: Preços atuais
            **kwargs: Argumentos adicionais (threshold, confidence, etc)
            
        Returns:
            Array de sinais: 1 (long), -1 (short), 0 (sem posição)
        """
        ...
    
    def calculate_position_size(
        self, 
        capital: float, 
        price: float,
        signal: int,
        **kwargs
    ) -> float:
        """
        Calcula tamanho da posição.
        
        Args:
            capital: Capital disponível
            price: Preço atual
            signal: Sinal de trading
            **kwargs: Argumentos adicionais
            
        Returns:
            Quantidade a comprar/vender
        """
        ...


class BaseBacktester(ABC):
    """
    Interface base para engines de backtest.
    
    Responsabilidades:
    - Simular execução de trades
    - Calcular custos (fees, slippage)
    - Gerenciar capital e posições
    - Gerar relatórios de performance
    """
    
    def __init__(
        self,
        initial_capital: float,
        fee_bps: float,
        slippage_bps: float,
        **kwargs
    ):
        """
        Args:
            initial_capital: Capital inicial
            fee_bps: Taxa em basis points
            slippage_bps: Slippage em basis points
            **kwargs: Configurações adicionais
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.position = 0.0
        self.history = []
    
    @abstractmethod
    def run_backtest(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        **kwargs
    ) -> pd.DataFrame:
        """
        Executa o backtest.
        
        Args:
            df: DataFrame com dados de mercado
            predictions: Predições do modelo
            **kwargs: Argumentos adicionais
            
        Returns:
            DataFrame com histórico de operações
        """
        pass
    
    @abstractmethod
    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calcula métricas de performance.
        
        Returns:
            Dict com métricas (Sharpe, Sortino, Max DD, etc)
        """
        pass
    
    @abstractmethod
    def calculate_fees(self, amount: float) -> float:
        """
        Calcula taxas de transação.
        
        Args:
            amount: Valor da transação
            
        Returns:
            Taxa a pagar
        """
        pass
    
    @abstractmethod
    def apply_slippage(self, price: float, direction: str) -> float:
        """
        Aplica slippage ao preço.
        
        Args:
            price: Preço base
            direction: 'buy' ou 'sell'
            
        Returns:
            Preço com slippage
        """
        pass
    
    def save_history(self, path: str) -> None:
        """
        Salva histórico de operações.
        
        Args:
            path: Caminho do arquivo
        """
        df = pd.DataFrame(self.history)
        df.to_csv(path, sep=';', index=False)
    
    @property
    def total_return(self) -> float:
        """Retorna o retorno total."""
        return (self.current_capital - self.initial_capital) / self.initial_capital
