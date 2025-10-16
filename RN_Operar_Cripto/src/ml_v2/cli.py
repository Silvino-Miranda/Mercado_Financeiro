"""
CLI principal do pipeline ML v2.
Subcomandos: train, evaluate, walkforward, backtest.
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from tensorflow import keras

from src.ml_v2.preprocess import DataPreprocessor
from src.ml_v2.models.lstm_model import build_lstm, get_callbacks
from src.ml_v2.metrics import compare_with_baselines, print_comparison
from src.ml_v2.validation.walkforward import run_walkforward
from src.ml_v2.backtest.engine import backtest_regression, print_backtest_report

# Seeds para reprodutibilidade
os.environ["PYTHONHASHSEED"] = "0"
random.seed(42)
np.random.seed(42)
sys.path.append(str(Path(__file__).parent))


def setup_tensorflow():
    """Configura TensorFlow para reprodutibilidade."""
    import tensorflow as tf
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
        "artifacts/metrics",
        "artifacts/equity",
        "artifacts/checkpoints",
        "artifacts/logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def get_feature_cols(df: pd.DataFrame) -> List[str]:
    """
    Extrai colunas de features do DataFrame.
    
    Exclui: Date, Close (é o target)
    """
    exclude = ['Date', 'Close']
    return [c for c in df.columns if c not in exclude]


def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    Carrega e prepara dados.
    
    Args:
        csv_path: Caminho do CSV
        
    Returns:
        DataFrame preparado
    """
    df = pd.read_csv(csv_path)
    
    # Converter Date se existir
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Ordenar por data
    df = df.sort_values('Date').reset_index(drop=True)
    
    return df


def cmd_train(args):
    """Comando: train - Treina o modelo LSTM."""
    print("\n" + "="*80)
    print("COMANDO: TRAIN")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    print(f"Dataset: {len(df)} amostras")
    print(f"Features: {len(feature_cols)}")
    print(f"Lookback: {args.lookback}")
    
    # Split temporal: 70% train, 15% val, 15% test
    n = len(df)
    i_train = int(n * 0.70)
    i_val = int(n * 0.85)
    
    df_train = df.iloc[:i_train]
    df_val = df.iloc[i_train:i_val]
    df_test = df.iloc[i_val:]
    
    print(f"Split: train={len(df_train)}, val={len(df_val)}, test={len(df_test)}")
    
    # Preprocessamento (fit APENAS no treino)
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=args.lookback)
    preprocessor.fit(df_train)
    
    X_train, y_train = preprocessor.transform(df_train)
    X_val, y_val = preprocessor.transform(df_val)
    
    print(f"\nSequências: X_train={X_train.shape}, X_val={X_val.shape}")
    
    # Modelo
    model = build_lstm(input_shape=X_train.shape[1:], learning_rate=args.lr)
    
    print(f"\nModelo: {model.count_params():,} parâmetros")
    
    # Callbacks
    callbacks = get_callbacks(patience_early=args.patience, patience_lr=args.patience // 2)
    
    # Treino
    print("\nIniciando treino...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        shuffle=False,  # TEMPORAL: sem shuffle!
        callbacks=callbacks,
        verbose=1
    )
    
    # Salvar modelo
    ts = time.strftime("%Y%m%d_%H%M%S")
    model_path = f"artifacts/checkpoints/lstm_model_{ts}.keras"
    model.save(model_path)
    
    print(f"\n✅ Modelo salvo em: {model_path}")
    
    # Salvar histórico
    history_path = f"artifacts/logs/history_{ts}.json"
    with open(history_path, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")


def cmd_evaluate(args):
    """Comando: evaluate - Avalia modelo vs baselines."""
    print("\n" + "="*80)
    print("COMANDO: EVALUATE")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    # Split
    n = len(df)
    i_train = int(n * 0.70)
    i_val = int(n * 0.85)
    
    df_train = df.iloc[:i_train]
    df_test = df.iloc[i_val:]
    
    # Preprocessamento
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=args.lookback)
    preprocessor.fit(df_train)
    
    X_test, y_test = preprocessor.transform(df_test)
    
    # Carregar último modelo
    checkpoint_dir = Path("artifacts/checkpoints")
    models = sorted(checkpoint_dir.glob("*.keras"))
    
    if not models:
        print("❌ Nenhum modelo encontrado! Execute 'train' primeiro.")
        return
    
    model_path = models[-1]
    print(f"Carregando modelo: {model_path.name}")
    
    model = keras.models.load_model(model_path)
    
    # Predições
    y_pred_scaled = model.predict(X_test, verbose=0).ravel()
    y_pred_usd = preprocessor.inverse_target(y_pred_scaled)
    
    # Comparar com baselines
    results = compare_with_baselines(df_test, y_pred_usd, y_pred_usd, args.lookback)
    
    # Imprimir
    print_comparison(results)
    
    # Salvar JSON
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_path = f"artifacts/metrics/eval_{ts}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Resultados salvos em: {results_path}")


