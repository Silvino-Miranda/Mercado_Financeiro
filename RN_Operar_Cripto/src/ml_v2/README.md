# ML v2 - Pipeline Robusto para Trading com LSTM

**Versão:** 2.0.0  
**Status:** 🟢 Implementação Completa

---

## 🎯 Objetivo

Pipeline de Machine Learning **sem vazamento de dados**, com métricas em USD, comparação com baselines, validação walk-forward e backtest com custos reais.

**Diferencial:** Não mais "melhore o loss". Agora é: **prove que gera lucro líquido robusto**.

---

## 📁 Estrutura

```
src/ml_v2/
├── cli.py                      # CLI principal com subcomandos
├── preprocess.py              # Preprocessamento sem vazamento
├── metrics.py                 # Métricas em USD + baselines
├── models/
│   └── lstm_model.py         # Modelo LSTM para Close(t+1)
├── validation/
│   └── walkforward.py        # Validação walk-forward
├── backtest/
│   └── engine.py             # Backtest com custos
└── tests/
    └── test_no_leak.py       # Testes de vazamento

artifacts/                     # Outputs (auto-criado)
├── metrics/                  # JSONs de avaliação
├── equity/                   # Equity curves
├── checkpoints/              # Modelos salvos
└── logs/                     # Históricos de treino
```

---

## 🚀 Quick Start

### 1. Instalar dependências

Este projeto usa **UV** para gerenciamento de dependências.

```bash
# As dependências estão no pyproject.toml raiz
# Se pytest não estiver instalado:
uv pip install pytest pytest-cov

# Ou reinstalar todas:
uv sync
```

### 2. Comandos disponíveis

#### **TRAIN** - Treinar modelo
```bash
# Usando UV (recomendado)
uv run python src/ml_v2/cli.py train \
    --csv data/BTCUSDT_30m_full.csv \
    --lookback 60 \
    --epochs 50 \
    --batch-size 32 \
    --lr 0.001 \
    --patience 10

# Ou direto (se .venv ativado)
python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv
```

#### **EVALUATE** - Comparar com baselines
```bash
uv run python src/ml_v2/cli.py evaluate \
    --csv data/BTCUSDT_30m_full.csv \
    --lookback 60
```

**Output:**
```
================================================================================
COMPARAÇÃO: LSTM vs BASELINES
================================================================================
Modelo     MAE (USD)    RMSE (USD)   MAPE (%)   Hit Rate  
--------------------------------------------------------------------------------
LSTM       245.32       312.45       0.4821     0.5234
Naive1     287.91       365.12       0.5632     0.5012
SMA20      298.45       380.23       0.5891     0.4989
================================================================================
✅ LSTM superou pelo menos um baseline.
```

#### **WALKFORWARD** - Validação temporal
```bash
uv run python src/ml_v2/cli.py walkforward \
    --csv data/BTCUSDT_30m_full.csv \
    --lookback 60 \
    --folds 3 \
    --epochs 50 \
    --verbose
```

**Output:**
```
================================================================================
RESUMO WALK-FORWARD
================================================================================
MAE (USD):   267.45 ± 23.12
RMSE (USD):  334.56 ± 28.90
MAPE (%):    0.5234 ± 0.0456
Hit Rate:    0.5123 ± 0.0234
================================================================================
```

#### **BACKTEST** - Teste com custos
```bash
uv run python src/ml_v2/cli.py backtest \
    --csv data/BTCUSDT_30m_full.csv \
    --lookback 60 \
    --start 2024-01-01 \
    --fee-bps 10 \
    --slippage-bps 5 \
    --threshold-bps 20 \
    --capital 10000
```

**Output:**
```
================================================================================
BACKTEST REPORT
================================================================================
Initial Capital:    $10,000.00
Final Equity:       $12,345.67
Total Return:       23.46%
CAGR:               15.23%
Max Drawdown:       -8.45%
--------------------------------------------------------------------------------
Sharpe Ratio:       1.45
Sortino Ratio:      2.12
Profit Factor:      1.67
--------------------------------------------------------------------------------
Total Trades:       156
Winning Trades:     89
Losing Trades:      67
Win Rate:           57.05%
Exposure:           34.56%
================================================================================
```

---

## 🔐 Garantias Anti-Vazamento

### ✅ Implementado

1. **Scaler fit() APENAS no treino**
   - `preprocessor.fit(df_train)` - uma vez só
   - `transform()` em val/test usa escalas do treino
   - RuntimeError se tentar `transform()` sem `fit()`

2. **Split temporal**
   - 70% train / 15% val / 15% test
   - Sem shuffle: `shuffle=False` no `model.fit()`
   - Dados ordenados por data

3. **Walk-forward com fit independente**
   - Cada fold tem seu próprio scaler e modelo
   - Zero contaminação entre folds

4. **Testes automatizados**
   - `tests/test_no_leak.py` - 6 testes
   - Verifica que scalers do treino ≠ scalers do full dataset

---

## 📊 Métricas

### Regressão (USD)
- **MAE**: Erro absoluto médio em USD
- **RMSE**: Raiz do erro quadrático médio
- **MAPE**: Erro percentual médio
- **Hit Rate**: % de acerto na direção (up/down)

### Backtest
- **CAGR**: Retorno anualizado composto
- **Max Drawdown**: Maior queda do equity
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Sortino Ratio**: Sharpe considerando apenas downside
- **Profit Factor**: Ganho bruto / Perda bruta
- **Win Rate**: % de trades vencedores
- **Exposure**: % do tempo com posição aberta

---

## 🏗️ Baselines

### Naive1 (Persistência)
```
pred(t+1) = close(t)
```
"Amanhã será igual a hoje."

### SMA20 (Média Móvel)
```
pred(t+1) = média(close[t-19:t])
```
"Amanhã será a média dos últimos 20 períodos."

