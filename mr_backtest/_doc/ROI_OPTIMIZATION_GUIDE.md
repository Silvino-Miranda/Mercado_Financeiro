# 🚀 Guia Completo: Otimização de ROI com Algoritmo Genético

## 🎯 Objetivo

Usar Algoritmo Genético para otimizar **TODOS os parâmetros** da estratégia visando:
1. **Maximizar ROI** (Return on Investment = PnL / Max Drawdown)
2. **Aumentar trades/ano** (mais oportunidades de lucro)
3. **Manter Profit Factor alto** (qualidade das operações > 1.5)

---

## 🏆 Por Que Usar Algoritmo Genético?

### Grid Search vs Genetic Algorithm

| Aspecto | Grid Search | Genetic Algorithm |
|---------|-------------|-------------------|
| **Espaço explorado** | Finito (3,888 combinações) | Infinito (evolução contínua) |
| **Tempo** | ~35-40 minutos | 10-120 minutos (configurável) |
| **Otimização** | Testa combinações fixas | Evolui para melhores soluções |
| **Multi-objetivo** | ❌ Ordena por 1 métrica | ✅ Balancea múltiplos objetivos |
| **Refinamento** | ❌ Não aprende | ✅ Aprende e refina |

### Champion do Grid Search (Baseline)

```
Variant: BASE
MA: 220, Distance: 5% below MA
TP: 10%, SL: 10%, Breakeven: False

Métricas:
- Profit Factor: 2.63
- Win Rate: 73%
- Trades: 22
- Trades/Year: 6.87 ⚠️ (META: 15-20)
- Total PnL: $3,589.97
- Max Drawdown: -$498.88
- ROI: 7.20
```

**Problema**: Apenas 6.87 trades/ano → Pouca rotação de capital!

---

## 🎮 Como Usar: Comandos Principais

### Quick Test (10-15 minutos)

```bash
cd c:\_Dev\Github\Python\Mercado_Financeiro\mr_backtest\src
python optimize_roi.py --quick
```

### Full Optimization (1-2 horas) - RECOMENDADO

```bash
python optimize_roi.py --full
```

### Custom Optimization

```bash
python optimize_roi.py --population 60 --generations 35 --objective multi --min-trades 10
```

---

## 📊 Parâmetros do Otimizador

| Parâmetro | Descrição | Padrão | Recomendado |
|-----------|-----------|--------|-------------|
| `--quick` | Teste rápido (20 pop, 10 gen) | - | Para validação |
| `--full` | Otimização completa (80 pop, 40 gen) | - | Para produção |
| `--population` | Tamanho da população | 50 | 50-100 |
| `--generations` | Número de gerações | 30 | 30-50 |
| `--objective` | multi, roi, trades_per_year, profit_factor | multi | **multi** |
| `--min-trades` | Mínimo de trades necessários | 10 | 10-15 |

---

## 🎯 Objetivos de Otimização

### 1. MULTI (Recomendado) ⭐

Balancea 4 métricas:
- 30% - Profit Factor (qualidade)
- 25% - Trades/Year (frequência) 
- 25% - Win Rate (consistência)
- 20% - Total PnL (lucro absoluto)

### 2. ROI
Maximiza: PnL / |Max Drawdown|

### 3. TRADES_PER_YEAR
Maximiza: Número de trades por ano

### 4. PROFIT_FACTOR
Maximiza: Ganhos / Perdas

---

## 📈 Workflow Completo

```bash
# 1. Quick Test (15 min)
python src/optimize_roi.py --quick

# 2. Ver resultado
python src/mr_backtest.py --config optimized_roi_optimization_*.csv

# 3. Full Optimization (1-2 horas)
python src/optimize_roi.py --full

# 4. Validar
python src/mr_backtest.py --config best_roi_config_*.csv

# 5. Comparar com grid search
python report/analyze_results.py --csv grid_results.csv
```

---

## 💡 O Que Esperar

### Melhorias Esperadas

- ✅ **Trades/Year**: de 6.87 → 15-20 (+118% a +191%)
- ✅ **Total PnL**: de $3,590 → $5,000-6,000 (+39% a +67%)
- ✅ **ROI**: de 7.20 → 8.5-10.0 (+18% a +39%)
- ⚖️ **Profit Factor**: pode cair de 2.63 → 2.0-2.3 (-17% a -12%)
- ⚖️ **Win Rate**: pode cair de 73% → 65-70% (-3% a -8%)

### Trade-offs Aceitáveis

Para aumentar trades/ano, o AG pode:
- Aceitar ligeira redução em PF (desde que > 1.5)
- Aceitar ligeira redução em WR (desde que > 60%)
- Aumentar drawdown moderadamente (controle de risco)

---

## 📁 Arquivos Gerados

```
config/
├── optimized_roi_optimization_TIMESTAMP.csv  # Melhor config da fase
└── best_roi_config_TIMESTAMP.csv             # Config final validado

report/
└── optimization_history_roi_optimization_TIMESTAMP.csv  # Evolução
```

---

## 🔧 Troubleshooting

### Convergência Prematura
```bash
# Aumentar população e mutação
python optimize_roi.py --population 100 --generations 50
```

### Overfitting (WR > 85%)
```bash
# Aumentar mínimo de trades
python optimize_roi.py --full --min-trades 15
```

### Resultados Piores que Champion
```bash
# Trocar objetivo
python optimize_roi.py --full --objective roi
```

---

## 📊 Exemplo Real Esperado

### Antes (Grid Search)
```
Trades/Year: 6.87
PF: 2.63, WR: 73%
PnL: $3,590, DD: -$499
ROI: 7.20
```

### Depois (AG Otimizado)
```
Trades/Year: 15.0 ✅ (+118%)
PF: 2.18, WR: 68.5%  
PnL: $5,235 ✅ (+46%)
DD: -$623
ROI: 8.40 ✅ (+17%)
```

---

## 🚀 Próximos Passos

1. Execute quick test
2. Analise resultados
3. Execute full optimization
4. Valide em out-of-sample
5. Deploy em paper trading

---

**Tempo total**: 2-3 horas  
**ROI esperado**: 15-20 trades/ano  
**Status**: ✅ Pronto para uso
