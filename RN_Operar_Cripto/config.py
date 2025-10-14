# config.py
# Configurações centralizadas do projeto

# ========================================
# CONFIGURAÇÕES DE DADOS
# ========================================
DATA_CONFIG = {
    "symbol": "BTCUSDT",
    "interval": "30m",
    "use_local_file": True,
    "local_filename": "BTCUSDT_30m_full.csv",  # Base completa com 8 anos de histórico
    "data_dir": "data"
}

# ========================================
# CONFIGURAÇÕES DO MODELO LSTM
# ========================================
MODEL_CONFIG = {
    "sequence_length": 60,  # Número de períodos anteriores para previsão
    "epochs": 10,           # Número de épocas de treinamento
    "batch_size": 64,       # Tamanho do lote
    "model_save_path": "lstm_model.keras"
}

# ========================================
# FEATURES E TARGETS
# ========================================
FEATURE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "SMA_20",
    "EMA_20",
    "RSI_14",
    "MACD",
    "MACD_Signal",
    "BB_High",
    "BB_Low",
    "Stoch",
    "OBV",
]

TARGET_COLUMNS = ["Close", "High", "Low"]

# ========================================
# CONFIGURAÇÕES DE BACKTESTING
# ========================================
BACKTEST_CONFIG = {
    "initial_capital": 10000.0,
    "commission": 0.001,  # 0.1% de comissão
    "output_file": "capital_history-BTCUSDT.csv"
}

# ========================================
# CONFIGURAÇÕES DO DASHBOARD
# ========================================
DASHBOARD_CONFIG = {
    "title": "Análise de Previsões - BTC/USDT (30min)",
    "description": "Comparação entre as previsões do modelo LSTM e os valores reais do Bitcoin.",
    "port": 8050,
    "debug": True
}
