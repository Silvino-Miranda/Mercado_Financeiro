# 🚀 Quick Start - ML v3 (Clean Architecture)

## TL;DR - Comandos Rápidos

```powershell
# 1. Ativar ambiente
.\.venv\Scripts\Activate.ps1

# 2. Treinar modelo (10 épocas)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10

# 3. Continuar treinamento (+20 épocas)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 20 --resume

# 4. Avaliar modelo
python -m src.ml_v3_arch.cli evaluate --model artifacts/v3/models/lstm_v3.keras --csv data/BTCUSDT_30m_full.csv

# 5. Backtest
python -m src.ml_v3_arch.cli backtest --model artifacts/v3/models/lstm_v3.keras --csv data/BTCUSDT_30m_full.csv
```

## Instalação (Primeira Vez)

### 1. Criar Ambiente com UV

```powershell
# Criar .venv com Python 3.12
uv venv .venv --python 3.12

# Ativar
.\.venv\Scripts\Activate.ps1

# Instalar dependências
uv pip install -r requirements.txt

# OU instalar diretamente
uv pip install numpy pandas scikit-learn tensorflow ta-lib matplotlib
```

### 2. Verificar Instalação

```powershell
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import numpy as np; print(f'NumPy: {np.__version__}')"
python -c "import pandas as pd; print(f'Pandas: {pd.__version__}')"
```

**Saída esperada:**
```
TensorFlow: 2.20.0
NumPy: 2.3.4
Pandas: 2.3.3
```

## Comandos Disponíveis

### 🎯 train - Treinar modelo LSTM

```powershell
python -m src.ml_v3_arch.cli train [opções]
```

**Opções principais:**
- `--csv PATH` - Caminho do arquivo CSV (**obrigatório**)
- `--epochs N` - Número de épocas (padrão: 10)
- `--units N` - Unidades LSTM (padrão: 64)
- `--lookback N` - Janela temporal (padrão: 60)
- `--learning-rate F` - Taxa de aprendizado (padrão: 0.001)
- `--batch-size N` - Tamanho do batch (padrão: 32)
- `--dropout F` - Taxa de dropout (padrão: 0.2)
- `--resume` - Continuar de checkpoint existente

**Exemplos:**

```powershell
# Treino básico (10 épocas, 64 units, 60 lookback)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10

# Treino customizado
python -m src.ml_v3_arch.cli train `
    --csv data/BTCUSDT_30m_full.csv `
    --epochs 50 `
    --units 128 `
    --lookback 120 `
    --learning-rate 0.0005 `
    --batch-size 64

# Treino com GPU (se disponível)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 100 --batch-size 128

# Continuar treinamento existente
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 30 --resume
```

### 🔄 Checkpoint & Resume

Sistema automático de checkpoint permite continuar treinamento sem perder progresso.

**Arquivos checkpoint (nomes fixos):**
- `artifacts/v3/models/lstm_v3.keras` - Modelo com pesos
- `artifacts/v3/logs/history_lstm_v3.json` - Histórico acumulado

**Workflow típico:**

```powershell
# 1. Treinar 10 épocas iniciais
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 10
# Saída: "Épocas TOTAIS acumuladas: 10"

# 2. Verificar checkpoint
python -c "import json; h = json.load(open('artifacts/v3/logs/history_lstm_v3.json')); print(f'Épocas: {len(h[\"loss\"])}')"
# Saída: "Épocas: 10"

# 3. Continuar por mais 20 épocas
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 20 --resume
# Saída: "✅ Histórico carregado: 10 épocas já treinadas"
#        "🔄 Histórico mesclado: 10 épocas antigas + 20 novas"
#        "Épocas TOTAIS acumuladas: 30"

# 4. Continuar novamente (+50 épocas)
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50 --resume
# Saída: "Épocas TOTAIS acumuladas: 80"
```

**Guia detalhado:** Ver `_doc/CHECKPOINT_RESUME_GUIDE.md`

### 📊 evaluate - Avaliar modelo

```powershell
python -m src.ml_v3_arch.cli evaluate --model PATH --csv PATH
```

**Exemplo:**
```powershell
python -m src.ml_v3_arch.cli evaluate `
    --model artifacts/v3/models/lstm_v3.keras `
    --csv data/BTCUSDT_30m_full.csv
```

**Métricas retornadas:**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score
- Sharpe Ratio (se aplicável)

### 💰 backtest - Simular trading

```powershell
python -m src.ml_v3_arch.cli backtest --model PATH --csv PATH [opções]
```

**Opções:**
- `--initial-capital F` - Capital inicial (padrão: 10000.0)
- `--position-size F` - Tamanho da posição (padrão: 0.1 = 10%)
- `--stop-loss F` - Stop loss % (padrão: 0.02 = 2%)
- `--take-profit F` - Take profit % (padrão: 0.05 = 5%)

**Exemplo:**
```powershell
python -m src.ml_v3_arch.cli backtest `
    --model artifacts/v3/models/lstm_v3.keras `
    --csv data/BTCUSDT_30m_full.csv `
    --initial-capital 10000 `
    --position-size 0.15 `
    --stop-loss 0.015 `
    --take-profit 0.04
```

### 🏷️ train_classifier - Treinar classificador direcional

```powershell
python -m src.ml_v3_arch.cli train_classifier --csv PATH [opções]
```

**Exemplo:**
```powershell
python -m src.ml_v3_arch.cli train_classifier `
    --csv data/BTCUSDT_30m_full.csv `
    --epochs 50 `
    --units 128
```

## Scripts PowerShell Prontos

### run_v3_train.ps1 - Treino rápido

```powershell
# Treino com defaults
.\run_v3_train.ps1

