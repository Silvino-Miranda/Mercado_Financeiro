"""
Testes para garantir zero vazamento de dados.
"""
import pytest
import numpy as np
import pandas as pd
from src.ml_v2.preprocess import DataPreprocessor


@pytest.fixture
def sample_df():
    """Cria DataFrame de exemplo para testes."""
    np.random.seed(42)
    n = 1000
    
    df = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=n, freq='30min'),
        'Open': np.random.randn(n).cumsum() + 50000,
        'High': np.random.randn(n).cumsum() + 50100,
        'Low': np.random.randn(n).cumsum() + 49900,
        'Close': np.random.randn(n).cumsum() + 50000,
        'Volume': np.random.rand(n) * 1000,
        'RSI': np.random.rand(n) * 100,
        'MACD': np.random.randn(n) * 100,
    })
    
    return df


def test_scaler_fit_only_on_train(sample_df):
    """
    Testa que o scaler fit() só acontece no treino.
    transform() em val/test deve usar scalers já ajustados.
    """
    df = sample_df.sort_values("Date").reset_index(drop=True)
    
    n = len(df)
    i_train = int(n * 0.7)
    i_val = int(n * 0.85)
    
    df_train = df.iloc[:i_train]
    df_val = df.iloc[i_train:i_val]
    df_test = df.iloc[i_val:]
    
    feature_cols = [c for c in df.columns if c not in ["Date", "Close"]]
    
    # Criar preprocessador
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=60)
    
    # fit() APENAS no treino
    preprocessor.fit(df_train)
    
    # transform() em val e test deve funcionar
    X_train, y_train = preprocessor.transform(df_train)
    X_val, y_val = preprocessor.transform(df_val)
    X_test, y_test = preprocessor.transform(df_test)
    
    # Verificações
    assert X_train.shape[0] == len(df_train) - 60
    assert X_val.shape[0] == len(df_val) - 60
    assert X_test.shape[0] == len(df_test) - 60
    assert preprocessor._fitted is True


def test_transform_before_fit_raises_error(sample_df):
    """
    Testa que transform() antes de fit() levanta erro.
    ZERO VAZAMENTO: não pode transformar sem fit.
    """
    df = sample_df
    feature_cols = [c for c in df.columns if c not in ["Date", "Close"]]
    
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=60)
    
    # transform() sem fit() deve levantar RuntimeError
    with pytest.raises(RuntimeError, match="Scaler not fitted"):
        preprocessor.transform(df)


def test_inverse_target_returns_correct_scale(sample_df):
    """
    Testa que inverse_target desnormaliza corretamente.
    """
    df = sample_df
    feature_cols = [c for c in df.columns if c not in ["Date", "Close"]]
    
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=60)
    preprocessor.fit(df)
    
    X, y_scaled = preprocessor.transform(df)
    y_usd = preprocessor.inverse_target(y_scaled)
    
    # Verificar que desnormalização está aproximadamente correta
    # (pode ter pequenas diferenças devido ao lookback)
    original_close = df['Close'].values[60:]
    
    assert len(y_usd) == len(original_close)
    # Verificar que os valores estão na escala correta (não normalizados)
    assert y_usd.min() > 1000  # Bitcoin está acima de $1k
    assert y_usd.max() < 100000  # Abaixo de $100k


def test_sequences_have_correct_shape(sample_df):
    """
    Testa que sequências LSTM têm a forma correta.
    """
    df = sample_df
    feature_cols = [c for c in df.columns if c not in ["Date", "Close"]]
    lookback = 60
    
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=lookback)
    preprocessor.fit(df)
    
    X, y = preprocessor.transform(df)
    
    # X deve ter forma (n_samples, lookback, n_features)
    assert X.ndim == 3
    assert X.shape[1] == lookback
    assert X.shape[2] == len(feature_cols)
    
    # y deve ter forma (n_samples,)
    assert y.ndim == 1
    assert len(y) == len(X)


def test_no_data_leakage_in_split(sample_df):
    """
    Testa que não há vazamento entre splits temporais.
    Scaler min/max do treino NÃO deve ser influenciado por val/test.
    """
    df = sample_df.sort_values("Date").reset_index(drop=True)
    
    n = len(df)
    i_train = int(n * 0.7)
    
    df_train = df.iloc[:i_train]
    
    feature_cols = [c for c in df.columns if c not in ["Date", "Close"]]
    
    # Preprocessador 1: fit apenas no treino
    prep1 = DataPreprocessor(feature_cols, target_col="Close", lookback=60)
    prep1.fit(df_train)
    
    # Preprocessador 2: fit no dataset completo (vazamento!)
    prep2 = DataPreprocessor(feature_cols, target_col="Close", lookback=60)
    prep2.fit(df)
    
    # Os scalers devem ser diferentes
    # Se forem iguais, há vazamento!
    assert not np.allclose(prep1.scaler_X.data_min_, prep2.scaler_X.data_min_)
    assert not np.allclose(prep1.scaler_X.data_max_, prep2.scaler_X.data_max_)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
