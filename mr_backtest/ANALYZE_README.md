# 📊 Grid Search Results Analyzer - Guia Completo

Sistema completo de análise e visualização dos resultados do grid search para estratégias de Mean-Reversion no Bitcoin (BTCUSDT).

## 🎯 Visão Geral

O `analyze_results.py` é uma ferramenta poderosa para analisar os resultados do grid search executado pelo `mr_backtest.py`. Ele fornece:

- ✅ Estatísticas detalhadas de performance
- ✅ Comparação entre variantes de estratégia
- ✅ Identificação das melhores configurações
- ✅ Análise de sensibilidade de parâmetros
- ✅ Visualizações gráficas interativas
- ✅ Exportação de resultados filtrados

---

## 📋 Pré-requisitos

### Dependências Obrigatórias
```bash
pip install pandas numpy
```

### Dependências Opcionais (para gráficos)
```bash
pip install matplotlib seaborn
```

Ou instale tudo de uma vez:
```bash
pip install -e ".[viz]"
```

---

## 🚀 Uso Básico

### 1. Análise Simples (padrão)
Executa todas as análises básicas sem gráficos:

```powershell
python analyze_results.py --csv grid_results.csv
```

**Saída:**
- Estatísticas gerais
- Comparação entre variantes (base, rsi, reclaim)
- Top 10 melhores configurações
- Análise de sensibilidade de parâmetros
- Configurações robustas

---

## 🔍 Opções de Filtragem

### 2. Ver Top N Configurações
Mostra as N melhores configurações ordenadas por Profit Factor:

```powershell
# Ver top 20 configurações
python analyze_results.py --csv grid_results.csv --top 20

# Ver top 50 configurações
python analyze_results.py --csv grid_results.csv --top 50
```

### 3. Filtrar por Número Mínimo de Trades
Considera apenas configurações com pelo menos X trades:

```powershell
# Mínimo de 10 trades
python analyze_results.py --csv grid_results.csv --min-trades 10

# Mínimo de 20 trades (mais conservador)
python analyze_results.py --csv grid_results.csv --min-trades 20

# Mínimo de 5 trades (menos restritivo)
python analyze_results.py --csv grid_results.csv --min-trades 5
```

### 4. Filtrar por Variante Específica
Analisa apenas uma estratégia específica:

```powershell
# Apenas estratégia Base (filtro de inclinação MA)
python analyze_results.py --csv grid_results.csv --variant base

# Apenas estratégia RSI (cruzamento do RSI)
python analyze_results.py --csv grid_results.csv --variant rsi

# Apenas estratégia Reclaim (reconquista da MA200)
python analyze_results.py --csv grid_results.csv --variant reclaim
```

### 5. Filtrar por Profit Factor Mínimo
Define um limite mínimo de Profit Factor:

```powershell
# PF >= 1.5
python analyze_results.py --csv grid_results.csv --pf-min 1.5

# PF >= 2.0 (muito seletivo)
python analyze_results.py --csv grid_results.csv --pf-min 2.0

# PF >= 1.2
python analyze_results.py --csv grid_results.csv --pf-min 1.2
```

---

## 📊 Visualizações

### 6. Gerar Gráficos
Cria 4 gráficos de análise e salva como imagem:

```powershell
python analyze_results.py --csv grid_results.csv --plot
```

**Gráficos gerados:**
1. **Profit Factor vs Total PnL** - Scatter plot por variante
2. **Win Rate Distribution** - Box plot comparando variantes
3. **Profit Factor vs Max Drawdown** - Colorido por win rate
4. **Trade Count Distribution** - Histograma

**Arquivo gerado:** `grid_results_analysis.png`

---

## 💾 Exportação de Resultados

### 7. Salvar Resultados Filtrados
Exporta configurações filtradas para novo CSV:

```powershell
# Salvar melhores configurações
python analyze_results.py --csv grid_results.csv --save-filtered best_configs.csv

# Salvar com filtro de PF >= 1.5
python analyze_results.py --csv grid_results.csv --save-filtered best_configs.csv --pf-min 1.5

# Salvar com mínimo de 10 trades
python analyze_results.py --csv grid_results.csv --save-filtered best_configs.csv --min-trades 10
```

---

## 🎛️ Combinações de Comandos

### 8. Análise Completa com Todos os Recursos

```powershell
python analyze_results.py --csv grid_results.csv --top 30 --min-trades 10 --plot --save-filtered best_results.csv --pf-min 1.3
```

**O que esse comando faz:**
- Mostra top 30 configurações
- Considera apenas configs com 10+ trades
- Gera gráficos de visualização
- Salva resultados filtrados (PF >= 1.3, trades >= 10)

### 9. Análise Focada em Uma Variante

```powershell
python analyze_results.py --csv grid_results.csv --variant base --top 20 --min-trades 15 --plot --save-filtered base_best.csv
```

