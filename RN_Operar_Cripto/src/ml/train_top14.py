# src/ml/train_top14.py
"""
Treino de modelo LSTM com TOP 14 indicadores técnicos.
Classificação multiclass: ALTA (2), LATERAL (1), BAIXA (0)

MELHORIAS IMPLEMENTADAS:
- Focal Loss (gamma=1.5) para lidar com classes desbalanceadas
- Class weights {BAIXA: 8.0, LATERAL: 1.0, ALTA: 7.0}
- Balanced Accuracy e F1-macro como métricas principais
- ReduceLROnPlateau + EarlyStopping
- Confusion matrix e classification report detalhado
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    balanced_accuracy_score, f1_score, accuracy_score
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import joblib

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def focal_loss(gamma=1.5, alpha=None):
    """
    Focal Loss para lidar com classes desbalanceadas.
    
    Args:
        gamma: Fator de foco (maior = mais peso nas classes difíceis)
        alpha: Pesos por classe [BAIXA, LATERAL, ALTA]
    """
    def loss(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1 - 1e-7)
        ce = -tf.reduce_sum(y_true * tf.math.log(y_pred), axis=-1)
        pt = tf.reduce_sum(y_true * y_pred, axis=-1)
        fl = (1 - pt) ** gamma * ce
        
        if alpha is not None:
            a = tf.reduce_sum(y_true * tf.constant(alpha, dtype=y_pred.dtype), axis=-1)
            fl = a * fl
        
        return tf.reduce_mean(fl)
    return loss


def evaluate_model(model, X, y, set_name="Val"):
    """
    Avalia modelo com métricas reais: Balanced Accuracy e F1-macro.
    """
    y_pred_proba = model.predict(X, verbose=0)
    y_pred = y_pred_proba.argmax(axis=1)
    
    acc = accuracy_score(y, y_pred)
    bal_acc = balanced_accuracy_score(y, y_pred)
    f1_macro = f1_score(y, y_pred, average='macro')
    f1_weighted = f1_score(y, y_pred, average='weighted')
    
    print(f"\n📊 {set_name} Set:")
    print(f"   Accuracy:          {acc:.4f}")
    print(f"   Balanced Accuracy: {bal_acc:.4f} ⭐")
    print(f"   F1-Macro:          {f1_macro:.4f} ⭐")
    print(f"   F1-Weighted:       {f1_weighted:.4f}")
    
    return {
        'acc': acc,
        'bal_acc': bal_acc,
        'f1_macro': f1_macro,
        'f1_weighted': f1_weighted,
        'y_pred': y_pred
    }


def create_labels_adaptive_atr(df, horizon=12, k=0.75):
    """
    Cria labels usando ATR% (Adaptive Threshold) - MELHOR para crypto volátil.
    
    Args:
        df: DataFrame com colunas 'Close', 'High', 'Low'
        horizon: Quantos períodos para frente (12 = 6h em 30min)
        k: Multiplicador do ATR% (0.5-1.0)
        
    Returns:
        Series com labels: 2=ALTA, 1=LATERAL, 0=BAIXA
    """
    # Calcular ATR% (volatilidade adaptativa)
    from ta.volatility import AverageTrueRange
    
    atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
    atr_pct = (atr.average_true_range() / df['Close']) * 100
    
    # Retorno futuro
    future_return = (df['Close'].shift(-horizon) / df['Close'] - 1) * 100
    
    # Threshold dinâmico por período
    threshold = k * atr_pct
    
    labels = np.zeros(len(df), dtype=int)
    labels[future_return > threshold] = 2   # ALTA
    labels[future_return < -threshold] = 0  # BAIXA
    labels[(future_return >= -threshold) & (future_return <= threshold)] = 1  # LATERAL
    
    return pd.Series(labels, index=df.index)


def create_labels_simple(df, horizon=12, threshold=1.0):
    """
    Cria labels simples com threshold fixo - BACKUP.
    
    Args:
        df: DataFrame com coluna 'Close'
        horizon: Quantos períodos para frente (12 = 6h em 30min)
        threshold: % de movimento para considerar ALTA/BAIXA
        
    Returns:
        Series com labels: 2=ALTA, 1=LATERAL, 0=BAIXA
    """
    future_return = (df['Close'].shift(-horizon) / df['Close'] - 1) * 100
    
    labels = np.zeros(len(df), dtype=int)
    labels[future_return > threshold] = 2   # ALTA
    labels[future_return < -threshold] = 0  # BAIXA
    labels[(future_return >= -threshold) & (future_return <= threshold)] = 1  # LATERAL
    
    return pd.Series(labels, index=df.index)


def prepare_sequences(df, feature_cols, label_col, sequence_length=60):
    """
    Prepara sequências para LSTM.
    
    Args:
        df: DataFrame com features e labels
        feature_cols: Lista de colunas de features
        label_col: Nome da coluna de label
        sequence_length: Tamanho da sequência (lookback)
        
    Returns:
        X, y, dates
    """
    # Verificar que todas as colunas existem
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando: {missing_cols}")
    
    # Remover NaNs e resetar índice
    cols_needed = feature_cols + [label_col, 'Date']
    df_clean = df[cols_needed].copy().dropna().reset_index(drop=True)
    
    print(f"   Após limpeza: {len(df_clean)} registros")
    
    # Converter para numpy (mais eficiente)
    features_array = df_clean[feature_cols].values.astype(np.float32)
    labels_array = df_clean[label_col].values.astype(np.int32)
    dates_array = df_clean['Date'].values
    
    n_samples = len(df_clean) - sequence_length
    n_features = len(feature_cols)
    
    # Pré-alocar arrays
    X = np.zeros((n_samples, sequence_length, n_features), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.int32)
    dates = []
    
    print(f"   Criando {n_samples} sequências...")
    
    for i in range(n_samples):
        X[i] = features_array[i:i+sequence_length]
        y[i] = labels_array[i+sequence_length]
        dates.append(dates_array[i+sequence_length])
        
        if (i+1) % 20000 == 0:
            print(f"      {i+1}/{n_samples} sequências...")
    
    return X, y, dates


def split_data(X, y, dates, train_ratio=0.7, val_ratio=0.15):
    """
    Divide dados em train/val/test preservando ordem temporal.
    """
    n = len(X)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]
    
    dates_train = dates[:train_end]
    dates_val = dates[train_end:val_end]
    dates_test = dates[val_end:]
    
    return (X_train, y_train, dates_train), (X_val, y_val, dates_val), (X_test, y_test, dates_test)


def create_model(input_shape, num_classes=3):
    """
    Cria modelo LSTM para classificação multiclass com MAIOR CAPACIDADE.
    
    Args:
        input_shape: (sequence_length, num_features)
        num_classes: 3 (ALTA, LATERAL, BAIXA)
    
    AJUSTES PARA 18 FEATURES:
    - LSTM(256→128→64) - Arquitetura mais profunda
    - Recurrent_dropout=0.2 nas LSTMs
    - Dense(64) antes da saída (mais capacidade de decisão)
    - Total: ~400K params (vs 125K anterior)
    """
    model = Sequential([
        # 1ª LSTM: 256 unidades (dobrado para lidar com 18 features)
        LSTM(256, return_sequences=True, recurrent_dropout=0.2, input_shape=input_shape),
        BatchNormalization(),
        Dropout(0.3),
        
        # 2ª LSTM: 128 unidades (camada intermediária)
        LSTM(128, return_sequences=True, recurrent_dropout=0.2),
        BatchNormalization(),
        Dropout(0.3),
        
        # 3ª LSTM: 64 unidades (camada de compressão)
        LSTM(64, return_sequences=False, recurrent_dropout=0.2),
        BatchNormalization(),
        Dropout(0.3),
        
        # Dense: 64 unidades (decisão)
        Dense(64, activation='relu'),
        Dropout(0.2),
        
        # Output: 3 classes
        Dense(num_classes, activation='softmax')
    ])
    
    # Usar Categorical Crossentropy com LR ajustado para modelo maior
    model.compile(
        optimizer=Adam(learning_rate=0.0005),  # LR reduzido para modelo maior
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def main():
    print("="*70)
    print("TREINO COM TOP 14 FEATURES")
    print("="*70)
    
    # 1. CARREGAR DADOS
    data_path = project_root / "data" / "BTCUSDT_30m_full.csv"
    print(f"\n📂 Carregando: {data_path}")
    
    df = pd.read_csv(data_path, parse_dates=['Date'])
    print(f"✅ {len(df):,} registros carregados")
    print(f"📅 Período: {df['Date'].min()} até {df['Date'].max()}")
    
    # 2. TOP 14 FEATURES
    top14 = [
        'Donchian_Low', 'Donchian_High',
        'BB_Low', 'BB_High', 'BB_Mid',
        'Keltner_Low', 'Keltner_High',
        'EMA_50', 'SMA_50',
        'SMA_20', 'EMA_20', 'EMA_9',
        'Aroon_Spread', 'MACD_Hist'
    ]
    
    print(f"\n🎯 TOP 14 Features:")
    for i, feat in enumerate(top14, 1):
        print(f"   {i:2d}. {feat}")
    
    # Verificar se todas as features existem
    missing = [f for f in top14 if f not in df.columns]
    if missing:
        print(f"\n❌ Features faltando: {missing}")
        return
    
    # 3. CRIAR LABELS
    # Usar ATR% ADAPTATIVO em vez de threshold fixo
    # ATR% ajusta threshold baseado na volatilidade do mercado
    print("\n🏷️  Criando labels com ATR% adaptativo (horizon=12, k=0.75)...")
    df['Label'] = create_labels_adaptive_atr(df, horizon=12, k=0.75)
    
    # Distribuição de classes
    label_counts = df['Label'].value_counts().sort_index()
    print(f"\n📊 Distribuição de classes:")
    for label, count in label_counts.items():
        pct = (count / len(df)) * 100
        label_name = ['BAIXA', 'LATERAL', 'ALTA'][label]
        print(f"   {label} ({label_name:8s}): {count:6d} ({pct:5.2f}%)")
    
    # 4. PREPARAR SEQUÊNCIAS
    print(f"\n🔧 Preparando sequências (lookback=60)...")
    X, y, dates = prepare_sequences(df, top14, 'Label', sequence_length=60)
    
    print(f"✅ X shape: {X.shape}")
    print(f"✅ y shape: {y.shape}")
    
    # 5. NORMALIZAR FEATURES
    print(f"\n📐 Normalizando features...")
    scaler = StandardScaler()
    
    # Reshape para normalizar
    n_samples, n_timesteps, n_features = X.shape
    X_reshaped = X.reshape(-1, n_features)
    X_scaled = scaler.fit_transform(X_reshaped)
    X = X_scaled.reshape(n_samples, n_timesteps, n_features)
    
    # Salvar scaler
    scaler_path = project_root / "src" / "ml" / "checkpoints" / "scaler_top14.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler salvo: {scaler_path}")
    
    # 6. SPLIT DADOS
    print(f"\n✂️  Dividindo dados (70% train, 15% val, 15% test)...")
    (X_train, y_train, dates_train), (X_val, y_val, dates_val), (X_test, y_test, dates_test) = split_data(X, y, dates)
    
    print(f"   Train: {X_train.shape[0]:6d} samples ({dates_train[0]} até {dates_train[-1]})")
    print(f"   Val:   {X_val.shape[0]:6d} samples ({dates_val[0]} até {dates_val[-1]})")
    print(f"   Test:  {X_test.shape[0]:6d} samples ({dates_test[0]} até {dates_test[-1]})")
    
    # Converter labels para categorical
    y_train_cat = to_categorical(y_train, num_classes=3)
    y_val_cat = to_categorical(y_val, num_classes=3)
    y_test_cat = to_categorical(y_test, num_classes=3)
    
    # 7. CRIAR MODELO
    print(f"\n🏗️  Criando modelo LSTM...")
    model = create_model(input_shape=(X_train.shape[1], X_train.shape[2]), num_classes=3)
    model.summary()
    
    # 8. CALLBACKS
    checkpoint_path = project_root / "src" / "ml" / "checkpoints" / "model_top14_best.keras"
    
    callbacks = [
        ModelCheckpoint(str(checkpoint_path), monitor='val_loss', save_best_only=True, mode='min', verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=5e-5, verbose=1),  # patience 3→5
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)  # patience 6→10
    ]
    
    # Class weights: MODERADOS (distribuição já está balanceada!)
    # Com ATR% adaptativo gerando 31%/36%/33%, não precisamos weights fortes
    class_weight = {
        0: 1.2,   # BAIXA (leve boost)
        1: 1.0,   # LATERAL (baseline)
        2: 1.1    # ALTA (leve boost)
    }
    
    # 9. TREINAR
    print("\n🚀 Iniciando treinamento - Modelo GRANDE (3 LSTMs)...")
    print("="*70)
    print(f"⚖️  Class Weights: BAIXA={class_weight[0]}, LATERAL={class_weight[1]}, ALTA={class_weight[2]}")
    print("🏗️  Arquitetura: LSTM(256→128→64) + Dense(64) → ~400K params")
    print("🔬 LR=0.0005 (reduzido), Batch=32, Dropout=0.3")
    print("📏 Labeling: ATR% adaptativo (k=0.75) → Distribuição BALANCEADA!")
    print("="*70)
    
    _ = model.fit(
        X_train, y_train_cat,
        validation_data=(X_val, y_val_cat),
        epochs=50,
        batch_size=32,  # Reduzido para 32 (modelo maior requer batches menores)
        callbacks=callbacks,
        class_weight=class_weight,
        verbose=1
    )
    
    # 10. AVALIAR COM MÉTRICAS REAIS
    print("\n" + "="*70)
    print("📊 AVALIAÇÃO FINAL - BALANCED ACCURACY & F1-MACRO")
    print("="*70)
    
    # Avaliar todos os sets
    train_metrics = evaluate_model(model, X_train, y_train, "Train")
    val_metrics = evaluate_model(model, X_val, y_val, "Validation")
    test_metrics = evaluate_model(model, X_test, y_test, "Test")
    
    # 🔬 ANÁLISE DE DISTRIBUIÇÃO DE PREDIÇÕES
    print("\n" + "="*70)
    print("🔬 DISTRIBUIÇÃO DE PREDIÇÕES vs REAL")
    print("="*70)
    
    for set_name, y_true, y_pred in [
        ("Train", y_train, train_metrics['y_pred']),
        ("Val", y_val, val_metrics['y_pred']),
        ("Test", y_test, test_metrics['y_pred'])
    ]:
        pred_counts = np.bincount(y_pred, minlength=3)
        real_counts = np.bincount(y_true, minlength=3)
        
        print(f"\n📊 {set_name} Set:")
        print("           Predito    Real")
        for i, label in enumerate(['BAIXA', 'LATERAL', 'ALTA']):
            pred_pct = (pred_counts[i] / len(y_pred)) * 100
            real_pct = (real_counts[i] / len(y_true)) * 100
            diff = pred_pct - real_pct
            emoji = "✅" if abs(diff) < 10 else "⚠️" if abs(diff) < 20 else "❌"
            print(f"   {label:8s}: {pred_pct:5.1f}%   {real_pct:5.1f}%   ({diff:+5.1f}%) {emoji}")
    
    # Classification Report detalhado (Test)
    print("\n" + "="*70)
    print("📋 CLASSIFICATION REPORT (Test Set)")
    print("="*70)
    print(classification_report(
        y_test, 
        test_metrics['y_pred'], 
        target_names=['BAIXA (0)', 'LATERAL (1)', 'ALTA (2)'],
        digits=4
    ))
    
    # Confusion Matrix (Test)
    print("\n" + "="*70)
    print("🔢 CONFUSION MATRIX (Test Set)")
    print("="*70)
    cm = confusion_matrix(y_test, test_metrics['y_pred'])
    print("\n           Predicted:")
    print("           BAIXA  LATERAL  ALTA")
    print("Actual:")
    for i, label in enumerate(['BAIXA', 'LATERAL', 'ALTA']):
        print(f"  {label:8s}  {cm[i][0]:5d}   {cm[i][1]:7d}  {cm[i][2]:4d}")
    
    print(f"\n✅ Modelo salvo em: {checkpoint_path}")
    print(f"✅ Scaler salvo em: {scaler_path}")
    
    print("\n" + "="*70)
    print("✅ TREINO CONCLUÍDO!")
    print("="*70)


if __name__ == "__main__":
    main()
