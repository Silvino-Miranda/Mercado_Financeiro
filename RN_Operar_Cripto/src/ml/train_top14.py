# src/ml/train_top14.py
"""
Treino de modelo LSTM com TOP 14 indicadores técnicos.
Classificação multiclass: ALTA (2), LATERAL (1), BAIXA (0)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import joblib

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def create_labels_simple(df, horizon=12, threshold=1.5):
    """
    Cria labels simples com threshold fixo.
    
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
    Cria modelo LSTM para classificação multiclass.
    
    Args:
        input_shape: (sequence_length, num_features)
        num_classes: 3 (ALTA, LATERAL, BAIXA)
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        BatchNormalization(),
        
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        BatchNormalization(),
        
        Dense(32, activation='relu'),
        Dropout(0.2),
        
        Dense(num_classes, activation='softmax')  # 3 classes
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
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
    print(f"\n🏷️  Criando labels (horizon=12, threshold=1.5%)...")
    df['Label'] = create_labels_simple(df, horizon=12, threshold=1.5)
    
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
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7, verbose=1),
        ModelCheckpoint(str(checkpoint_path), monitor='val_accuracy', save_best_only=True, verbose=1)
    ]
    
    # 9. TREINAR
    print(f"\n🚀 Iniciando treinamento...")
    print("="*70)
    
    history = model.fit(
        X_train, y_train_cat,
        validation_data=(X_val, y_val_cat),
        epochs=50,
        batch_size=64,
        callbacks=callbacks,
        verbose=1
    )
    
    # 10. AVALIAR
    print(f"\n" + "="*70)
    print("📊 AVALIAÇÃO FINAL")
    print("="*70)
    
    # Predictions
    y_train_pred = np.argmax(model.predict(X_train), axis=1)
    y_val_pred = np.argmax(model.predict(X_val), axis=1)
    y_test_pred = np.argmax(model.predict(X_test), axis=1)
    
    # Accuracy
    train_acc = accuracy_score(y_train, y_train_pred)
    val_acc = accuracy_score(y_val, y_val_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    print(f"\n🎯 Acurácia:")
    print(f"   Train: {train_acc*100:.2f}%")
    print(f"   Val:   {val_acc*100:.2f}%")
    print(f"   Test:  {test_acc*100:.2f}%")
    
    # Classification Report (Test)
    print(f"\n📋 Classification Report (Test):")
    print(classification_report(y_test, y_test_pred, target_names=['BAIXA', 'LATERAL', 'ALTA']))
    
    # Confusion Matrix (Test)
    print(f"\n🔢 Confusion Matrix (Test):")
    cm = confusion_matrix(y_test, y_test_pred)
    print("          BAIXA  LATERAL  ALTA")
    for i, label in enumerate(['BAIXA', 'LATERAL', 'ALTA']):
        print(f"{label:8s}  {cm[i][0]:5d}   {cm[i][1]:5d}  {cm[i][2]:5d}")
    
    print(f"\n✅ Modelo salvo em: {checkpoint_path}")
    print(f"✅ Scaler salvo em: {scaler_path}")
    
    print("\n" + "="*70)
    print("✅ TREINO CONCLUÍDO!")
    print("="*70)


if __name__ == "__main__":
    main()
