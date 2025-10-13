# 🎯 Otimizador para 1 Trade por Dia

## Meta Específica
- **365 trades/ano** (~1 por dia útil)
- **2-3% de lucro por trade** (líquido, após custos)
- **Atual**: 6.87 trades/ano → **Meta**: 365 trades/ano (+5,200%)

## 🚀 Quick Start

```bash
# 1. Quick Test (10 gerações, ~30 min)
python src/optimize_daily_trader.py --quick

# 2. Full Optimization (80 gerações, ~8-10 horas)
python src/optimize_daily_trader.py --new

# 3. Retomar se interrompido
python src/optimize_daily_trader.py --resume
```

## 💾 Checkpoint Automático

**Cada geração salva:**
- `checkpoints/daily_trader_checkpoint_YYYYMMDD.pkl` - Estado completo
- `checkpoints/daily_trader_checkpoint_YYYYMMDD_summary.json` - Resumo legível

**Se interromper, retome com:** `--resume`

## 📊 Configuração

### Ranges Agressivos para Alta Frequência

| Parâmetro | Range | Motivo |
|-----------|-------|--------|
| `ma_len` | 150-220 | MA mais reativa |
| `dist_below_ma_pct` | 5-15% | **Mais sinais** |
| `tp_pct` | 2-5% | TP pequeno para saídas rápidas |
| `sl_pct` | 1-3% | SL pequeno para controle |
| `time_stop` | 5-20 dias | Rotação rápida de capital |

### População e Gerações

- **População**: 100 indivíduos (alta diversidade)
- **Gerações**: 80 (convergência robusta)
- **Tempo estimado**: 8-10 horas

## 📈 O Que Esperar

### Baseline (Champion do Grid Search)
```
Trades/Year: 6.87
Profit/Trade: ~3.3%
Total PnL: $3,590
```

### Meta (Daily Trader)
```
Trades/Year: 365 (+5,200%)
Profit/Trade: 2-3%
Total PnL: $7,300-$10,950 (365 × $20-30 por trade)
```

### Trade-offs Esperados
- ✅ **Muito mais trades** (53x mais)
- ✅ **Rotação rápida** de capital
- ⚠️ **PF pode cair** (1.3-1.8 vs 2.63)
- ⚠️ **WR pode cair** (60-65% vs 73%)
- ⚠️ **DD pode aumentar** (~$1,000-1,500 vs $499)

## 📁 Outputs

```
checkpoints/
├── daily_trader_checkpoint_YYYYMMDD.pkl      # Estado para resume
└── daily_trader_checkpoint_YYYYMMDD_summary.json  # Progresso

config/
└── daily_trader_best_YYYYMMDD_HHMMSS.csv    # Melhor config

report/
├── daily_trader_evolution_YYYYMMDD_HHMMSS.json   # Histórico
└── daily_trader_metrics_YYYYMMDD_HHMMSS.json     # Métricas finais
```

## 🎮 Workflow Completo

```bash
# Passo 1: Quick test para validar (30 min)
python src/optimize_daily_trader.py --quick

# Passo 2: Se satisfeito, rodar full (8-10 horas)
python src/optimize_daily_trader.py --new

# Passo 3: Se interromper, retomar
python src/optimize_daily_trader.py --resume

# Passo 4: Testar melhor config
python src/mr_backtest.py --config daily_trader_best_*.csv

# Passo 5: Comparar com champion
python report/analyze_results.py --csv grid_results.csv
```

## ⏱️ Tempo Estimado

| Modo | População | Gerações | Tempo |
|------|-----------|----------|-------|
| Quick | 100 | 10 | ~30-40 min |
| Full | 100 | 80 | ~8-10 horas |

## 🔧 Parâmetros Customizados

```bash
# Custom population/generations
python src/optimize_daily_trader.py --new --population 150 --generations 100

# Resume com mais gerações
python src/optimize_daily_trader.py --resume --generations 120
```

## 💡 Dicas

1. **Deixe rodando overnight**: Full optimization demora
2. **Monitor checkpoints**: Veja progresso em `_summary.json`
3. **Teste incremental**: Quick → validate → Full
4. **Backup checkpoints**: São seu seguro de vida!

## ⚠️ Realismo

**Meta de 365 trades/ano é agressiva!**

Mesmo otimizado, pode alcançar:
- **Otimista**: 50-100 trades/ano (+600% a +1,300%)
- **Realista**: 30-50 trades/ano (+336% a +600%)
- **Conservador**: 20-30 trades/ano (+191% a +336%)

Todos ainda seriam **EXCELENTES** melhorias sobre 6.87 atual!

---

**Pronto para começar?**
```bash
python src/optimize_daily_trader.py --quick
```
