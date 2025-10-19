"""
Exemplo de uso dos Adapters - Migração gradual v2 → v3.

Este exemplo mostra como usar os adapters para:
1. Manter código v2 funcionando
2. Usar implementação v3 (mais robusta)
3. Migração gradual sem quebrar

Execute: python -m src.ml_v3_arch.adapters.example_usage
"""
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

import pandas as pd
import numpy as np

from ml_v3_arch.adapters import (
    DataPreprocessorAdapter,
    ModelBuilderAdapter,
    BacktestAdapter
)


def example_preprocessor_adapter():
    """Exemplo: DataPreprocessorAdapter mantém interface v2."""
    print("\n" + "="*80)
    print("1️⃣ EXEMPLO: DataPreprocessorAdapter")
    print("="*80)
    
    # Criar dados de exemplo
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=1000, freq='30min')
    df = pd.DataFrame({
        'Date': dates,
        'Open': np.random.randn(1000).cumsum() + 100,
        'High': np.random.randn(1000).cumsum() + 101,
        'Low': np.random.randn(1000).cumsum() + 99,
        'Close': np.random.randn(1000).cumsum() + 100,
        'Volume': np.random.randint(1000, 10000, 1000)
    })
    
    # Split
    df_train = df.iloc[:700]
    df_val = df.iloc[700:]
    
    # USO IDÊNTICO À V2 (código não quebra!)
    preprocessor = DataPreprocessorAdapter(
        feature_cols=['Open', 'High', 'Low', 'Volume'],
        target_col='Close',
        lookback=60
    )
    
    # Fit apenas no treino
    preprocessor.fit(df_train)
    
    # Transform em train e val
    X_train, y_train = preprocessor.transform(df_train)
    X_val, y_val = preprocessor.transform(df_val)
    
    print(f"✅ Preprocessor fitted")
    print(f"📊 X_train: {X_train.shape}")
    print(f"📊 X_val: {X_val.shape}")
    print(f"\n💡 Código v2 funcionando com implementação v3!")


def example_model_builder_adapter():
    """Exemplo: ModelBuilderAdapter mantém interface v2."""
    print("\n" + "="*80)
    print("2️⃣ EXEMPLO: ModelBuilderAdapter")
    print("="*80)
    
    # USO IDÊNTICO À V2 (código não quebra!)
    
    # 1. Modelo LSTM de regressão
    model_reg = ModelBuilderAdapter.build_lstm(
        input_shape=(60, 10),
        learning_rate=1e-3
    )
    
    print(f"✅ Modelo LSTM (regressão): {model_reg.count_params():,} parâmetros")
    
    # 2. Modelo classificação direcional
    model_cls = ModelBuilderAdapter.build_directional_lstm(
        input_shape=(60, 10),
        n_classes=3,
        lstm_units=64,
        dropout=0.3,
        learning_rate=1e-3
    )
    
    print(f"✅ Modelo classificação: {model_cls.count_params():,} parâmetros")
    
    # 3. Callbacks (igual v2)
    callbacks = ModelBuilderAdapter.get_callbacks(
        patience_early=10,
        patience_lr=5
    )
    
    print(f"✅ Callbacks: {len(callbacks)} criados")
    print(f"\n💡 Código v2 funcionando com ModelFactory v3!")


def example_backtest_adapter():
    """Exemplo: BacktestAdapter mantém interface v2."""
    print("\n" + "="*80)
    print("3️⃣ EXEMPLO: BacktestAdapter")
    print("="*80)
    
    # Criar dados de exemplo
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=500, freq='30min')
    close = np.random.randn(500).cumsum() + 100
    
    df_backtest = pd.DataFrame({
        'Date': dates,
        'Close': close
    })
    
    # Predições simuladas (regressão)
    preds_usd = close + np.random.randn(500) * 2
    
    # USO IDÊNTICO À V2 (código não quebra!)
    equity_curve, metrics = BacktestAdapter.backtest_regression(
        df=df_backtest,
        preds_usd=preds_usd,
        fee_bps=10.0,
        slippage_bps=5.0,
        threshold_bps=20.0,
        initial_capital=10000.0
    )
    
    print(f"✅ Backtest executado")
    print(f"📊 Equity curve: {len(equity_curve)} pontos")
    print(f"📈 Retorno total: {metrics['total_return']:.2%}")
    print(f"🎯 Total de trades: {metrics['total_trades']}")
    
    # Imprimir relatório (igual v2)
    BacktestAdapter.print_backtest_report(metrics)
    
    print(f"💡 Código v2 funcionando com BacktestService v3!")


