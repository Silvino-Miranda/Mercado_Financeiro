"""
Database Configuration
Configurações de conexão e paths do banco de dados
"""
from pathlib import Path
from typing import Optional
import os


class DatabaseConfig:
    """Configurações do banco de dados SQLite"""
    
    # Paths
    ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent
    DATA_DIR = ROOT_DIR / "data"
    DB_PATH = DATA_DIR / "trading_bot.db"
    
    # Connection settings
    CHECK_SAME_THREAD = False  # Permite uso em múltiplas threads (Dash)
    TIMEOUT = 30.0  # Timeout em segundos
    
    # Backup settings
    BACKUP_DIR = DATA_DIR / "backups"
    AUTO_BACKUP = True
    MAX_BACKUPS = 10
    
    @classmethod
    def get_db_path(cls, db_name: Optional[str] = None) -> str:
        """
        Retorna o caminho do banco de dados
        
        Args:
            db_name: Nome customizado do banco (opcional)
            
        Returns:
            str: Caminho completo do arquivo .db
        """
        if db_name:
            return str(cls.DATA_DIR / db_name)
        return str(cls.DB_PATH)
    
    @classmethod
    def ensure_directories(cls):
        """Garante que os diretórios necessários existam"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        if cls.AUTO_BACKUP:
            cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Retorna string de conexão SQLite"""
        return f"sqlite:///{cls.get_db_path()}"
    
    @classmethod
    def is_database_exists(cls) -> bool:
        """Verifica se o banco de dados existe"""
        return cls.DB_PATH.exists()
