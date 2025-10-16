# 🔧 Troubleshooting Guide - ML v2

## Erros Comuns e Soluções

---

## ❌ Erro: "Scaler not fitted"

### Mensagem Completa
```
RuntimeError: Scaler not fitted. Call fit() on train split first. 
ZERO VAZAMENTO: fit() só no treino!
```

### Causa
Tentou chamar `transform()` antes de `fit()`.

### Solução
```python
# ❌ ERRADO
preprocessor = DataPreprocessor(feature_cols, target_col="Close")
X, y = preprocessor.transform(df)  # ERRO!

# ✅ CORRETO
preprocessor = DataPreprocessor(feature_cols, target_col="Close")
preprocessor.fit(df_train)  # PRIMEIRO: fit no treino
X, y = preprocessor.transform(df)  # DEPOIS: transform
```

---

## ❌ Erro: "Nenhum modelo encontrado"

### Mensagem
```
❌ Nenhum modelo encontrado! Execute 'train' primeiro.
```

### Causa
Tentou executar `evaluate` ou `backtest` sem modelo treinado.

### Solução
```bash
# 1. Treinar primeiro
python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv

# 2. Depois avaliar
python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv
```

### Verificar Modelos
```powershell
# Windows
ls artifacts/checkpoints/*.keras

# Deve mostrar: lstm_model_YYYYMMDD_HHMMSS.keras
```

---

## ⚠️ Warning: "LSTM NÃO SUPEROU OS BASELINES"

### Mensagem
```
⚠️  ALERTA: LSTM NÃO SUPEROU OS BASELINES!
💡 Considere mudar para CLASSIFICAÇÃO DIRECIONAL.
```

### Causa
MAE do LSTM >= MAE do Naive1 E >= MAE do SMA20.

### Interpretação
O modelo não aprendeu padrões úteis. Está apenas "chutando" próximo à última observação.

### Soluções

#### 1. Revisar Features
```python
# ❌ Usar preços absolutos (não estacionário)
feature_cols = ['Close', 'Open', 'High', 'Low']

# ✅ Usar retornos ou diferenças (estacionário)
df['ret_close'] = df['Close'].pct_change()
df['ret_open'] = df['Open'].pct_change()
feature_cols = ['ret_close', 'ret_open', 'RSI', 'MACD']
```

#### 2. Aumentar Lookback
```bash
# Testar janelas maiores
python src/ml_v2/cli.py train --csv data.csv --lookback 90
python src/ml_v2/cli.py train --csv data.csv --lookback 120
```

#### 3. Adicionar Features de Volatilidade
```python
# ATR%, Bollinger Bands, etc.
df['atr_pct'] = ta.ATR(df['High'], df['Low'], df['Close']) / df['Close']
df['bb_width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
```

#### 4. Pivotar para Classificação
```python
# Em vez de prever Close(t+1), prever direção:
# 0: BAIXA, 1: LATERAL, 2: ALTA

# Labeling adaptativo com ATR
atr_pct = ta.ATR(...) / close
threshold = 0.75 * atr_pct

labels = []
for i in range(len(df)-H):
    ret = (close[i+H] - close[i]) / close[i]
    if ret > threshold[i]:
        labels.append(2)  # ALTA
    elif ret < -threshold[i]:
        labels.append(0)  # BAIXA
    else:
        labels.append(1)  # LATERAL
```

---

## ❌ Erro: ImportError no cli.py

### Mensagem
```
ModuleNotFoundError: No module named 'src.ml_v2'
```

### Causa
Python não encontrou o módulo no PYTHONPATH.

### Solução 1: Executar da raiz do projeto
```bash
# ❌ ERRADO (dentro de ml_v2/)
cd src/ml_v2
python cli.py train --csv ../../data/BTCUSDT_30m_full.csv

# ✅ CORRETO (raiz do projeto)
cd c:\_Dev\Github\Python\Mercado_Financeiro\RN_Operar_Cripto
python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
```

### Solução 2: Adicionar ao PYTHONPATH
```powershell
# Windows PowerShell
$env:PYTHONPATH = "c:\_Dev\Github\Python\Mercado_Financeiro\RN_Operar_Cripto"
python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
```

---

## ❌ Erro: TensorFlow GPU não detectada

### Mensagem
```
Could not load dynamic library 'cudart64_110.dll'
```

### Causa
CUDA não instalado ou versão incompatível.

### Solução 1: Usar CPU
```python
# TensorFlow automaticamente usa CPU se GPU não disponível
# Performance: ~2-3x mais lento, mas funciona
```

### Solução 2: Instalar CUDA
```bash
# Verificar versão TensorFlow
python -c "import tensorflow as tf; print(tf.__version__)"

# TensorFlow 2.13 requer:
# - CUDA 11.8
# - cuDNN 8.6

# Download: https://developer.nvidia.com/cuda-toolkit
```

### Solução 3: Forçar CPU
```python
# No início do cli.py
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Força CPU
```

---

## ⚠️ Warning: Overfitting Detectado

### Sintomas
```
Epoch 50/50
train_loss: 0.0012 - train_mae: 0.0234
val_loss: 0.0089 - val_mae: 0.0678
```

`val_loss >> train_loss` → Overfitting!

### Soluções

#### 1. Aumentar Dropout
```python
# Em models/lstm_model.py
x = keras.layers.Dropout(0.4)(x)  # Era 0.2, aumentar para 0.4-0.5
```

