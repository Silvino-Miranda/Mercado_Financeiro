# 📊 Features do Modelo LSTM v3

## Resumo Executivo

**Total de Features Usadas: 18**

### 🎯 Colunas do CSV (20 total)

| Coluna | Uso | Tipo |
|--------|-----|------|
| **Date** | ❌ Excluída (index temporal) | Timestamp |
| **Close** | 🎯 **TARGET** (valor a prever) | Float |
| **Demais (18)** | ✅ **FEATURES** de entrada | Float |

---

## 📋 Lista Completa de Features (18)

### 1. OHLCV (4 features)
Dados brutos de mercado:
- **Open**: Preço de abertura
- **High**: Preço máximo
- **Low**: Preço mínimo
- **Volume**: Volume negociado

### 2. Bandas de Bollinger (3 features)
Indicador de volatilidade:
- **BB_High**: Banda superior (BB Upper)
- **BB_Mid**: Banda média (SMA 20)
- **BB_Low**: Banda inferior (BB Lower)

### 3. Bandas de Keltner (2 features)
Indicador de canais baseado em ATR:
- **Keltner_High**: Canal superior
- **Keltner_Low**: Canal inferior

### 4. Donchian Channel (2 features)
Indicador de breakout:
- **Donchian_High**: Máxima de N períodos
- **Donchian_Low**: Mínima de N períodos

### 5. Médias Móveis (5 features)
Indicadores de tendência:
- **EMA_9**: Média Móvel Exponencial 9 períodos
- **EMA_20**: Média Móvel Exponencial 20 períodos
- **EMA_50**: Média Móvel Exponencial 50 períodos
- **SMA_20**: Média Móvel Simples 20 períodos
- **SMA_50**: Média Móvel Simples 50 períodos

### 6. Osciladores (2 features)
Indicadores de momentum:
- **Aroon_Spread**: Diferença entre Aroon Up e Aroon Down
- **MACD_Hist**: Histograma do MACD

---

## 🔢 Formato dos Dados

### Input (X) - Features

```
Shape por amostra: (lookback, n_features)
Exemplo com lookback=60: (60, 18)
```

**Interpretação:**
- Cada predição usa uma **janela de 60 timesteps** (30 horas em timeframe 30min)
- Cada timestep tem **18 valores** (uma feature por coluna)
- **Total: 1.080 valores** por predição (60 × 18)

**Exemplo visual de uma amostra:**
```
timestep  Open    High    Low     Volume  BB_High  BB_Mid  ...  MACD_Hist
   t-60   4123    4124    4120    100.5   4200     4100    ...   -0.23
   t-59   4125    4128    4122    105.2   4201     4101    ...   -0.18
   t-58   4127    4130    4125    110.8   4203     4103    ...   -0.12
   ...     ...     ...     ...     ...     ...      ...    ...    ...
   t-2    4200    4205    4198    120.3   4250     4150    ...    0.45
   t-1    4202    4208    4200    125.1   4252     4152    ...    0.52
```

### Output (y) - Target

```
Shape: (1,)
Valor: Close (preço de fechamento no timestep t)
```

**Interpretação:**
- Modelo prevê **1 valor único**: o preço de fechamento **Close**
- Target é o valor em **t** (próximo timestep após a janela de lookback)

---

## 🧠 Arquitetura do Modelo

```
Input: (batch_size, 60, 18)
   ↓
LSTM Layer 1: 64 units (ou configurado)
   ↓
Dropout: 0.3 (30% dropout)
   ↓
LSTM Layer 2: 64 units
   ↓
Dropout: 0.3
   ↓
Dense: 1 output (regressão)
   ↓
Output: (batch_size, 1) → Predição de Close
```

---

## 📊 Estatísticas de Treinamento

Com dataset `BTCUSDT_30m_full.csv`:
- **Total de linhas**: 142.665
- **Período**: 2017-08-19 até 2025-10-14
- **Lookback**: 60 timesteps
- **Samples válidas**: 142.665 - 60 = 142.605

