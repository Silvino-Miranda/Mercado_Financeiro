"""
Interfaces para preprocessamento de dados.
Princípios aplicados:
- SRP (Single Responsibility): Cada interface tem uma responsabilidade
- ISP (Interface Segregation): Interfaces específicas
"""
from abc import ABC, abstractmethod
from typing import Tuple, List, Protocol
import numpy as np
import pandas as pd


class DataScaler(Protocol):
    """Interface para scalers de dados."""
    
    def fit(self, data: np.ndarray) -> 'DataScaler':
        """
        Ajusta o scaler aos dados.
        
        Args:
            data: Dados de treino
            
        Returns:
            Self para chaining
        """
        ...
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """
        Transforma os dados.
        
        Args:
            data: Dados a transformar
            
        Returns:
            Dados transformados
        """
        ...
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        Reverte a transformação.
        
        Args:
            data: Dados transformados
            
        Returns:
            Dados originais
        """
        ...


class DataTransformer(Protocol):
    """Interface para transformadores de dados."""
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transforma DataFrame em features e targets.
        
        Args:
            df: DataFrame de entrada
            
        Returns:
            Tuple (X, y)
        """
        ...


class BasePreprocessor(ABC):
    """
    Interface base para preprocessadores.
    
    Responsabilidades:
    - Normalização de features e targets
    - Criação de sequências temporais
    - Garantir zero vazamento de dados
    """
    
    def __init__(
        self, 
        feature_cols: List[str], 
        target_col: str,
        lookback: int
    ):
        """
        Args:
            feature_cols: Colunas de features
            target_col: Coluna target
            lookback: Janela temporal
        """
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.lookback = lookback
        self._fitted = False
    
    @abstractmethod
    def fit(self, df_train: pd.DataFrame) -> 'BasePreprocessor':
        """
        Ajusta o preprocessador aos dados de treino.
        CRÍTICO: Apenas chamar no treino para evitar vazamento!
        
        Args:
            df_train: DataFrame de treino
            
        Returns:
            Self para chaining
        """
        pass
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transforma dados usando parâmetros já ajustados.
        
        Args:
            df: DataFrame a transformar
            
        Returns:
            Tuple (X_sequences, y_sequences)
            
        Raises:
            RuntimeError: Se não foi fitted antes
        """
        pass
    
    def fit_transform(
        self, 
        df_train: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit e transform em uma chamada.
        
        Args:
            df_train: DataFrame de treino
            
        Returns:
            Tuple (X, y)
        """
        return self.fit(df_train).transform(df_train)
    
    @abstractmethod
    def inverse_target(self, y_scaled: np.ndarray) -> np.ndarray:
        """
        Desnormaliza o target.
        
        Args:
            y_scaled: Target normalizado
            
        Returns:
            Target em escala original
        """
        pass
    
    @property
    def is_fitted(self) -> bool:
        """Verifica se foi fitted."""
        return self._fitted
