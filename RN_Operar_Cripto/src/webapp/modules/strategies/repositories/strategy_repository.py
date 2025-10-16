"""
Strategy Repository
Repositório para gerenciar estratégias de trading
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.webapp.shared.core.base_repository import BaseRepository


class StrategyRepository(BaseRepository):
    """Repositório de estratégias"""
    
    def __init__(self):
        super().__init__('strategies')
    
    def get_columns(self) -> List[str]:
        """Retorna colunas da tabela strategies"""
        return [
            'id', 'name', 'description', 'model_type',
            'take_profit', 'stop_loss', 'threshold',
            'position_size', 'min_holding_periods',
            'created_at', 'updated_at', 'is_active',
            'lstm_layers', 'lstm_units', 'sequence_length',
            'features_count', 'total_return', 'sharpe_ratio',
            'max_drawdown', 'win_rate', 'total_trades',
            'config_json'
        ]
    
    def find_active(self) -> List[Dict[str, Any]]:
        """
        Busca estratégias ativas
        
        Returns:
            List[Dict]: Lista de estratégias ativas
        """
        return self.find_where({'is_active': 1}, order_by='created_at DESC')
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca estratégia por nome
        
        Args:
            name: Nome da estratégia
            
        Returns:
            Dict ou None: Estratégia encontrada
        """
        results = self.find_where({'name': name}, limit=1)
        return results[0] if results else None
    
    def create_strategy(
        self,
        name: str,
        model_type: str,
        take_profit: float,
        stop_loss: float,
        **kwargs
    ) -> int:
        """
        Cria nova estratégia
        
        Args:
            name: Nome da estratégia
            model_type: Tipo do modelo (LSTM, GRU, etc)
            take_profit: % de lucro para saída
            stop_loss: % de perda para stop
            **kwargs: Outros campos opcionais
            
        Returns:
            int: ID da estratégia criada
        """
        data = {
            'name': name,
            'model_type': model_type,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_active': 1,
            **kwargs
        }
        
        return self.insert(data)
    
    def update_metrics(self, strategy_id: int, metrics: Dict[str, Any]) -> bool:
        """
        Atualiza métricas de performance da estratégia
        
        Args:
            strategy_id: ID da estratégia
            metrics: Dict com métricas (total_return, sharpe_ratio, etc)
            
        Returns:
            bool: True se atualizou com sucesso
        """
        data = {
            **metrics,
            'updated_at': datetime.now().isoformat()
        }
        
        return self.update(strategy_id, data)
    
    def activate(self, strategy_id: int) -> bool:
        """Ativa estratégia"""
        return self.update(strategy_id, {'is_active': 1})
    
    def deactivate(self, strategy_id: int) -> bool:
        """Desativa estratégia"""
        return self.update(strategy_id, {'is_active': 0})
    
    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna top N estratégias por retorno
        
        Args:
            limit: Número de estratégias
            
        Returns:
            List[Dict]: Top estratégias
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_active = 1 AND total_return IS NOT NULL
            ORDER BY total_return DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (limit,))
    
    def get_comparison(self, strategy_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Compara múltiplas estratégias
        
        Args:
            strategy_ids: Lista de IDs
            
        Returns:
            List[Dict]: Estratégias para comparação
        """
        placeholders = ','.join(['?' for _ in strategy_ids])
        query = f"""
            SELECT id, name, total_return, sharpe_ratio, 
                   max_drawdown, win_rate, total_trades
            FROM {self.table_name}
            WHERE id IN ({placeholders})
        """
        return self.db.execute_query(query, tuple(strategy_ids))
