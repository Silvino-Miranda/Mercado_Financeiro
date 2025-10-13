# 📊 Relatório Executivo - Grid Search Backtest BTCUSDT

**Data da Análise**: 12 de Outubro de 2025  
**Dataset**: BTCUSDT Daily  
**Total de Combinações Testadas**: 3,888  
**Período**: Grid Search completo de 3 variantes de estratégia

---

## 🎯 Resumo Executivo

### Performance Geral
- ✅ **Combinações com trades**: 3,348 (86.1%)
- ❌ **Combinações sem trades**: 540 (13.9%)
- 🏆 **Melhor PnL Total**: $1,232.24
- 📉 **Pior Drawdown**: $-1,116.16

### Conclusão Principal
**A estratégia BASE (filtro de inclinação MA) claramente supera as outras duas variantes**, com:
- Profit Factor médio de **1.03** (único positivo)
- Win Rate médio de **37.20%**
- PnL médio de **-$44.82** (melhor resultado negativo)

---

## 🥇 TOP 3 Configurações Mais Robustas

### #1 - Configuração Campeã ⭐
```
Variante: BASE
Parâmetros:
  - dist_below_ma_pct: 0.05 (5% abaixo da MA)
  - tp_pct: 0.10 (10% take profit)
  - sl_pct: 0.10 (10% stop loss)
  - time_stop: 30 ou 45 barras
  - ma_len: 220
  - breakeven: False
  - atr_mult: Qualquer (1.5 ou 2.0)

Performance:
  - Profit Factor: 2.63
  - Win Rate: 73.08%
  - Total PnL: $1,159.24
  - Max Drawdown: ~$-162
  - Trades/Ano: ~6-7
  - Expectancy: ~$44-46 por trade
```

### #2 - Configuração Runner-up 🥈
```
Variante: BASE
Parâmetros:
  - dist_below_ma_pct: 0.03 (3% abaixo da MA)
  - tp_pct: 0.10
  - sl_pct: 0.10
  - time_stop: 30 ou 45
  - ma_len: 220
  - breakeven: False

Performance:
  - Profit Factor: 2.32
  - Win Rate: 66.67%
  - Total PnL: $1,232.24 (MELHOR PNL TOTAL!)
  - Trades: Mais frequente que #1
```

### #3 - Configuração Bronze 🥉
```
Variante: BASE
Parâmetros:
  - dist_below_ma_pct: 0.07 (7% abaixo da MA)
  - tp_pct: 0.10
  - sl_pct: 0.10
  - time_stop: 20, 30 ou 45
  - ma_len: 220
  - breakeven: False

Performance:
  - Profit Factor: 2.59-2.61
  - Win Rate: 72.73%
  - Total PnL: $965-976
```

---

## 📈 Comparação Entre Variantes

### 1. BASE Strategy (Filtro de Inclinação MA) ✅ VENCEDOR
- **Conceito**: Compra quando preço < MA200 E MA200 está subindo
- **Profit Factor**: 1.03 (único positivo)
- **Win Rate**: 37.20%
- **PnL Médio**: -$44.82 (menos negativo)
- **Trades/Ano**: 5.26
- **Melhor Config**: PF=2.78, PnL=$819
- **Status**: ✅ **RECOMENDADO**

### 2. RECLAIM Strategy (Reconquista da MA200)
- **Conceito**: Compra quando preço reconquista MA200 após estar abaixo
- **Profit Factor**: infinito (muitas configs com 0 perdas)
- **Win Rate**: 22.13%
- **PnL Médio**: -$70.45
- **Trades/Ano**: 0.59 (MUITO BAIXO)
- **Problema**: Pouquíssimos sinais, muitas configs sem trades
- **Status**: ⚠️ **NÃO RECOMENDADO** (sinais muito raros)

### 3. RSI Strategy (Cruzamento RSI) ❌ PIOR
- **Conceito**: Compra quando preço < MA200 E RSI cruza acima de 30
- **Profit Factor**: 0.45 (menos de 1 = perdedor)
- **Win Rate**: 20.39% (MUITO BAIXO)
- **PnL Médio**: -$183.71 (PIOR RESULTADO)
- **Trades/Ano**: 1.57
- **Status**: ❌ **NÃO RECOMENDADO**

