# src/ml/compare_features.py
"""
Script para comparar as features antigas (6) vs novas (18).
"""

print("="*70)
print("COMPARACAO DE FEATURES - ANTES vs DEPOIS")
print("="*70)

# Features antigas (6)
features_old = [
    "Open",
    "High",
    "Low",
    "Close",
    "SMA_20",
    "EMA_20",
]

# Features novas (18)
features_new = [
    # OHLC (4)
    "Open", "High", "Low", "Close",
    # Bollinger Bands (3)
    "BB_High", "BB_Mid", "BB_Low",
    # Keltner Channel (2)
    "Keltner_High", "Keltner_Low",
    # Donchian Channel (2)
    "Donchian_High", "Donchian_Low",
    # EMAs (3)
    "EMA_9", "EMA_20", "EMA_50",
    # SMAs (2)
    "SMA_20", "SMA_50",
    # Momentum (2)
    "Aroon_Spread", "MACD_Hist",
]

print("\n--- FEATURES ANTIGAS (6) ---")
for i, feat in enumerate(features_old, 1):
    print(f"{i}. {feat}")

print("\n--- FEATURES NOVAS (18) ---")
for i, feat in enumerate(features_new, 1):
    categoria = ""
    if feat in ["Open", "High", "Low", "Close"]:
        categoria = "[OHLC]"
    elif "BB_" in feat:
        categoria = "[Bollinger]"
    elif "Keltner_" in feat:
        categoria = "[Keltner]"
    elif "Donchian_" in feat:
        categoria = "[Donchian]"
    elif "EMA_" in feat:
        categoria = "[EMA]"
    elif "SMA_" in feat:
        categoria = "[SMA]"
    elif feat in ["Aroon_Spread", "MACD_Hist"]:
        categoria = "[Momentum]"
    
    novo = " (NOVO!)" if feat not in features_old else ""
    print(f"{i:2d}. {feat:20s} {categoria:12s} {novo}")

print("\n--- RESUMO ---")
print(f"Features antigas: {len(features_old)}")
print(f"Features novas:   {len(features_new)}")
print(f"Incremento:       +{len(features_new) - len(features_old)} features ({((len(features_new)/len(features_old))-1)*100:.0f}% aumento)")

print("\n--- FEATURES ADICIONADAS ---")
added = [f for f in features_new if f not in features_old]
for i, feat in enumerate(added, 1):
    print(f"{i:2d}. {feat}")

print("="*70)
