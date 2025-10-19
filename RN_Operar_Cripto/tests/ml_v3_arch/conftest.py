"""
Fixtures compartilhadas para testes do ml_v3_arch.

Fixtures disponíveis:
- sample_model_config: Configuração de modelo de exemplo
- sample_backtest_config: Configuração de backtest de exemplo
- mock_keras_model: Mock de modelo Keras
- mock_preprocessor: Mock de preprocessor sklearn
- sample_data: Dados de exemplo (X, y)
- sample_prices: Preços para backtesting
- tmp_artifacts_dir: Diretório temporário para artifacts
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

# Adicionar src ao path
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from ml_v3_arch.domain.entities import (
    ModelConfig,
    BacktestConfig,
    TradeDirection
)


# ============================================================================
# FIXTURES DE CONFIGURAÇÃO
# ============================================================================

@pytest.fixture
def sample_model_config():
    """Configuração de modelo padrão para testes."""
    return ModelConfig(
        model_type='lstm',
        lookback=60,
        lstm_units=64,
        lstm_layers=2,
        dropout=0.3,
        learning_rate=0.001,
        batch_size=32,
        epochs=10,
        patience=5
    )


@pytest.fixture
def sample_backtest_config():
    """Configuração de backtest padrão para testes."""
    return BacktestConfig(
        initial_capital=10000.0,
        fee_bps=10.0,
        slippage_bps=5.0,
        position_size=0.95,
        min_confidence=0.6,
        threshold_bps=20.0
    )


# ============================================================================
# FIXTURES DE DADOS
# ============================================================================

@pytest.fixture
def sample_data():
    """
    Gera dados sintéticos para testes.
    
    Returns:
        tuple: (X_train, y_train, X_val, y_val, X_test, y_test)
    """
    np.random.seed(42)
    
    n_samples = 1000
    n_timesteps = 60
    n_features = 10
    n_classes = 3
    
    # Gerar dados
    X = np.random.randn(n_samples, n_timesteps, n_features).astype(np.float32)
    y = np.random.randint(0, n_classes, size=n_samples)
    
    # Split
    train_size = int(0.7 * n_samples)
    val_size = int(0.15 * n_samples)
    
    X_train = X[:train_size]
    y_train = y[:train_size]
    
    X_val = X[train_size:train_size+val_size]
    y_val = y[train_size:train_size+val_size]
    
    X_test = X[train_size+val_size:]
    y_test = y[train_size+val_size:]
    
    return X_train, y_train, X_val, y_val, X_test, y_test


@pytest.fixture
def sample_prices():
    """
    Gera série de preços sintética para backtesting.
    
    Returns:
        tuple: (prices, timestamps)
    """
    np.random.seed(42)
    
    n_samples = 150
    base_price = 50000.0
    
    # Random walk
    returns = np.random.randn(n_samples) * 100
    prices = base_price + np.cumsum(returns)
    
    # Timestamps
    timestamps = np.arange(n_samples)
    
    return prices, timestamps


@pytest.fixture
def sample_dataframe():
    """
    Gera DataFrame de exemplo para DataLoader.
    
    Returns:
        pd.DataFrame
    """
    np.random.seed(42)
    
    n_samples = 1000
    dates = pd.date_range('2024-01-01', periods=n_samples, freq='30min')
    
    # OHLC data
    close = 50000 + np.cumsum(np.random.randn(n_samples) * 100)
    high = close + np.abs(np.random.randn(n_samples) * 50)
    low = close - np.abs(np.random.randn(n_samples) * 50)
    open_price = close + np.random.randn(n_samples) * 20
    volume = np.random.randint(100, 10000, n_samples)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    return df


# ============================================================================
# FIXTURES DE MOCKS
# ============================================================================

@pytest.fixture
def mock_keras_model():
    """
    Mock de modelo Keras para testes.
    
    Returns:
        Mock com métodos fit, predict, save, count_params
    """
    model = Mock()
    
    # Mock de métodos
    model.fit = Mock(return_value=Mock(history={
        'loss': [0.8, 0.6, 0.5],
        'accuracy': [0.5, 0.6, 0.7],
        'val_loss': [0.9, 0.7, 0.6],
        'val_accuracy': [0.45, 0.55, 0.65]
    }))
    
    model.predict = Mock(return_value=np.random.rand(100, 3).astype(np.float32))
    model.save = Mock()
    model.count_params = Mock(return_value=100000)
    
    # Mock de atributos
    model.input_shape = [(None, 60, 10)]
    model.output_shape = [(None, 3)]
    
    return model


@pytest.fixture
def mock_preprocessor():
    """
    Mock de preprocessor sklearn para testes.
    
    Returns:
        Mock com métodos fit, transform, fit_transform
    """
    preprocessor = Mock()
    
    # Mock de métodos - retornam tuplas (X, y) por padrão
    preprocessor.fit = Mock(return_value=preprocessor)
    preprocessor.transform = Mock(return_value=(
        np.random.rand(20, 60, 2).astype(np.float32),
        np.random.rand(20).astype(np.float32)
    ))
    preprocessor.fit_transform = Mock(return_value=(
        np.random.rand(100, 60, 2).astype(np.float32),
        np.random.rand(100).astype(np.float32)
    ))
    
    return preprocessor


@pytest.fixture
def mock_base_model(mock_keras_model):
    """
    Mock de BaseModel para testes.
    
    Returns:
        Mock que implementa interface BaseModel
    """
    from ml_v3_arch.interfaces import BaseModel
    
    class MockModel(BaseModel):
        def __init__(self):
            self._model = mock_keras_model
        
        def fit(self, X, y, validation_data=None, epochs=10, batch_size=32, callbacks=None, verbose=0):
            return self._model.fit(X, y, validation_data=validation_data, epochs=epochs, 
                                  batch_size=batch_size, callbacks=callbacks, verbose=verbose)
        
        def predict(self, X):
            return self._model.predict(X)
        
        def evaluate(self, X, y):
            return {'loss': 0.5, 'accuracy': 0.7}
        
        def save(self, filepath):
            self._model.save(filepath)
        
        def count_params(self):
            return self._model.count_params()
    
    return MockModel()


# ============================================================================
# FIXTURES DE FILESYSTEM
# ============================================================================

@pytest.fixture
def tmp_artifacts_dir():
    """
    Cria diretório temporário para artifacts e limpa após teste.
    
    Returns:
        Path: Caminho para diretório temporário
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="ml_v3_test_"))
    
    yield tmp_dir
    
    # Cleanup
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)


