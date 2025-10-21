"""
Script para analisar as predições do classificador.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml_v2.cli import load_and_prepare_data
from tensorflow import keras
import pickle


def analyze_classifier_predictions():
    """Analisa distribuição de confiança das predições."""
    print("🔍 ANÁLISE DAS PREDIÇÕES DO CLASSIFICADOR")
    print("="*60)
    
    # Load data
    df = load_and_prepare_data("data/BTCUSDT_30m_full.csv")
    
    # Get test data
    n = len(df)
    i_val = int(n * 0.85)
    df_test = df.iloc[i_val:].reset_index(drop=True)
    
    print(f"📊 Período de análise: {df_test['Date'].min()} a {df_test['Date'].max()}")
    print(f"📊 Amostras: {len(df_test):,}")
    
    # Load model and preprocessor
    checkpoint_dir = Path("artifacts/checkpoints")
    classifiers = sorted(checkpoint_dir.glob("classifier_*.keras"))
    
    if not classifiers:
        print("❌ Nenhum classificador encontrado!")
        return
    
    model_path = classifiers[-1]
    ts_model = model_path.stem.replace('classifier_', '')
    preprocessor_path = checkpoint_dir / f"preprocessor_{ts_model}.pkl"
    
    print(f"🤖 Modelo: {model_path.name}")
    print(f"🔧 Preprocessor: {preprocessor_path.name}")
    
    # Load
    model = keras.models.load_model(model_path)
    with open(preprocessor_path, 'rb') as f:
        preprocessor = pickle.load(f)
    
    # Transform data
    X_test, y_test = preprocessor.transform(df_test)
    
    # Predict
    print("\n🔮 Gerando predições...")
    probabilities = model.predict(X_test, verbose=0)
    predictions = np.argmax(probabilities, axis=1)
    max_probs = np.max(probabilities, axis=1)
    
    # Analyze confidence distribution
    print(f"\n📊 DISTRIBUIÇÃO DE CONFIANÇA:")
    print(f"   Confiança média: {max_probs.mean():.3f}")
    print(f"   Confiança mediana: {np.median(max_probs):.3f}")
    print(f"   Confiança mínima: {max_probs.min():.3f}")
    print(f"   Confiança máxima: {max_probs.max():.3f}")
    
    # Confidence thresholds
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print(f"\n📈 PREDIÇÕES POR THRESHOLD:")
    label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
    
    for threshold in thresholds:
        mask = max_probs >= threshold
        n_confident = mask.sum()
        pct_confident = n_confident / len(max_probs) * 100
        
        print(f"\n   Threshold {threshold:.1f}: {n_confident:,} predições ({pct_confident:.1f}%)")
        
        if n_confident > 0:
            confident_preds = predictions[mask]
            for label in [0, 1, 2]:
                count = (confident_preds == label).sum()
                pct = count / n_confident * 100 if n_confident > 0 else 0
                print(f"     {label_names[label]}: {count:,} ({pct:.1f}%)")
    
    # Analyze by class
    print(f"\n📊 CONFIANÇA POR CLASSE:")
    for label in [0, 1, 2]:
        mask = predictions == label
        if mask.sum() > 0:
            avg_conf = max_probs[mask].mean()
            print(f"   {label_names[label]}: {avg_conf:.3f} confiança média")


if __name__ == "__main__":
    analyze_classifier_predictions()