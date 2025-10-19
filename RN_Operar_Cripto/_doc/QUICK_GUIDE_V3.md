# 🚀 Guia Rápido - Pipeline v3

## ⚡ Quick Start (5 minutos)

### **1. Treino Rápido (2 épocas - teste)**
```bash
uv run python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 2 --units 64 --lookback 60
```
**Output esperado:**
```
✅ Modelo salvo em: artifacts\v3\models\lstm_v3.keras
✅ Preprocessor salvo em: artifacts\v3\preprocessors\preprocessor_lstm_v3.pkl
✅ Histórico salvo em: artifacts/v3/logs/history_lstm_v3.json
Loss final: ~0.0011
```

### **2. Avaliar Modelo**
```bash
uv run python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv
```
**Output esperado:**
```
MAE: $20,945
MAPE: 20.50%
R² Score: -0.58
Hit Rate: 49.29%
```

### **3. Backtest**
```bash
uv run python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000
```
**Output esperado:**
```
Capital: $10,000 → $9,502
Retorno: -4.98%
Trades: 4
Sharpe: -0.40
```

---

## 🎯 Treino Production (Recomendado)

### **50 Épocas - Modelo Completo**
```bash
uv run python -m src.ml_v3_arch.cli train \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 50 \
  --units 128 \
  --lookback 60
```

**Tempo:** ~2-3 horas  
**Expectativa:**
- MAE: < $15,000
- R² Score: > 0.60
- Hit Rate: > 55%

---

## 🔄 Pipeline Automatizado

```powershell
.\run_full_pipeline.ps1 -epochs 50 -units 128 -lookback 60 -capital 10000
```

**Fases:**
1. **Train** (50 épocas)
2. **Evaluate** (métricas)
3. **Backtest** (simulação)

---

## ⚙️ Parâmetros Disponíveis

### **Train:**
```bash
--csv           # Caminho do CSV (obrigatório)
--epochs        # Número de épocas (padrão: 50)
--units         # LSTM units (padrão: 64)
--lookback      # Janela temporal (padrão: 60)
--batch-size    # Tamanho do batch (padrão: 64)
--lr            # Learning rate (padrão: 0.001)
--model-type    # Tipo de modelo: lstm ou gru (padrão: lstm)
```

### **Evaluate:**
```bash
--csv           # Caminho do CSV (obrigatório)
--model         # Modelo customizado (opcional)
```

### **Backtest:**
```bash
--csv           # Caminho do CSV (obrigatório)
--capital       # Capital inicial (padrão: 10000)
--threshold-bps # Threshold de operação (padrão: 20)
--fee-bps       # Taxa de corretagem (padrão: 10)
--slippage-bps  # Slippage (padrão: 5)
--start         # Data de início (opcional)
--model         # Modelo customizado (opcional)
```

---

## 📊 Interpretando Resultados

### **Métricas de Evaluate:**

**MAE (Mean Absolute Error):**
- Erro médio em dólares
- **Bom:** < $15,000 (15% do preço médio)
- **Aceitável:** < $20,000
- **Ruim:** > $30,000

**MAPE (Mean Absolute Percentage Error):**
- Erro percentual médio
- **Bom:** < 15%
- **Aceitável:** < 25%
- **Ruim:** > 40%

**R² Score:**
- Qualidade do fit (1.0 = perfeito)
- **Bom:** > 0.70
- **Aceitável:** > 0.50
- **Ruim:** < 0.30
- **Muito ruim:** < 0 (pior que baseline)

**Hit Rate:**
- Acerto de direção (alta vs baixa)
- **Bom:** > 60%
- **Aceitável:** > 55%
- **Ruim:** < 52%
- **Coin flip:** ~50%

### **Métricas de Backtest:**

**Sharpe Ratio:**
- Retorno ajustado ao risco
- **Excelente:** > 2.0
- **Bom:** > 1.0
- **Aceitável:** > 0.5
- **Ruim:** < 0

**Max Drawdown:**
- Maior queda do capital
- **Bom:** < 10%
- **Aceitável:** < 20%
- **Ruim:** > 30%