@pytest.fixture
def sample_csv_file(sample_dataframe, tmp_artifacts_dir):
    """
    Cria arquivo CSV temporário com dados de exemplo.
    
    Returns:
        Path: Caminho para arquivo CSV
    """
    csv_path = tmp_artifacts_dir / "sample_data.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    
    return csv_path


# ============================================================================
# FIXTURES DE HELPERS
# ============================================================================

@pytest.fixture
def assert_model_config_valid():
    """Helper para validar ModelConfig."""
    def _validate(config: ModelConfig):
        assert config.model_type is not None
        assert config.lookback > 0
        assert config.lstm_units > 0
        assert config.lstm_layers > 0
        assert 0 <= config.dropout < 1
        assert config.learning_rate > 0
        assert config.batch_size > 0
        assert config.epochs > 0
    
    return _validate


@pytest.fixture
def assert_backtest_config_valid():
    """Helper para validar BacktestConfig."""
    def _validate(config: BacktestConfig):
        assert config.initial_capital > 0
        assert config.fee_bps >= 0
        assert config.slippage_bps >= 0
        assert 0 < config.position_size <= 1
        assert 0 <= config.min_confidence <= 1
    
    return _validate


# ============================================================================
# PARAMETRIZE FIXTURES
# ============================================================================

@pytest.fixture(params=['lstm', 'gru', 'directional', 'improved_directional'])
def model_type(request):
    """Parametriza tipos de modelos para testes."""
    return request.param


@pytest.fixture(params=['regression', 'classification'])
def evaluator_type(request):
    """Parametriza tipos de evaluators para testes."""
    return request.param


@pytest.fixture(params=['drop', 'forward_fill', 'interpolate'])
def missing_value_strategy(request):
    """Parametriza estratégias de missing values para testes."""
    return request.param


# ============================================================================
# AUTOUSE FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed antes de cada teste."""
    np.random.seed(42)


@pytest.fixture(autouse=True)
def suppress_tensorflow_warnings():
    """Suprime warnings do TensorFlow nos testes."""
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
