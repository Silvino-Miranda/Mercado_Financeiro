# 🧠 Sistema de Memória e Persistência da Rede Neural LSTM

## Como a LSTM Salva Sua "Memória" (Modelo Treinado)

A rede neural LSTM não perde o progresso porque salva sua **memória aprendida** em arquivos no disco. Aqui está como funciona:

---

## 📦 Tipos de Arquivos Salvos

### 1. **Modelo Completo** (Recomendado)
📄 **Arquivo:** `lstm_model.keras`  
📍 **Localização:** Raiz do projeto  
💾 **Tamanho:** ~5-20 MB (depende da arquitetura)

**O que contém:**
- ✅ Arquitetura completa do modelo (layers, neurônios)
- ✅ Pesos de todas as conexões neurais
- ✅ Configuração do otimizador
- ✅ Estado do treinamento
- ✅ Função de perda e métricas

**Como é salvo:**
```python
# Em src/main_train.py (linha 97)
lstm_model.model.save("lstm_model.keras")
```

**Como é carregado:**
```python
# Em src/main_predict.py (linha 60)
lstm_model = LSTMModel(
    input_shape=(X_predict.shape[1], 1), 
    model_path="lstm_model.keras"
)
```

---

### 2. **Checkpoints Intermediários** (Opcional)
📄 **Arquivos:** `model_weights_epoch_01.h5`, `model_weights_epoch_02.h5`, etc.  
📍 **Localização:** Raiz do projeto  
💾 **Salvamento:** A cada época durante o treinamento

**O que contém:**
- ✅ Apenas os pesos (não a arquitetura)
- ✅ Estado do modelo em cada época
- ✅ Útil para recuperar treinamento interrompido

**Como é salvo:**
```python
# Em src/models/lstm_model.py (linhas 43-49)
checkpoint = ModelCheckpoint(
    filepath="model_weights_epoch_{epoch:02d}.h5",
    save_weights_only=True,
    monitor="val_loss",
    mode="min",
    save_best_only=False,
    verbose=1,
)
```

---

## 🔄 Fluxo de Persistência

### Durante o Treinamento:

```
1. Início do Treinamento
   └─> Época 1
       └─> Salva: model_weights_epoch_01.h5 ✅
   
   └─> Época 2
       └─> Salva: model_weights_epoch_02.h5 ✅
   
   └─> ...
   
   └─> Época 10 (final)
       └─> Salva: model_weights_epoch_10.h5 ✅

2. Fim do Treinamento
   └─> Salva: lstm_model.keras ✅ (MODELO COMPLETO)
```

### Durante a Previsão:

```
1. Carregar Modelo
   └─> Lê: lstm_model.keras
   └─> Reconstrói arquitetura
   └─> Carrega todos os pesos

2. Fazer Previsões
   └─> Usa conhecimento aprendido
   └─> Gera previsões
```

---

## 🧩 O Que É "Memória" da LSTM?

### 1. **Pesos das Conexões**
Cada conexão entre neurônios tem um peso que representa o conhecimento aprendido:

```python
# Exemplo simplificado
Input Layer    →  LSTM Layer 1  →  LSTM Layer 2  →  Output
   (12)              (64)              (64)           (3)

Pesos totais: ~100.000+ parâmetros
```

### 2. **Estados das Células LSTM**
As células LSTM têm "memória de longo prazo" através de:
- **Cell State (c_t):** Memória de longo prazo
- **Hidden State (h_t):** Memória de curto prazo
- **Gates:** Controlam o que lembrar/esquecer

```
┌─────────────────────────────────┐
│    Célula LSTM                  │
│                                 │
│  Forget Gate  →  [Esquecer]    │
│  Input Gate   →  [Lembrar]     │
│  Output Gate  →  [Usar]        │
│                                 │
│  Cell State   →  [Memória]     │
└─────────────────────────────────┘
```

### 3. **Padrões Aprendidos**
Durante o treinamento, a LSTM aprende:
- 📈 Tendências de alta/baixa
- 🔄 Padrões cíclicos
- 📊 Correlações entre indicadores
- ⏰ Dependências temporais

---

## 📂 Estrutura de Arquivos no Projeto

```
RN_Operar_Cripto/
├── lstm_model.keras                    # ✅ MODELO PRINCIPAL
├── model_weights_epoch_01.h5           # Checkpoint época 1
├── model_weights_epoch_02.h5           # Checkpoint época 2
├── ...                                 # Outros checkpoints
└── model_weights_epoch_10.h5           # Checkpoint época 10
```

---

## 🔍 Verificar Se o Modelo Está Salvo

### No PowerShell:
```powershell
# Verificar se o modelo principal existe
Test-Path lstm_model.keras

# Listar todos os checkpoints
Get-ChildItem -Filter "model_weights_*.h5"

# Ver tamanho do modelo
Get-Item lstm_model.keras | Select-Object Name, Length
```

### No Python:
```python
import os
import tensorflow as tf

# Verificar existência
if os.path.exists('lstm_model.keras'):
    print("✅ Modelo encontrado!")
    
    # Carregar e verificar
    model = tf.keras.models.load_model('lstm_model.keras')
    print(f"Parâmetros treináveis: {model.count_params()}")
    model.summary()
else:
    print("❌ Modelo não encontrado. Execute o treinamento primeiro.")
```