**Resultado:**
- Analisa apenas estratégia "base"
- Top 20 configurações dessa variante
- Mínimo de 15 trades
- Gráficos focados na variante
- Exporta para `base_best.csv`

### 10. Análise Conservadora (Alta Qualidade)

```powershell
python analyze_results.py --csv grid_results.csv --top 15 --min-trades 20 --pf-min 1.5 --save-filtered robust_configs.csv
```

**Critérios:**
- PF >= 1.5
- Mínimo de 20 trades
- Top 15 mais robustas

### 11. Análise Exploratória (Menos Restritiva)

```powershell
python analyze_results.py --csv grid_results.csv --top 50 --min-trades 3 --pf-min 1.0 --plot
```

**Critérios:**
- PF >= 1.0 (qualquer positivo)
- Mínimo de 3 trades
- Top 50 para explorar mais opções

---

## 📖 Referência Completa de Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `--csv` | string | `grid_results.csv` | Caminho para o arquivo de resultados |
| `--top` | int | `10` | Número de top configurações a exibir |
| `--min-trades` | int | `5` | Número mínimo de trades para considerar |
| `--variant` | string | - | Filtrar por variante: `base`, `rsi` ou `reclaim` |
| `--plot` | flag | False | Gerar gráficos de visualização |
| `--save-filtered` | string | - | Caminho para salvar resultados filtrados |
| `--pf-min` | float | `1.0` | Profit Factor mínimo para filtragem |

---

## 📈 Interpretando os Resultados

### Estatísticas Básicas
```
Total combinations tested: 3888
Variants tested: ['base', 'rsi', 'reclaim']
Combinations with trades: 2456 (63.2%)
```

### Comparação de Variantes
```
--- BASE Strategy ---
Combinations tested: 845
Avg Profit Factor: 1.45
Avg Win Rate: 58.30%
Avg Total PnL: $234.56
```

### Top Configurações
```
#1 - Variant: base | PF: 2.3456 | PnL: $567.89
    Params: dist=0.05, tp=0.10, sl=0.08, atr=2.0, ts=30, ma=200, be=True
    Metrics: Trades=45, WinRate=64.44%, Expectancy=$12.62, MaxDD=$-123.45
```

### Análise de Sensibilidade
Mostra como cada parâmetro afeta a performance:
```
--- DIST ---
             profit_factor                    total_pnl  win_rate  trades
                      mean       std      max      mean      mean   count
dist                                                                      
0.03                1.2345  0.4567  2.1234   123.45    0.5234     972
0.05                1.4567  0.5678  2.4567   234.56    0.5678     972
0.07                1.3456  0.4321  2.2345   198.76    0.5456     972
0.10                1.1234  0.3456  1.9876   145.67    0.5123     972
```

### Configurações Robustas
Identifica setups que atendem múltiplos critérios:
```
Criteria: PF >= 1.5, Trades >= 10, Positive PnL

123 configurations meet the criteria

#1 - BASE | Score: 85.67
    PF: 2.1234, WinRate: 62.22%, PnL: $456.78
    Params: dist=0.05, tp=0.10, sl=0.08, ts=30, ma=200
```

---

## 🎨 Visualizações Detalhadas

Quando usar `--plot`, os seguintes gráficos são gerados:

### 1. Profit Factor vs Total PnL
- **Eixo X**: Profit Factor
- **Eixo Y**: Total PnL em dólares
- **Cores**: Uma cor por variante (base, rsi, reclaim)
- **Uso**: Identificar configurações com alto PF e alto PnL

### 2. Win Rate Distribution
- **Tipo**: Box plot
- **Grupos**: Por variante
- **Uso**: Comparar consistência de win rate entre estratégias

### 3. Profit Factor vs Max Drawdown
- **Eixo X**: Max Drawdown (negativo)
- **Eixo Y**: Profit Factor
- **Cor**: Win Rate (vermelho = baixo, verde = alto)
- **Uso**: Trade-off entre retorno e risco

### 4. Trade Count Distribution
- **Tipo**: Histograma
- **Uso**: Entender frequência de operações

---

## 💡 Casos de Uso Recomendados

### Cenário 1: Primeira Análise (Exploração)
```powershell
python analyze_results.py --csv grid_results.csv --plot
```

### Cenário 2: Identificar Melhores Setups por Variante
```powershell
# Base
python analyze_results.py --csv grid_results.csv --variant base --top 10 --save-filtered base_top10.csv

# RSI
python analyze_results.py --csv grid_results.csv --variant rsi --top 10 --save-filtered rsi_top10.csv

# Reclaim
python analyze_results.py --csv grid_results.csv --variant reclaim --top 10 --save-filtered reclaim_top10.csv
```

### Cenário 3: Buscar Configurações Ultra-Robustas
```powershell
python analyze_results.py --csv grid_results.csv --min-trades 30 --pf-min 2.0 --save-filtered ultra_robust.csv
```

