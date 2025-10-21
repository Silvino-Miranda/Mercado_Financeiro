"""
Trade Model
Modelo de dados para operações de trading
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Trade:
    """Modelo de trade (operação de compra/venda)"""
    
    id: int
    strategy_id: int
    data: str
    operacao: str  # 'Compra' ou 'Venda'
    status: str    # 'Entrada' ou 'Saida'
    previsao: float
    valor_atual: float
    preco: float
    quantidade: float
    capital: float
    
    # Opcionais
    custo: float = 0.0
    retorno_percentual: Optional[float] = None
    retorno_absoluto: Optional[float] = None
    drawdown: Optional[float] = None
    erro_previsao: Optional[float] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trade':
        """
        Cria instância a partir de dicionário
        
        Args:
            data: Dicionário com dados do trade
            
        Returns:
            Trade: Instância do modelo
        """
        return cls(
            id=data.get('id'),
            strategy_id=data.get('strategy_id'),
            data=data.get('data'),
            operacao=data.get('operacao'),
            status=data.get('status'),
            previsao=data.get('previsao'),
            valor_atual=data.get('valor_atual'),
            preco=data.get('preco'),
            quantidade=data.get('quantidade'),
            custo=data.get('custo', 0.0),
            capital=data.get('capital'),
            retorno_percentual=data.get('retorno_percentual'),
            retorno_absoluto=data.get('retorno_absoluto'),
            drawdown=data.get('drawdown'),
            erro_previsao=data.get('erro_previsao'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'data': self.data,
            'operacao': self.operacao,
            'status': self.status,
            'previsao': self.previsao,
            'valor_atual': self.valor_atual,
            'preco': self.preco,
            'quantidade': self.quantidade,
            'custo': self.custo,
            'capital': self.capital,
            'retorno_percentual': self.retorno_percentual,
            'retorno_absoluto': self.retorno_absoluto,
            'drawdown': self.drawdown,
            'erro_previsao': self.erro_previsao,
            'created_at': self.created_at
        }
    
    def is_buy(self) -> bool:
        """Verifica se é compra"""
        return self.operacao == 'Compra'
    
    def is_sell(self) -> bool:
        """Verifica se é venda"""
        return self.operacao == 'Venda'
    
    def is_entry(self) -> bool:
        """Verifica se é entrada"""
        return self.status == 'Entrada'
    
    def is_exit(self) -> bool:
        """Verifica se é saída"""
        return self.status == 'Saida'
    
    def is_profitable(self) -> bool:
        """Verifica se foi lucrativo"""
        return self.retorno_percentual is not None and self.retorno_percentual > 0
    
    def get_prediction_accuracy(self) -> float:
        """Retorna precisão da previsão (%)"""
        if self.erro_previsao is None:
            return 0.0
        return abs((self.erro_previsao / self.valor_atual) * 100)
    
    def __str__(self) -> str:
        return f"Trade(id={self.id}, {self.operacao}, {self.status}, capital={self.capital})"
