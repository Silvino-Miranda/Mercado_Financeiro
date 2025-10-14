"""
Script para analisar as previsões do modelo e entender por que a estratégia não está operando
"""
import sys
sys.path.append('src')

import numpy as np
import pandas as pd
from data.data_loader import DataLoader
from utils.data_preprocessing import DataPreprocessor
from models.lstm_model import LSTMModel

# Configurações
symbol = "BTCUSDT"
interval = "30m"
sequence_length = 60
feature_columns = ["Open", "High", "Low", "SMA_20", "EMA_20"]
target_columns = ["Close", "High", "Low"]

print("Carregando dados e modelo...")
data_loader = DataLoader(symbol=symbol, interval=interval, use_local_file=True)
df = data_loader.load_data()

preprocessor = DataPreprocessor(
    feature_columns=feature_columns,
    target_columns=target_columns,
    sequence_length=sequence_length
)

X, Y, dates = preprocessor.fit_transform(df)
scaler = preprocessor.scaler
print(f"X shape: {X.shape}, Y shape: {Y.shape}")

# Carregar modelo
print("\nCarregando modelo treinado...")
import tensorflow as tf
model = tf.keras.models.load_model("lstm_model.keras")

# Fazer previsões
print("Gerando previsões...")
Y_pred = model.predict(X, verbose=0)

# Desnormalizar
Y_actual_scaled = scaler.inverse_transform(Y)
Y_pred_scaled = scaler.inverse_transform(Y_pred)

# Extrair Close
Y_actual_close = Y_actual_scaled[:, 0]
Y_pred_close = Y_pred_scaled[:, 0]

# Análise estatística
print("\n" + "="*70)
print("ANÁLISE DE PREVISÕES")
print("="*70)

print(f"\n1. Estatísticas dos Valores Reais (Close):")
print(f"   Média: {Y_actual_close.mean():.2f}")
print(f"   Min: {Y_actual_close.min():.2f}")
print(f"   Max: {Y_actual_close.max():.2f}")
print(f"   Desvio: {Y_actual_close.std():.2f}")

print(f"\n2. Estatísticas das Previsões:")
print(f"   Média: {Y_pred_close.mean():.2f}")
print(f"   Min: {Y_pred_close.min():.2f}")
print(f"   Max: {Y_pred_close.max():.2f}")
print(f"   Desvio: {Y_pred_close.std():.2f}")

# Calcular erro
errors = Y_pred_close - Y_actual_close
mape = np.mean(np.abs(errors / Y_actual_close)) * 100
print(f"\n3. Erro de Previsão:")
print(f"   Erro Médio: {errors.mean():.2f}")
print(f"   MAPE: {mape:.2f}%")
print(f"   Viés consistente: {'SIM - modelo SUPERESTIMA' if errors.mean() > 0 else 'SIM - modelo SUBESTIMA'}")

# Análise de tendências
pred_changes = np.diff(Y_pred_close)
actual_changes = np.diff(Y_actual_close)

print(f"\n4. Análise de Variações:")
print(f"   Variações nas previsões:")
print(f"     - Positivas: {(pred_changes > 0).sum()} ({(pred_changes > 0).sum()/len(pred_changes)*100:.1f}%)")
print(f"     - Negativas: {(pred_changes < 0).sum()} ({(pred_changes < 0).sum()/len(pred_changes)*100:.1f}%)")
print(f"     - Variação média: {pred_changes.mean():.4f}")
print(f"     - Variação máxima: {pred_changes.max():.2f}")
print(f"     - Variação mínima: {pred_changes.min():.2f}")

# Verificar variações significativas
threshold = 0.005  # 0.5%
pred_changes_pct = pred_changes / Y_pred_close[:-1]
significant_up = (pred_changes_pct > threshold).sum()
significant_down = (pred_changes_pct < -threshold).sum()

print(f"\n5. Sinais de Trading (threshold=0.5%):")
print(f"   Sinais de COMPRA (variação > 0.5%): {significant_up}")
print(f"   Sinais de VENDA (variação < -0.5%): {significant_down}")

# Análise do viés
prediction_bias = (Y_pred_close - Y_actual_close) / Y_actual_close
bias_acceptable = (np.abs(prediction_bias) < 0.05).sum()

print(f"\n6. Análise de Viés (threshold=5%):")
print(f"   Previsões com viés aceitável (<5%): {bias_acceptable} ({bias_acceptable/len(prediction_bias)*100:.1f}%)")
print(f"   Viés médio: {prediction_bias.mean()*100:.2f}%")

# Simulação de sinais
print(f"\n7. Simulação de Sinais de Trading:")
buy_signals = 0
sell_signals = 0

for i in range(2, len(Y_pred_close)):
    pred_change = (Y_pred_close[i] - Y_pred_close[i-1]) / Y_pred_close[i-1]
    bias = (Y_pred_close[i] - Y_actual_close[i]) / Y_actual_close[i]
    
    if pred_change > threshold and abs(bias) < 0.05:
        buy_signals += 1
    elif pred_change < -threshold:
        sell_signals += 1

print(f"   Sinais de COMPRA gerados: {buy_signals}")
print(f"   Sinais de VENDA gerados: {sell_signals}")

# Amostras
print(f"\n8. Amostra dos Dados (primeiras 20 linhas):")
sample_df = pd.DataFrame({
    'Real': Y_actual_close[:20],
    'Previsto': Y_pred_close[:20],
    'Erro': errors[:20],
    'Viés%': prediction_bias[:20] * 100
})
print(sample_df.to_string())

print("\n" + "="*70)
print("CONCLUSÃO:")
print("="*70)
if bias_acceptable < len(prediction_bias) * 0.5:
    print("❌ O modelo tem um viés muito grande (>5%) na maioria das previsões.")
    print("   Isso impede a estratégia de operar com segurança.")
    print("\n💡 RECOMENDAÇÃO: Re-treinar o modelo com mais epochs ou ajustar hiperparâmetros")
if significant_up == 0 and significant_down == 0:
    print("❌ O modelo não gera variações significativas entre períodos consecutivos.")
    print("   As previsões são muito 'suaves' e não capturam a volatilidade do mercado.")
    print("\n💡 RECOMENDAÇÃO: Ajustar a arquitetura da rede ou adicionar mais features")
if buy_signals == 0:
    print("❌ A combinação de baixa variação + alto viés resulta em ZERO sinais de compra.")
    print("\n💡 RECOMENDAÇÃO: Ajustar os thresholds da estratégia ou melhorar o modelo")
