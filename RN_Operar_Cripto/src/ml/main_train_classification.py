# src/ml/main_train_classification.py
"""
Script de treinamento para CLASSIFICAÇÃO (em vez de regressão).
Usa o novo AdvancedDataPreprocessor com ~50 features técnicas.

Objetivo: Aumentar acurácia de 52.2% para 60-65% (primeira fase).
"""

import sys
from pathlib import Path
import os
import numpy as np

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml.data.data_loader import DataLoader
from src.ml.utils.advanced_preprocessing import AdvancedDataPreprocessor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM, Dense, Dropout, BatchNormalization, Input
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
import joblib


def create_classification_model(input_shape):
    """
    Cria modelo LSTM para CLASSIFICAÇÃO BINÁRIA.
    
    Mudanças principais:
    - Última camada: Dense(1, activation='sigmoid')
    - Loss: binary_crossentropy (em vez de MSE)
    - Métricas: accuracy, precision, recall, AUC
    
    Args:
        input_shape: (sequence_length, num_features)
        
    Returns:
        Modelo compilado
    """
    model = Sequential([
        Input(shape=input_shape),
        
        # LSTM Layer 1
        LSTM(units=64, return_sequences=True),
        BatchNormalization(),
        Dropout(0.3),
        
        # LSTM Layer 2
        LSTM(units=64, return_sequences=False),
        BatchNormalization(),
        Dropout(0.3),
        
        # Dense Layers
        Dense(units=32, activation='relu'),
        Dropout(0.2),
        
        # Output Layer - CLASSIFICAÇÃO BINÁRIA
        Dense(units=1, activation='sigmoid')  # 🔴 MUDANÇA PRINCIPAL
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',  # 🔴 MUDANÇA PRINCIPAL
        metrics=[
            'accuracy',  # 🔴 MUDANÇA PRINCIPAL
            'precision',
            'recall',
            'AUC'
        ]
    )
    
    return model


def evaluate_classification(y_true, y_pred_prob, threshold=0.5):
    """
    Avaliação completa do modelo de classificação.
    
    Args:
        y_true: Labels verdadeiros (0 ou 1)
        y_pred_prob: Probabilidades preditas (0 a 1)
        threshold: Limiar para classificação (padrão 0.5)
        
    Returns:
        dict com métricas
    """
    y_pred = (y_pred_prob > threshold).astype(int).flatten()
    
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1_score': f1_score(y_true, y_pred, zero_division=0),
        'auc_roc': roc_auc_score(y_true, y_pred_prob)
    }
    
    print("\n" + "=" * 70)
    print("📊 MÉTRICAS DE CLASSIFICAÇÃO")
    print("=" * 70)
    for metric_name, value in metrics.items():
        status = "✅" if value > 0.65 else "⚠️" if value > 0.55 else "❌"
        print(f"{status} {metric_name.upper():15s}: {value:.4f} ({value*100:.2f}%)")
    
    print("\n" + "=" * 70)
    print("🎯 CONFUSION MATRIX")
    print("=" * 70)
    cm = confusion_matrix(y_true, y_pred)
    print(f"          Pred 0    Pred 1")
    print(f"True 0  {cm[0,0]:7d}   {cm[0,1]:7d}   (TN, FP)")
    print(f"True 1  {cm[1,0]:7d}   {cm[1,1]:7d}   (FN, TP)")
    print("=" * 70)
    
    print("\n📋 CLASSIFICATION REPORT:")
    print(classification_report(y_true, y_pred, target_names=['Não Sobe', 'Sobe']))
    
    return metrics