---

## 🔐 Proteção Contra Perda de Dados

### 1. **Salvamento Automático**
```python
# Configurado em src/models/lstm_model.py
early_stopping = EarlyStopping(
    monitor="val_loss", 
    patience=10, 
    restore_best_weights=True  # ✅ Restaura melhores pesos
)
```

### 2. **Checkpoints Frequentes**
```python
checkpoint = ModelCheckpoint(
    filepath="model_weights_epoch_{epoch:02d}.h5",
    save_best_only=False  # Salva TODAS as épocas
)
```

### 3. **Backup Manual (Recomendado)**
```powershell
# Criar backup antes de novo treinamento
Copy-Item lstm_model.keras lstm_model_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').keras

# Criar pasta de backups
New-Item -ItemType Directory -Force -Path "backups"
Copy-Item lstm_model.keras backups/
```

---

## 🔄 Recuperar Treinamento Interrompido

### Opção 1: Carregar Modelo Completo
```python
from keras.models import load_model

# Carregar modelo salvo anteriormente
model = load_model('lstm_model.keras')

# Continuar treinamento
history = model.fit(
    X_train, Y_train,
    epochs=10,  # Mais 10 épocas
    initial_epoch=10  # Começa da época 11
)
```

### Opção 2: Carregar Checkpoint Específico
```python
from src.models.lstm_model import LSTMModel

# Criar modelo com mesma arquitetura
lstm_model = LSTMModel(input_shape=(60, 12), output_size=3)

# Carregar pesos de uma época específica
lstm_model.load_weights('model_weights_epoch_08.h5')

# Continuar treinamento
history = lstm_model.train(X_train, Y_train, epochs=20)
```

---

## 📊 Informações Armazenadas

### No Arquivo `lstm_model.keras`:

```json
{
  "arquitetura": {
    "layers": [
      {"type": "LSTM", "units": 64, "return_sequences": true},
      {"type": "Dropout", "rate": 0.2},
      {"type": "LSTM", "units": 64},
      {"type": "Dropout", "rate": 0.2},
      {"type": "Dense", "units": 3}
    ]
  },
  "pesos": {
    "layer_1_weights": [...100.000+ valores...],
    "layer_2_weights": [...],
    "biases": [...]
  },
  "otimizador": {
    "name": "adam",
    "learning_rate": 0.001,
    "beta_1": 0.9,
    "beta_2": 0.999
  },
  "loss": "mean_squared_error",
  "metrics": ["mean_absolute_error"]
}
```

---

## 💡 Boas Práticas

### 1. **Sempre Salve Após Treinar**
```python
# ✅ BOM
lstm_model.model.save("lstm_model.keras")

# ❌ RUIM (perda de todo o treinamento)
# Não salvar o modelo
```

### 2. **Versionamento de Modelos**
```python
import datetime

# Salvar com timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
model_name = f"lstm_model_{timestamp}.keras"
lstm_model.model.save(model_name)
```

### 3. **Documentar Parâmetros**
```python
# Salvar metadados junto com o modelo
metadata = {
    "date": "2025-10-13",
    "epochs": 10,
    "batch_size": 64,
    "sequence_length": 60,
    "train_loss": 0.0023,
    "val_loss": 0.0031
}

import json
with open("lstm_model_metadata.json", "w") as f:
    json.dump(metadata, f)
```

---

## 🎯 Resumo

| Aspecto | Detalhes |
|---------|----------|
| **Arquivo Principal** | `lstm_model.keras` |
| **Formato** | Keras/TensorFlow SavedModel |
| **Conteúdo** | Arquitetura + Pesos + Configuração |
| **Tamanho** | ~5-20 MB |
| **Localização** | Raiz do projeto |
| **Backup** | Manual (recomendado) |
| **Checkpoints** | `model_weights_epoch_*.h5` |
| **Restauração** | Automática via `load_model()` |

---

## 🔍 FAQ

### P: O modelo perde memória ao fechar o programa?
**R:** ❌ NÃO! O arquivo `.keras` mantém TUDO salvo no disco.

### P: Posso treinar em partes?
**R:** ✅ SIM! Carregue o modelo e continue o treinamento.

### P: Os checkpoints são necessários?
**R:** ⚠️ Opcional, mas útil para experimentos e recuperação.

### P: Quanto espaço em disco é necessário?
**R:** ~20-100 MB para modelo + checkpoints.

### P: O modelo funciona em outro computador?
**R:** ✅ SIM! Basta copiar o arquivo `.keras`.

---

## 🚀 Comandos Úteis

```powershell
# Ver modelos salvos
Get-ChildItem -Filter "*.keras"

# Ver tamanho total de modelos
(Get-ChildItem -Filter "*.keras","*.h5" | Measure-Object -Property Length -Sum).Sum / 1MB

# Limpar checkpoints antigos (manter só o modelo principal)
Remove-Item model_weights_*.h5

# Backup rápido
Copy-Item lstm_model.keras "lstm_model_backup_$(Get-Date -Format 'yyyyMMdd').keras"
```

---

**✅ Conclusão:** A LSTM salva toda sua "memória" no arquivo `lstm_model.keras`, garantindo que o conhecimento aprendido nunca seja perdido! 🧠💾