---

## 🔍 Insights de Sensibilidade de Parâmetros

### Parâmetros Mais Importantes (BASE Strategy)

#### 1. MA Length (CRÍTICO) 🎯
- **MA=220**: MELHOR! (PF médio 0.69, PnL -$50)
- **MA=200**: Neutro (PF médio 0.60, PnL -$118)
- **MA=180**: PIOR (PF médio inf*, PnL -$154)
- **Recomendação**: Use **MA=220**

#### 2. Distance Below MA (IMPORTANTE)
- **dist=0.10 (10%)**: MELHOR! (PF 0.77, mais conservador)
- **dist=0.05 (5%)**: Bom (PF 0.58)
- **dist=0.07 (7%)**: Bom (PF 0.57)
- **dist=0.03 (3%)**: Muitos sinais, mas menos seletivo
- **Recomendação**: Use **0.05 a 0.10**

#### 3. Take Profit / Stop Loss
- **TP=0.10, SL=0.10**: Balanceado e eficaz ✅
- **TP=0.12, SL=0.08**: Também funciona bem
- **Recomendação**: Mantenha **TP=SL=0.10** (simétrico)

#### 4. Time Stop (MENOS IMPORTANTE)
- Pouca diferença entre 20, 30 ou 45 barras
- **Recomendação**: Use **30 barras** (meio-termo)

#### 5. ATR Multiplier (NEUTRO)
- 1.5 vs 2.0: Diferença mínima
- **Recomendação**: Use **1.5** (mais conservador)

#### 6. Breakeven (SURPREENDENTE) ⚠️
- **Breakeven=False**: Melhores resultados!
- **Breakeven=True**: Piora performance
- **Conclusão**: O breakeven pode estar cortando winners prematuramente
- **Recomendação**: **Desabilitar breakeven**

---

## 💡 Padrões Identificados

### Configurações Vencedoras Compartilham:
1. ✅ **Sempre variante BASE**
2. ✅ **Sempre MA=220**
3. ✅ **Sempre breakeven=False**
4. ✅ **Sempre TP e SL entre 8-12%**
5. ✅ **Distance 3-10% abaixo da MA**
6. ✅ **Win Rate entre 65-73%**
7. ✅ **Profit Factor > 2.3**

### Red Flags a Evitar:
1. ❌ Variante RSI (consistentemente negativa)
2. ❌ MA=180 (pior performance)
3. ❌ Breakeven=True (degrada performance)
4. ❌ Configurações com < 10 trades (pouca significância)

---

## 📊 Análise de Robustez

### Configurações Robustas Encontradas: 244
*Critérios: PF ≥ 1.5, Trades ≥ 15, PnL > 0*

**Observações importantes:**
1. 🎯 **Todas** as 244 configurações robustas usam **variante BASE**
2. 🎯 **Maioria absoluta** usa **MA=220**
3. 🎯 **Todas** têm **breakeven=False**
4. 🎯 Cluster de parâmetros similares indica robustez real (não overfitting)

---

## ⚖️ Trade-offs Identificados

### Frequência vs Qualidade
- **dist=0.03**: Mais trades (~12/ano), mas menor win rate (~67%)
- **dist=0.10**: Menos trades (~5/ano), mas maior win rate (~72%)
- **Recomendação**: Prefira **qualidade (dist=0.10)** sobre quantidade

### Risco vs Retorno
- Configurações com **melhor PF** têm drawdowns moderados ($-100 a $-163)
- Não há configurações com alto retorno E baixo drawdown
- **Expectancy** de $41-48 por trade é consistente nas top 10

---

## 🎯 Recomendação Final

### Configuração Recomendada para Trading Real:

```python
python mr_backtest.py --csv BTCUSDT_daily.csv \
  --variant base \
  --dist_below_ma_pct 0.05 \
  --tp_pct 0.10 \
  --sl_pct 0.10 \
  --atr_mult 1.5 \
  --time_stop 30 \
  --ma_len 220 \
  --no_breakeven
```

**Expectativa de Performance:**
- Profit Factor: ~2.5-2.6
- Win Rate: ~70-73%
- Expectancy: ~$45 por trade
- Trades/Ano: ~6-7 (baixa frequência)
- Max Drawdown esperado: ~$150-200

