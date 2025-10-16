"""
Exemplo de uso do pipeline ML v2.
Execute este script para testar o pipeline completo.
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ml_v2.preprocess import DataPreprocessor
from src.ml_v2.models.lstm_model import build_lstm
from src.ml_v2.metrics import compare_with_baselines, print_comparison
import pandas as pd
import numpy as np


def example_preprocessing():
    """Exemplo de preprocessamento sem vazamento."""
    print("\n" + "="*80)
    print("EXEMPLO 1: PREPROCESSAMENTO SEM VAZAMENTO")
    print("="*80 + "\n")
    
    # Criar dados de exemplo
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
    
    # Split temporal
    i_train = int(len(df) * 0.7)
    df_train = df.iloc[:i_train]
    df_test = df.iloc[i_train:]
    
    print(f"Dataset: {len(df)} amostras")
    print(f"Train: {len(df_train)} | Test: {len(df_test)}")
    
    # Preprocessamento
    feature_cols = ['Open', 'High', 'Low', 'Volume', 'RSI', 'MACD']
    preprocessor = DataPreprocessor(feature_cols, target_col='Close', lookback=60)
    
    print("\n✅ Fit APENAS no treino:")
    preprocessor.fit(df_train)
    
    print("✅ Transform em treino e teste:")
    X_train, y_train = preprocessor.transform(df_train)
    X_test, y_test = preprocessor.transform(df_test)
    
    print(f"\nSequências criadas:")
    print(f"  X_train: {X_train.shape}")
    print(f"  X_test: {X_test.shape}")
    
    # Desnormalizar
    y_train_usd = preprocessor.inverse_target(y_train)
    y_test_usd = preprocessor.inverse_target(y_test)
    
    print(f"\nDesnormalização:")
    print(f"  y_train range: ${y_train_usd.min():.2f} - ${y_train_usd.max():.2f}")
    print(f"  y_test range: ${y_test_usd.min():.2f} - ${y_test_usd.max():.2f}")


def example_model():
    """Exemplo de criação do modelo."""
    print("\n" + "="*80)
    print("EXEMPLO 2: MODELO LSTM")
    print("="*80 + "\n")
    
    # Criar modelo
    model = build_lstm(input_shape=(60, 6), learning_rate=1e-3)
    
    print("✅ Modelo criado:")
    model.summary()
    
    print(f"\nTotal de parâmetros: {model.count_params():,}")


def example_metrics():
    """Exemplo de métricas e baselines."""
    print("\n" + "="*80)
    print("EXEMPLO 3: MÉTRICAS E BASELINES")
    print("="*80 + "\n")
    
    # Dados de exemplo
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=n, freq='30min'),
        'Close': np.random.randn(n).cumsum() + 50000,
    })
    
    # Simular predições
    y_true = df['Close'].values[60:]
    y_pred_lstm = y_true + np.random.randn(len(y_true)) * 50  # LSTM com erro
    
    # Comparar
    results = compare_with_baselines(df, y_true, y_pred_lstm, lookback=60)
    print_comparison(results)


def example_no_leakage_check():
    """Exemplo de verificação de vazamento."""
    print("\n" + "="*80)
    print("EXEMPLO 4: VERIFICAÇÃO DE VAZAMENTO")
    print("="*80 + "\n")
    
    # Criar dados
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=n, freq='30min'),
        'Feature1': np.random.randn(n) * 100,
        'Feature2': np.random.randn(n) * 50,
        'Close': np.random.randn(n).cumsum() + 50000,
    })
    
    i_train = int(len(df) * 0.7)
    df_train = df.iloc[:i_train]
    
    feature_cols = ['Feature1', 'Feature2']
    
    # Preprocessador 1: fit apenas no treino (CORRETO)
    prep_correct = DataPreprocessor(feature_cols, target_col='Close', lookback=60)
    prep_correct.fit(df_train)
    
    # Preprocessador 2: fit no dataset completo (VAZAMENTO!)
    prep_leakage = DataPreprocessor(feature_cols, target_col='Close', lookback=60)
    prep_leakage.fit(df)
    
    print("✅ Scaler do TREINO (correto):")
    print(f"  Feature1 min/max: {prep_correct.scaler_X.data_min_[0]:.2f} / {prep_correct.scaler_X.data_max_[0]:.2f}")
    
    print("\n❌ Scaler do DATASET COMPLETO (vazamento!):")
    print(f"  Feature1 min/max: {prep_leakage.scaler_X.data_min_[0]:.2f} / {prep_leakage.scaler_X.data_max_[0]:.2f}")
    
    print("\n🔍 Diferença detectada:")
    if not np.allclose(prep_correct.scaler_X.data_min_, prep_leakage.scaler_X.data_min_):
        print("  ✅ Os scalers são DIFERENTES (sem vazamento!)")
    else:
        print("  ❌ Os scalers são IGUAIS (há vazamento!)")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ML v2 - EXEMPLOS DE USO")
    print("="*80)
    
    example_preprocessing()
    example_model()
    example_metrics()
    example_no_leakage_check()
    
    print("\n" + "="*80)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
    print("="*80)
    print("\nPróximos passos:")
    print("  1. Execute: python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv")
    print("  2. Execute: python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv")
    print("  3. Execute: python src/ml_v2/cli.py walkforward --csv data/BTCUSDT_30m_full.csv --folds 3")
    print("  4. Execute: python src/ml_v2/cli.py backtest --csv data/BTCUSDT_30m_full.csv --start 2024-01-01")
    print()
