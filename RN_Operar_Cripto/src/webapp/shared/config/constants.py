"""
Constants
Constantes globais da aplicação
"""
from enum import Enum


class TradeOperation(str, Enum):
    """Tipos de operação"""
    BUY = "Compra"
    SELL = "Venda"


class TradeStatus(str, Enum):
    """Status da operação"""
    ENTRY = "Entrada"
    EXIT = "Saida"


class StrategyStatus(str, Enum):
    """Status da estratégia"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ModelType(str, Enum):
    """Tipos de modelo de ML"""
    LSTM = "LSTM"
    GRU = "GRU"
    TRANSFORMER = "Transformer"
    CNN = "CNN"


class Constants:
    """Constantes da aplicação"""
    
    # Trading
    DEFAULT_INITIAL_CAPITAL = 100000.0
    DEFAULT_POSITION_SIZE = 0.95
    DEFAULT_TAKE_PROFIT = 3.0
    DEFAULT_STOP_LOSS = 1.5
    DEFAULT_MIN_HOLDING = 48
    
    # Formatação
    CURRENCY_FORMAT = "${:,.2f}"
    PERCENTAGE_FORMAT = "{:.2f}%"
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Cores (Plotly)
    COLOR_PROFIT = "#27ae60"
    COLOR_LOSS = "#e74c3c"
    COLOR_NEUTRAL = "#95a5a6"
    COLOR_PRIMARY = "#3498db"
    COLOR_SECONDARY = "#9b59b6"
    COLOR_WARNING = "#f39c12"
    COLOR_INFO = "#16a085"
    
    # Métricas - Thresholds
    GOOD_SHARPE_RATIO = 1.5
    EXCELLENT_SHARPE_RATIO = 2.0
    ACCEPTABLE_DRAWDOWN = -15.0
    CRITICAL_DRAWDOWN = -25.0
    GOOD_WIN_RATE = 55.0
    EXCELLENT_WIN_RATE = 65.0
    
    # Chart Settings
    CHART_HEIGHT = 500
    CHART_MARGIN = dict(l=50, r=50, t=50, b=50)
    CHART_TEMPLATE = "plotly_white"
    
    # API Settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    # File Upload
    MAX_UPLOAD_SIZE_MB = 50
    ALLOWED_EXTENSIONS = ['.csv', '.json', '.xlsx']
    
    @classmethod
    def format_currency(cls, value: float) -> str:
        """Formata valor monetário"""
        return cls.CURRENCY_FORMAT.format(value)
    
    @classmethod
    def format_percentage(cls, value: float) -> str:
        """Formata percentual"""
        return cls.PERCENTAGE_FORMAT.format(value)
