# Artifacts Directory
Este diretório contém todos os artefatos gerados pelo pipeline ML v2.

## Estrutura

```
artifacts/
├── metrics/           # JSONs de métricas (evaluate, walkforward, backtest)
├── equity/            # Equity curves (CSV)
├── checkpoints/       # Modelos treinados (.keras)
└── logs/              # Históricos de treino (JSON)
```

## Nomenclatura

Todos os arquivos são versionados com timestamp: `YYYYMMDD_HHMMSS`

**Exemplos:**
- `lstm_model_20250116_143022.keras`
- `eval_20250116_143045.json`
- `equity_20250116_143120.csv`
- `walkforward_20250116_143200.json`

## .gitignore

Este diretório não é versionado. Adicione ao `.gitignore` se necessário:

```
artifacts/
```

---

**Auto-criado pelo CLI:** `cli.py` cria automaticamente estas pastas.
