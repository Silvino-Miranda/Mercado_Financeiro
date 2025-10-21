import pandas as pd

# Carregar dados
df = pd.read_csv('data/BTCUSDT_30m_full.csv')

# Colunas totais
all_cols = list(df.columns)

# Features usadas no treinamento (todas exceto Date e Close)
feature_cols = [c for c in all_cols if c not in ['Date', 'Close']]

print("="*80)
print("📊 ANÁLISE DE FEATURES - ML v3")
print("="*80)
print(f"\n📁 Total de colunas no CSV: {len(all_cols)}")
print(f"❌ Colunas excluídas: Date (index), Close (target)")
print(f"\n🎯 FEATURES USADAS PARA TREINAR: {len(feature_cols)}")
print(f"\n📋 Lista de features:")
print("-"*80)

for i, col in enumerate(feature_cols, 1):
    # Pegar alguns valores para contexto
    sample_val = df[col].iloc[100]
    print(f"  {i:2d}. {col:20s} (ex: {sample_val:.4f})")

print("-"*80)

print(f"\n📐 Formato dos dados de entrada (X):")
print(f"   Shape por amostra: (lookback, n_features)")
print(f"   Exemplo com lookback=60: (60, {len(feature_cols)})")
print(f"\n   Isso significa: 60 timesteps × {len(feature_cols)} features = {60 * len(feature_cols)} valores por predição")

print(f"\n🎯 Target (y): Close")
print(f"   Shape: (1,) - Valor único de preço")

print(f"\n💡 Resumo:")
print(f"   - Cada janela deslizante usa {len(feature_cols)} features")
print(f"   - Cada timestep tem {len(feature_cols)} valores")
print(f"   - Total de dados por predição: {60 * len(feature_cols)} valores (com lookback=60)")
print("="*80)