### Cenário 4: Análise Visual Comparativa
```powershell
python analyze_results.py --csv grid_results.csv --min-trades 15 --plot
```

### Cenário 5: Exportar Todos os Setups Viáveis
```powershell
python analyze_results.py --csv grid_results.csv --min-trades 5 --pf-min 1.2 --save-filtered viable_configs.csv
```

---

## 🔄 Workflow Recomendado

### Passo 1: Análise Inicial
```powershell
python analyze_results.py --csv grid_results.csv
```
- Examine estatísticas gerais
- Identifique qual variante teve melhor performance média

### Passo 2: Visualização
```powershell
python analyze_results.py --csv grid_results.csv --plot
```
- Analise os gráficos
- Identifique padrões e outliers

### Passo 3: Foco na Melhor Variante
```powershell
python analyze_results.py --csv grid_results.csv --variant [MELHOR_VARIANTE] --top 20 --min-trades 10
```
- Aprofunde na variante mais promissora

### Passo 4: Exportar Melhores Configurações
```powershell
python analyze_results.py --csv grid_results.csv --variant [MELHOR_VARIANTE] --top 10 --min-trades 15 --pf-min 1.5 --save-filtered final_candidates.csv
```
- Salve os candidatos finais para backtesting forward

### Passo 5: Validação
- Teste as configurações salvas em períodos out-of-sample
- Compare performance entre bull/bear markets
- Verifique robustez com walk-forward analysis

---

## ⚠️ Dicas Importantes

### 1. Overfitting
- ⚠️ Não confie apenas no melhor resultado
- ✅ Procure por **clusters de configurações similares** com boa performance
- ✅ Prefira configurações que aparecem no top 20-50 consistentemente

### 2. Número de Trades
- ⚠️ Configurações com poucos trades podem ter métricas enganosas
- ✅ Use `--min-trades 15` ou mais para análise séria
- ✅ Mais trades = mais significância estatística

### 3. Profit Factor vs PnL Total
- 📊 PF alto + PnL baixo = poucos trades ou baixa exposição
- 📊 PF médio + PnL alto = muitos trades consistentes
- ✅ Balanceie ambas as métricas

### 4. Drawdown
- ⚠️ Não ignore max drawdown mesmo com PF alto
- ✅ Drawdown < 20% do capital é desejável
- ✅ Compare drawdown com expectancy por trade

### 5. Robustez
- ✅ Use a seção "Robust Configurations" como ponto de partida
- ✅ Teste configurações em diferentes períodos
- ✅ Prefira parâmetros que funcionam em múltiplas faixas

---

## 📝 Exemplos Práticos

### Exemplo 1: Análise Rápida
```powershell
python analyze_results.py --csv grid_results.csv
```

### Exemplo 2: Análise Profunda com Visualizações
```powershell
python analyze_results.py --csv grid_results.csv --top 25 --min-trades 12 --plot
```

### Exemplo 3: Filtrar e Exportar Melhores RSI
```powershell
python analyze_results.py --csv grid_results.csv --variant rsi --top 15 --pf-min 1.4 --save-filtered rsi_best.csv
```

### Exemplo 4: Busca por Setup Conservador
```powershell
python analyze_results.py --csv grid_results.csv --min-trades 25 --pf-min 1.8 --save-filtered conservative.csv --plot
```

### Exemplo 5: Comparação Visual de Todas as Variantes
```powershell
python analyze_results.py --csv grid_results.csv --min-trades 10 --plot
```

---

## 🆘 Troubleshooting

### Erro: "File not found"
```
❌ Error: File 'grid_results.csv' not found.
```
**Solução:** Certifique-se que o grid search terminou e gerou o arquivo.

### Erro: "No configurations with trades"
```
No configurations meet the robustness criteria.
```
**Solução:** Reduza os critérios (`--min-trades 3` ou `--pf-min 1.0`)

### Warning: "tqdm not installed"
```
Warning: Matplotlib/Seaborn not installed. Skipping plots.
```
**Solução:** `pip install matplotlib seaborn`

---

## 📞 Suporte e Próximos Passos

Após identificar as melhores configurações:

1. **Teste Individual**: Execute backtest individual com `mr_backtest.py`
2. **Walk-Forward**: Valide em diferentes períodos
3. **Monte Carlo**: Simule variações de performance
4. **Paper Trading**: Teste em ambiente simulado antes de real

---

## 📚 Arquivos Relacionados

- **`mr_backtest.py`** - Executa backtests e grid search
- **`download_btc_csv.py`** - Baixa dados históricos do Binance
- **`README.md`** - Documentação principal do projeto
- **`grid_results.csv`** - Resultados gerados pelo grid search

---

**Desenvolvido para análise quantitativa de estratégias de trading**  
**Versão**: 1.0 | **Data**: Outubro 2025