# Treino customizado
.\run_v3_train.ps1 data/custom.csv 50 128 120
```

### test_resume.ps1 - Testar checkpoint/resume

```powershell
# Executa 3 fases de treinamento incremental
.\test_resume.ps1

# Com parâmetros customizados
.\test_resume.ps1 -csv data/custom.csv -units 128 -lookback 120
```

**O que faz:**
1. Fase 1: Treina 2 épocas (inicial)
2. Fase 2: Resume +3 épocas (total: 5)
3. Fase 3: Resume +5 épocas (total: 10)
4. Verifica se histórico foi mesclado corretamente

## Estrutura de Saída

```
artifacts/v3/
├── models/
│   └── lstm_v3.keras              ← Modelo treinado (nome fixo)
├── logs/
│   ├── history_lstm_v3.json       ← Histórico acumulado (nome fixo)
│   └── lstm_v3.json               ← Metadados do modelo
└── metrics/
    └── [métricas de avaliação]
```

## Verificar Status do Modelo

```powershell
# Script rápido PowerShell
$history = Get-Content "artifacts/v3/logs/history_lstm_v3.json" | ConvertFrom-Json
$epochs = $history.loss.Count
$lastLoss = $history.loss[-1]
$lastValLoss = $history.val_loss[-1]

Write-Host "Épocas: $epochs"
Write-Host "Loss final: $($lastLoss.ToString('F6'))"
Write-Host "Val Loss final: $($lastValLoss.ToString('F6'))"
```

**Ou com Python:**
```powershell
python -c "import json; h = json.load(open('artifacts/v3/logs/history_lstm_v3.json')); print(f'Épocas: {len(h[\"loss\"])}\nLoss: {h[\"loss\"][-1]:.6f}\nVal Loss: {h[\"val_loss\"][-1]:.6f}')"
```

## Fluxo de Trabalho Completo

### 1. Treino Inicial Rápido (Teste)

```powershell
# Testar com 5 épocas para verificar se tudo funciona
python -m src.ml_v3_arch.cli train `
    --csv data/BTCUSDT_30m_full.csv `
    --epochs 5 `
    --units 64 `
    --lookback 60

# Tempo esperado: ~3-5 minutos (142k linhas)
```

### 2. Avaliar Resultado

```powershell
python -m src.ml_v3_arch.cli evaluate `
    --model artifacts/v3/models/lstm_v3.keras `
    --csv data/BTCUSDT_30m_full.csv
```

Se MAE < 0.005 e Val Loss < 0.003, continuar:

### 3. Treino Completo Incremental

```powershell
# +20 épocas (total: 25)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 20 --resume

# +25 épocas (total: 50)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 25 --resume

# +50 épocas (total: 100)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50 --resume
```

### 4. Avaliação Final

```powershell
python -m src.ml_v3_arch.cli evaluate `
    --model artifacts/v3/models/lstm_v3.keras `
    --csv data/BTCUSDT_30m_full.csv
```

### 5. Backtest

```powershell
python -m src.ml_v3_arch.cli backtest `
    --model artifacts/v3/models/lstm_v3.keras `
    --csv data/BTCUSDT_30m_full.csv `
    --initial-capital 10000
```

## Troubleshooting

### RecursionError no NumPy

```
❌ Erro: RecursionError: maximum recursion depth exceeded
✅ Solução: Recriar ambiente com UV (não usar pip)
```

```powershell
# Deletar .venv antigo
Remove-Item -Recurse -Force .venv

# Criar novo com UV
uv venv .venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

### "ValueError: input shape mismatch" no --resume

```
❌ Erro: Tentou --resume mas mudou --units ou --lookback
✅ Solução: Delete checkpoint e treine do zero
```

```powershell
Remove-Item artifacts/v3/models/lstm_v3.keras
Remove-Item artifacts/v3/logs/history_lstm_v3.json
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50
```

### Modelo não aprende (loss não diminui)

```
❌ Causa: Learning rate muito alto ou dataset com problemas
✅ Solução: Reduzir learning rate ou verificar dados
```

```powershell
# Testar com LR menor
python -m src.ml_v3_arch.cli train `
    --csv data.csv `
    --epochs 20 `
    --learning-rate 0.0001

# Verificar dados
python -c "import pandas as pd; df = pd.read_csv('data.csv'); print(df.describe())"
```

### Out of Memory (OOM)

```
❌ Causa: Batch size ou lookback muito grande
✅ Solução: Reduzir batch-size e/ou lookback
```

```powershell
# Usar batch menor
python -m src.ml_v3_arch.cli train `
    --csv data.csv `
    --epochs 50 `
    --batch-size 16 `
    --lookback 30
```

## Performance Esperada

**Dataset:** BTCUSDT_30m_full.csv (142k linhas)

| Configuração | Tempo/Época | Tempo 50 Épocas |
|--------------|-------------|-----------------|
| CPU (64 units, bs=32) | ~2-3 min | ~2h |
| CPU (128 units, bs=32) | ~4-5 min | ~4h |
| GPU (64 units, bs=64) | ~30-40s | ~30 min |
| GPU (128 units, bs=64) | ~1-1.5 min | ~1h |

**Nota:** GPU requer TensorFlow-GPU e CUDA instalados.

## Próximos Passos

- 📚 **Arquitetura Detalhada:** Ver `_doc/ESTRUTURA_PROJETO.md`
- 🔄 **Checkpoint Completo:** Ver `_doc/CHECKPOINT_RESUME_GUIDE.md`
- 📊 **Métricas de Trading:** Ver `_doc/PROJECT_SUMMARY.md`
- 🧪 **Testes:** Ver `_doc/V3_SUCCESS_REPORT.md`

---

**🎯 Objetivo:** Com v3, você tem controle total sobre treinamento incremental e checkpoint/resume automático!
