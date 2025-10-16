"""
Strategy Model
Modelo de dados para estratégias de trading
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Strategy:
    """Modelo de estratégia de trading"""
    
    id: int
    name: str
    model_type: str
    take_profit: float
    stop_loss: float
    
    # Opcionais
    description: Optional[str] = None
    threshold: Optional[float] = None
    position_size: float = 0.95
    min_holding_periods: int = 48
    
    # Metadados do modelo
    lstm_layers: Optional[int] = None
    lstm_units: Optional[int] = None
    sequence_length: Optional[int] = None
    features_count: Optional[int] = None
    
    # Métricas
    total_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    
    # Config
    config_json: Optional[str] = None
    
    # Timestamps
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """
        Cria instância a partir de dicionário
        
        Args:
            data: Dicionário com dados da estratégia
            
        Returns:
            Strategy: Instância do modelo
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            model_type=data.get('model_type'),
            take_profit=data.get('take_profit'),
            stop_loss=data.get('stop_loss'),
            threshold=data.get('threshold'),
            position_size=data.get('position_size', 0.95),
            min_holding_periods=data.get('min_holding_periods', 48),
            lstm_layers=data.get('lstm_layers'),
            lstm_units=data.get('lstm_units'),
            sequence_length=data.get('sequence_length'),
            features_count=data.get('features_count'),
            total_return=data.get('total_return'),
            sharpe_ratio=data.get('sharpe_ratio'),
            max_drawdown=data.get('max_drawdown'),
            win_rate=data.get('win_rate'),
            total_trades=data.get('total_trades'),
            config_json=data.get('config_json'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_active=bool(data.get('is_active', 1))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário
        
        Returns:
            Dict: Dicionário com dados da estratégia
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_type': self.model_type,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'threshold': self.threshold,
            'position_size': self.position_size,
            'min_holding_periods': self.min_holding_periods,
            'lstm_layers': self.lstm_layers,
            'lstm_units': self.lstm_units,
            'sequence_length': self.sequence_length,
            'features_count': self.features_count,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'config_json': self.config_json,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
    
    def get_risk_level(self) -> str:
        """Retorna nível de risco baseado em drawdown"""
        if self.max_drawdown is None:
            return "Desconhecido"
        elif self.max_drawdown > -10:
            return "Baixo"
        elif self.max_drawdown > -20:
            return "Moderado"
        else:
            return "Alto"
    
    def get_performance_rating(self) -> str:
        """Retorna rating de performance"""
        if self.sharpe_ratio is None:
            return "N/A"
        elif self.sharpe_ratio >= 2.0:
            return "Excelente"
        elif self.sharpe_ratio >= 1.5:
            return "Muito Bom"
        elif self.sharpe_ratio >= 1.0:
            return "Bom"
        elif self.sharpe_ratio >= 0.5:
            return "Regular"
        else:
            return "Ruim"
    
    def __str__(self) -> str:
        return f"Strategy(id={self.id}, name='{self.name}', return={self.total_return}%)"
