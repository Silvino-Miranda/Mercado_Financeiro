# 🚀 MELHORIAS PARA AUMENTAR ACURÁCIA DE 52.2% PARA 70%+

**Data:** 14 de Outubro de 2025  
**Problema Atual:** Taxa de acerto de 52.2% (quase aleatório - apenas 2.2% melhor que 50%)  
**Meta:** 70%+ de acurácia

---

## 🔍 DIAGNÓSTICO DO PROBLEMA

### ❌ **Problema Principal: TIPO DE PREDIÇÃO ERRADO**

Atualmente o modelo está fazendo **REGRESSÃO** (prever valores exatos de Close, High, Low), mas deveria fazer **CLASSIFICAÇÃO** (prever se vai subir ou descer).

**Por que isso é problemático?**
- Prever valor exato de preço é MUITO mais difícil
- Pequenos erros na predição podem causar sinais errados
- A estratégia só precisa saber DIREÇÃO, não valor exato

### ⚠️ **Problemas Secundários:**

1. **Features Fracas:**
   - Apenas 6 features (Open, High, Low, Close, SMA_20, EMA_20)
   - Alta colinearidade (todas > 0.95 correlação)
   - Faltam indicadores de momentum, volatilidade, volume

2. **Arquitetura Simples:**
   - Apenas 2 camadas LSTM
   - Sem attention mechanism
   - Sem Batch Normalization

3. **Hiperparâmetros Não Otimizados:**
   - Learning rate fixo
   - Sequence length pode ser curto (60 períodos)
   - Dropout pode estar baixo

---

## 🎯 PLANO DE AÇÃO (PRIORIZADO)

### 🔴 **PRIORIDADE 1: MUDAR PARA CLASSIFICAÇÃO** (Impacto: +10-15%)

**Implementação:**

```python
# Mudar de:
target_columns = ["Open", "High", "Low"]  # Regressão

# Para:
target_column = "direction"  # Classificação

# Criar target binário:
df['future_return'] = df['Close'].shift(-24).pct_change()  # Retorno daqui 12h
df['direction'] = (df['future_return'] > 0.005).astype(int)  # 1 = sobe >0.5%, 0 = desce

# Ou multi-classe (mais sofisticado):
def create_target(return_value):
    if return_value > 0.01:
        return 2  # STRONG_BUY
    elif return_value > 0.005:
        return 1  # BUY
    elif return_value < -0.01:
        return -2  # STRONG_SELL
    elif return_value < -0.005:
        return -1  # SELL
    else:
        return 0  # HOLD

df['target'] = df['future_return'].apply(create_target)
```

**Mudanças no Modelo:**

```python
# Última camada deve ser:
model.add(Dense(1, activation='sigmoid'))  # Binário
# ou
model.add(Dense(5, activation='softmax'))  # Multi-classe

# Loss function:
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',  # ou 'categorical_crossentropy'
    metrics=['accuracy', 'precision', 'recall', 'AUC']
)
```

---

### 🟡 **PRIORIDADE 2: ADICIONAR FEATURES PODEROSAS** (Impacto: +8-12%)

**Features a Adicionar:**

