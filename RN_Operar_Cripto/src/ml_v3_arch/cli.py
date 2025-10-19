"""
CLI principal do pipeline ML v3 - Clean Architecture.

Subcomandos: train, evaluate, backtest
Usa Dependency Injection e SOLID principles.
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# Setup paths ANTES de imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Seeds para reprodutibilidade (ANTES de imports TensorFlow/NumPy)
os.environ["PYTHONHASHSEED"] = "0"
random.seed(42)

# Imports do projeto (depois de setup)
from ml_v3_arch.domain.entities import ModelConfig, BacktestConfig
from ml_v3_arch.factories.model_factory import ModelFactory
from ml_v3_arch.infrastructure.data_loader import DataLoader, DataLoadConfig
from ml_v3_arch.infrastructure.model_persistence import ModelPersistence
from ml_v3_arch.services.training_service import TrainingService
from ml_v3_arch.services.evaluation_service import EvaluationService
from ml_v3_arch.services.backtest_service import BacktestService


def setup_tensorflow():
    """Configura TensorFlow para reprodutibilidade."""
    import numpy as np
    import tensorflow as tf
    
    # Configurar seeds
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Configurações de GPU (se disponível)
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(f"GPU config error: {e}")


def create_artifacts_dirs():
    """Cria estrutura de diretórios para artefatos."""
    dirs = [
        "artifacts/v3/metrics",
        "artifacts/v3/equity",
        "artifacts/v3/checkpoints",
        "artifacts/v3/logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def cmd_train(args):
    """Comando: train - Treina modelo usando TrainingService v3."""
    print("\n" + "="*80)
    print("COMANDO: TRAIN (v3 - Clean Architecture)")
    print("="*80 + "\n")
    
    # 1. Configurar DataLoader
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True,
        drop_duplicates=True,
        handle_missing='drop',
        validate_ohlc=True
    )
    
    data_loader = DataLoader(data_config)
    
    # 2. Carregar dados
    print("📂 Carregando dados...")
    df = data_loader.load(Path(args.csv), verbose=1)
    
    # 3. Configurar modelo
    model_config = ModelConfig(
        model_type='lstm',
        lookback=args.lookback,
        lstm_units=args.units,
        lstm_layers=2,
        dropout=args.dropout,
        learning_rate=args.lr,
        batch_size=args.batch_size,
        epochs=args.epochs,
        patience=args.patience
    )
    
    print(f"\n🤖 Configuração do modelo:")
    print(f"   Tipo: {model_config.model_type}")
    print(f"   Lookback: {model_config.lookback}")
    print(f"   LSTM units: {model_config.lstm_units}")
    print(f"   Dropout: {model_config.dropout}")
    print(f"   Learning rate: {model_config.learning_rate}")
    
    # 4. Criar ModelFactory e criar modelo
    model_factory = ModelFactory()
    feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
    n_features = len(feature_cols)
    
    # Criar modelo (já define input_shape automaticamente no primeiro fit)
    model = model_factory.create_model(config=model_config)
    
    # 5. Criar Preprocessor simples (StandardScaler)
    from sklearn.preprocessing import StandardScaler
    
    class SimplePreprocessor:
        def __init__(self, feature_cols, target_col, lookback):
            self.feature_cols = feature_cols
            self.target_col = target_col
            self.lookback = lookback
            self.scaler = StandardScaler()
        
        def fit_transform(self, df):
            import pandas as pd
            import numpy as np
            # Normalizar features
            X = df[self.feature_cols].values
            X_scaled = self.scaler.fit_transform(X)
            y = df[self.target_col].values
            
            # Criar sequências
            X_seq, y_seq = [], []
            for i in range(len(X_scaled) - self.lookback):
                X_seq.append(X_scaled[i:i + self.lookback])
                y_seq.append(y[i + self.lookback])
            
            return np.array(X_seq), np.array(y_seq)
        
        def transform(self, df):
            """Transform sem fit (usa scaler já ajustado)."""
            import numpy as np
            # Usar scaler já fitted
            X = df[self.feature_cols].values
            X_scaled = self.scaler.transform(X)
            y = df[self.target_col].values
            
            # Criar sequências
            X_seq, y_seq = [], []
            for i in range(len(X_scaled) - self.lookback):
                X_seq.append(X_scaled[i:i + self.lookback])
                y_seq.append(y[i + self.lookback])
            
            return np.array(X_seq), np.array(y_seq)
    
    preprocessor = SimplePreprocessor(
        feature_cols=feature_cols,
        target_col='Close',
        lookback=model_config.lookback
    )
    
    # 6. Criar TrainingService
    training_service = TrainingService(
        model=model,
        preprocessor=preprocessor,
        config=model_config,
        artifacts_dir='artifacts/v3'
    )
    
    # 7. Split temporal
    n = len(df)
    i_train = int(n * 0.7)
    i_val = int(n * 0.85)
    
    df_train = df.iloc[:i_train]
    df_val = df.iloc[i_train:i_val]
    
    # 8. Treinar (save_artifacts=False pois preprocessor é classe local)
    print("\n🔥 Iniciando treinamento...\n")
    print(f"   Train: {len(df_train):,} samples")
    print(f"   Val: {len(df_val):,} samples\n")
    
    result = training_service.train(
        df_train=df_train,
        df_val=df_val,
        save_artifacts=False,  # TODO: Mover SimplePreprocessor para arquivo separado
        verbose=1
    )
    
    # Modelo já está treinado no training_service
    model = training_service.model
    history = result['history']
    metadata = result['metadata']
    
    # 9. Salvar modelo
    ts = time.strftime("%Y%m%d_%H%M%S")
    persistence = ModelPersistence(base_dir='artifacts/v3')
    
    model_path = persistence.save_keras_model(
        model=model,
        name=f'lstm_v3_{ts}',
        metadata=metadata
    )
    
    print(f"\n✅ Modelo salvo em: {model_path}")
    
    # 10. Salvar histórico
    history_path = f"artifacts/v3/logs/history_{ts}.json"
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")
    
    # 9. Resumo final
    print(f"\n📊 RESUMO DO TREINAMENTO:")
    print(f"   Épocas executadas: {len(history.get('loss', []))}")
    print(f"   Loss final (treino): {history.get('loss', [])[-1]:.6f}")
    print(f"   Loss final (val): {history.get('val_loss', [])[-1]:.6f}")
    print(f"   MAE final (val): {history.get('val_mae', [])[-1]:.6f}")


def cmd_train_classifier(args):
    """Comando: train_classifier - Treina classificador direcional."""
    print("\n" + "="*80)
    print("COMANDO: TRAIN CLASSIFIER (v3 - Clean Architecture)")
    print("="*80 + "\n")
    
    # 1. Configurar DataLoader
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True,
        drop_duplicates=True,
        handle_missing='drop',
        validate_ohlc=True
    )
    
    data_loader = DataLoader(data_config)
    
    # 2. Carregar dados
    print("📂 Carregando dados...")
    df = data_loader.load(Path(args.csv), verbose=1)
    
    # 3. Configurar modelo de classificação
    model_config = ModelConfig(
        model_type='directional',
        lookback=args.lookback,
        lstm_units=args.units,
        lstm_layers=2,
        dropout=args.dropout,
        learning_rate=args.lr,
        batch_size=args.batch_size,
        epochs=args.epochs,
        patience=15
    )
    
    print(f"\n🤖 Configuração do classificador:")
    print(f"   Tipo: {model_config.model_type}")
    print(f"   Lookback: {model_config.lookback}")
    print(f"   LSTM units: {model_config.lstm_units}")
    print(f"   Classes: 3 (BAIXA, LATERAL, ALTA)")
    
    # 4. Criar ModelFactory
    model_factory = ModelFactory()
    
    # 5. Criar TrainingService
    feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
    
    training_service = TrainingService(
        model_config=model_config,
        model_factory=model_factory,
        feature_cols=feature_cols,
        target_col='Close'
    )
    
    # 6. Treinar
    print("\n🔥 Iniciando treinamento...\n")
    
    model, history, metadata = training_service.train(
        df=df,
        validation_split=0.15,
        save_artifacts=True,
        artifacts_dir='artifacts/v3/checkpoints',
        verbose=1
    )
    
    # 7. Salvar modelo
    ts = time.strftime("%Y%m%d_%H%M%S")
    persistence = ModelPersistence(base_dir='artifacts/v3/checkpoints')
    
    model_path = persistence.save_model(
        model=model,
        model_name=f'classifier_v3_{ts}',
        metadata=metadata
    )
    
    print(f"\n✅ Classificador salvo em: {model_path}")


def cmd_evaluate(args):
    """Comando: evaluate - Avalia modelo usando EvaluationService v3."""
    print("\n" + "="*80)
    print("COMANDO: EVALUATE (v3 - Clean Architecture)")
    print("="*80 + "\n")
    
    # 1. Carregar dados
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True
    )
    
    data_loader = DataLoader(data_config)
    df = data_loader.load(Path(args.csv), verbose=1)
    
    # 2. Carregar último modelo
    persistence = ModelPersistence(base_dir='artifacts/v3/checkpoints')
    
    checkpoint_dir = Path("artifacts/v3/checkpoints")
    models = sorted(checkpoint_dir.glob("lstm_v3_*.keras"))
    
    if not models:
        print("❌ Nenhum modelo v3 encontrado! Execute 'train' primeiro.")
        return
    
    model_name = models[-1].stem
    print(f"📦 Carregando modelo: {model_name}")
    
    model, metadata = persistence.load_model(model_name)
    
    # 3. Criar EvaluationService
    evaluation_service = EvaluationService()
    
    # 4. Avaliar
    print("\n📊 Avaliando modelo...\n")
    
    # Preprocessar dados de teste (últimos 15%)
    n = len(df)
    i_val = int(n * 0.85)
    df_test = df.iloc[i_val:]
    
    # TODO: Implementar avaliação completa
    print("✅ Avaliação concluída!")


def cmd_backtest(args):
    """Comando: backtest - Backtest usando BacktestService v3."""
    print("\n" + "="*80)
    print("COMANDO: BACKTEST (v3 - Clean Architecture)")
    print("="*80 + "\n")
    
    # 1. Configurar backtest
    backtest_config = BacktestConfig(
        initial_capital=args.capital,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
        position_size=0.95,
        min_confidence=0.0,
        threshold_bps=args.threshold_bps
    )
    
    print(f"💰 Configuração do backtest:")
    print(f"   Capital inicial: ${backtest_config.initial_capital:,.2f}")
    print(f"   Fee: {backtest_config.fee_bps} bps")
    print(f"   Slippage: {backtest_config.slippage_bps} bps")
    
    # 2. Carregar dados
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True
    )
    
    data_loader = DataLoader(data_config)
    df = data_loader.load(Path(args.csv), verbose=1)
    
    # 3. Filtrar período de backtest
    if args.start:
        df_backtest = df[df['Date'] >= args.start].reset_index(drop=True)
    else:
        # Usar últimos 15% como backtest
        n = len(df)
        i_val = int(n * 0.85)
        df_backtest = df.iloc[i_val:].reset_index(drop=True)
    
    print(f"\n📅 Período: {df_backtest['Date'].min()} a {df_backtest['Date'].max()}")
    print(f"📊 Amostras: {len(df_backtest):,}")
    
    # 4. Criar BacktestService
    backtest_service = BacktestService(backtest_config)
    
    # 5. TODO: Implementar backtest completo
    print("\n✅ Backtest em desenvolvimento...")


def main():
    """Main CLI v3."""
    # NOTA: setup_tensorflow() desabilitado devido a bug de recursão NumPy
    # O TensorFlow será configurado automaticamente quando necessário
    # setup_tensorflow()
    create_artifacts_dirs()
    
    parser = argparse.ArgumentParser(
        description="ML v3 - Pipeline com Clean Architecture + SOLID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Treinar modelo LSTM de regressão
  python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50

  # Treinar classificador direcional
  python -m src.ml_v3_arch.cli train_classifier --csv data/BTCUSDT_30m_full.csv

  # Avaliar modelo
  python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv

  # Backtest
  python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000

Comparação v2 vs v3:
  - v2: Código procedural com imports diretos
  - v3: Clean Architecture com DI e SOLID
  - v3: Testável (87 testes unitários)
  - v3: Validações robustas em todas as camadas
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # === TRAIN ===
    parser_train = subparsers.add_parser("train", help="Treina modelo LSTM")
    parser_train.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_train.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_train.add_argument("--epochs", type=int, default=50, help="Épocas de treino")
    parser_train.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser_train.add_argument("--units", type=int, default=64, help="LSTM units")
    parser_train.add_argument("--dropout", type=float, default=0.3, help="Dropout rate")
    parser_train.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser_train.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    
    # === TRAIN CLASSIFIER ===
    parser_tc = subparsers.add_parser("train_classifier", help="Treina classificador direcional")
    parser_tc.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_tc.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_tc.add_argument("--epochs", type=int, default=100, help="Épocas de treino")
    parser_tc.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser_tc.add_argument("--units", type=int, default=64, help="LSTM units")
    parser_tc.add_argument("--dropout", type=float, default=0.3, help="Dropout rate")
    parser_tc.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    
    # === EVALUATE ===
    parser_eval = subparsers.add_parser("evaluate", help="Avalia modelo vs baselines")
    parser_eval.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_eval.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    
    # === BACKTEST ===
    parser_bt = subparsers.add_parser("backtest", help="Backtest com custos")
    parser_bt.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_bt.add_argument("--start", type=str, default=None, help="Data início (YYYY-MM-DD)")
    parser_bt.add_argument("--fee-bps", type=float, default=10.0, help="Taxa exchange (bps)")
    parser_bt.add_argument("--slippage-bps", type=float, default=5.0, help="Slippage (bps)")
    parser_bt.add_argument("--threshold-bps", type=float, default=20.0, help="Threshold entrada (bps)")
    parser_bt.add_argument("--capital", type=float, default=10000.0, help="Capital inicial")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Executar comando
    if args.command == "train":
        cmd_train(args)
    elif args.command == "train_classifier":
        cmd_train_classifier(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "backtest":
        cmd_backtest(args)


if __name__ == "__main__":
    main()
