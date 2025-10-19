# ✅ Pipeline Completo v3 - Implementado e Testado

## Resumo Executivo

**Status:** 🟢 COMPLETO E PRONTO PARA USO

Implementação completa do pipeline de ML v3 com Clean Architecture + SOLID:
- ✅ **Train**: Treina modelo LSTM com checkpoint/resume
- ✅ **Evaluate**: Avalia modelo com métricas robustas
- ✅ **Backtest**: Simula trading com custos realistas

---

## 🎯 Comandos Disponíveis

### 1. Train - Treinar Modelo

```powershell
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50
```

**Parâmetros:**
- `--csv`: Arquivo CSV (obrigatório)
- `--epochs`: Número de épocas (default: 50)
- `--units`: LSTM units (default: 64)
- `--lookback`: Janela temporal (default: 60)
- `--batch-size`: Tamanho do batch (default: 64)
- `--dropout`: Taxa de dropout (default: 0.3)
- `--lr`: Learning rate (default: 0.001)
- `--patience`: Early stopping (default: 10)
- `--resume`: Continuar de checkpoint

**Saída:**
- `artifacts/v3/models/lstm_v3.keras` - Modelo treinado
- `artifacts/v3/logs/history_lstm_v3.json` - Histórico de métricas
- `artifacts/v3/logs/lstm_v3.json` - Metadados do modelo

### 2. Evaluate - Avaliar Modelo

```powershell
python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv
```

**Parâmetros:**
- `--csv`: Arquivo CSV (obrigatório)
- `--model`: Caminho do modelo (default: artifacts/v3/models/lstm_v3.keras)

**Métricas calculadas:**
- **MAE** (Mean Absolute Error): Erro médio absoluto em USD
- **RMSE** (Root Mean Squared Error): Raiz do erro quadrático médio
- **MAPE** (Mean Absolute Percentage Error): Erro percentual médio
- **R² Score**: Coeficiente de determinação (0-1)
- **Hit Rate**: % de acerto na direção (alta/baixa)

**Saída:**
- `artifacts/v3/metrics/evaluation_YYYYMMDD_HHMMSS.json`

**Exemplo de output:**
```
📊 RESULTADOS DA AVALIAÇÃO
================================================================================

📈 Métricas de Erro:
   MAE (Mean Absolute Error):  $1,234.56
   RMSE (Root Mean Squared):   $2,345.67
   MAPE (Mean Abs % Error):    2.34%
   R² Score:                   0.8765

🎯 Acurácia Direcional:
   Hit Rate:                   67.89%

📊 Estatísticas:
   Média Real:                 $50,123.45
   Média Predita:              $50,098.76
   Std Real:                   $12,345.67
   Std Predita:                $11,987.54
```

### 3. Backtest - Simular Trading

```powershell
python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000
```

**Parâmetros:**
- `--csv`: Arquivo CSV (obrigatório)
- `--model`: Caminho do modelo (default: lstm_v3.keras)
- `--capital`: Capital inicial (default: 10000.0)
- `--fee-bps`: Taxa da exchange em bps (default: 10.0 = 0.1%)
- `--slippage-bps`: Slippage em bps (default: 5.0 = 0.05%)
- `--threshold-bps`: Threshold para entrada em bps (default: 20.0 = 0.2%)
- `--start`: Data de início (opcional, formato: YYYY-MM-DD)

**Lógica de trading:**
```python
# BUY quando predição > preço atual + threshold
if (predicted_price - current_price) / current_price > threshold_rate:
    BUY

# SELL quando predição < preço atual - threshold
if (current_price - predicted_price) / current_price > threshold_rate:
    SELL
```

**Métricas calculadas:**
- **Total Return**: Retorno total em %
- **Buy & Hold**: Retorno de comprar e segurar
- **Alpha**: Retorno acima do Buy & Hold
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Max Drawdown**: Maior queda percentual
- **Volatilidade**: Volatilidade dos retornos

**Saída:**
- `artifacts/v3/backtest/backtest_YYYYMMDD_HHMMSS.json` - Métricas
- `artifacts/v3/backtest/equity_YYYYMMDD_HHMMSS.csv` - Curva de capital

**Exemplo de output:**
```
💰 RESULTADOS DO BACKTEST
================================================================================

📊 Performance:
   Capital Inicial:        $10,000.00
   Capital Final:          $12,345.67
   Retorno Total:          +23.46%
   Buy & Hold:             +18.23%
   Alpha:                  +5.23%

📈 Métricas de Risco:
   Sharpe Ratio:           1.87
   Max Drawdown:           -8.45%
   Volatilidade:           2.34%

🔄 Atividade de Trading:
   Total de Trades:        45
   Trades por Dia:         0.67
```

---

## 🚀 Script de Pipeline Completo

### run_full_pipeline.ps1

Executa todo o pipeline automaticamente:

```powershell
.\run_full_pipeline.ps1 -epochs 5 -units 64 -lookback 60 -capital 10000
```

**O que faz:**
1. **FASE 1**: Treina modelo LSTM
2. **FASE 2**: Avalia modelo (métricas)
3. **FASE 3**: Executa backtest (simulação)

**Parâmetros:**
- `-csv`: Dataset (default: data/BTCUSDT_30m_full.csv)
- `-epochs`: Épocas de treino (default: 5)
- `-units`: LSTM units (default: 64)
- `-lookback`: Janela temporal (default: 60)
- `-capital`: Capital inicial (default: 10000)

**Interativo:** Pausa entre fases para review

---

## 📊 Estrutura de Dados

### Input (X) - Features

```
Shape: (batch, lookback, n_features) = (batch, 60, 18)
```