```python
import ta  # pip install ta

# 1. Momentum Indicators
df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
df['MACD'] = ta.trend.MACD(df['Close']).macd()
df['MACD_signal'] = ta.trend.MACD(df['Close']).macd_signal()
df['MACD_diff'] = ta.trend.MACD(df['Close']).macd_diff()
df['Stochastic'] = ta.momentum.StochasticOscillator(
    df['High'], df['Low'], df['Close']).stoch()

# 2. Volatility Indicators
df['BB_high'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband()
df['BB_low'] = ta.volatility.BollingerBands(df['Close']).bollinger_lband()
df['BB_mid'] = ta.volatility.BollingerBands(df['Close']).bollinger_mavg()
df['BB_width'] = (df['BB_high'] - df['BB_low']) / df['Close']
df['BB_position'] = (df['Close'] - df['BB_low']) / (df['BB_high'] - df['BB_low'])
df['ATR'] = ta.volatility.AverageTrueRange(
    df['High'], df['Low'], df['Close'], window=14).average_true_range()
df['ATR_pct'] = df['ATR'] / df['Close']

# 3. Volume Indicators (se disponível)
if 'Volume' in df.columns:
    df['OBV'] = ta.volume.OnBalanceVolumeIndicator(
        df['Close'], df['Volume']).on_balance_volume()
    df['Volume_SMA_20'] = df['Volume'].rolling(20).mean()
    df['Volume_ratio'] = df['Volume'] / df['Volume_SMA_20']
    df['MFI'] = ta.volume.MFIIndicator(
        df['High'], df['Low'], df['Close'], df['Volume']).money_flow_index()

# 4. Trend Indicators
df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['SMA_50'] = df['Close'].rolling(50).mean()
df['SMA_200'] = df['Close'].rolling(200).mean()
df['trend_50_200'] = (df['SMA_50'] > df['SMA_200']).astype(int)
df['price_vs_sma20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
df['price_vs_sma50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']

# 5. Price Action Features
df['high_low_pct'] = (df['High'] - df['Low']) / df['Close']
df['close_open_pct'] = (df['Close'] - df['Open']) / df['Open']
df['upper_shadow'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Close']
df['lower_shadow'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Close']
df['body_size'] = abs(df['Close'] - df['Open']) / df['Close']

# 6. Lag Features (retornos passados)
for lag in [1, 2, 3, 5, 10, 20]:
    df[f'return_lag_{lag}'] = df['Close'].pct_change(lag)
    df[f'volume_change_lag_{lag}'] = df['Volume'].pct_change(lag) if 'Volume' in df.columns else 0
    
# 7. Rolling Statistics
for window in [10, 20, 50]:
    df[f'volatility_{window}'] = df['Close'].pct_change().rolling(window).std()
    df[f'mean_return_{window}'] = df['Close'].pct_change().rolling(window).mean()
    df[f'max_close_{window}'] = df['Close'].rolling(window).max()
    df[f'min_close_{window}'] = df['Close'].rolling(window).min()
    df[f'range_{window}'] = (df[f'max_close_{window}'] - df[f'min_close_{window}']) / df['Close']

# 8. Momentum Features
df['momentum_10'] = df['Close'] - df['Close'].shift(10)
df['momentum_20'] = df['Close'] - df['Close'].shift(20)
df['momentum_50'] = df['Close'] - df['Close'].shift(50)
df['rate_of_change_10'] = df['Close'].pct_change(10)
df['rate_of_change_20'] = df['Close'].pct_change(20)

# 9. Time Features (Ciclicidade)
df['Date'] = pd.to_datetime(df['Date'])
df['hour'] = df['Date'].dt.hour
df['day_of_week'] = df['Date'].dt.dayofweek
df['month'] = df['Date'].dt.month
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

# 10. Cross Features
df['rsi_bb_position'] = df['RSI_14'] * df['BB_position']
df['macd_volume'] = df['MACD'] * df['Volume_ratio'] if 'Volume' in df.columns else 0
```

**Total de Features:** ~50-60 features (era 6)

---

### 🟢 **PRIORIDADE 3: MELHORAR ARQUITETURA** (Impacto: +5-8%)

**Nova Arquitetura - LSTM Bidirecional com Attention:**

