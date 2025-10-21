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
from src.ml_v2.preprocess_classification import DirectionalPreprocessor
from src.ml_v2.models.lstm_model import build_lstm, get_callbacks
from src.ml_v2.models.directional_model import (
    build_directional_lstm, 
    get_directional_callbacks, 
    calculate_class_weights,
    evaluate_directional_model,
    print_directional_results
)
from src.ml_v2.metrics import compare_with_baselines, print_comparison
from src.ml_v2.validation.walkforward import run_walkforward
from src.ml_v2.validation.walkforward_classification import walkforward_classification, save_walkforward_results
from src.ml_v2.backtest.engine import backtest_regression, print_backtest_report
from src.ml_v2.backtest.directional_backtester import DirectionalBacktester

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


def cmd_train_classifier(args):
    """Comando: train_classifier - Treina modelo de classificação direcional."""
    print("\n" + "="*80)
    print("COMANDO: TRAIN CLASSIFIER (DIRECCIONAL)")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    print(f"📊 Dataset carregado: {len(df):,} samples, {len(feature_cols)} features")
    
    # Split temporal
    n = len(df)
    i_train = int(n * 0.70)
    i_val = int(n * 0.85)
    
    df_train = df.iloc[:i_train]
    df_val = df.iloc[i_train:i_val]
    df_test = df.iloc[i_val:]
    
    print(f"📊 Split: Train={len(df_train):,}, Val={len(df_val):,}, Test={len(df_test):,}")
    
    # Preprocessamento direcional
    horizon = getattr(args, 'horizon', 12)  # 6 horas
    threshold = getattr(args, 'threshold', 0.5)  # 0.5%
    
    preprocessor = DirectionalPreprocessor(
        feature_cols=feature_cols,
        price_col="Close",
        lookback=args.lookback,
        horizon=horizon,
        threshold_pct=threshold
    )
    
    # Fit e transform
    X_train, y_train = preprocessor.fit_transform(df_train)
    X_val, y_val = preprocessor.transform(df_val)
    
    print(f"\n🎯 Sequências de treino: {X_train.shape}")
    print(f"🎯 Sequências de validação: {X_val.shape}")
    
    # Class weights
    class_weights = calculate_class_weights(y_train)
    
    # Construir modelo
    input_shape = (X_train.shape[1], X_train.shape[2])
    
    model = build_directional_lstm(
        input_shape=input_shape,
        n_classes=3,
        lstm_units=getattr(args, 'units', 64),
        dropout=getattr(args, 'dropout', 0.3),
        learning_rate=getattr(args, 'lr', 1e-3)
    )
    
    print(f"\n🤖 Modelo criado: {model.count_params():,} parâmetros")
    model.summary()
    
    # Callbacks
    callbacks = get_directional_callbacks(
        patience_early=15,
        patience_lr=7,
        monitor='val_accuracy'
    )
    
    # Treinamento
    print("\n🔥 Iniciando treinamento...")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=getattr(args, 'epochs', 100),
        batch_size=getattr(args, 'batch_size', 64),
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    # Avaliação rápida
    print("\n📊 Avaliação final no conjunto de validação:")
    
    results = evaluate_directional_model(model, X_val, y_val)
    print_directional_results(results)
    
    # Salvar modelo
    ts = time.strftime("%Y%m%d_%H%M%S")
    model_path = f"artifacts/checkpoints/classifier_{ts}.keras"
    model.save(model_path)
    
    print(f"\n✅ Classificador salvo em: {model_path}")
    
    # Salvar histórico
    history_path = f"artifacts/logs/classifier_history_{ts}.json"
    with open(history_path, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")
    
    # Salvar preprocessor
    preprocessor_path = f"artifacts/checkpoints/preprocessor_{ts}.pkl"
    import pickle
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    print(f"✅ Preprocessor salvo em: {preprocessor_path}")


def cmd_train_improved_classifier(args):
    """Comando: train_improved_classifier - Treina modelo aprimorado com todas as melhorias."""
    print("\n" + "="*80)
    print("COMANDO: TRAIN IMPROVED CLASSIFIER (TODAS AS MELHORIAS)")
    print("="*80 + "\n")
    
    # Imports aqui para evitar problemas de módulo
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from models.improved_directional_model import build_improved_directional_lstm, get_aggressive_class_weights, get_improved_callbacks
    from preprocess.improved_preprocessor import ImprovedDirectionalPreprocessor
    import tensorflow as tf
    from datetime import datetime
    
    print("🚀 Iniciando treinamento do classificador APRIMORADO...")
    
    # Carregar dados
    df = pd.read_csv(args.csv)
    print(f"📊 Dataset carregado: {len(df):,} samples, {len(df.columns)} features")
    
    # Configurar preprocessor aprimorado
    preprocessor = ImprovedDirectionalPreprocessor(
        lookback_window=getattr(args, 'lookback', 60),
        horizon_periods=getattr(args, 'horizon', 24),  # 12h ao invés de 6h
        threshold_multiplier=getattr(args, 'threshold', 1.0),  # ATR-based
        adaptive_threshold=True,
        use_advanced_features=True,
        balance_method="adaptive"
    )
    
    # Preprocessar dados
    print("\n🔧 Preprocessando com melhorias avançadas...")
    X, y = preprocessor.fit_transform(df)
    
    # Split temporal
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"🎯 Sequências de treino: {X_train.shape}")
    print(f"🎯 Sequências de validação: {X_val.shape}")
    
    # Class weights agressivos
    class_weights = get_aggressive_class_weights(y_train, strategy="aggressive")
    
    # Construir modelo aprimorado
    model = build_improved_directional_lstm(
        input_shape=(X_train.shape[1], X_train.shape[2]),
        lstm_units=getattr(args, 'lstm_units', 128),
        lstm_layers=getattr(args, 'lstm_layers', 3),
        dropout=getattr(args, 'dropout', 0.4),
        learning_rate=getattr(args, 'learning_rate', 1e-3),
        use_focal_loss=getattr(args, 'use_focal_loss', True)
    )
    
    # Callbacks aprimorados
    patience = getattr(args, 'patience', 20)
    callbacks = get_improved_callbacks(
        patience_early=patience,
        patience_lr=patience // 2
    )
    
    # Salvar checkpoints
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_path = f"artifacts/checkpoints/improved_classifier_{timestamp}"
    
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(
        f"{checkpoint_path}_best.keras",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ))
    
    # Treinar
    print("\n🤖 Iniciando treinamento aprimorado...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=getattr(args, 'epochs', 100),
        batch_size=getattr(args, 'batch_size', 64),
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    # Salvar modelo e preprocessor
    model_path = f"{checkpoint_path}_final.keras"
    preprocessor_path = f"artifacts/checkpoints/improved_preprocessor_{timestamp}.pkl"
    
    model.save(model_path)
    preprocessor.save(preprocessor_path)
    
    # Avaliar performance final
    print("\n📊 Avaliação final:")
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    # Predições para métricas detalhadas
    y_pred = model.predict(X_val)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    from sklearn.metrics import classification_report, balanced_accuracy_score
    
    balanced_acc = balanced_accuracy_score(y_val, y_pred_classes)
    
    print(f"   Accuracy: {val_acc:.4f}")
    print(f"   Balanced Accuracy: {balanced_acc:.4f}")
    print(f"   Loss: {val_loss:.4f}")
    
    print(f"\n✅ Modelo aprimorado salvo em: {model_path}")
    print(f"✅ Preprocessor salvo em: {preprocessor_path}")
    
    # Relatório por classe
    label_names = ['BAIXA', 'LATERAL', 'ALTA']
    report = classification_report(y_val, y_pred_classes, target_names=label_names)
    print(f"\n📈 Relatório por classe:\n{report}")
    
    # Salvar histórico
    history_path = f"artifacts/logs/improved_classifier_history_{timestamp}.json"
    with open(history_path, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")
    
    return history, model, preprocessor


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
    
    print(f"DEBUG: y_pred_usd shape: {y_pred_usd.shape}")
    print(f"DEBUG: y_pred_usd primeiros 5 valores: {y_pred_usd[:5]}")
    print(f"DEBUG: df_test shape: {df_test.shape}")
    
    # Obter y_true (Close real)
    y_true_usd = df_test['Close'].values[args.lookback:]
    
    print(f"DEBUG: y_true_usd shape: {y_true_usd.shape}")
    print(f"DEBUG: y_true_usd primeiros 5 valores: {y_true_usd[:5]}")
    
    # Comparar com baselines
    results = compare_with_baselines(df_test, y_true_usd, y_pred_usd, args.lookback)
    
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


def cmd_evaluate_classifier(args):
    """Comando: evaluate_classifier - Avalia classificador direcional."""
    print("\n" + "="*80)
    print("COMANDO: EVALUATE CLASSIFIER")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    # Split (usar apenas test set)
    n = len(df)
    i_val = int(n * 0.85)
    df_test = df.iloc[i_val:]
    
    print(f"📊 Dataset test: {len(df_test):,} samples")
    
    # Carregar último classificador
    checkpoint_dir = Path("artifacts/checkpoints")
    classifiers = sorted(checkpoint_dir.glob("classifier_*.keras"))
    
    if not classifiers:
        print("❌ Nenhum classificador encontrado! Execute 'train_classifier' primeiro.")
        return
    
    model_path = classifiers[-1]
    print(f"Carregando classificador: {model_path.name}")
    
    # Carregar preprocessor correspondente
    ts_model = model_path.stem.replace('classifier_', '')  # timestamp completo
    preprocessor_path = checkpoint_dir / f"preprocessor_{ts_model}.pkl"
    
    if not preprocessor_path.exists():
        print(f"❌ Preprocessor não encontrado: {preprocessor_path}")
        print("Execute 'train_classifier' novamente para salvar o preprocessor.")
        return
    
    import pickle
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    print(f"✅ Preprocessor carregado: {preprocessor_path.name}")
    
    # Preprocessar dados de teste
    X_test, y_test = preprocessor.transform(df_test)
    
    print(f"🎯 Sequências de teste: {X_test.shape}")
    
    # Carregar modelo
    model = keras.models.load_model(model_path)
    
    # Avaliar
    results = evaluate_directional_model(model, X_test, y_test)
    
    # Imprimir resultados
    print_directional_results(results)
    
    # Salvar resultados
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_path = f"artifacts/metrics/classifier_eval_{ts}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Resultados salvos em: {results_path}")


def cmd_walkforward_classifier(args):
    """Comando: walkforward_classifier - Walk-forward validation do classificador."""
    print("\n" + "="*80)
    print("COMANDO: WALK-FORWARD CLASSIFIER")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    feature_cols = get_feature_cols(df)
    
    print(f"📊 Dataset: {len(df):,} samples, {len(feature_cols)} features")
    
    # Parâmetros
    model_params = {
        'lookback': args.lookback,
        'horizon': getattr(args, 'horizon', 6),
        'threshold': getattr(args, 'threshold', 0.3),
        'epochs': getattr(args, 'epochs', 20),
        'batch_size': getattr(args, 'batch_size', 64),
        'units': getattr(args, 'units', 64),
        'dropout': getattr(args, 'dropout', 0.4),
        'lr': getattr(args, 'lr', 1e-3)
    }
    
    # Executar walk-forward
    results = walkforward_classification(
        df=df,
        feature_cols=feature_cols,
        n_folds=getattr(args, 'folds', 3),
        train_size_months=getattr(args, 'train_months', 12),
        test_size_months=getattr(args, 'test_months', 3),
        **model_params
    )
    
    # Salvar resultados
    ts = time.strftime("%Y%m%d_%H%M%S")
    results_path = f"artifacts/metrics/walkforward_classifier_{ts}.json"
    save_walkforward_results(results, results_path)


def cmd_backtest_classifier(args):
    """Comando: backtest_classifier - Backtest do classificador direcional."""
    print("\n" + "="*80)
    print("COMANDO: BACKTEST CLASSIFIER")
    print("="*80 + "\n")
    
    # Load data
    df = load_and_prepare_data(args.csv)
    
    # Filtrar período de backtest
    if args.start:
        df_backtest = df[df['Date'] >= args.start].reset_index(drop=True)
        df_train = df[df['Date'] < args.start].reset_index(drop=True)
    else:
        # Usar últimos 15% como backtest (dados de teste)
        n = len(df)
        i_val = int(n * 0.85)
        df_backtest = df.iloc[i_val:].reset_index(drop=True)
        df_train = df.iloc[:i_val].reset_index(drop=True)
    
    print(f"📅 Período de backtest: {df_backtest['Date'].min()} a {df_backtest['Date'].max()}")
    print(f"📊 Amostras de backtest: {len(df_backtest):,}")
    
    # Carregar último classificador
    checkpoint_dir = Path("artifacts/checkpoints")
    classifiers = sorted(checkpoint_dir.glob("classifier_*.keras"))
    
    if not classifiers:
        print("❌ Nenhum classificador encontrado! Execute 'train_classifier' primeiro.")
        return
    
    model_path = classifiers[-1]
    print(f"🤖 Carregando classificador: {model_path.name}")
    
    # Carregar preprocessor correspondente
    ts_model = model_path.stem.replace('classifier_', '')
    preprocessor_path = checkpoint_dir / f"preprocessor_{ts_model}.pkl"
    
    if not preprocessor_path.exists():
        print(f"❌ Preprocessor não encontrado: {preprocessor_path}")
        print("Execute 'train_classifier' novamente para salvar o preprocessor.")
        return
    
    import pickle
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    print(f"✅ Preprocessor carregado: {preprocessor_path.name}")
    
    # Preprocessar dados de backtest
    X_backtest, y_backtest = preprocessor.transform(df_backtest)
    
    print(f"🎯 Sequências para backtest: {X_backtest.shape}")
    
    # Carregar modelo e fazer predições
    model = keras.models.load_model(model_path)
    
    print("🔮 Gerando predições...")
    probabilities = model.predict(X_backtest, verbose=0)
    predictions = np.argmax(probabilities, axis=1)
    
    # Alinhar dados para backtest
    # X_backtest tem menos samples que df_backtest devido ao lookback
    lookback = preprocessor.lookback
    df_bt = df_backtest.iloc[lookback:].reset_index(drop=True)
    
    print(f"📊 Dados alinhados para backtest: {len(df_bt):,} samples")
    
    # Verificar alinhamento
    if len(df_bt) != len(predictions):
        print(f"⚠️  Alinhamento: df_bt={len(df_bt)}, predictions={len(predictions)}")
        min_len = min(len(df_bt), len(predictions))
        df_bt = df_bt.iloc[:min_len]
        predictions = predictions[:min_len]
        probabilities = probabilities[:min_len]
    
    # Configurar backtester
    backtester = DirectionalBacktester(
        initial_capital=getattr(args, 'capital', 100000.0),
        fee_bps=getattr(args, 'fee_bps', 10.0),
        slippage_bps=getattr(args, 'slippage_bps', 5.0),
        min_confidence=getattr(args, 'min_confidence', 0.6),
        position_size=getattr(args, 'position_size', 0.95)
    )
    
    # Executar backtest
    history_df = backtester.run_backtest(df_bt, predictions, probabilities)
    
    # Salvar histórico (formato compatível com dashboard)
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_path = f"artifacts/equity/capital_history-CLASSIFIER_{ts}.csv"
    backtester.save_history(history_df, output_path)
    
    # Também salvar em formato padrão para comparação
    history_standard = f"artifacts/equity/backtest_classifier_{ts}.csv"
    history_df.to_csv(history_standard, index=False)
    
    print(f"\n✅ Histórico do dashboard salvo: {output_path}")
    print(f"✅ Histórico padrão salvo: {history_standard}")
    
    # Estatísticas resumidas
    if len(history_df) > 0:
        capital_inicial = float(history_df['Capital'].iloc[0])
        capital_final = float(history_df['Capital'].iloc[-1])
        retorno_total = (capital_final - capital_inicial) / capital_inicial
        num_trades = len(history_df[history_df['Status'] == 'Entrada'])
        
        print(f"\n📈 RESUMO DO BACKTEST:")
        print(f"   Capital inicial: ${capital_inicial:,.2f}")
        print(f"   Capital final: ${capital_final:,.2f}")
        print(f"   Retorno total: {retorno_total:.2%}")
        print(f"   Número de trades: {num_trades}")
        print(f"   Arquivo para dashboard: {output_path}")


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
    
    # === TRAIN CLASSIFIER ===
    parser_tc = subparsers.add_parser("train_classifier", help="Treina classificador direcional")
    parser_tc.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_tc.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_tc.add_argument("--horizon", type=int, default=12, help="Períodos futuros (6h = 12×30min)")
    parser_tc.add_argument("--threshold", type=float, default=0.5, help="Threshold ALTA/BAIXA (%)")
    parser_tc.add_argument("--epochs", type=int, default=100, help="Épocas de treino")
    parser_tc.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser_tc.add_argument("--units", type=int, default=64, help="LSTM units")
    parser_tc.add_argument("--dropout", type=float, default=0.3, help="Dropout rate")
    parser_tc.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    
    # === EVALUATE CLASSIFIER ===
    parser_ec = subparsers.add_parser("evaluate_classifier", help="Avalia classificador direcional")
    parser_ec.add_argument("--csv", required=True, help="Caminho do CSV")
    
    # === WALKFORWARD CLASSIFIER ===
    parser_wfc = subparsers.add_parser("walkforward_classifier", help="Walk-forward do classificador")
    parser_wfc.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_wfc.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_wfc.add_argument("--folds", type=int, default=3, help="Número de folds")
    parser_wfc.add_argument("--train-months", type=int, default=12, help="Meses de treino")
    parser_wfc.add_argument("--test-months", type=int, default=3, help="Meses de teste")
    parser_wfc.add_argument("--horizon", type=int, default=6, help="Períodos futuros")
    parser_wfc.add_argument("--threshold", type=float, default=0.3, help="Threshold %")
    parser_wfc.add_argument("--epochs", type=int, default=20, help="Épocas por fold")
    parser_wfc.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser_wfc.add_argument("--units", type=int, default=64, help="LSTM units")
    parser_wfc.add_argument("--dropout", type=float, default=0.4, help="Dropout rate")
    
    # === TRAIN IMPROVED CLASSIFIER ===
    parser_tic = subparsers.add_parser("train_improved_classifier", help="Treina classificador APRIMORADO")
    parser_tic.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_tic.add_argument("--lookback", type=int, default=60, help="Janela temporal")
    parser_tic.add_argument("--horizon", type=int, default=24, help="Horizontes futuros (12h)")
    parser_tic.add_argument("--threshold", type=float, default=1.0, help="Multiplicador ATR threshold")
    parser_tic.add_argument("--epochs", type=int, default=100, help="Épocas máximas")
    parser_tic.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser_tic.add_argument("--lstm-units", type=int, default=128, help="LSTM units primeira camada")
    parser_tic.add_argument("--lstm-layers", type=int, default=3, help="Número camadas LSTM")
    parser_tic.add_argument("--dropout", type=float, default=0.4, help="Dropout rate")
    parser_tic.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate inicial")
    parser_tic.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser_tic.add_argument("--use-focal-loss", action="store_true", default=True, help="Usar Focal Loss")

    # === BACKTEST CLASSIFIER ===
    parser_btc = subparsers.add_parser("backtest_classifier", help="Backtest do classificador")
    parser_btc.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_btc.add_argument("--start", type=str, default=None, help="Data início (YYYY-MM-DD)")
    parser_btc.add_argument("--capital", type=float, default=100000.0, help="Capital inicial")
    parser_btc.add_argument("--fee-bps", type=float, default=10.0, help="Taxa exchange (bps)")
    parser_btc.add_argument("--slippage-bps", type=float, default=5.0, help="Slippage (bps)")
    parser_btc.add_argument("--min-confidence", type=float, default=0.6, help="Confiança mínima (0-1)")
    parser_btc.add_argument("--position-size", type=float, default=0.95, help="Fração do capital (0-1)")
    
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
    elif args.command == "train_classifier":
        cmd_train_classifier(args)
    elif args.command == "train_improved_classifier":
        cmd_train_improved_classifier(args)
    elif args.command == "evaluate_classifier":
        cmd_evaluate_classifier(args)
    elif args.command == "walkforward_classifier":
        cmd_walkforward_classifier(args)
    elif args.command == "backtest_classifier":
        cmd_backtest_classifier(args)


if __name__ == "__main__":
    main()
