"""
Teste simplificado da v3 - bypass CLI
"""
import sys
import time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

print("="*80)
print("TESTE SIMPLIFICADO V3")
print("="*80)

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 1. Importar componentes
print("\n1️⃣ Importando componentes v3...")
start = time.time()

from ml_v3_arch.domain import ModelConfig, DataConfig
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.infrastructure import DataLoader

print(f"   ✅ Imports OK ({time.time()-start:.2f}s)")

# 2. Carregar dados (apenas 10k linhas)
print("\n2️⃣ Carregando dados (10k linhas)...")
start = time.time()

data_config = DataConfig(
    required_columns=['Date', 'Open', 'High', 'Low', 'Close'],
    date_column='Date',
    drop_duplicates=True,
    validate_ohlc=False
)

data_loader = DataLoader(data_config)
df = data_loader.load(Path('data/BTCUSDT_30m_test.csv'), verbose=0)

print(f"   ✅ Dados carregados: {len(df)} linhas ({time.time()-start:.2f}s)")

# 3. Criar modelo
print("\n3️⃣ Criando modelo LSTM...")
start = time.time()

model_config = ModelConfig(
    model_type='lstm',
    lookback=30,
    lstm_units=32,
    lstm_layers=2,
    dropout=0.3,
    learning_rate=0.001,
    batch_size=64,
    epochs=2
)

model_factory = ModelFactory()
model = model_factory.create_model(config=model_config)

print(f"   ✅ Modelo criado: {model.name} ({time.time()-start:.2f}s)")

# 4. Preparar dados
print("\n4️⃣ Preparando dados (criar sequências)...")
start = time.time()

feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
lookback = 30

# Split temporal
n = len(df)
i_train = int(n * 0.7)
df_train = df.iloc[:i_train]

# Normalizar
X = df_train[feature_cols].values
y = df_train['Close'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Criar sequências
print(f"   📊 Criando {len(X_scaled) - lookback} sequências...")
X_seq, y_seq = [], []
for i in range(len(X_scaled) - lookback):
    X_seq.append(X_scaled[i:i + lookback])
    y_seq.append(y[i + lookback])
    
    if (i+1) % 1000 == 0:
        print(f"      {i+1}/{len(X_scaled)-lookback} sequências criadas...")

X_train = np.array(X_seq)
y_train = np.array(y_seq)

print(f"   ✅ X_train: {X_train.shape}, y_train: {y_train.shape} ({time.time()-start:.2f}s)")

# 5. Treinar (1 época apenas)
print("\n5️⃣ Treinando modelo (1 época)...")
start = time.time()

history = model.fit(
    X_train, y_train,
    batch_size=64,
    epochs=1,
    validation_split=0.15,
    verbose=1
)

print(f"   ✅ Treinamento completo ({time.time()-start:.2f}s)")

# 6. Resumo
print("\n" + "="*80)
print("✅ TESTE V3 CONCLUÍDO COM SUCESSO!")
print("="*80)
print(f"📊 Loss final: {history.history['loss'][-1]:.2f}")
print(f"📊 Val Loss final: {history.history['val_loss'][-1]:.2f}")
print("="*80)