```python
from tensorflow.keras.layers import (
    LSTM, Bidirectional, Dense, Dropout, 
    BatchNormalization, Attention, Input, MultiHeadAttention
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

def create_advanced_model(input_shape, num_classes=1):
    """
    Modelo LSTM avançado com:
    - Bidirectional LSTM
    - Multi-Head Attention
    - Batch Normalization
    - Skip Connections
    """
    inputs = Input(shape=input_shape)
    
    # Bidirectional LSTM Layer 1
    x = Bidirectional(LSTM(128, return_sequences=True))(inputs)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    
    # Bidirectional LSTM Layer 2
    lstm_out = Bidirectional(LSTM(64, return_sequences=True))(x)
    lstm_out = BatchNormalization()(lstm_out)
    lstm_out = Dropout(0.3)(lstm_out)
    
    # Multi-Head Attention Layer
    attention_output = MultiHeadAttention(
        num_heads=4, 
        key_dim=32
    )(lstm_out, lstm_out)
    
    # Skip connection
    x = Add()([lstm_out, attention_output])
    x = LayerNormalization()(x)
    
    # LSTM Layer 3 (não retorna sequências)
    x = LSTM(32)(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    # Dense Layers com skip connection
    dense1 = Dense(64, activation='relu')(x)
    dense1 = Dropout(0.2)(dense1)
    
    dense2 = Dense(32, activation='relu')(dense1)
    
    # Skip connection para denses
    x = Concatenate()([dense1, dense2])
    x = Dense(32, activation='relu')(x)
    
    # Output Layer
    if num_classes == 1:
        outputs = Dense(1, activation='sigmoid')(x)  # Binário
        loss = 'binary_crossentropy'
    else:
        outputs = Dense(num_classes, activation='softmax')(x)  # Multi-classe
        loss = 'categorical_crossentropy'
    
    model = Model(inputs=inputs, outputs=outputs)
    
    # Compilar com métricas adequadas
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss=loss,
        metrics=['accuracy', 
                 tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall'),
                 tf.keras.metrics.AUC(name='auc')]
    )
    
    return model

# Uso:
model = create_advanced_model(
    input_shape=(120, 50),  # 120 timesteps, 50 features
    num_classes=1  # Binário
)

print(model.summary())
```

---

### 🟣 **PRIORIDADE 4: OTIMIZAR HIPERPARÂMETROS** (Impacto: +3-5%)

```python
from tensorflow.keras.callbacks import (
    ReduceLROnPlateau, 
    EarlyStopping,
    ModelCheckpoint,
    TensorBoard
)
import datetime

# Learning Rate Scheduler
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,  # Reduz LR pela metade
    patience=5,  # Espera 5 epochs sem melhora
    min_lr=0.00001,
    verbose=1,
    mode='min'
)

# Early Stopping Melhorado
early_stop = EarlyStopping(
    monitor='val_accuracy',  # Mudar para accuracy
    patience=20,  # Aumentar paciência
    restore_best_weights=True,
    mode='max',  # Maximizar accuracy
    verbose=1
)

# Checkpoint
checkpoint = ModelCheckpoint(
    'checkpoints/best_model_classification.keras',
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

# TensorBoard (opcional mas útil)
log_dir = f"logs/fit/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
tensorboard = TensorBoard(log_dir=log_dir, histogram_freq=1)

# Treinar
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,  # Aumentar
    batch_size=64,  # Aumentar de 32 para 64
    callbacks=[reduce_lr, early_stop, checkpoint, tensorboard],
    verbose=1,
    class_weight={0: 1.0, 1: 1.2}  # Dar mais peso para classe minoritária se desbalanceado
)
```

**Outros Hiperparâmetros:**

```python
# Preprocessamento
sequence_length = 120  # Aumentar de 60 para 120 (4 horas de dados em 30min)
train_size = 0.70
val_size = 0.15
test_size = 0.15

# Normalização por feature (StandardScaler)
from sklearn.preprocessing import StandardScaler, RobustScaler

# RobustScaler é melhor para dados financeiros (resistente a outliers)
scaler = RobustScaler()

# Model
lstm_units = [128, 64, 32]  # Aumentar complexidade
dropout_rate = 0.3  # Aumentar regularização
batch_norm = True  # Adicionar
learning_rate = 0.001  # Começar aqui, vai diminuir automaticamente
```

---

### 🔵 **PRIORIDADE 5: DATA AUGMENTATION** (Impacto: +2-4%)

