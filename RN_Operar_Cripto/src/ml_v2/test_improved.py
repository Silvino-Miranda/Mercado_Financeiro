"""
Teste direto do sistema aprimorado sem CLI.
"""
import sys
import os
import pandas as pd
import numpy as np

# Adicionar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.improved_directional_model import build_improved_directional_lstm, get_aggressive_class_weights, get_improved_callbacks
from preprocess.improved_preprocessor import ImprovedDirectionalPreprocessor

def test_improved_system():
    """Teste completo do sistema aprimorado."""
    print("🧪 TESTE DO SISTEMA CLASSIFICADOR APRIMORADO")
    print("="*60)
    
    # Carregar dados
    print("📊 Carregando dados...")
    df = pd.read_csv("../../data/BTCUSDT_30m_full.csv")
    print(f"   Dataset: {len(df):,} samples, {len(df.columns)} features")
    
    # Preprocessor aprimorado
    print("\n🔧 Configurando preprocessor aprimorado...")
    preprocessor = ImprovedDirectionalPreprocessor(
        lookback_window=60,
        horizon_periods=24,  # 12h
        threshold_multiplier=1.0,  # ATR adaptativo
        adaptive_threshold=True,
        use_advanced_features=True,  # 51+ features avançadas
        balance_method="adaptive"    # Balanceamento inteligente
    )
    
    # Preprocessar
    print("\n🔄 Preprocessando...")
    X, y = preprocessor.fit_transform(df)
    
    # Split
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"   Treino: {X_train.shape}")
    print(f"   Validação: {X_val.shape}")
    
    # Class weights agressivos
    print("\n⚖️ Calculando class weights...")
    class_weights = get_aggressive_class_weights(y_train, strategy="aggressive")
    
    # Modelo aprimorado
    print("\n🤖 Construindo modelo...")
    model = build_improved_directional_lstm(
        input_shape=(X_train.shape[1], X_train.shape[2]),
        lstm_units=64,  # Menor para teste rápido
        lstm_layers=2,
        dropout=0.4,
        learning_rate=1e-3,
        use_focal_loss=True
    )
    
    # Callbacks
    callbacks = get_improved_callbacks(
        patience_early=5,  # Menor para teste
        patience_lr=3
    )
    
    # Treinar (poucas épocas para teste)
    print("\n🔥 Treinamento...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=3,  # Só 3 épocas para teste
        batch_size=32,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    # Avaliar
    print("\n📊 Avaliação:")
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    y_pred = model.predict(X_val, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    from sklearn.metrics import balanced_accuracy_score, classification_report
    
    balanced_acc = balanced_accuracy_score(y_val, y_pred_classes)
    
    print(f"   Accuracy: {val_acc:.4f}")
    print(f"   Balanced Accuracy: {balanced_acc:.4f}")
    print(f"   Loss: {val_loss:.4f}")
    
    # Relatório detalhado
    label_names = ['BAIXA', 'LATERAL', 'ALTA']
    report = classification_report(y_val, y_pred_classes, target_names=label_names)
    print(f"\n📈 Relatório por classe:\n{report}")
    
    print(f"\n✅ TESTE CONCLUÍDO!")
    print(f"   Features engineered: {len(preprocessor.feature_engineer.feature_names) if preprocessor.feature_engineer else 0}")
    print(f"   Model parameters: {model.count_params():,}")
    print(f"   Final accuracy: {val_acc:.1%}")
    print(f"   Final balanced accuracy: {balanced_acc:.1%}")
    
    return model, preprocessor, history


if __name__ == "__main__":
    test_improved_system()