"""
Application Configuration
Configurações gerais da aplicação Dash
"""
from typing import Dict, Any


class AppConfig:
    """Configurações da aplicação"""
    
    # App Settings
    APP_NAME = "Trading Bot Dashboard"
    APP_VERSION = "2.0.0"
    DEBUG = True
    
    # Server Settings
    HOST = "127.0.0.1"
    PORT = 8050
    
    # Dash Settings
    SUPPRESS_CALLBACK_EXCEPTIONS = True
    ASSETS_FOLDER = "assets"
    
    # Update Intervals (milliseconds)
    REALTIME_UPDATE_INTERVAL = 5000  # 5 segundos
    CHART_UPDATE_INTERVAL = 10000    # 10 segundos
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 200
    
    # Cache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/webapp.log"
    LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Converte configurações para dicionário"""
        return {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith('_') and not callable(v)
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return getattr(cls, key, default)