def main():
    print("\n" + "=" * 70)
    print("🚀 TREINAMENTO COM CLASSIFICAÇÃO - VERSÃO MELHORADA")
    print("=" * 70)
    print("MUDANÇAS PRINCIPAIS:")
    print("  ✅ Target: CLASSIFICAÇÃO (direção) em vez de REGRESSÃO (preço)")
    print("  ✅ Features: ~50 features técnicas (era 6)")
    print("  ✅ Loss: binary_crossentropy (era MSE)")
    print("  ✅ Métricas: accuracy, precision, recall, AUC")
    print("  ✅ Scaler: RobustScaler (melhor para dados financeiros)")
    print("=" * 70 + "\n")
    
    # 1. CARREGAR DADOS
    print("📂 Carregando dados...")
    data_loader = DataLoader(
        symbol="BTCUSDT",
        interval="30m",
        use_local_file=True,
        local_filename="BTCUSDT_30m_full.csv"
    )
    df = data_loader.load_data()
    
    print(f"\n{'='*70}")
    print("📊 BASE DE DADOS COMPLETA - 8 ANOS DE HISTÓRICO")
    print(f"{'='*70}")
    print(f"Total de registros: {len(df):,}")
    print(f"Período: {df['Date'].min()} a {df['Date'].max()}")
    print(f"{'='*70}\n")
    
    # 2. PRÉ-PROCESSAR DADOS (com features poderosas)
    preprocessor = AdvancedDataPreprocessor(
        sequence_length=120,  # 4 horas (era 60)
        prediction_horizon=24,  # 12 horas à frente
        threshold=0.005  # 0.5% movimento mínimo
    )
    
    # Preparar dados (adiciona features + cria target)
    df_prepared = preprocessor.prepare_data(df)
    
    # Criar sequências
    X, y, dates = preprocessor.create_sequences(df_prepared, is_train=True)
    
    # 3. DIVIDIR DADOS (70/15/15)
    (
        X_train, y_train, dates_train,
        X_val, y_val, dates_val,
        X_test, y_test, dates_test
    ) = preprocessor.split_data(X, y, dates)
    
    # 4. CRIAR MODELO
    print("\n" + "=" * 70)
    print("🏗️ CRIANDO MODELO DE CLASSIFICAÇÃO")
    print("=" * 70)
    input_shape = (X_train.shape[1], X_train.shape[2])
    print(f"Input shape: {input_shape}")
    print(f"  - Sequence length: {input_shape[0]}")
    print(f"  - Num features: {input_shape[1]}")
    
    model = create_classification_model(input_shape)
    print("\n📐 Arquitetura do modelo:")
    model.summary()
    
    # 5. CONFIGURAR CALLBACKS
    print("\n" + "=" * 70)
    print("⚙️ CONFIGURANDO CALLBACKS")
    print("=" * 70)
    
    os.makedirs("src/ml/checkpoints", exist_ok=True)
    
    callbacks = [
        # Early Stopping - para quando não houver melhoria
        EarlyStopping(
            monitor='val_accuracy',  # 🔴 Mudou de val_loss para val_accuracy
            patience=20,
            restore_best_weights=True,
            mode='max',  # 🔴 Maximizar accuracy (era 'min' para loss)
            verbose=1
        ),
        
        # Learning Rate Scheduler - reduz LR quando estagnado
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001,
            verbose=1
        ),
        
        # Model Checkpoint - salva melhor modelo
        ModelCheckpoint(
            filepath='src/ml/checkpoints/best_classification_model.keras',
            monitor='val_accuracy',  # 🔴 Mudou
            save_best_only=True,
            mode='max',  # 🔴 Maximizar
            verbose=1
        )
    ]
    
    print("✓ EarlyStopping (monitor=val_accuracy, patience=20)")
    print("✓ ReduceLROnPlateau (factor=0.5, patience=5)")
    print("✓ ModelCheckpoint (salva melhor modelo)")
    
    # 6. TREINAR MODELO
    print("\n" + "=" * 70)
    print("🎯 INICIANDO TREINAMENTO")
    print("=" * 70)
    print(f"Epochs: 100 (com early stopping)")
    print(f"Batch size: 64")
    print(f"Learning rate: 0.001 (com scheduler)")
    print("=" * 70 + "\n")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=64,
        callbacks=callbacks,
        verbose=1
    )
    
    # 7. AVALIAR MODELO
    print("\n" + "=" * 70)
    print("📈 AVALIAÇÃO NO CONJUNTO DE VALIDAÇÃO")
    print("=" * 70)
    y_val_pred_prob = model.predict(X_val, verbose=0)
    metrics_val = evaluate_classification(y_val, y_val_pred_prob)
    
    print("\n" + "=" * 70)
    print("🎯 AVALIAÇÃO NO CONJUNTO DE TESTE (DADOS NÃO VISTOS)")
    print("=" * 70)
    y_test_pred_prob = model.predict(X_test, verbose=0)
    metrics_test = evaluate_classification(y_test, y_test_pred_prob)
    
    # 8. COMPARAÇÃO COM BASELINE
    print("\n" + "=" * 70)
    print("📊 COMPARAÇÃO: BASELINE vs NOVO MODELO")
    print("=" * 70)
    print(f"Baseline (Regressão):      52.2%")
    print(f"Novo Modelo (Classificação): {metrics_test['accuracy']*100:.1f}%")
    print(f"Melhoria:                   {(metrics_test['accuracy'] - 0.522)*100:+.1f}%")
    
    if metrics_test['accuracy'] >= 0.60:
        print("\n🎉 META ATINGIDA! Acurácia >= 60%")
    elif metrics_test['accuracy'] >= 0.55:
        print("\n⚠️ Progresso moderado. Considere adicionar mais features.")
    else:
        print("\n❌ Meta não atingida. Revisar abordagem.")
    
    print("=" * 70)
    
    # 9. SALVAR MODELO E SCALER
    print("\n" + "=" * 70)
    print("💾 SALVANDO MODELO E SCALER")
    print("=" * 70)
    
    model_path = "src/ml/checkpoints/classification_model_final.keras"
    scaler_path = "src/ml/checkpoints/scaler_classification.pkl"
    
    model.save(model_path)
    joblib.dump(preprocessor.scaler, scaler_path)
    
    # Salvar também informações de configuração
    config = {
        'sequence_length': preprocessor.sequence_length,
        'prediction_horizon': preprocessor.prediction_horizon,
        'threshold': preprocessor.threshold,
        'feature_columns': preprocessor.feature_columns,
        'num_features': len(preprocessor.feature_columns),
        'input_shape': input_shape,
        'metrics_test': metrics_test,
        'metrics_val': metrics_val
    }
    
    import json
    config_path = "src/ml/checkpoints/classification_config.json"
    with open(config_path, 'w') as f:
        # Converter numpy types para tipos Python nativos
        config_serializable = {
            k: (v.tolist() if isinstance(v, np.ndarray) else 
                int(v) if isinstance(v, (np.integer, np.int64)) else
                float(v) if isinstance(v, (np.floating, np.float64)) else
                list(v) if isinstance(v, (list, tuple)) and any(isinstance(i, (np.integer, np.floating)) for i in v) else
                v)
            for k, v in config.items()
        }
        json.dump(config_serializable, f, indent=2)
    
    print(f"✅ Modelo salvo: {model_path}")
    print(f"✅ Scaler salvo: {scaler_path}")
    print(f"✅ Config salvo: {config_path}")
    print("=" * 70)
    
    # 10. RESUMO FINAL
    print("\n" + "=" * 70)
    print("🎯 RESUMO FINAL DO TREINAMENTO")
    print("=" * 70)
    print(f"Dataset: {len(df):,} registros")
    print(f"Features: {len(preprocessor.feature_columns)} (era 6)")
    print(f"Treino: {len(X_train):,} amostras")
    print(f"Validação: {len(X_val):,} amostras")
    print(f"Teste: {len(X_test):,} amostras")
    print(f"\nMétricas de Teste:")
    print(f"  Accuracy:  {metrics_test['accuracy']*100:.2f}%")
    print(f"  Precision: {metrics_test['precision']*100:.2f}%")
    print(f"  Recall:    {metrics_test['recall']*100:.2f}%")
    print(f"  F1-Score:  {metrics_test['f1_score']*100:.2f}%")
    print(f"  AUC-ROC:   {metrics_test['auc_roc']:.4f}")
    print("=" * 70)
    
    print("\n✅ TREINAMENTO CONCLUÍDO COM SUCESSO!\n")
    
    return model, preprocessor, history, metrics_test


if __name__ == "__main__":
    model, preprocessor, history, metrics = main()