def cmd_walkforward(args):
    """Comando: walkforward - Validação walk-forward."""
    print("\n" + "="*80)
    print("COMANDO: WALK-FORWARD")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    # Run walk-forward
    results = run_walkforward(
        df=df,
        feature_cols=feature_cols,
        lookback=args.lookback,
        n_folds=args.folds,
        epochs=args.epochs,
        batch_size=args.batch_size,
        verbose=1 if args.verbose else 0
    )
    
    # Salvar resultados
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_path = f"artifacts/metrics/walkforward_{ts}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Resultados salvos em: {results_path}")


def cmd_backtest(args):
    """Comando: backtest - Backtest com custos."""
    print("\n" + "="*80)
    print("COMANDO: BACKTEST")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    # Filtrar período
    if args.start:
        df_backtest = df[df['Date'] >= args.start].reset_index(drop=True)
        df_train = df[df['Date'] < args.start].reset_index(drop=True)
    else:
        # Usar últimos 30% como backtest
        split_idx = int(len(df) * 0.70)
        df_train = df.iloc[:split_idx]
        df_backtest = df.iloc[split_idx:]
    
    print(f"Período de backtest: {df_backtest['Date'].min()} a {df_backtest['Date'].max()}")
    print(f"Amostras: {len(df_backtest)}")
    
    # Preprocessamento (fit no passado)
    preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=args.lookback)
    preprocessor.fit(df_train)
    
    # Carregar modelo
    checkpoint_dir = Path("artifacts/checkpoints")
    models = sorted(checkpoint_dir.glob("*.keras"))
    
    if not models:
        print("❌ Nenhum modelo encontrado! Execute 'train' primeiro.")
        return
    
    model_path = models[-1]
    print(f"Carregando modelo: {model_path.name}\n")
    
    model = keras.models.load_model(model_path)
    
    # Predições
    X_backtest, _ = preprocessor.transform(df_backtest)
    y_pred_scaled = model.predict(X_backtest, verbose=0).ravel()
    y_pred_usd = preprocessor.inverse_target(y_pred_scaled)
    
    # Backtest
    df_bt = df_backtest.iloc[args.lookback:].reset_index(drop=True)
    
    equity_curve, metrics = backtest_regression(
        df=df_bt,
        preds_usd=y_pred_usd,
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
        latency=1,
        threshold_bps=args.threshold_bps,
        initial_capital=args.capital
    )
    
    # Salvar equity curve
    ts = time.strftime("%Y%m%d_%H%M%S")
    equity_path = f"artifacts/equity/equity_{ts}.csv"
    equity_curve.to_csv(equity_path, index=False)
    
    print(f"✅ Equity curve salva em: {equity_path}")
    
    # Salvar métricas
    metrics_path = f"artifacts/metrics/backtest_{ts}.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Métricas salvas em: {metrics_path}\n")
    
    # Imprimir relatório
    print_backtest_report(metrics)


def main():
    """Main CLI."""
    setup_tensorflow()
    create_artifacts_dirs()
    
    parser = argparse.ArgumentParser(
        description="ML v2 - Pipeline robusto para trading com LSTM",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # === TRAIN ===
    parser_train = subparsers.add_parser("train", help="Treina o modelo")
    parser_train.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_train.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_train.add_argument("--epochs", type=int, default=10, help="Épocas de treino")
    parser_train.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser_train.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser_train.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    
    # === EVALUATE ===
    parser_eval = subparsers.add_parser("evaluate", help="Avalia modelo vs baselines")
    parser_eval.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_eval.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    
    # === WALKFORWARD ===
    parser_wf = subparsers.add_parser("walkforward", help="Validação walk-forward")
    parser_wf.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_wf.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_wf.add_argument("--folds", type=int, default=3, help="Número de folds")
    parser_wf.add_argument("--epochs", type=int, default=10, help="Épocas por fold")
    parser_wf.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser_wf.add_argument("--verbose", action="store_true", help="Verbose training")
    
    # === BACKTEST ===
    parser_bt = subparsers.add_parser("backtest", help="Backtest com custos")
    parser_bt.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_bt.add_argument("--lookback", type=int, default=60, help="Janela temporal")
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
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "walkforward":
        cmd_walkforward(args)
    elif args.command == "backtest":
        cmd_backtest(args)


if __name__ == "__main__":
    main()