**Split treino/validação (70/30):**
- **Treino**: ~99.800 samples
- **Validação**: ~21.400 samples

**Batch processing:**
- Batch size: 64 (padrão)
- Steps por época: 99.800 / 64 ≈ 1.560 steps

---

## 🔄 Normalização

**Método:** StandardScaler (z-score normalization)

```python
X_scaled = (X - mean) / std
```

**Aplicado a:**
- ✅ Todas as 18 features
- ❌ Target (Close) **não normalizado** no código atual

**Por feature:**
- Cada uma das 18 features é normalizada **independentemente**
- Mean e Std calculados no **conjunto de treino**
- Transform aplicado em **treino e validação** com mesmos parâmetros

---

## 🎯 Predição

### Para Treinar
```python
Input: 60 timesteps × 18 features = 1.080 valores
Output: 1 valor (Close no timestep seguinte)
```

### Para Prever (Inference)
```python
# Mesmo formato que treino
Input: (1, 60, 18)  # 1 amostra, 60 timesteps, 18 features
Output: (1, 1)      # 1 predição de Close
```

**Exemplo de uso:**
```python
# Últimos 60 timesteps do mercado
last_60_candles = df.tail(60)

# Extrair features
X_recent = last_60_candles[feature_cols].values  # Shape: (60, 18)

# Normalizar
X_scaled = scaler.transform(X_recent)

# Reshape para LSTM
X_input = X_scaled.reshape(1, 60, 18)  # Batch de 1 amostra

# Prever
predicted_close = model.predict(X_input)  # Shape: (1, 1)
print(f"Previsão do próximo Close: ${predicted_close[0][0]:.2f}")
```

---

## ⚠️ Limitações Atuais

1. **Target não normalizado**: Close está em escala real (20k-100k), causando loss alto
2. **Sem desnormalização**: Predições estão em escala normalizada (se target fosse normalizado)
3. **Volume zero**: Muitos períodos com Volume=0 (pode causar ruído)

---

## 💡 Melhorias Recomendadas

### 1. Normalizar Target
```python
# Normalizar Close também
scaler_target = StandardScaler()
y_scaled = scaler_target.fit_transform(y.reshape(-1, 1))

# Após predição, desnormalizar
y_pred_original = scaler_target.inverse_transform(y_pred)
```

### 2. Remover Features Redundantes
- BB_Mid é igual a SMA_20 (redundante)
- Considerar remover ou usar apenas uma

### 3. Feature Engineering Adicional
- **RSI**: Relative Strength Index
- **Stochastic**: Oscilador estocástico
- **ATR**: Average True Range (volatilidade)
- **Volume MA**: Média móvel do volume
- **Price Change %**: Variação percentual

### 4. Log Transform para Volume
```python
df['Volume_log'] = np.log1p(df['Volume'])  # log(1 + x) para evitar log(0)
```

---

## 📈 Performance Esperada

Com as 18 features atuais + normalização adequada:

| Métrica | Target (50 épocas) |
|---------|-------------------|
| **MAE** | < 500 USD |
| **RMSE** | < 1000 USD |
| **R²** | > 0.85 |
| **Loss (MSE)** | < 1.000.000 |

**Nota:** Valores atuais estão muito altos devido à falta de normalização do target.

---

## 🔍 Verificar Features no Código

```python
# No arquivo: src/ml_v3_arch/cli.py (linha 135)
feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]

# Resultado: 18 features
# ['Open', 'High', 'Low', 'Volume', 'BB_High', 'BB_Mid', 'BB_Low',
#  'Keltner_High', 'Keltner_Low', 'Donchian_High', 'Donchian_Low',
#  'EMA_9', 'EMA_20', 'EMA_50', 'SMA_20', 'SMA_50', 
#  'Aroon_Spread', 'MACD_Hist']
```

---

**Última atualização:** 2025-10-19  
**Versão do modelo:** v3 (Clean Architecture)
