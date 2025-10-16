# ML v2 - Quick Reference

## 🚀 Comandos Rápidos

### Setup Inicial
```powershell
# Instalar e configurar (usando UV)
./src/ml_v2/setup.ps1

# Ou manual
uv pip install pytest pytest-cov
uv run pytest src/ml_v2/tests/ -v
```

### Pipeline Completo
```bash
# 1. TRAIN
uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv

# 2. EVALUATE
uv run python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv

# 3. WALKFORWARD
uv run python src/ml_v2/cli.py walkforward --csv data/BTCUSDT_30m_full.csv --folds 3

# 4. BACKTEST
uv run python src/ml_v2/cli.py backtest --csv data/BTCUSDT_30m_full.csv --start 2024-01-01
```

---

## 📊 Interpretando Resultados

### EVALUATE - Comparação com Baselines

```
Modelo     MAE (USD)    RMSE (USD)   MAPE (%)   Hit Rate
----------------------------------------------------------------
LSTM       245.32       312.45       0.4821     0.5234
Naive1     287.91       365.12       0.5632     0.5012
SMA20      298.45       380.23       0.5891     0.4989
```

**✅ BOM:** LSTM tem menor MAE e maior Hit Rate  
**❌ RUIM:** LSTM pior que ambos os baselines → Pivotar para classificação

---

### WALKFORWARD - Robustez Temporal

```
MAE (USD):   267.45 ± 23.12
Hit Rate:    0.5123 ± 0.0234
```

**✅ BOM:** Desvio padrão baixo (< 10% da média)  
**❌ RUIM:** Desvio alto ou queda consistente em folds recentes

---

### BACKTEST - Performance Real

```
Total Return:       23.46%
CAGR:               15.23%
Max Drawdown:       -8.45%
Sharpe Ratio:       1.45
Win Rate:           57.05%
Exposure:           34.56%
```

**Métricas chave:**
- **Sharpe > 1.0:** Bom
- **Max DD < -20%:** Tolerável
- **Win Rate > 50%:** Positivo
- **Exposure < 50%:** Seletivo (bom!)

---

## 🔐 Checklist Anti-Vazamento

- [ ] `preprocessor.fit()` chamado APENAS no treino
- [ ] `shuffle=False` no `model.fit()`
- [ ] Split temporal (não aleatório)
- [ ] Walk-forward com fit independente por fold
- [ ] Testes `test_no_leak.py` passando

---

## ⚙️ Configurações Típicas

### Conservador (Menos overfitting)
```bash
uv run python src/ml_v2/cli.py train \
    --lookback 90 \
    --epochs 30 \
    --patience 15 \
    --lr 0.0001
```

### Agressivo (Mais capacidade)
```bash
uv run python src/ml_v2/cli.py train \
    --lookback 40 \
    --epochs 100 \
    --patience 8 \
    --lr 0.003
```

### Custos Reais Binance
```bash
uv run python src/ml_v2/cli.py backtest \
    --fee-bps 10 \        # 0.10% (maker/taker)
    --slippage-bps 5 \    # 0.05% slippage médio
    --threshold-bps 30    # 0.30% threshold conservador
```

---

## 🐛 Troubleshooting

### "Scaler not fitted"
```python
# ❌ ERRADO
prep = DataPreprocessor(...)
X, y = prep.transform(df)  # ERRO!

# ✅ CORRETO
prep = DataPreprocessor(...)
prep.fit(df_train)
X, y = prep.transform(df)
```

### "Nenhum modelo encontrado"
```bash
# Execute train primeiro
uv run python src/ml_v2/cli.py train --csv data/BTCUSDT_30m_full.csv

# Depois evaluate/backtest
uv run python src/ml_v2/cli.py evaluate --csv data/BTCUSDT_30m_full.csv
```

### LSTM pior que baselines
```python
# Opções:
1. Revisar features (usar retornos log)
2. Aumentar lookback (60 → 90)
3. Adicionar features de volatilidade (ATR%)
4. Testar classificação (ALTA/LATERAL/BAIXA)
5. Ensemble: LSTM + Naive1 + SMA20
```

---

## 📁 Estrutura de Arquivos

```
src/ml_v2/
├── cli.py              # ← ENTRYPOINT principal
├── preprocess.py       # Preprocessamento sem leak
├── metrics.py          # Métricas + baselines
├── models/
│   └── lstm_model.py
├── validation/
│   └── walkforward.py
├── backtest/
│   └── engine.py
└── tests/
    └── test_no_leak.py

artifacts/              # ← OUTPUTS (auto-criado)
├── metrics/*.json
├── equity/*.csv
├── checkpoints/*.keras
└── logs/*.json
```

---

## 🎯 Decisões de Design

### Por que sem shuffle?
**Séries temporais:** Ordem importa! Shuffle quebra dependências temporais.

### Por que Naive1 e SMA20?
**Baselines fortes:** Se LSTM não bate eles, não adianta complexidade.

### Por que walk-forward?
**Validação temporal:** Train/val/test único vaza informação do futuro.

### Por que fee + slippage + threshold?
**Custos reais:** Sem isso, qualquer modelo "funciona" no backtest.

---

## 💡 Próximos Passos

### Se LSTM funcionar bem:
1. Adicionar mais features (ATR%, BB%, ADX)
2. Testar GRU no lugar de LSTM
3. Ensemble: LSTM + XGBoost
4. Paper trading (simulação real)

### Se LSTM falhar:
1. ✅ **Pivotar para CLASSIFICAÇÃO** (ALTA/LATERAL/BAIXA)
2. Testar threshold adaptativo (ATR%)
3. Aumentar horizon (12 → 24 candles)
4. Class weights / Focal Loss

---

## 📚 Referências Rápidas

- **User Story:** `US.md`
- **README Completo:** `README.md`
- **Exemplos:** `examples.py`
- **Testes:** `tests/test_no_leak.py`

---

**Última atualização:** 2025-10-16  
**Versão:** 2.0.0