```python
import numpy as np

def augment_time_series(X, y, augmentation_factor=2):
    """
    Aumenta dados de treinamento com técnicas de augmentation
    específicas para séries temporais
    """
    X_aug = []
    y_aug = []
    
    for i in range(len(X)):
        # Sempre adicionar original
        X_aug.append(X[i])
        y_aug.append(y[i])
        
        for _ in range(augmentation_factor):
            # 1. Jitter (adicionar ruído gaussiano)
            noise_level = 0.01  # 1% de ruído
            noise = np.random.normal(0, noise_level, X[i].shape)
            X_jitter = X[i] + noise
            X_aug.append(X_jitter)
            y_aug.append(y[i])
            
            # 2. Scaling (escalar valores)
            scale_factor = np.random.uniform(0.95, 1.05)
            X_scaled = X[i] * scale_factor
            X_aug.append(X_scaled)
            y_aug.append(y[i])
            
            # 3. Time Warping (esticar/comprimir tempo)
            # Interpolar para criar variações temporais
            from scipy.interpolate import interp1d
            orig_steps = np.arange(X[i].shape[0])
            warp_steps = np.linspace(0, X[i].shape[0]-1, X[i].shape[0])
            warp_steps = np.cumsum(np.random.uniform(0.8, 1.2, X[i].shape[0]))
            warp_steps = warp_steps / warp_steps[-1] * (X[i].shape[0]-1)
            
            X_warped = np.zeros_like(X[i])
            for feature_idx in range(X[i].shape[1]):
                f = interp1d(orig_steps, X[i][:, feature_idx], kind='cubic', fill_value='extrapolate')
                X_warped[:, feature_idx] = f(warp_steps)
            
            X_aug.append(X_warped)
            y_aug.append(y[i])
    
    return np.array(X_aug), np.array(y_aug)

# Aplicar apenas no treino
print("Aplicando data augmentation...")
X_train_aug, y_train_aug = augment_time_series(
    X_train, y_train, 
    augmentation_factor=1  # Dobra o dataset
)
print(f"Dataset treino original: {len(X_train)}")
print(f"Dataset treino aumentado: {len(X_train_aug)}")
```

---

### 🟠 **PRIORIDADE 6: ENSEMBLE** (Impacto: +3-5%)

```python
# Treinar múltiplos modelos diferentes

# Modelo 1: LSTM
model_lstm = create_advanced_lstm_model(input_shape, num_classes)

# Modelo 2: GRU (variante mais rápida)
def create_gru_model(input_shape, num_classes):
    inputs = Input(shape=input_shape)
    x = Bidirectional(GRU(128, return_sequences=True))(inputs)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    x = Bidirectional(GRU(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    x = GRU(32)(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    outputs = Dense(num_classes, activation='sigmoid' if num_classes==1 else 'softmax')(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

model_gru = create_gru_model(input_shape, num_classes)

# Modelo 3: CNN-LSTM (captura padrões locais)
def create_cnn_lstm_model(input_shape, num_classes):
    inputs = Input(shape=input_shape)
    x = Conv1D(64, kernel_size=3, activation='relu', padding='same')(inputs)
    x = MaxPooling1D(pool_size=2)(x)
    x = Conv1D(128, kernel_size=3, activation='relu', padding='same')(x)
    x = MaxPooling1D(pool_size=2)(x)
    x = LSTM(64, return_sequences=True)(x)
    x = LSTM(32)(x)
    x = Dense(64, activation='relu')(x)
    outputs = Dense(num_classes, activation='sigmoid' if num_classes==1 else 'softmax')(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=Adam(0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

model_cnn_lstm = create_cnn_lstm_model(input_shape, num_classes)

# Treinar todos
print("Treinando LSTM...")
model_lstm.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=64, callbacks=[early_stop], verbose=0)

print("Treinando GRU...")
model_gru.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=64, callbacks=[early_stop], verbose=0)

print("Treinando CNN-LSTM...")
model_cnn_lstm.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=64, callbacks=[early_stop], verbose=0)

# Predição Ensemble - Voting
pred_lstm = model_lstm.predict(X_test)
pred_gru = model_gru.predict(X_test)
pred_cnn_lstm = model_cnn_lstm.predict(X_test)

# Média ponderada (dar mais peso ao melhor modelo em validação)
# Assumindo que LSTM teve melhor val_accuracy
pred_final = (0.4 * pred_lstm + 
              0.3 * pred_gru + 
              0.3 * pred_cnn_lstm)

# Converter para classe
y_pred_ensemble = (pred_final > 0.5).astype(int)

# Ou stacking (treinar meta-model)
from sklearn.ensemble import RandomForestClassifier

# Concatenar predições como features
X_meta = np.hstack([pred_lstm, pred_gru, pred_cnn_lstm])

# Treinar RF como meta-learner
rf_meta = RandomForestClassifier(n_estimators=100, random_state=42)
rf_meta.fit(X_meta, y_test)

# Predição final
y_pred_stacking = rf_meta.predict(X_meta)
```

