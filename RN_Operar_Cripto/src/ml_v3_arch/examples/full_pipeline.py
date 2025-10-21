"""
Exemplo Completo: Pipeline de Classificação End-to-End

Demonstra:
1. DataLoader: Carregamento robusto
2. ModelFactory: Criação de modelo
3. TrainingService: Treinamento com DI
4. EvaluationService: Avaliação robusta
5. BacktestService: Simulação de trading
6. ModelPersistence: Save/load de artifacts
"""
from pathlib import Path
import sys

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

import numpy as np
from ml_v3_arch.domain.entities import ModelConfig, BacktestConfig
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.services import (
    TrainingService,
    EvaluationService,
    BacktestService
)
from ml_v3_arch.infrastructure import (
    DataLoader,
    DataLoadConfig,
    ModelPersistence
)


def main():
    """Pipeline completo de classificação."""
    
    print("\n" + "="*80)
    print("🚀 PIPELINE COMPLETO - ml_v3_arch")
    print("="*80)
    print()
    
    # ===================================================================
    # 1. CONFIGURAÇÃO
    # ===================================================================
    print("📋 FASE 1: Configuração")
    print("-" * 80)
    
    # Paths
    data_path = Path("data/BTCUSDT_30m_full.csv")
    artifacts_dir = Path("artifacts_v3")
    
    # Data config
    data_config = DataLoadConfig(
        required_columns=['open', 'high', 'low', 'close', 'volume'],
        optional_columns=['rsi_14', 'bb_upper', 'bb_lower', 'macd'],
        date_column='timestamp',
        parse_dates=True,
        drop_duplicates=True,
        handle_missing='forward_fill',
        validate_ohlc=True
    )
    
    # Model config
    model_config = ModelConfig(
        input_shape=(60, 10),
        output_shape=3,
        lstm_units=[128, 64],
        dropout_rate=0.3,
        learning_rate=0.001,
        batch_size=32,
        epochs=50
    )
    
    # Backtest config
    backtest_config = BacktestConfig(
        initial_capital=10000.0,
        transaction_cost=0.1
    )
    
    print("✅ Configurações criadas")
    print()
    
    # ===================================================================
    # 2. CARREGAR DADOS
    # ===================================================================
    print("📂 FASE 2: Carregamento de Dados")
    print("-" * 80)
    
    loader = DataLoader(data_config)
    
    try:
        df = loader.load(data_path, verbose=1)
        
        # Mostrar info
        info = loader.get_info(df)
        print(f"ℹ️  Info:")
        print(f"   Período: {info['date_range']['days']} dias")
        print(f"   Memória: {info['memory_usage_mb']:.2f} MB")
        print()
    
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        print("💡 Verifique se o arquivo existe e está no formato correto")
        return
    
    # ===================================================================
    # 3. PREPARAR DADOS (Simulado - você implementaria preprocessing real)
    # ===================================================================
    print("🔧 FASE 3: Preparação de Dados")
    print("-" * 80)
    
    # Simulação de dados (na prática, você usaria seus features reais)
    n_samples = min(10000, len(df))
    X = np.random.randn(n_samples, 60, 10).astype(np.float32)
    y = np.random.randint(0, 3, size=n_samples)
    
    # Split train/val/test
    train_size = int(0.7 * n_samples)
    val_size = int(0.15 * n_samples)
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
    X_test, y_test = X[train_size+val_size:], y[train_size+val_size:]
    
    print(f"✅ Dados preparados:")
    print(f"   Train: {len(X_train):,} samples")
    print(f"   Val:   {len(X_val):,} samples")
    print(f"   Test:  {len(X_test):,} samples")
    print()
    
    # ===================================================================
    # 4. CRIAR MODELO (Factory Pattern)
    # ===================================================================
    print("🏗️  FASE 4: Criação de Modelo")
    print("-" * 80)
    
    model = ModelFactory.create_model(
        model_type='improved_directional',
        config=model_config
    )
    
    print(f"✅ Modelo criado: {type(model).__name__}")
    print(f"   Parâmetros: {model.count_params():,}")
    print()
    
    # ===================================================================
    # 5. TREINAR MODELO (TrainingService)
    # ===================================================================
    print("🎓 FASE 5: Treinamento")
    print("-" * 80)
    
    # Criar preprocessor mock (na prática, seria real)
    class MockPreprocessor:
        def fit(self, X, y=None):
            return self
        def transform(self, X):
            return X
        def fit_transform(self, X, y=None):
            return X
    
    preprocessor = MockPreprocessor()
    
    trainer = TrainingService(
        model=model,
        preprocessor=preprocessor,
        config=model_config
    )
    
    history = trainer.train(
        X_train, y_train,
        X_val, y_val,
        output_dir=artifacts_dir,
        save_best=True,
        verbose=1
    )
    
    print(f"✅ Treinamento concluído")
    print(f"   Épocas: {len(history['loss'])}")
    print(f"   Val Accuracy final: {history['val_accuracy'][-1]:.4f}")
    print()
    
    # ===================================================================
    # 6. AVALIAR MODELO (EvaluationService)
    # ===================================================================
    print("📊 FASE 6: Avaliação")
    print("-" * 80)
    
    evaluator = EvaluationService(
        model=model,
        evaluator_type='classification',
        class_names=['BAIXA', 'LATERAL', 'ALTA']
    )
    
    metrics = evaluator.evaluate(
        X_test, y_test,
        verbose=1
    )
    
    # Comparar com baseline
    baseline_preds = np.ones(len(y_test), dtype=int)  # Sempre LATERAL
    
    comparison = evaluator.compare_with_baselines(
        X_test, y_test,
        baselines={'Baseline_LATERAL': baseline_preds},
        verbose=1
    )
    
    print()
    
    # ===================================================================
    # 7. BACKTEST (BacktestService)
    # ===================================================================
    print("💹 FASE 7: Backtesting")
    print("-" * 80)
    
    # Simular preços
    prices = np.cumsum(np.random.randn(len(X_test)) * 100) + 50000
    timestamps = np.arange(len(X_test))
    
    backtester = BacktestService(
        model=model,
        config=backtest_config,
        strategy_type='classification'
    )
    
    result = backtester.run(
        X_test, prices, timestamps,
        verbose=1
    )
    
    # Salvar resultados
    backtester.save_results(
        result,
        output_dir=artifacts_dir / "backtest",
        prefix="classification_example"
    )
    
    print()
    
    # ===================================================================
    # 8. PERSISTÊNCIA (ModelPersistence)
    # ===================================================================
    print("💾 FASE 8: Persistência")
    print("-" * 80)
    
    persistence = ModelPersistence(artifacts_dir)
    
    # Salvar modelo
    model_path = persistence.save_keras_model(
        model,
        name="classification_example",
        metadata={
            'type': 'improved_directional',
            'val_accuracy': float(history['val_accuracy'][-1]),
            'epochs': len(history['loss']),
            'f1_macro': float(metrics['f1_macro'])
        },
        verbose=1
    )
    
    # Salvar preprocessor
    prep_path = persistence.save_preprocessor(
        preprocessor,
        name="classification_example",
        metadata={'type': 'mock'},
        verbose=1
    )
    
    # Salvar history
    history_path = persistence.save_history(
        history,
        name="classification_example",
        verbose=1
    )
    
    # Salvar config
    config_path = persistence.save_config(
        {
            'model_config': model_config.__dict__,
            'backtest_config': backtest_config.__dict__,
            'data_config': {
                'required_columns': data_config.required_columns,
                'optional_columns': data_config.optional_columns
            }
        },
        name="classification_example",
        verbose=1
    )
    
    print()
    
    # ===================================================================
    # 9. CARREGAR DE VOLTA (Demonstração)
    # ===================================================================
    print("🔄 FASE 9: Carregar Modelo")
    print("-" * 80)
    
    # Carregar modelo mais recente
    latest_model_path = persistence.get_latest_model("classification_example")
    
    if latest_model_path:
        loaded_model, loaded_metadata = persistence.load_keras_model(
            latest_model_path,
            verbose=1
        )
        
        print(f"✅ Modelo carregado com sucesso")
        print(f"   Val Accuracy: {loaded_metadata.get('val_accuracy', 'N/A')}")
        print(f"   F1-Macro: {loaded_metadata.get('f1_macro', 'N/A')}")
    
    print()
    
    # ===================================================================
    # RESUMO FINAL
    # ===================================================================
    print("="*80)
    print("✅ PIPELINE COMPLETO - FINALIZADO COM SUCESSO")
    print("="*80)
    print()
    print("📊 RESUMO:")
    print(f"   • Dados carregados e validados: {n_samples:,} samples")
    print(f"   • Modelo treinado: {len(history['loss'])} épocas")
    print(f"   • Val Accuracy: {history['val_accuracy'][-1]:.4f}")
    print(f"   • F1-Macro: {metrics['f1_macro']:.4f}")
    print(f"   • Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"   • Backtest Win Rate: {result.win_rate*100:.2f}%")
    print(f"   • Backtest Return: {result.total_return:.2f}%")
    print(f"   • Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print()
    print("💡 ARQUITETURA SOLID:")
    print("   ✅ SRP: Cada classe tem uma responsabilidade")
    print("   ✅ DIP: Services dependem de abstrações")
    print("   ✅ Factory Pattern: ModelFactory cria modelos")
    print("   ✅ Strategy Pattern: Evaluators e TradingStrategy")
    print()
    print(f"📁 Artifacts salvos em: {artifacts_dir}")
    print()


if __name__ == "__main__":
    main()