def example_full_pipeline():
    """Exemplo: Pipeline completo usando adapters."""
    print("\n" + "="*80)
    print("4️⃣ EXEMPLO: PIPELINE COMPLETO COM ADAPTERS")
    print("="*80)
    
    # Dados
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=1000, freq='30min')
    df = pd.DataFrame({
        'Date': dates,
        'Open': np.random.randn(1000).cumsum() + 100,
        'High': np.random.randn(1000).cumsum() + 101,
        'Low': np.random.randn(1000).cumsum() + 99,
        'Close': np.random.randn(1000).cumsum() + 100,
        'Volume': np.random.randint(1000, 10000, 1000)
    })
    
    # Split
    df_train = df.iloc[:700]
    df_val = df.iloc[700:850]
    df_test = df.iloc[850:]
    
    print("\n📊 ETAPA 1: Preprocessamento")
    preprocessor = DataPreprocessorAdapter(
        feature_cols=['Open', 'High', 'Low', 'Volume'],
        target_col='Close',
        lookback=60
    )
    
    X_train, y_train = preprocessor.fit_transform(df_train)
    X_val, y_val = preprocessor.transform(df_val)
    X_test, y_test = preprocessor.transform(df_test)
    
    print(f"✅ Dados preprocessados: train={X_train.shape}, val={X_val.shape}, test={X_test.shape}")
    
    print("\n🤖 ETAPA 2: Construção do Modelo")
    model = ModelBuilderAdapter.build_lstm(
        input_shape=X_train.shape[1:],
        learning_rate=1e-3
    )
    
    callbacks = ModelBuilderAdapter.get_callbacks(patience_early=5, patience_lr=3)
    
    print(f"✅ Modelo criado: {model.count_params():,} parâmetros")
    
    print("\n🔥 ETAPA 3: Treinamento (simulado - 2 épocas)")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=2,  # Reduzido para exemplo
        batch_size=32,
        callbacks=callbacks,
        verbose=0
    )
    
    print(f"✅ Treinamento concluído: {len(history.history['loss'])} épocas")
    
    print("\n🔮 ETAPA 4: Predições")
    y_pred_scaled = model.predict(X_test, verbose=0).ravel()
    y_pred_usd = preprocessor.inverse_target(y_pred_scaled)
    
    print(f"✅ Predições geradas: {len(y_pred_usd)} amostras")
    
    print("\n📈 ETAPA 5: Backtest")
    equity_curve, metrics = BacktestAdapter.backtest_regression(
        df=df_test.iloc[60:].reset_index(drop=True),  # Alinhar com lookback
        preds_usd=y_pred_usd,
        fee_bps=10.0,
        slippage_bps=5.0,
        initial_capital=10000.0
    )
    
    BacktestAdapter.print_backtest_report(metrics)
    
    print("\n✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
    print("💡 Todo código v2 migrado para v3 sem quebrar!")


def main():
    """Executa todos os exemplos."""
    print("\n" + "="*80)
    print("🎯 ADAPTERS - MIGRAÇÃO GRADUAL V2 → V3")
    print("="*80)
    print("\nObjetivo: Manter código v2 funcionando usando implementação v3")
    print("Padrão: Adapter (GoF Design Patterns)")
    
    # Executar exemplos
    example_preprocessor_adapter()
    example_model_builder_adapter()
    example_backtest_adapter()
    example_full_pipeline()
    
    print("\n" + "="*80)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
    print("="*80)
    print("\n📚 Próximos passos:")
    print("   1. Atualizar CLI v2 para usar adapters")
    print("   2. Criar testes para adapters")
    print("   3. Migrar gradualmente para v3 pura")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