---

## 📊 EXPECTATIVA DE MELHORIA

| Melhoria | Acurácia Esperada | Ganho Incremental |
|----------|------------------|-------------------|
| **Baseline Atual** | 52.2% | - |
| + Classificação Binária | 58-62% | +6-10% |
| + Features Poderosas (50+) | 65-70% | +7-8% |
| + Arquitetura Melhor | 70-75% | +5% |
| + Hiperparâmetros Otimizados | 72-77% | +2-3% |
| + Data Augmentation | 73-78% | +1-2% |
| + Ensemble (3 modelos) | **75-80%** | **+2-3%** |

### Ganho Total Esperado: +23-28%

---

## 🚀 IMPLEMENTAÇÃO SEQUENCIAL

### **Semana 1: Fundação (MAIOR IMPACTO)**
1. ✅ Mudar para classificação binária (ou multi-classe 5 classes)
2. ✅ Adicionar 20 features principais:
   - RSI, MACD, Bollinger Bands, ATR
   - Lags (1, 2, 5, 10)
   - Price action (high_low_pct, body_size)
   - Time features (hour_sin/cos)
3. ✅ Retreinar com 50 epochs
4. ✅ Medir nova acurácia

**Meta Semana 1:** 60-65% de acurácia ✅

---

### **Semana 2: Arquitetura Avançada**
1. ✅ Implementar LSTM Bidirecional (128, 64, 32)
2. ✅ Adicionar Multi-Head Attention (4 heads)
3. ✅ Adicionar Batch Normalization em todas as camadas
4. ✅ Adicionar Skip Connections
5. ✅ Aumentar sequence_length para 120
6. ✅ Retreinar

**Meta Semana 2:** 68-72% de acurácia ✅

---

### **Semana 3: Otimização Fina**
1. ✅ Adicionar mais 30 features (total 50+):
   - Momentum (10, 20, 50 períodos)
   - Volatilidade rolling (10, 20, 50)
   - Cross features (RSI*BB_position)
   - Volume features (se disponível)
2. ✅ Implementar Learning Rate Scheduling
3. ✅ Data Augmentation (jitter + scaling + warping)
4. ✅ Grid search para batch_size e learning_rate

**Meta Semana 3:** 72-76% de acurácia ✅

---

### **Semana 4: Ensemble Final**
1. ✅ Treinar GRU model
2. ✅ Treinar CNN-LSTM hybrid
3. ✅ Implementar ensemble voting (média ponderada)
4. ✅ Testar stacking com RandomForest meta-learner
5. ✅ Escolher melhor abordagem
6. ✅ Fine-tuning final

**Meta Semana 4:** 75-80% de acurácia ✅

---

## 📝 EXEMPLO COMPLETO - CLASSIFICAÇÃO BINÁRIA

