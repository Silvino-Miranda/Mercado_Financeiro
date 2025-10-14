"""
Configuração Centralizada de Caminhos
======================================

Define todos os caminhos do projeto em um único local
para facilitar manutenção e evitar erros.
"""

from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent

# ===================================================================
# DADOS (DATA)
# ===================================================================
DATA_DIR = PROJECT_ROOT / "data"
DATA_BTCUSDT_30M = DATA_DIR / "BTCUSDT_30m.csv"
DATA_BTCUSDT_30M_FULL = DATA_DIR / "BTCUSDT_30m_full.csv"

# ===================================================================
# MACHINE LEARNING (SRC/ML)
# ===================================================================
ML_DIR = PROJECT_ROOT / "src" / "ml"

# Checkpoints (modelos salvos e pesos)
ML_CHECKPOINTS_DIR = ML_DIR / "checkpoints"
ML_MODEL_PATH = ML_CHECKPOINTS_DIR / "lstm_model.keras"
ML_WEIGHTS_PATTERN = ML_CHECKPOINTS_DIR / "model_weights_epoch_{epoch:02d}.weights.h5"

# Outputs (resultados de backtesting)
ML_OUTPUTS_DIR = ML_DIR / "outputs"
ML_CAPITAL_HISTORY = ML_OUTPUTS_DIR / "capital_history-BTCUSDT.csv"

# ===================================================================
# WEBAPP (SRC/WEBAPP)
# ===================================================================
WEBAPP_DIR = PROJECT_ROOT / "src" / "webapp"

# ===================================================================
# DOCUMENTAÇÃO (_DOC)
# ===================================================================
DOC_DIR = PROJECT_ROOT / "_doc"

# ===================================================================
# ARQUIVOS AUXILIARES
# ===================================================================
FILES_DIR = PROJECT_ROOT / "_Arquivos"

# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def ensure_directories():
    """Cria todos os diretórios necessários se não existirem"""
    directories = [
        DATA_DIR,
        ML_CHECKPOINTS_DIR,
        ML_OUTPUTS_DIR,
        DOC_DIR,
        FILES_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Todos os diretórios necessários foram criados/verificados")

def get_relative_path(path: Path) -> str:
    """Retorna caminho relativo à raiz do projeto"""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)

# ===================================================================
# CONFIGURAÇÕES DE TREINAMENTO
# ===================================================================

TRAINING_CONFIG = {
    "sequence_length": 60,
    "epochs": 50,
    "batch_size": 32,
    "validation_split": 0.15,
    "test_split": 0.15,
    "early_stopping_patience": 10,
}

# ===================================================================
# CONFIGURAÇÕES DE BACKTESTING
# ===================================================================

BACKTEST_CONFIG = {
    "initial_capital": 100000.0,
    "commission": 0.001,  # 0.1%
}

# ===================================================================
# FEATURES E TARGETS
# ===================================================================

FEATURES = [
    "Open",
    "High",
    "Low",
    "Close",
    "SMA_20",
    "EMA_20",
]

TARGETS = [
    "Close",
    "High",
    "Low",
]

# ===================================================================
# CONFIGURAÇÕES DO DATASET
# ===================================================================

DATASET_CONFIG = {
    "symbol": "BTCUSDT",
    "interval": "30m",
    "use_local_file": True,
    "local_filename": "BTCUSDT_30m_full.csv",
}


if __name__ == "__main__":
    # Testar criação de diretórios
    print("\n" + "="*70)
    print("TESTANDO CONFIGURAÇÃO DE CAMINHOS")
    print("="*70)
    
    ensure_directories()
    
    print("\n📁 Caminhos Configurados:")
    print(f"  Raiz do Projeto: {PROJECT_ROOT}")
    print(f"  Dados: {get_relative_path(DATA_DIR)}")
    print(f"  ML Checkpoints: {get_relative_path(ML_CHECKPOINTS_DIR)}")
    print(f"  ML Outputs: {get_relative_path(ML_OUTPUTS_DIR)}")
    print(f"  WebApp: {get_relative_path(WEBAPP_DIR)}")
    print(f"  Documentação: {get_relative_path(DOC_DIR)}")
    
    print("\n📊 Arquivos Principais:")
    print(f"  Dataset: {get_relative_path(DATA_BTCUSDT_30M_FULL)}")
    print(f"  Modelo: {get_relative_path(ML_MODEL_PATH)}")
    print(f"  Capital History: {get_relative_path(ML_CAPITAL_HISTORY)}")
    
    print("\n" + "="*70)
    print("✅ CONFIGURAÇÃO OK")
    print("="*70 + "\n")
