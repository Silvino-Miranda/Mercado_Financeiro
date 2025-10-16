"""
Base Repository
Classe base para todos os repositórios com operações CRUD genéricas
"""
from typing import List, Dict, Any, Optional, Type, TypeVar
from abc import ABC, abstractmethod
import pandas as pd
from src.webapp.shared.core.database import db

T = TypeVar('T')


class BaseRepository(ABC):
    """Repositório base com operações CRUD genéricas"""
    
    def __init__(self, table_name: str):
        """
        Inicializa repositório
        
        Args:
            table_name: Nome da tabela no banco
        """
        self.table_name = table_name
        self.db = db
    
    @abstractmethod
    def get_columns(self) -> List[str]:
        """Retorna lista de colunas da tabela (deve ser implementado)"""
        pass
    
    def find_all(self, order_by: str = None) -> List[Dict[str, Any]]:
        """
        Busca todos os registros
        
        Args:
            order_by: Coluna para ordenação (opcional)
            
        Returns:
            List[Dict]: Lista de registros
        """
        query = f"SELECT * FROM {self.table_name}"
        if order_by:
            query += f" ORDER BY {order_by}"
        
        return self.db.execute_query(query)
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Busca registro por ID
        
        Args:
            id: ID do registro
            
        Returns:
            Dict ou None: Registro encontrado
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.db.execute_query(query, (id,), fetch='one')
    
    def find_where(
        self,
        conditions: Dict[str, Any],
        order_by: str = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Busca registros com condições
        
        Args:
            conditions: Dict com {coluna: valor}
            order_by: Coluna para ordenação
            limit: Limite de registros
            
        Returns:
            List[Dict]: Registros encontrados
        """
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.db.execute_query(query, tuple(conditions.values()))
    
    def insert(self, data: Dict[str, Any]) -> int:
        """
        Insere novo registro
        
        Args:
            data: Dict com dados do registro
            
        Returns:
            int: ID do registro inserido
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid
    
    def bulk_insert(self, data_list: List[Dict[str, Any]]) -> int:
        """
        Insere múltiplos registros
        
        Args:
            data_list: Lista de dicts com dados
            
        Returns:
            int: Número de registros inseridos
        """
        if not data_list:
            return 0
        
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['?' for _ in data_list[0]])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        params_list = [tuple(d.values()) for d in data_list]
        self.db.execute_many(query, params_list)
        
        return len(data_list)
    
    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """
        Atualiza registro
        
        Args:
            id: ID do registro
            data: Dict com campos a atualizar
            
        Returns:
            bool: True se atualizou com sucesso
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        
        params = list(data.values()) + [id]
        
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete(self, id: int) -> bool:
        """
        Deleta registro
        
        Args:
            id: ID do registro
            
        Returns:
            bool: True se deletou com sucesso
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            return cursor.rowcount > 0
    
    def count(self, conditions: Dict[str, Any] = None) -> int:
        """
        Conta registros
        
        Args:
            conditions: Condições opcionais
            
        Returns:
            int: Número de registros
        """
        if conditions:
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE {where_clause}"
            result = self.db.execute_query(query, tuple(conditions.values()), fetch='one')
        else:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            result = self.db.execute_query(query, fetch='one')
        
        return result['count'] if result else 0
    
    def exists(self, id: int) -> bool:
        """Verifica se registro existe"""
        return self.find_by_id(id) is not None
    
    def to_dataframe(self, query: str = None, params: tuple = None) -> pd.DataFrame:
        """
        Converte resultados para DataFrame
        
        Args:
            query: Query SQL customizada (opcional)
            params: Parâmetros da query
            
        Returns:
            pd.DataFrame: DataFrame com resultados
        """
        if query is None:
            query = f"SELECT * FROM {self.table_name}"
        
        with self.db.get_connection() as conn:
            if params:
                return pd.read_sql_query(query, conn, params=params)
            else:
                return pd.read_sql_query(query, conn)
    
    def execute_raw(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Executa query SQL customizada"""
        return self.db.execute_query(query, params)
