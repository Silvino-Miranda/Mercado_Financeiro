"""
Database Core Module
Gerenciamento de conexão com banco de dados SQLite
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from src.webapp.shared.config.database_config import DatabaseConfig


class Database:
    """Singleton para gerenciar conexão com banco de dados"""
    
    _instance: Optional['Database'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa configuração do banco"""
        if not hasattr(self, '_initialized'):
            DatabaseConfig.ensure_directories()
            self._initialized = True
    
    def connect(self) -> sqlite3.Connection:
        """
        Estabelece conexão com o banco
        
        Returns:
            sqlite3.Connection: Conexão ativa
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                DatabaseConfig.get_db_path(),
                check_same_thread=DatabaseConfig.CHECK_SAME_THREAD,
                timeout=DatabaseConfig.TIMEOUT
            )
            self._connection.row_factory = sqlite3.Row
            print(f"✅ Conectado ao banco: {DatabaseConfig.get_db_path()}")
        
        return self._connection
    
    def disconnect(self):
        """Fecha conexão com o banco"""
        if self._connection:
            self._connection.close()
            self._connection = None
            print("❌ Conexão com banco encerrada")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obter conexão temporária
        
        Yields:
            sqlite3.Connection: Conexão temporária
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            pass  # Não fecha a conexão singleton
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transações
        
        Yields:
            sqlite3.Connection: Conexão com transação
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Executa query SQL
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            fetch: 'all', 'one' ou 'none'
            
        Returns:
            List[Dict]: Resultados
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch == 'all':
                return [dict(row) for row in cursor.fetchall()]
            elif fetch == 'one':
                row = cursor.fetchone()
                return dict(row) if row else None
            else:  # 'none'
                conn.commit()
                return []
                
        except Exception as e:
            print(f"❌ Erro ao executar query: {e}")
            raise e
        finally:
            cursor.close()
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """
        Executa query com múltiplos parâmetros (bulk insert)
        
        Args:
            query: Query SQL
            params_list: Lista de tuplas de parâmetros
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(query, params_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao executar bulk operation: {e}")
            raise e
        finally:
            cursor.close()
    
    def table_exists(self, table_name: str) -> bool:
        """Verifica se tabela existe"""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,), fetch='one')
        return result is not None
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Retorna schema de uma tabela"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)


# Instância global
db = Database()
