"""
Interfaces para avaliação de modelos.
Princípios aplicados:
- SRP: Cada interface tem responsabilidade única
- ISP: Interfaces específicas para diferentes tipos de métricas
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Protocol
import numpy as np


class MetricsCalculator(Protocol):
    """Interface para calculadores de métricas."""
    
    def calculate(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calcula métricas.
        
        Args:
            y_true: Valores reais
            y_pred: Predições
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict com métricas
        """
        ...


class BaseEvaluator(ABC):
    """
    Interface base para avaliadores de modelos.
    
    Responsabilidades:
    - Calcular métricas de erro (MAE, RMSE, MAPE)
    - Métricas direcionais (Hit Rate, Accuracy)
    - Comparar com baselines
    - Gerar relatórios formatados
    """
    
    @abstractmethod
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Avalia predições.
        
        Args:
            y_true: Valores reais
            y_pred: Predições
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict com todas as métricas
        """
        pass
    
    @abstractmethod
    def compare_with_baselines(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        baselines: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compara modelo com baselines.
        
        Args:
            y_true: Valores reais
            y_pred: Predições do modelo
            baselines: Dict com predições dos baselines
            
        Returns:
            Dict com comparação de métricas
        """
        pass
    
    @abstractmethod
    def print_report(self, results: Dict[str, Any]) -> None:
        """
        Imprime relatório formatado.
        
        Args:
            results: Resultados da avaliação
        """
        pass
    
    @abstractmethod
    def save_results(self, results: Dict[str, Any], path: str) -> None:
        """
        Salva resultados em arquivo.
        
        Args:
            results: Resultados da avaliação
            path: Caminho do arquivo
        """
        pass
