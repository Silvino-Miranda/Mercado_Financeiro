"""
Executar treinamento do classificador aprimorado diretamente.
"""
import sys
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Adicionar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
ml_v2_dir = os.path.join(current_dir, 'src', 'ml_v2')
sys.path.append(ml_v2_dir)

from models.improved_directional_model import build_improved_directional_lstm, get_aggressive_class_weights, get_improved_callbacks
from preprocess.improved_preprocessor import ImprovedDirectionalPreprocessor

def run_improved_training():
    """Executa treinamento completo do classificador aprimorado."""
    print("=" * 80)
    print("COMANDO: TRAIN IMPROVED CLASSIFIER (TODAS AS MELHORIAS)")
    print("=" * 80 + "\n")
    
    import tensorflow as tf
    
    print("🚀 Iniciando treinamento do classificador APRIMORADO...")
    
    # Carregar dados
    df = pd.read_csv("data/BTCUSDT_30m_full.csv")
    print(f"📊 Dataset carregado: {len(df):,} samples, {len(df.columns)} features")
    
    # Configurar preprocessor aprimorado
    preprocessor = ImprovedDirectionalPreprocessor(
        lookback_window=60,
        horizon_periods=24,  # 12h ao invés de 6h
        threshold_multiplier=1.0,  # ATR-based
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
        lstm_units=128,
        lstm_layers=3,
        dropout=0.4,
        learning_rate=1e-3,
        use_focal_loss=True
    )
    
    # Callbacks aprimorados
    callbacks = get_improved_callbacks(
        patience_early=20,
        patience_lr=10
    )
    
    # Salvar checkpoints
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_path = f"artifacts/checkpoints/improved_classifier_{timestamp}"
    
    # Criar diretório se não existir
    os.makedirs("artifacts/checkpoints", exist_ok=True)
    os.makedirs("artifacts/logs", exist_ok=True)
    
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
        epochs=10,
        batch_size=64,
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
    results = model.evaluate(X_val, y_val, verbose=0)
    val_loss = results[0]
    val_acc = results[1]
    
    # Predições para métricas detalhadas
    y_pred = model.predict(X_val, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    from sklearn.metrics import classification_report, balanced_accuracy_score, confusion_matrix
    
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
    
    # Confusion Matrix
    cm = confusion_matrix(y_val, y_pred_classes)
    print(f"\n📊 Confusion Matrix:")
    print(f"        Pred: BAIXA  LATERAL  ALTA")
    for i, label in enumerate(label_names):
        print(f"Real {label:7}: {cm[i][0]:5}    {cm[i][1]:5}  {cm[i][2]:5}")
    
    # Salvar histórico
    history_path = f"artifacts/logs/improved_classifier_history_{timestamp}.json"
    with open(history_path, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)
    
    print(f"✅ Histórico salvo em: {history_path}")
    
    # Análise das melhorias
    print(f"\n🎯 ANÁLISE DAS MELHORIAS:")
    print(f"   ✅ Features avançadas: {len(preprocessor.feature_engineer.feature_names)} criadas")
    print(f"   ✅ Threshold adaptativo: ATR-based com k={preprocessor.threshold_multiplier}")
    print(f"   ✅ Horizon estendido: {preprocessor.horizon_periods} períodos (12h)")
    print(f"   ✅ Balanceamento: {len(y_train)} → amostras balanceadas")
    print(f"   ✅ Focal Loss: Implementado com class weights agressivos")
    print(f"   ✅ Arquitetura: {model.count_params():,} parâmetros, 3 LSTMs + BatchNorm")
    
    # Comparação com baseline
    baseline_acc = max(np.bincount(y_val)) / len(y_val)  # Sempre prever classe majoritária
    improvement = balanced_acc - baseline_acc
    
    print(f"\n📈 COMPARAÇÃO COM BASELINE:")
    print(f"   Baseline (sempre majoritária): {baseline_acc:.1%}")
    print(f"   Balanced Accuracy obtida: {balanced_acc:.1%}")
    print(f"   Melhoria: {improvement:+.1%}")
    
    if balanced_acc > 0.6:
        print(f"   🎉 SUCESSO! Balanced Accuracy > 60%")
    elif balanced_acc > 0.55:
        print(f"   ✅ BOM! Balanced Accuracy > 55%")
    else:
        print(f"   ⚠️ Precisamos ajustar mais...")
    
    return history, model, preprocessor


if __name__ == "__main__":
    run_improved_training()