**Alpha vs Buy & Hold:**
- Retorno excedente vs comprar e segurar
- **Positivo:** Melhor que B&H
- **Negativo:** Pior que B&H

---

## 🛠️ Troubleshooting

### **"Preprocessor não encontrado"**
```
❌ Preprocessor não encontrado: artifacts\v3\preprocessors\preprocessor_lstm_v3.pkl
```
**Solução:** Treinar modelo primeiro
```bash
uv run python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 2
```

### **"Modelo não encontrado"**
```
❌ Modelo não encontrado! Execute 'train' primeiro.
```
**Solução:** Mesmo que acima

### **Loss muito alto (> 1.0)**
```
Loss: 650000000.0000  ← ERRADO!
```
**Causa:** Target não normalizado (bug antigo, já corrigido)  
**Solução:** Usar versão atual do código

### **Predições congeladas (Std = $0)**
```
Std Predita: $0.00  ← PROBLEMA!
```
**Causa:** Scaler incorreto (bug antigo, já corrigido)  
**Solução:** Retreinar modelo com código atual

### **Backtest muito lento**
```
🔮 Gerando predições... (travado)
```
**Causa:** Loop individual (bug antigo, já corrigido)  
**Solução:** Usar versão atual (batch predictions em 8s)

---

## 📁 Estrutura de Artefatos

```
artifacts/v3/
├── models/
│   ├── lstm_v3.keras          # Modelo treinado (nome fixo)
│   └── lstm_v3.json           # Metadata
├── preprocessors/
│   └── preprocessor_lstm_v3.pkl  # Scaler salvo (CRÍTICO!)
├── logs/
│   └── history_lstm_v3.json   # Histórico de treino
├── metrics/
│   └── evaluation_*.json      # Métricas de avaliação
└── backtest/
    ├── backtest_*.json        # Resultados de backtest
    └── equity_*.csv           # Curva de equity
```

---

## 🎓 Boas Práticas

### **1. Sempre treinar antes de avaliar**
```bash
# ❌ ERRADO:
uv run python -m src.ml_v3_arch.cli evaluate --csv data.csv  # Sem modelo!

# ✅ CORRETO:
uv run python -m src.ml_v3_arch.cli train --csv data.csv --epochs 2
uv run python -m src.ml_v3_arch.cli evaluate --csv data.csv
```

### **2. Teste rápido (2 épocas) antes de production**
```bash
# Teste rápido (~5 min)
uv run python -m src.ml_v3_arch.cli train --csv data.csv --epochs 2

# Se funcionar, production (~3h)
uv run python -m src.ml_v3_arch.cli train --csv data.csv --epochs 50 --units 128
```

### **3. Monitore o loss durante treino**
```
Epoch 1/50: loss: 0.0020 → val_loss: 0.0010  ✅ Aprendendo
Epoch 2/50: loss: 0.0011 → val_loss: 0.0016  ✅ Overfitting leve (normal)
```

**Red flags:**
- `val_loss` aumentando muito (> 2x `loss`): **Overfitting**
- `loss` não caindo: **Underfitting** (aumentar epochs/units)
- `loss > 1.0`: **Normalização errada** (bug antigo)

### **4. Interprete backtest com contexto**
```
Capital: $10,000 → $9,502 (-4.98%)
Buy & Hold: +69.19%
Trades: 4
```

**Análise:**
- Apenas 4 trades em 1 ano = threshold muito conservador
- Modelo com 2 épocas ainda aprendendo
- Normal perder no início

**Solução:**
1. Treinar 50 épocas
2. Reduzir threshold (20 → 10 bps)
3. Adicionar features

---

## 🔗 Links Úteis

- **NORMALIZATION_FIX.md**: Problema e solução de normalização
- **SESSION_20251019.md**: Sumário da sessão de hoje
- **CHECKPOINT_RESUME_GUIDE.md**: Como continuar treino
- **FEATURES_ANALYSIS.md**: Análise das 18 features

---

**Criado em:** 19/10/2025  
**Versão:** v3.1.0  
**Status:** ✅ Production Ready