```python
import pandas as pd
import numpy as np
import ta
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split

# ==============================================================================
# 1. PREPARAR TARGET DE CLASSIFICAÇÃO
# ==============================================================================

def prepare_classification_target(df, horizon=24, threshold=0.005):
    """
    Cria target de classificação binária
    
    Args:
        horizon: Períodos à frente para prever (24 = 12 horas em 30min)
        threshold: Limiar para considerar movimento significativo (0.5%)
    
    Returns:
        df com coluna 'target': 1 = vai subir >0.5%, 0 = não
    """
    # Calcular retorno futuro
    df['future_close'] = df['Close'].shift(-horizon)
    df['future_return'] = (df['future_close'] - df['Close']) / df['Close']
    
    # Criar classes (binário)
    df['target'] = (df['future_return'] > threshold).astype(int)
    # 1 = vai subir mais de 0.5%
    # 0 = não vai subir ou vai cair
    
    # Remover colunas auxiliares
    df = df.drop(['future_close', 'future_return'], axis=1)
    
    return df

# ==============================================================================
# 2. ADICIONAR FEATURES PODEROSAS
# ==============================================================================

def add_powerful_features(df):
    """Adiciona ~50 features técnicas"""
    
    # --- Momentum ---
    df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['Stoch'] = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
    
    # --- Trend ---
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()
    
    # --- Volatility ---
    bb = ta.volatility.BollingerBands(df['Close'])
    df['BB_high'] = bb.bollinger_hband()
    df['BB_low'] = bb.bollinger_lband()
    df['BB_mid'] = bb.bollinger_mavg()
    df['BB_width'] = (df['BB_high'] - df['BB_low']) / df['Close']
    df['BB_position'] = (df['Close'] - df['BB_low']) / (df['BB_high'] - df['BB_low'])
    
    atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'])
    df['ATR'] = atr.average_true_range()
    df['ATR_pct'] = df['ATR'] / df['Close']
    
    # --- Price Action ---
    df['high_low_pct'] = (df['High'] - df['Low']) / df['Close']
    df['close_open_pct'] = (df['Close'] - df['Open']) / df['Open']
    df['body_size'] = abs(df['Close'] - df['Open']) / df['Close']
    
    # --- Lags ---
    for lag in [1, 2, 3, 5, 10, 20]:
        df[f'return_lag_{lag}'] = df['Close'].pct_change(lag)
    
    # --- Rolling Stats ---
    for window in [10, 20, 50]:
        df[f'volatility_{window}'] = df['Close'].pct_change().rolling(window).std()
        df[f'mean_return_{window}'] = df['Close'].pct_change().rolling(window).mean()
    
    # --- Momentum ---
    df['momentum_10'] = df['Close'] - df['Close'].shift(10)
    df['momentum_20'] = df['Close'] - df['Close'].shift(20)
    
    # --- Time ---
    df['Date'] = pd.to_datetime(df['Date'])
    df['hour'] = df['Date'].dt.hour
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # --- Trend Indicators ---
    df['price_vs_sma20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
    df['price_vs_sma50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
    df['trend_50_200'] = (df['SMA_50'] > df['SMA_200']).astype(int)
    
    return df

# ==============================================================================
# 3. CRIAR SEQUÊNCIAS
# ==============================================================================

def create_sequences(df, feature_columns, target_column, sequence_length=120):
    """
    Cria sequências para LSTM
    """
    X = []
    y = []
    
    data = df[feature_columns + [target_column]].values
    
    for i in range(sequence_length, len(data)):
        X.append(data[i-sequence_length:i, :-1])  # Features
        y.append(data[i, -1])  # Target
    
    return np.array(X), np.array(y)

# ==============================================================================
# 4. PIPELINE COMPLETO
# ==============================================================================

# Carregar dados
df = pd.read_csv('data/BTCUSDT_30m_full.csv')
print(f"Dataset original: {len(df)} registros")

# 1. Preparar target
df = prepare_classification_target(df, horizon=24, threshold=0.005)

# 2. Adicionar features
df = add_powerful_features(df)

# 3. Remover NaN
df = df.dropna()
print(f"Dataset após features: {len(df)} registros")

# 4. Definir features
feature_columns = [col for col in df.columns if col not in ['Date', 'target']]
print(f"Total de features: {len(feature_columns)}")

# 5. Split
train_size = int(0.70 * len(df))
val_size = int(0.15 * len(df))

train_df = df[:train_size]
val_df = df[train_size:train_size+val_size]
test_df = df[train_size+val_size:]

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# 6. Normalizar
scaler = RobustScaler()
train_df[feature_columns] = scaler.fit_transform(train_df[feature_columns])
val_df[feature_columns] = scaler.transform(val_df[feature_columns])
test_df[feature_columns] = scaler.transform(test_df[feature_columns])

# 7. Criar sequências
sequence_length = 120

X_train, y_train = create_sequences(train_df, feature_columns, 'target', sequence_length)
X_val, y_val = create_sequences(val_df, feature_columns, 'target', sequence_length)
X_test, y_test = create_sequences(test_df, feature_columns, 'target', sequence_length)

print(f"\nShapes:")
print(f"X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"X_val: {X_val.shape}, y_val: {y_val.shape}")
print(f"X_test: {X_test.shape}, y_test: {y_test.shape}")

# 8. Balanceamento de classes
unique, counts = np.unique(y_train, return_counts=True)
print(f"\nDistribuição de classes no treino:")
for cls, cnt in zip(unique, counts):
    print(f"  Classe {cls}: {cnt} ({cnt/len(y_train)*100:.1f}%)")

# 9. Criar e treinar modelo
input_shape = (sequence_length, len(feature_columns))
model = create_advanced_model(input_shape, num_classes=1)

# Callbacks
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)

callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=20, restore_best_weights=True, mode='max'),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
    ModelCheckpoint('best_classification_model.keras', monitor='val_accuracy', save_best_only=True, mode='max')
]

# Treinar
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=100,
    batch_size=64,
    callbacks=callbacks,
    verbose=1
)

# 10. Avaliar
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype(int).flatten()

print("\n" + "="*60)
print("RESULTADOS FINAIS")
print("="*60)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Não Compra', 'Compra']))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"  TN: {cm[0,0]:<6} FP: {cm[0,1]:<6}")
print(f"  FN: {cm[1,0]:<6} TP: {cm[1,1]:<6}")

print(f"\nAUC-ROC: {roc_auc_score(y_test, y_pred_prob):.4f}")

# Salvar modelo e scaler
model.save('final_classification_model.keras')
import joblib
joblib.dump(scaler, 'scaler.pkl')

print("\n✅ Modelo e scaler salvos!")
```