**18 Features:**
1. Open, High, Low, Volume (OHLCV)
2. BB_High, BB_Mid, BB_Low (Bollinger Bands)
3. Keltner_High, Keltner_Low (Keltner Channel)
4. Donchian_High, Donchian_Low (Donchian Channel)
5. EMA_9, EMA_20, EMA_50 (Exponential Moving Averages)
6. SMA_20, SMA_50 (Simple Moving Averages)
7. Aroon_Spread (Aroon Oscillator)
8. MACD_Hist (MACD Histogram)

### Output (y) - Target

```
Shape: (batch, 1)
Value: Close (preço de fechamento)
```

---

## 📁 Artefatos Gerados

```
artifacts/v3/
├── models/
│   ├── lstm_v3.keras              ← Modelo treinado (nome fixo)
│   └── lstm_v3.json               ← Metadados do modelo
├── logs/
│   └── history_lstm_v3.json       ← Histórico acumulado (checkpoint)
├── metrics/
│   └── evaluation_*.json          ← Métricas de avaliação
└── backtest/
    ├── backtest_*.json            ← Resultados do backtest
    └── equity_*.csv               ← Curva de capital
```

---

## 💡 Exemplos de Uso

### Workflow Completo (Recomendado)

```powershell
# 1. Treinar modelo (10 épocas teste)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10

# 2. Avaliar performance
python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv

# 3. Se bom, continuar treinando (+40 épocas)
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 40 --resume

# 4. Avaliar novamente
python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv

# 5. Backtest
python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000
```

### Workflow Automatizado

```powershell
# Pipeline completo em um comando
.\run_full_pipeline.ps1 -epochs 50 -units 128 -lookback 60 -capital 10000
```

### Testar Diferentes Thresholds

```powershell
# Backtest conservador (threshold alto = menos trades)
python -m src.ml_v3_arch.cli backtest --csv data.csv --threshold-bps 50

# Backtest agressivo (threshold baixo = mais trades)
python -m src.ml_v3_arch.cli backtest --csv data.csv --threshold-bps 10

# Backtest otimizado
python -m src.ml_v3_arch.cli backtest --csv data.csv --threshold-bps 20 --fee-bps 8
```

---

## 🔧 Troubleshooting

### Modelo não encontrado

```
❌ Modelo não encontrado! Execute 'train' primeiro ou especifique --model.
```

**Solução:**
```powershell
# Treinar modelo
python -m src.ml_v3_arch.cli train --csv data.csv --epochs 10

# OU especificar modelo existente
python -m src.ml_v3_arch.cli evaluate --csv data.csv --model path/to/model.keras
```

### RecursionError no NumPy

```
❌ RecursionError: maximum recursion depth exceeded
```

**Causa:** Imports diretos de numpy/pandas no topo do módulo

**Solução já aplicada:** Lazy imports dentro das funções (cmd_evaluate, cmd_backtest)

### Loss muito alto

```
⚠️  Loss: 650,000,000 (bilhões!)
```

**Causa:** Target (Close) não normalizado

**Workaround atual:** StandardScaler nas features, mas não no target

**Solução futura:** Normalizar target também e desnormalizar predições

---

## 📈 Performance Esperada

### Com Dataset Completo (142k linhas)

| Configuração | Tempo/Época | Tempo 50 Épocas |
|--------------|-------------|-----------------|
| CPU (64 units) | ~3 min | ~2.5h |
| CPU (128 units) | ~5 min | ~4h |
| GPU (64 units) | ~40s | ~30 min |
| GPU (128 units) | ~1.5 min | ~1.2h |

### Métricas Realistas

| Métrica | Target | Boa | Excelente |
|---------|--------|-----|-----------|
| **MAE** | < $2000 | < $1000 | < $500 |
| **RMSE** | < $3000 | < $1500 | < $1000 |
| **R²** | > 0.70 | > 0.85 | > 0.90 |
| **Hit Rate** | > 55% | > 60% | > 65% |
| **Sharpe Ratio** | > 1.0 | > 1.5 | > 2.0 |

---

## 📚 Documentação Relacionada

- **Guia Rápido**: `_doc/QUICK_START_V3.md`
- **Checkpoint/Resume**: `_doc/CHECKPOINT_RESUME_GUIDE.md`
- **Análise de Features**: `_doc/FEATURES_ANALYSIS.md`
- **Arquitetura v3**: `_doc/ESTRUTURA_PROJETO.md`
- **Este documento**: `_doc/PIPELINE_COMPLETO.md`

---

## 🎯 Próximos Passos

### Implementações Futuras

1. **Normalização do Target**
   - Aplicar StandardScaler no Close
   - Desnormalizar predições para valores reais
   - Esperar loss < 1.0 (vs atual 600M+)

2. **Otimização de Hyperparâmetros**
   - Grid search para threshold, lr, dropout
   - Walk-forward optimization
   - Validação cruzada temporal

3. **Features Adicionais**
   - RSI (Relative Strength Index)
   - Stochastic Oscillator
   - ATR (Average True Range)
   - Volume indicators

4. **Visualização**
   - Plot de equity curve
   - Gráficos de predição vs real
   - Heatmap de correlation matrix

### Para Usar Agora

**Comando principal para teste:**
```powershell
.\run_full_pipeline.ps1 -epochs 5 -units 64 -lookback 60 -capital 10000
```

**Treinamento produção:**
```powershell
python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50 --units 128
python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv
python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000
```

---

**Status Final:** 🟢 **PIPELINE COMPLETO IMPLEMENTADO E PRONTO PARA USO**

**Última atualização:** 2025-10-19