#### 2. Reduzir Complexidade
```python
# Menos neurônios
x = keras.layers.LSTM(32, return_sequences=True)(inputs)  # Era 64
x = keras.layers.LSTM(16)(x)  # Era 32
```

#### 3. Aumentar Paciência
```bash
python src/ml_v2/cli.py train --csv data.csv --patience 15
```

#### 4. Adicionar Regularização L2
```python
from tensorflow.keras import regularizers

x = keras.layers.Dense(
    32, 
    kernel_regularizer=regularizers.l2(0.01)
)(x)
```

---

## ❌ Erro: Out of Memory (OOM)

### Mensagem
```
ResourceExhaustedError: OOM when allocating tensor
```

### Causa
Batch size muito grande ou modelo muito profundo.

### Soluções

#### 1. Reduzir Batch Size
```bash
python src/ml_v2/cli.py train --csv data.csv --batch-size 16  # Era 32
```

#### 2. Reduzir Lookback
```bash
python src/ml_v2/cli.py train --csv data.csv --lookback 40  # Era 60
```

#### 3. Usar Gradient Accumulation
```python
# Em models/lstm_model.py
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate, clipnorm=1.0),  # Clip gradients
    ...
)
```

#### 4. Liberar Memória GPU
```python
import tensorflow as tf

# Crescimento dinâmico de memória
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

---

## ⚠️ Warning: Underfitting

### Sintomas
```
train_loss: 0.0234 - train_mae: 0.1123
val_loss: 0.0267 - val_mae: 0.1201
```

Ambas as losses altas, próximas → Underfitting.

### Soluções

#### 1. Aumentar Capacidade
```python
# Mais neurônios
x = keras.layers.LSTM(128, return_sequences=True)(inputs)  # Era 64
x = keras.layers.LSTM(64)(x)  # Era 32
```

#### 2. Mais Épocas
```bash
python src/ml_v2/cli.py train --csv data.csv --epochs 100
```

#### 3. Learning Rate Maior
```bash
python src/ml_v2/cli.py train --csv data.csv --lr 0.003
```

#### 4. Adicionar Features
```python
# Mais indicadores técnicos
df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'])
df['CCI'] = ta.CCI(df['High'], df['Low'], df['Close'])
df['MOM'] = ta.MOM(df['Close'])
```

---

## ❌ Erro: ValueError no shape

### Mensagem
```
ValueError: Input 0 of layer "lstm_1" is incompatible with the layer: 
expected ndim=3, found ndim=2
```

### Causa
Shape das sequências LSTM incorreto.

### Diagnóstico
```python
print(X_train.shape)  # Deve ser (n_samples, lookback, n_features)
# Exemplo: (5000, 60, 10)
```

### Solução
```python
# Verificar preprocessamento
X_train, y_train = preprocessor.transform(df_train)
assert X_train.ndim == 3, "X deve ter 3 dimensões!"
assert X_train.shape[1] == preprocessor.lookback
```

---

## ⚠️ Warning: Convergência Lenta

### Sintomas
```
Epoch 1/50: val_loss: 0.0234
Epoch 10/50: val_loss: 0.0231
Epoch 20/50: val_loss: 0.0230
...
```

Loss caindo muito devagar.

### Soluções

#### 1. Aumentar Learning Rate
```bash
python src/ml_v2/cli.py train --csv data.csv --lr 0.003  # Era 0.001
```

#### 2. Usar Learning Rate Scheduler
```python
# Em models/lstm_model.py
callbacks.append(
    keras.callbacks.LearningRateScheduler(
        lambda epoch: 1e-3 * 0.95 ** epoch
    )
)
```

#### 3. Normalização Diferente
```python
# Testar StandardScaler em vez de MinMaxScaler
from sklearn.preprocessing import StandardScaler

self.scaler_X = StandardScaler()  # Em vez de MinMaxScaler()
```

---

## 🔍 Debugging Tips

### 1. Ativar Verbose
```bash
# Treino
python src/ml_v2/cli.py train --csv data.csv  # verbose=1 por padrão

# Walk-forward
python src/ml_v2/cli.py walkforward --csv data.csv --folds 3 --verbose
```

### 2. Inspecionar Dados
```python
# Verificar shapes
print(f"X_train: {X_train.shape}")
print(f"y_train: {y_train.shape}")

# Verificar ranges (após desnormalização)
print(f"y_true range: {y_true_usd.min():.2f} - {y_true_usd.max():.2f}")

# Verificar NaN
print(f"NaN em features: {df[feature_cols].isna().sum().sum()}")
```

### 3. Visualizar Predições
```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(y_true_usd[:200], label='True', alpha=0.7)
plt.plot(y_pred_usd[:200], label='LSTM', alpha=0.7)
plt.legend()
plt.title('Primeiras 200 predições')
plt.show()
```

### 4. Testar com Dataset Pequeno
```python
# Criar mini-dataset para debug rápido
df_mini = df.iloc[:1000].copy()
# Treinar rapidamente
```

---

## 📞 Suporte

### Se nada funcionar:

1. **Verificar instalação**
   ```bash
   pip list | grep -E "tensorflow|numpy|pandas|scikit-learn"
   ```

2. **Rodar testes**
   ```bash
   pytest src/ml_v2/tests/ -v
   ```

3. **Checar logs**
   ```bash
   cat artifacts/logs/history_*.json
   ```

4. **Gerar relatório completo**
   ```bash
   python src/ml_v2/examples.py > debug_report.txt 2>&1
   ```

---

**Última atualização:** 2025-10-16  
**Para mais ajuda:** Ver `README.md` e `QUICK_REFERENCE.md`