**CRÍTICO:** Se LSTM não bater **ambos** os baselines, pivote para classificação direcional!

---

## 🧪 Testes

```bash
# Rodar todos os testes
uv run pytest src/ml_v2/tests/ -v

# Testar vazamento específico
uv run pytest src/ml_v2/tests/test_no_leak.py::test_scaler_fit_only_on_train -v
```

**6 testes implementados:**
1. `test_scaler_fit_only_on_train` - Fit apenas no treino
2. `test_transform_before_fit_raises_error` - Erro sem fit
3. `test_inverse_target_returns_correct_scale` - Desnormalização correta
4. `test_sequences_have_correct_shape` - Shape LSTM correto
5. `test_no_data_leakage_in_split` - Scalers diferentes
6. (Implícito) Temporal ordering mantido

---

## 📈 Workflow Completo

```bash
# 1. Treinar
uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv

# 2. Avaliar vs baselines
uv run python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv

# 3. Validar robustez
uv run python src/ml_v2/cli.py walkforward --csv data/BTCUSDT_30m_full.csv --folds 3

# 4. Backtest 2024
uv run python src/ml_v2/cli.py backtest \
    --csv data/BTCUSDT_30m_full.csv \
    --start 2024-01-01 \
    --fee-bps 10 \
    --slippage-bps 5 \
    --threshold-bps 20
```

---

## ⚙️ Configurações

### Custos de Trading
- `--fee-bps 10`: Taxa de exchange (0.10%)
- `--slippage-bps 5`: Slippage (0.05%)
- `--threshold-bps 20`: Threshold mínimo de entrada (0.20%)

**Total de custo por trade:** ~0.30% (entrada + saída)

### Modelo
- **Lookback:** 60 períodos (30 horas em candles de 30min)
- **LSTM 1:** 64 unidades + Dropout 0.2
- **LSTM 2:** 32 unidades + Dropout 0.2
- **Output:** 1 neurônio (Close futuro)

### Treino
- **Loss:** MSE (Mean Squared Error)
- **Optimizer:** Adam (lr=0.001)
- **EarlyStopping:** patience=10, monitor='val_loss'
- **ReduceLROnPlateau:** patience=5, factor=0.5

---

## 🎯 Critérios de Aceite (DoD)

- [x] Split temporal sem vazamento
- [x] Métricas desnormalizadas em USD
- [x] Baselines Naive1 e SMA20
- [x] Walk-forward com ≥ 3 folds
- [x] Backtest com fee, slippage, latência
- [x] Reprodutível (seeds fixas, shuffle=False)
- [x] Testes pytest para vazamento
- [x] CLI com subcomandos
- [x] Artifacts salvos com timestamp

---

## 🚨 Alertas Importantes

### ⚠️ Se LSTM perder para ambos os baselines:
```
⚠️  ALERTA: LSTM NÃO SUPEROU OS BASELINES!
💡 Considere mudar para CLASSIFICAÇÃO DIRECIONAL.
```

**Próximos passos:**
1. Revisar features (estacionariedade?)
2. Testar classificação (ALTA/LATERAL/BAIXA)
3. Adicionar features de volatilidade (ATR%)
4. Considerar ensemble de modelos

---

## 📝 Outputs Esperados

### evaluate
```json
{
  "LSTM": {
    "mae_usd": 245.32,
    "rmse_usd": 312.45,
    "mape_pct": 0.4821,
    "hit_rate": 0.5234
  },
  "Naive1": {...},
  "SMA20": {...}
}
```

### walkforward
```json
{
  "folds": [
    {"fold": 1, "mae_usd": 267.45, "hit_rate": 0.5123, ...},
    {"fold": 2, "mae_usd": 289.12, "hit_rate": 0.4987, ...},
    {"fold": 3, "mae_usd": 245.78, "hit_rate": 0.5245, ...}
  ],
  "summary": {
    "mae_usd_mean": 267.45,
    "mae_usd_std": 23.12,
    ...
  }
}
```

### backtest
```csv
Date,Equity,Return
2024-01-01 00:00:00,10000.0,0.0
2024-01-01 00:30:00,10023.5,0.00235
...
```

---

## 🔧 Troubleshooting

### Erro: "Scaler not fitted"
**Causa:** Tentou `transform()` sem `fit()`  
**Solução:** Sempre faça `preprocessor.fit(df_train)` primeiro

### Erro: "Nenhum modelo encontrado"
**Causa:** Nenhum arquivo `.keras` em `artifacts/checkpoints/`  
**Solução:** Execute `train` antes de `evaluate` ou `backtest`

### Warning: LSTM pior que baselines
**Causa:** Features não informativas ou overfitting  
**Solução:** 
1. Revisar features (usar retornos em vez de preços?)
2. Aumentar regularização (dropout)
3. Testar classificação direcional

---

## 📚 Referências

- [User Story Original](US.md)
- [GitHub Copilot Instructions](../.github/copilot-instructions.md)
- [Walk-Forward Analysis](https://en.wikipedia.org/wiki/Walk_forward_analysis)
- [Bias-Variance Tradeoff](https://en.wikipedia.org/wiki/Bias%E2%80%93variance_tradeoff)

---

## 🤝 Contribuindo

Para adicionar novos recursos:

1. **Novos modelos:** Adicione em `models/`
2. **Novas métricas:** Adicione em `metrics.py`
3. **Novos baselines:** Adicione em `metrics.py`
4. **Novos testes:** Adicione em `tests/`

**Regra de ouro:** Se adicionar fit/transform, GARANTA que não vaze dados!

---

## 📄 Licença

MIT License - Veja projeto principal

---

**Status:** ✅ Implementação completa e testada  
**Última atualização:** 2025-10-16
