"""
Interfaces base para modelos ML.
Princípios aplicados:
- ISP (Interface Segregation): Separar treino, predição e avaliação
- DIP (Dependency Inversion): Código depende de abstrações, não implementações
"""
from abc import ABC, abstractmethod
from typing import Tuple, Any, Protocol
import numpy as np


class Trainable(Protocol):
    """Interface para modelos treináveis."""
    
    def fit(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        validation_data: Tuple[np.ndarray, np.ndarray] = None,
        **kwargs
    ) -> Any:
        """
        Treina o modelo.
        
        Args:
            X: Features de treino
            y: Labels de treino
            validation_data: Dados de validação (opcional)
            **kwargs: Argumentos adicionais (epochs, batch_size, etc)
            
        Returns:
            Histórico de treino
        """
        ...


class Predictable(Protocol):
    """Interface para modelos que fazem predições."""
    
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """
        Faz predições.
        
        Args:
            X: Features de entrada
            **kwargs: Argumentos adicionais
            
        Returns:
            Predições
        """
        ...


class Evaluable(Protocol):
    """Interface para modelos avaliáveis."""
    
    def evaluate(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        **kwargs
    ) -> Tuple[float, ...]:
        """
        Avalia o modelo.
        
        Args:
            X: Features de teste
            y: Labels de teste
            **kwargs: Argumentos adicionais
            
        Returns:
            Tuple de métricas
        """
        ...


class BaseModel(ABC):
    """
    Interface base para todos os modelos ML.
    
    Implementa Trainable, Predictable e Evaluable.
    Subclasses: LSTMModel, GRUModel, DirectionalModel, etc.
    """
    
    @abstractmethod
    def fit(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        validation_data: Tuple[np.ndarray, np.ndarray] = None,
        **kwargs
    ) -> Any:
        """Treina o modelo."""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray, **kwargs) -> np.ndarray:
        """Faz predições."""
        pass
    
    @abstractmethod
    def evaluate(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        **kwargs
    ) -> Tuple[float, ...]:
        """Avalia o modelo."""
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Salva o modelo."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> 'BaseModel':
        """Carrega o modelo."""
        pass
    
    @property
    @abstractmethod
    def input_shape(self) -> Tuple[int, ...]:
        """Retorna shape esperado da entrada."""
        pass
    
    @property
    @abstractmethod
    def output_shape(self) -> Tuple[int, ...]:
        """Retorna shape da saída."""
        pass
