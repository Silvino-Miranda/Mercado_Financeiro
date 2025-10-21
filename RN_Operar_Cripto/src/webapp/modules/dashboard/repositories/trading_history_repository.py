"""
Trading History Repository
Repositório para gerenciar histórico de operações de trading
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from src.webapp.shared.core.base_repository import BaseRepository


class TradingHistoryRepository(BaseRepository):
    """Repositório de histórico de trading"""
    
    def __init__(self):
        super().__init__('trading_history')
    
    def get_columns(self) -> List[str]:
        """Retorna colunas da tabela trading_history"""
        return [
            'id', 'strategy_id', 'data', 'operacao', 'status',
            'previsao', 'valor_atual', 'preco', 'quantidade',
            'custo', 'capital', 'retorno_percentual',
            'retorno_absoluto', 'drawdown', 'erro_previsao',
            'created_at'
        ]
    
    def find_by_strategy(
        self,
        strategy_id: int,
        order_by: str = 'data ASC'
    ) -> List[Dict[str, Any]]:
        """
        Busca todos os trades de uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            order_by: Ordenação (padrão: por data)
            
        Returns:
            List[Dict]: Lista de trades
        """
        return self.find_where({'strategy_id': strategy_id}, order_by=order_by)
    
    def find_by_date_range(
        self,
        strategy_id: int,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Busca trades em um período
        
        Args:
            strategy_id: ID da estratégia
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Lista de trades no período
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE strategy_id = ? 
            AND date(data) BETWEEN ? AND ?
            ORDER BY data ASC
        """
        return self.db.execute_query(query, (strategy_id, start_date, end_date))
    
    def get_profitable_trades(self, strategy_id: int) -> List[Dict[str, Any]]:
        """
        Busca trades lucrativos
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            List[Dict]: Trades com lucro
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE strategy_id = ? 
            AND retorno_percentual > 0
            ORDER BY retorno_percentual DESC
        """
        return self.db.execute_query(query, (strategy_id,))
    
    def get_loss_trades(self, strategy_id: int) -> List[Dict[str, Any]]:
        """
        Busca trades com prejuízo
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            List[Dict]: Trades com prejuízo
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE strategy_id = ? 
            AND retorno_percentual < 0
            ORDER BY retorno_percentual ASC
        """
        return self.db.execute_query(query, (strategy_id,))
    
    def get_summary(self, strategy_id: int) -> Dict[str, Any]:
        """
        Retorna resumo estatístico dos trades
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Dict: Estatísticas resumidas
        """
        query = f"""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(CASE WHEN operacao = 'Compra' THEN 1 END) as total_compras,
                COUNT(CASE WHEN operacao = 'Venda' THEN 1 END) as total_vendas,
                MIN(data) as first_trade,
                MAX(data) as last_trade,
                MIN(capital) as min_capital,
                MAX(capital) as max_capital,
                AVG(erro_previsao) as avg_prediction_error,
                COUNT(CASE WHEN retorno_percentual > 0 THEN 1 END) as profitable_trades,
                COUNT(CASE WHEN retorno_percentual < 0 THEN 1 END) as loss_trades
            FROM {self.table_name}
            WHERE strategy_id = ?
        """
        return self.db.execute_query(query, (strategy_id,), fetch='one')
    
    def get_trades_by_operation(
        self,
        strategy_id: int,
        operation: str
    ) -> List[Dict[str, Any]]:
        """
        Busca trades por tipo de operação
        
        Args:
            strategy_id: ID da estratégia
            operation: 'Compra' ou 'Venda'
            
        Returns:
            List[Dict]: Trades da operação especificada
        """
        return self.find_where(
            {'strategy_id': strategy_id, 'operacao': operation},
            order_by='data ASC'
        )
    
    def create_trade(
        self,
        strategy_id: int,
        data: str,
        operacao: str,
        status: str,
        previsao: float,
        valor_atual: float,
        preco: float,
        quantidade: float,
        capital: float,
        **kwargs
    ) -> int:
        """
        Cria novo trade
        
        Args:
            strategy_id: ID da estratégia
            data: Data/hora da operação
            operacao: 'Compra' ou 'Venda'
            status: 'Entrada' ou 'Saida'
            previsao: Valor previsto
            valor_atual: Valor real
            preco: Preço de execução
            quantidade: Quantidade negociada
            capital: Capital após operação
            **kwargs: Campos opcionais
            
        Returns:
            int: ID do trade criado
        """
        trade_data = {
            'strategy_id': strategy_id,
            'data': data,
            'operacao': operacao,
            'status': status,
            'previsao': previsao,
            'valor_atual': valor_atual,
            'preco': preco,
            'quantidade': quantidade,
            'capital': capital,
            'erro_previsao': previsao - valor_atual,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        return self.insert(trade_data)
    
    def bulk_create_trades(
        self,
        strategy_id: int,
        trades: List[Dict[str, Any]]
    ) -> int:
        """
        Cria múltiplos trades de uma vez
        
        Args:
            strategy_id: ID da estratégia
            trades: Lista de dicts com dados dos trades
            
        Returns:
            int: Número de trades criados
        """
        # Adicionar strategy_id e erro_previsao a todos
        for trade in trades:
            trade['strategy_id'] = strategy_id
            if 'erro_previsao' not in trade:
                trade['erro_previsao'] = trade['previsao'] - trade['valor_atual']
            if 'created_at' not in trade:
                trade['created_at'] = datetime.now().isoformat()
        
        return self.bulk_insert(trades)
    
    def get_capital_evolution(self, strategy_id: int) -> pd.DataFrame:
        """
        Retorna evolução do capital ao longo do tempo
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            pd.DataFrame: DataFrame com data e capital
        """
        query = f"""
            SELECT data, capital
            FROM {self.table_name}
            WHERE strategy_id = ?
            ORDER BY data ASC
        """
        return self.to_dataframe(query, params=(strategy_id,))
    
    def get_monthly_performance(self, strategy_id: int) -> List[Dict[str, Any]]:
        """
        Retorna performance mensal
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            List[Dict]: Performance por mês
        """
        query = f"""
            SELECT 
                strftime('%Y-%m', data) as month,
                COUNT(*) as trades,
                AVG(retorno_percentual) as avg_return,
                SUM(CASE WHEN retorno_percentual > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN retorno_percentual < 0 THEN 1 ELSE 0 END) as losses
            FROM {self.table_name}
            WHERE strategy_id = ? AND operacao = 'Venda'
            GROUP BY strftime('%Y-%m', data)
            ORDER BY month ASC
        """
        return self.db.execute_query(query, (strategy_id,))
    
    def delete_by_strategy(self, strategy_id: int) -> int:
        """
        Deleta todos os trades de uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            int: Número de trades deletados
        """
        query = f"DELETE FROM {self.table_name} WHERE strategy_id = ?"
        
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (strategy_id,))
            return cursor.rowcount