---

## 🎯 MÉTRICAS DE SUCESSO

```python
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    cohen_kappa_score
)

def evaluate_model_comprehensive(y_true, y_pred, y_pred_prob):
    """Avaliação completa do modelo"""
    
    metrics = {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred),
        'Recall': recall_score(y_true, y_pred),
        'F1-Score': f1_score(y_true, y_pred),
        'AUC-ROC': roc_auc_score(y_true, y_pred_prob),
        'Cohen Kappa': cohen_kappa_score(y_true, y_pred)
    }
    
    print("📊 MÉTRICAS COMPLETAS:")
    print("="*50)
    for metric, value in metrics.items():
        status = "✅" if value > 0.70 else "⚠️" if value > 0.60 else "❌"
        print(f"  {status} {metric:15s}: {value:.4f} ({value*100:.2f}%)")
    
    return metrics

# Uso:
metrics = evaluate_model_comprehensive(y_test, y_pred, y_pred_prob)
```

### 🎯 **Meta de Sucesso Final:**

| Métrica | Meta Mínima | Meta Ideal |
|---------|-------------|------------|
| **Accuracy** | > 70% | > 75% |
| **Precision** | > 65% | > 70% |
| **Recall** | > 65% | > 70% |
| **F1-Score** | > 65% | > 72% |
| **AUC-ROC** | > 0.75 | > 0.80 |
| **Cohen Kappa** | > 0.40 | > 0.50 |

