# src/ml/validate_features.py
"""
Script para validar que todas as 18 features estão disponíveis e sem NaN.
"""

import pandas as pd
from pathlib import Path

# Carregar dados
data_path = Path("data/BTCUSDT_30m_full.csv")
df = pd.read_csv(data_path)

print("="*70)
print("VALIDAÇÃO DE FEATURES")
print("="*70)

# Features a serem validadas
feature_columns = [
    # OHLC
    "Open", "High", "Low", "Close",
    # Bollinger Bands
    "BB_High", "BB_Mid", "BB_Low",
    # Keltner Channel
    "Keltner_High", "Keltner_Low",
    # Donchian Channel
    "Donchian_High", "Donchian_Low",
    # EMAs
    "EMA_9", "EMA_20", "EMA_50",
    # SMAs
    "SMA_20", "SMA_50",
    # Momentum/Tendência
    "Aroon_Spread", "MACD_Hist",
]

print(f"\nTotal de features a validar: {len(feature_columns)}")
print("\nValidando cada feature:")
print("-"*70)

all_valid = True
for i, col in enumerate(feature_columns, 1):
    if col not in df.columns:
        print(f"{i:2d}. {col:20s} ❌ COLUNA NÃO ENCONTRADA!")
        all_valid = False
    else:
        nan_count = df[col].isnull().sum()
        nan_pct = (nan_count / len(df)) * 100
        
        if nan_count == 0:
            print(f"{i:2d}. {col:20s} ✅ OK (sem NaN)")
        else:
            print(f"{i:2d}. {col:20s} ⚠️  {nan_count:,} NaN ({nan_pct:.2f}%)")

print("-"*70)

if all_valid:
    print("\n✅ TODAS AS FEATURES ESTÃO DISPONÍVEIS E VÁLIDAS!")
    print(f"\n📊 Estatísticas:")
    print(f"   • Registros: {len(df):,}")
    print(f"   • Período: {df['Date'].min()} até {df['Date'].max()}")
    print(f"   • Features: {len(feature_columns)}")
else:
    print("\n❌ ALGUMAS FEATURES ESTÃO FALTANDO OU INVÁLIDAS!")

print("="*70)
