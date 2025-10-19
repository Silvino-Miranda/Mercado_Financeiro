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
    
    # 4. Verificar se deve carregar modelo existente (--resume)
    model_path_saved = Path('artifacts/v3/models/lstm_v3.keras')
    history_path_saved = Path('artifacts/v3/logs/history_lstm_v3.json')
    
    if args.resume and model_path_saved.exists():
        print(f"\n🔄 MODO RESUME: Carregando modelo existente...")
        from tensorflow import keras
        model = keras.models.load_model(model_path_saved)
        print(f"   ✅ Modelo carregado: {model_path_saved}")
        
        # Carregar histórico anterior se existir
        previous_history = {}
        if history_path_saved.exists():
            with open(history_path_saved, 'r') as f:
                previous_history = json.load(f)
            epochs_trained = len(previous_history.get('loss', []))
            print(f"   ✅ Histórico carregado: {epochs_trained} épocas já treinadas")
            print(f"   🔥 Continuando treinamento por mais {model_config.epochs} épocas...")
    else:
        if args.resume:
            print(f"\n⚠️  RESUME solicitado mas modelo não encontrado em {model_path_saved}")
            print(f"   🆕 Criando novo modelo...")
        
        # 4b. Criar ModelFactory e criar modelo novo
        model_factory = ModelFactory()
        model = model_factory.create_model(config=model_config)
        previous_history = {}
    
    # 5. Criar Preprocessor (DataPreprocessorAdapter - pode ser serializado!)
    feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
    
    from src.ml_v3_arch.adapters.preprocessor_adapter import DataPreprocessorAdapter
    
    preprocessor = DataPreprocessorAdapter(
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
    
    # 9. Salvar modelo (nome fixo, sem timestamp - sobrescreve sempre)
    persistence = ModelPersistence(base_dir='artifacts/v3')
    
    model_path = persistence.save_keras_model(
        model=model,
        name='lstm_v3',
        metadata=metadata,
        add_timestamp=False  # Nome fixo: lstm_v3.keras
    )
    
    print(f"\n✅ Modelo salvo em: {model_path}")
    
    # 9.1 Salvar preprocessor (nome fixo, sem timestamp)
    prep_dir = Path("artifacts/v3/preprocessors")
    prep_dir.mkdir(parents=True, exist_ok=True)
    prep_path = prep_dir / "preprocessor_lstm_v3.pkl"
    
    import pickle
    with open(prep_path, 'wb') as f:
        pickle.dump(preprocessor, f)
    
    print(f"✅ Preprocessor salvo em: {prep_path}")
    
    # 10. Salvar histórico (mesclando com histórico anterior se houver)
    history_path = "artifacts/v3/logs/history_lstm_v3.json"
    Path("artifacts/v3/logs").mkdir(parents=True, exist_ok=True)
    
    # Mesclar com histórico anterior (se modo resume)
    if previous_history:
        combined_history = {}
        for key in history.keys():
            # Concatena valores antigos + novos
            combined_history[key] = previous_history.get(key, []) + history[key]
        print(f"   🔄 Histórico mesclado: {len(previous_history.get('loss', []))} épocas antigas + {len(history.get('loss', []))} novas")
    else:
        combined_history = history
    
    with open(history_path, 'w') as f:
        json.dump(combined_history, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")
    
    # 9. Resumo final
    total_epochs = len(combined_history.get('loss', []))
    print(f"\n📊 RESUMO DO TREINAMENTO:")
    print(f"   Épocas TOTAIS acumuladas: {total_epochs}")
    print(f"   Loss final (treino): {combined_history.get('loss', [])[-1]:.6f}")
    print(f"   Loss final (val): {combined_history.get('val_loss', [])[-1]:.6f}")
    print(f"   MAE final (val): {combined_history.get('val_mae', [])[-1]:.6f}")


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
    import numpy as np
    import pandas as pd
    
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
    
    # 2. Carregar modelo especificado ou o último treinado
    from tensorflow import keras
    
    if args.model and Path(args.model).exists():
        model_path = Path(args.model)
        print(f"\n📦 Carregando modelo especificado: {model_path}")
        model = keras.models.load_model(model_path)
    else:
        # Tentar carregar modelo padrão
        model_path = Path("artifacts/v3/models/lstm_v3.keras")
        if not model_path.exists():
            print("❌ Modelo não encontrado! Execute 'train' primeiro ou especifique --model.")
            return
        print(f"\n📦 Carregando modelo padrão: {model_path}")
        model = keras.models.load_model(model_path)
    
    # 2.1 Carregar preprocessor salvo (CRÍTICO para desnormalização correta!)
    prep_path = Path("artifacts/v3/preprocessors/preprocessor_lstm_v3.pkl")
    
    if not prep_path.exists():
        print(f"❌ Preprocessor não encontrado: {prep_path}")
        print("   Treine um modelo primeiro para gerar o preprocessor.")
        return
    
    print(f"📦 Carregando preprocessor: {prep_path}")
    import pickle
    with open(prep_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    # 3. Extrair configuração do modelo (inferir do shape)
    input_shape = model.input_shape  # (None, lookback, n_features)
    lookback = input_shape[1]
    n_features = input_shape[2]
    
    print(f"\n� Configuração detectada:")
    print(f"   Lookback: {lookback}")
    print(f"   Features: {n_features}")
    
    # 4. Preparar dados de teste
    feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
    target_col = 'Close'
    
    if len(feature_cols) != n_features:
        print(f"⚠️  AVISO: CSV tem {len(feature_cols)} features, modelo espera {n_features}")
        print("   Ajustando features...")
        feature_cols = feature_cols[:n_features]
    
    # Usar últimos 15% para teste
    n = len(df)
    i_test = int(n * 0.85)
    df_test = df.iloc[i_test:].reset_index(drop=True)
    
    print(f"\n📊 Dados de teste:")
    print(f"   Período: {df_test['Date'].min()} → {df_test['Date'].max()}")
    print(f"   Samples: {len(df_test):,}")
    
    # 5. Preprocessar dados de teste USANDO O PREPROCESSOR SALVO
    # IMPORTANTE: Usar o mesmo scaler do treino (sem refit!)
    
    X_test = df_test[feature_cols].values
    y_test = df_test[target_col].values.reshape(-1, 1)
    
    # Transform (sem fit!) usando scalers do treino
    X_test_scaled = preprocessor.scaler_X.transform(X_test)
    y_test_scaled = preprocessor.scaler_y.transform(y_test).ravel()
    
    # Criar sequências
    X_seq, y_seq = [], []
    for i in range(len(X_test_scaled) - lookback):
        X_seq.append(X_test_scaled[i:i + lookback])
        y_seq.append(y_test_scaled[i + lookback])
    
    X_test_final = np.array(X_seq)
    y_test_final = np.array(y_seq)
    
    # Valores originais para comparação (sem normalizar, apenas pegar da fila)
    y_test_original = y_test.ravel()[lookback:]
    
    print(f"\n� Preprocessamento:")
    print(f"   X_test: {X_test_final.shape}")
    print(f"   y_test: {y_test_final.shape}")
    
    # 6. Fazer predições
    print(f"\n🔮 Gerando predições...")
    y_pred_scaled = model.predict(X_test_final, verbose=0).flatten()
    
    # Desnormalizar predições para valores reais em $ usando scaler do treino!
    y_pred_original = preprocessor.scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    
    # 7. Calcular métricas EM VALORES REAIS ($)
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(y_test_original, y_pred_original)
    rmse = np.sqrt(mean_squared_error(y_test_original, y_pred_original))
    r2 = r2_score(y_test_original, y_pred_original)
    mape = np.mean(np.abs((y_test_original - y_pred_original) / np.clip(y_test_original, 1e-6, None))) * 100
    
    # Hit rate (acerto de direção) - usar valores originais
    y_prev = y_test.ravel()[lookback-1:-1]  # Valor anterior
    true_dir = np.sign(y_test_original - y_prev)
    pred_dir = np.sign(y_pred_original - y_prev)
    hit_rate = np.mean(true_dir == pred_dir)
    
    # 8. Exibir resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DA AVALIAÇÃO")
    print("="*80)
    print(f"\n📈 Métricas de Erro (valores reais em $):")
    print(f"   MAE (Mean Absolute Error):  ${mae:,.2f}")
    print(f"   RMSE (Root Mean Squared):   ${rmse:,.2f}")
    print(f"   MAPE (Mean Abs % Error):    {mape:.2f}%")
    print(f"   R² Score:                   {r2:.4f}")
    
    print(f"\n🎯 Acurácia Direcional:")
    print(f"   Hit Rate:                   {hit_rate*100:.2f}%")
    
    print(f"\n📊 Estatísticas:")
    print(f"   Média Real:                 ${y_test_original.mean():,.2f}")
    print(f"   Média Predita:              ${y_pred_original.mean():,.2f}")
    print(f"   Std Real:                   ${y_test_original.std():,.2f}")
    print(f"   Std Predita:                ${y_pred_original.std():,.2f}")
    
    # 9. Salvar métricas
    metrics = {
        'mae': float(mae),
        'rmse': float(rmse),
        'mape': float(mape),
        'r2_score': float(r2),
        'hit_rate': float(hit_rate),
        'n_samples': len(y_test_final),
        'mean_true': float(y_test_original.mean()),
        'mean_pred': float(y_pred_original.mean()),
        'std_true': float(y_test_original.std()),
        'std_pred': float(y_pred_original.std())
    }
    
    metrics_path = Path("artifacts/v3/metrics")
    metrics_path.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_file = metrics_path / f"evaluation_{timestamp}.json"
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Métricas salvas em: {metrics_file}")
    print("="*80)


def cmd_backtest(args):
    """Comando: backtest - Backtest usando BacktestService v3."""
    import numpy as np
    import pandas as pd
    
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
    
    print("💰 Configuração do backtest:")
    print(f"   Capital inicial: ${backtest_config.initial_capital:,.2f}")
    print(f"   Fee: {backtest_config.fee_bps} bps")
    print(f"   Slippage: {backtest_config.slippage_bps} bps")
    print(f"   Position size: {backtest_config.position_size*100:.0f}%")
    print(f"   Threshold: {args.threshold_bps} bps")
    
    # 2. Carregar dados
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True
    )
    
    data_loader = DataLoader(data_config)
    df = data_loader.load(Path(args.csv), verbose=1)
    
    # 3. Carregar modelo
    from tensorflow import keras
    
    if args.model and Path(args.model).exists():
        model_path = Path(args.model)
        print(f"\n📦 Carregando modelo especificado: {model_path}")
        model = keras.models.load_model(model_path)
    else:
        model_path = Path("artifacts/v3/models/lstm_v3.keras")
        if not model_path.exists():
            print("❌ Modelo não encontrado! Execute 'train' primeiro ou especifique --model.")
            return
        print(f"\n📦 Carregando modelo padrão: {model_path}")
        model = keras.models.load_model(model_path)
    
    # 3.1 Carregar preprocessor salvo (CRÍTICO para desnormalização correta!)
    prep_path = Path("artifacts/v3/preprocessors/preprocessor_lstm_v3.pkl")
    
    if not prep_path.exists():
        print(f"❌ Preprocessor não encontrado: {prep_path}")
        print("   Treine um modelo primeiro para gerar o preprocessor.")
        return
    
    print(f"📦 Carregando preprocessor: {prep_path}")
    import pickle
    with open(prep_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    # 4. Extrair configuração do modelo
    input_shape = model.input_shape
    lookback = input_shape[1]
    n_features = input_shape[2]
    
    print(f"\n🔍 Configuração detectada:")
    print(f"   Lookback: {lookback}")
    print(f"   Features: {n_features}")
    
    # 5. Filtrar período de backtest
    if args.start:
        df_backtest = df[df['Date'] >= args.start].reset_index(drop=True)
    else:
        # Usar últimos 15% como backtest
        n = len(df)
        i_test = int(n * 0.85)
        df_backtest = df.iloc[i_test:].reset_index(drop=True)
    
    print(f"\n📅 Período de backtest:")
    print(f"   Início: {df_backtest['Date'].min()}")
    print(f"   Fim: {df_backtest['Date'].max()}")
    print(f"   Samples: {len(df_backtest):,}")
    
    # 6. Preparar features e fazer predições USANDO O PREPROCESSOR SALVO
    feature_cols = [c for c in df_backtest.columns if c not in ['Date', 'Close']]
    
    if len(feature_cols) != n_features:
        feature_cols = feature_cols[:n_features]
    
    # IMPORTANTE: Usar scalers do treino (sem refit!)
    X = df_backtest[feature_cols].values
    X_scaled = preprocessor.scaler_X.transform(X)
    
    # Criar sequências e fazer predições em BATCH (muito mais rápido!)
    print(f"\n🔮 Criando sequências para predição em batch...")
    
    # Criar todas as sequências de uma vez
    X_sequences = []
    for i in range(lookback, len(X_scaled)):
        X_sequences.append(X_scaled[i-lookback:i])
    
    X_sequences = np.array(X_sequences)  # Shape: (n_samples, lookback, n_features)
    actual_prices = df_backtest['Close'].iloc[lookback:].values
    
    print(f"   Shape das sequências: {X_sequences.shape}")
    print(f"   Total de predições: {len(X_sequences):,}")
    
    # Fazer predições em batch (1 única chamada ao modelo!)
    print(f"\n🚀 Gerando predições em batch (RÁPIDO)...")
    predictions_scaled = model.predict(X_sequences, verbose=1, batch_size=512).flatten()
    
    # Desnormalizar predições para valores reais em $ usando scaler do treino!
    predictions = preprocessor.scaler_y.inverse_transform(predictions_scaled.reshape(-1, 1)).ravel()
    
    # 7. Simular trading
    print(f"\n💹 Simulando trades...")
    
    capital = backtest_config.initial_capital
    position = 0  # BTC holdings
    trades = []
    capital_history = [capital]
    
    fee_rate = backtest_config.fee_bps / 10000
    slippage_rate = backtest_config.slippage_bps / 10000
    threshold_rate = args.threshold_bps / 10000
    
    for i in range(len(predictions) - 1):
        current_price = actual_prices[i]
        predicted_price = predictions[i]
        next_price = actual_prices[i + 1]
        
        # Calcular mudança esperada
        expected_change = (predicted_price - current_price) / current_price
        
        # Decisão de trading
        if expected_change > threshold_rate and position == 0:
            # BUY signal
            buy_price = current_price * (1 + slippage_rate)
            position = (capital * backtest_config.position_size) / buy_price
            capital -= position * buy_price * (1 + fee_rate)
            
            trades.append({
                'type': 'BUY',
                'price': buy_price,
                'amount': position,
                'capital': capital,
                'date': df_backtest['Date'].iloc[lookback + i]
            })
        
        elif expected_change < -threshold_rate and position > 0:
            # SELL signal
            sell_price = current_price * (1 - slippage_rate)
            capital += position * sell_price * (1 - fee_rate)
            
            trades.append({
                'type': 'SELL',
                'price': sell_price,
                'amount': position,
                'capital': capital,
                'date': df_backtest['Date'].iloc[lookback + i]
            })
            
            position = 0
        
        # Atualizar capital total (incluindo posição aberta)
        total_value = capital + (position * next_price if position > 0 else 0)
        capital_history.append(total_value)
    
    # Fechar posição final se aberta
    if position > 0:
        final_price = actual_prices[-1] * (1 - slippage_rate)
        capital += position * final_price * (1 - fee_rate)
        trades.append({
            'type': 'SELL (CLOSE)',
            'price': final_price,
            'amount': position,
            'capital': capital,
            'date': df_backtest['Date'].iloc[-1]
        })
        position = 0
    
    # 8. Calcular métricas de performance
    final_capital = capital
    total_return = (final_capital - backtest_config.initial_capital) / backtest_config.initial_capital
    
    capital_array = np.array(capital_history)
    returns = np.diff(capital_array) / capital_array[:-1]
    
    sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252 * 48) if returns.std() > 0 else 0
    max_drawdown = np.min(capital_array / np.maximum.accumulate(capital_array) - 1)
    
    # Buy and Hold
    buy_hold_return = (actual_prices[-1] - actual_prices[0]) / actual_prices[0]
    
    # 9. Exibir resultados
    print("\n" + "="*80)
    print("💰 RESULTADOS DO BACKTEST")
    print("="*80)
    
    print(f"\n📊 Performance:")
    print(f"   Capital Inicial:        ${backtest_config.initial_capital:,.2f}")
    print(f"   Capital Final:          ${final_capital:,.2f}")
    print(f"   Retorno Total:          {total_return*100:+.2f}%")
    print(f"   Buy & Hold:             {buy_hold_return*100:+.2f}%")
    print(f"   Alpha:                  {(total_return - buy_hold_return)*100:+.2f}%")
    
    print(f"\n📈 Métricas de Risco:")
    print(f"   Sharpe Ratio:           {sharpe_ratio:.2f}")
    print(f"   Max Drawdown:           {max_drawdown*100:.2f}%")
    print(f"   Volatilidade:           {returns.std()*100:.2f}%")
    
    print(f"\n🔄 Atividade de Trading:")
    print(f"   Total de Trades:        {len(trades)}")
    print(f"   Trades por Dia:         {len(trades) / (len(capital_history) / 48):.2f}")
    
    if len(trades) > 0:
        print(f"\n📋 Últimos 5 Trades:")
        for trade in trades[-5:]:
            print(f"   {trade['date']}: {trade['type']:12s} @ ${trade['price']:,.2f}")
    
    # 10. Salvar resultados
    backtest_results = {
        'config': {
            'initial_capital': backtest_config.initial_capital,
            'fee_bps': backtest_config.fee_bps,
            'slippage_bps': backtest_config.slippage_bps,
            'threshold_bps': args.threshold_bps
        },
        'performance': {
            'final_capital': float(final_capital),
            'total_return': float(total_return),
            'buy_hold_return': float(buy_hold_return),
            'alpha': float(total_return - buy_hold_return),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'volatility': float(returns.std())
        },
        'trading': {
            'n_trades': len(trades),
            'trades_per_day': float(len(trades) / (len(capital_history) / 48))
        }
    }
    
    results_path = Path("artifacts/v3/backtest")
    results_path.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar JSON
    results_file = results_path / f"backtest_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(backtest_results, f, indent=2)
    
    # Salvar equity curve
    equity_df = pd.DataFrame({
        'capital': capital_history
    })
    equity_file = results_path / f"equity_{timestamp}.csv"
    equity_df.to_csv(equity_file, index=False)
    
    print(f"\n✅ Resultados salvos:")
    print(f"   Métricas: {results_file}")
    print(f"   Equity curve: {equity_file}")
    print("="*80)


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
    parser_train.add_argument("--resume", action="store_true", help="Continuar treinamento do modelo salvo")
    
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
    parser_eval.add_argument("--model", type=str, default=None, help="Caminho do modelo (padrão: artifacts/v3/models/lstm_v3.keras)")
    
    # === BACKTEST ===
    parser_bt = subparsers.add_parser("backtest", help="Backtest com custos")
    parser_bt.add_argument("--csv", required=True, help="Caminho do CSV")
    parser_bt.add_argument("--model", type=str, default=None, help="Caminho do modelo (padrão: artifacts/v3/models/lstm_v3.keras)")
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