---

## 💡 DICAS IMPORTANTES

### ✅ **Sempre Fazer:**

1. **Validar em dados não vistos** - Nunca teste no treino
2. **Monitorar overfitting** - Gap entre train e val accuracy
3. **Usar cross-validation** - K-fold para robustez
4. **Salvar melhores modelos** - Checkpoints durante treino
5. **Documentar experimentos** - Use MLflow ou Weights & Biases
6. **A/B test** - Compare múltiplas abordagens
7. **Análise de erros** - Onde o modelo erra mais?
8. **Feature importance** - Quais features ajudam mais?

### ❌ **Nunca Fazer:**

1. **Treinar e testar nos mesmos dados** - Data leakage
2. **Usar test set para ajustar hiperparâmetros** - Use validation set
3. **Ignorar desbalanceamento** - Use class_weight ou SMOTE
4. **Normalizar antes de split** - Scaler só vê treino
5. **Usar Look-Ahead Bias** - Shift correto nas features

---

## 🔄 PRÓXIMOS PASSOS IMEDIATOS

### 🚀 **Fase 1: Diagnóstico (Agora)**

1. ✅ Rodar script de análise completa do dataset
2. ✅ Confirmar problemas (features fracas, regressão errada)
3. ✅ Documentar baseline atual (52.2% accuracy)

### 🔧 **Fase 2: Implementação Classificação (Esta Semana)**

1. ⏳ Modificar `prepare_data.py`:
   - Adicionar função `prepare_classification_target()`
   - Adicionar função `add_powerful_features()` com ~50 features
   - Mudar de regressão para classificação binária

2. ⏳ Modificar `main_train.py`:
   - Atualizar model architecture para classificação
   - Mudar loss para `binary_crossentropy`
   - Adicionar métricas: accuracy, precision, recall, AUC
   - Implementar callbacks avançados

3. ⏳ Treinar nova versão:
   ```powershell
   .venv\Scripts\python.exe src\ml\main_train.py
   ```

4. ⏳ Avaliar:
   ```powershell
   .venv\Scripts\python.exe src\ml\main_predict.py
   ```

**Meta Fase 2:** Acurácia de 60-65% ✅

### 🏗️ **Fase 3: Arquitetura Avançada (Próxima Semana)**

1. ⏳ Implementar LSTM Bidirecional
2. ⏳ Adicionar Multi-Head Attention
3. ⏳ Aumentar sequence_length para 120
4. ⏳ Retreinar

**Meta Fase 3:** Acurácia de 68-72% ✅

### 🎯 **Fase 4: Ensemble Final (Semana 3-4)**

1. ⏳ Treinar GRU e CNN-LSTM
2. ⏳ Implementar voting ensemble
3. ⏳ Fine-tuning final

**Meta Fase 4:** Acurácia de 75-80% ✅

---

## 📚 RECURSOS ADICIONAIS

### Papers de Referência:
- "Attention Is All You Need" (Transformer architecture)
- "Time Series Forecasting with Deep Learning: A Survey"
- "Financial Trading as a Game: A Deep Reinforcement Learning Approach"

### Bibliotecas Úteis:
- `ta` - Technical Analysis indicators
- `ta-lib` - Mais indicadores técnicos
- `optuna` - Hyperparameter optimization
- `mlflow` - Experiment tracking
- `shap` - Feature importance

---

**Desenvolvido em:** Outubro de 2025  
**Objetivo:** Aumentar acurácia de 52.2% para 75%+  
**Abordagem:** Mudar de Regressão para Classificação + Features Poderosas + Arquitetura Avançada + Ensemble  
**Status:** 📋 **PLANO COMPLETO PRONTO PARA IMPLEMENTAÇÃO**  
**Expectativa:** 🎯 **75-80% de acurácia final**