---

## ⚠️ Avisos e Limitações

### 1. Overfitting Risk
- ⚠️ Grid search sempre tem risco de overfitting
- ✅ **Mitigação**: Cluster de configs similares com boa performance sugere robustez
- ✅ **Próximo passo**: Walk-forward analysis em períodos out-of-sample

### 2. Baixa Frequência de Trades
- ⚠️ 6-7 trades/ano = pouca amostra estatística
- ⚠️ Período de 1+ ano sem trades é possível
- ✅ **Consideração**: Esta é uma estratégia de **paciência**

### 3. Performance em Bull vs Bear
- ❓ Não sabemos se funciona igual em diferentes regimes de mercado
- ✅ **Próximo passo**: Análise por período (2020-21 bull, 2022 bear, 2023-24 recovery)

### 4. Custos de Transação
- ✅ Já incluídos (10 bps fees + 5 bps slippage)
- ✅ Resultados são realistas para exchanges principais

### 5. Slippage em Execuções Reais
- ⚠️ Em momentos de alta volatilidade, slippage pode ser > 5 bps
- ⚠️ Gap downs podem resultar em stops piores que calculado

---

## 📋 Próximos Passos Recomendados

### 1. Validação (CRÍTICO)
```bash
# Teste a melhor config em período específico
python mr_backtest.py --csv BTCUSDT_daily.csv \
  --variant base --dist_below_ma_pct 0.05 --tp_pct 0.10 --sl_pct 0.10 \
  --ma_len 220 --no_breakeven
```

### 2. Walk-Forward Analysis
- Dividir dados em períodos (ex: 2020, 2021, 2022, 2023, 2024)
- Testar a config campeã em cada período separadamente
- Verificar consistência

### 3. Monte Carlo Simulation
- Simular 1000+ sequências de trades
- Estimar distribuição de drawdowns possíveis
- Calcular risk of ruin

### 4. Análise de Trades Individuais
```bash
# Ver arquivo trades.csv gerado
python mr_backtest.py --csv BTCUSDT_daily.csv --variant base \
  --dist_below_ma_pct 0.05 --tp_pct 0.10 --sl_pct 0.10 --ma_len 220 --no_breakeven
```
- Examinar cada trade
- Identificar padrões de winners vs losers
- Verificar se há viés temporal

### 5. Comparação com Buy & Hold
- Calcular retorno de simplesmente comprar e segurar BTC
- Comparar Sharpe Ratio
- Justificar a complexidade da estratégia

---

## 📁 Arquivos Gerados

1. ✅ **grid_results.csv** - Todos os 3,888 resultados
2. ✅ **best_robust_configs.csv** - 244 configurações robustas filtradas
3. ✅ **grid_results_analysis.png** - Visualizações gráficas
4. ✅ **Este relatório** - Análise executiva

---

## 🎓 Conclusões Estratégicas

### O Que Funcionou:
1. ✅ **Reversão à média funciona** quando bem parametrizada
2. ✅ **Filtro de tendência** (MA slope) é superior a RSI
3. ✅ **Médias móveis mais longas** (220) são melhores que curtas
4. ✅ **Simplicidade vence** (breakeven piora, não melhora)
5. ✅ **Stops simétricos** (TP=SL) funcionam bem

### O Que Não Funcionou:
1. ❌ **RSI como filtro** não adiciona valor
2. ❌ **RECLAIM** gera poucos sinais demais
3. ❌ **Breakeven automático** corta winners cedo demais
4. ❌ **MAs curtas** (180) são menos efetivas
5. ❌ **Alta frequência de trades** não compensa a menor qualidade

### Filosofia da Estratégia:
> **"Esta é uma estratégia de PACIÊNCIA e QUALIDADE sobre QUANTIDADE"**
> 
> Espera por configurações técnicas ideais (preço muito abaixo de MA ascendente)
> e então entra com alta convicção. Poucos trades, mas bem selecionados.

---

**Desenvolvido por**: Sistema de Backtest Mean-Reversion  
**Data**: 12 de Outubro de 2025  
**Status**: ✅ Análise Completa - Pronto para Validação
