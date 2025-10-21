# ⚠️ ANÁLISE CRÍTICA - 75 ÉPOCAS (BLOCO 1/6)

## 📊 Comparação: 50 vs 75 Épocas

| Métrica | 50 Épocas | 75 Épocas | Variação |
|---------|-----------|-----------|----------|
| **Train Loss** | 0.000461 | 0.000451 | ✅ -2% (melhor) |
| **Val Loss** | 0.000327 | 0.000092 | ✅ -72% (muito melhor!) |
| **Val MAE** | 0.0164 | 0.0066 | ✅ -60% (muito melhor!) |
| **MAE ($)** | $21,635 | $22,998 | ❌ +6.3% (pior) |
| **MAPE** | 20.79% | 21.95% | ❌ +5.6% (pior) |
| **R² Score** | -0.86 | -1.08 | ❌ -26% (muito pior) |
| **Backtest Return** | **+6.93%** | **-34.70%** | 🚨 **-41.6 p.p. (COLAPSO!)** |
| **Sharpe Ratio** | 0.29 | -1.44 | 🚨 **-597% (DESASTRE!)** |
| **Max Drawdown** | -27.40% | -39.57% | ❌ -12.2 p.p. (muito pior) |
| **Total Trades** | 18 | 320 | 🚨 **+1678% (OVER-TRADING!)** |

---

## 🔍 DIAGNÓSTICO CRÍTICO

### ❌ **Problema Principal: OVER-TRADING EXTREMO**

**O que aconteceu:**
- Modelo passou de **18 trades seletivos** para **320 trades indiscriminados**
- Taxa de trades: 0.04/dia → 0.72/dia (18x mais frequente!)
- Custos explodiram: 0.27% (18 trades) → **4.8% (320 trades)**

**Por que isso é catastrófico:**
- Cada trade custa 15 bps (10 fee + 5 slippage)
- 320 trades × 15 bps × 2 (entrada + saída) = **96 bps × 320 = ~48% em custos!**
- Modelo está "churning" (virando posição sem critério)

---

### 📉 **Overfitting Paradoxal**

**Métricas de Treino (MELHORARAM):**
- ✅ val_loss: 0.000327 → 0.000092 (-72%)
- ✅ val_mae: 0.0164 → 0.0066 (-60%)

**Métricas de Teste (PIORARAM):**
- ❌ MAE: $21k → $23k (+6%)
- ❌ R²: -0.86 → -1.08 (-26%)

**Backtest (COLAPSOU):**
- 🚨 Retorno: +6.93% → -34.70% (-41.6 p.p.)

**Interpretação:**
1. Modelo "decorou" padrões do validation set
2. Mas esses padrões NÃO generalizam para test set
3. Pior: modelo ficou "overconfident" → trada muito mais
4. Threshold de 20 bps não é mais respeitado (predições muito voláteis)

---

### 📊 **Análise de Predições**

**50 Épocas:**
- Média Predita: $71,667 (77% do real)
- Std Predita: $6,242
- Predições conservadoras e estáveis
- 18 trades apenas quando "muito confiante"

**75 Épocas:**
- Média Predita: $69,691 (75% do real)
- Std Predita: $4,564 (menor!)
- Predições ainda mais comprimidas
- Mas threshold de 20 bps é cruzado 320 vezes!

**Paradoxo:**
- Std diminuiu (predições mais concentradas)
- Mas trades aumentaram 18x!
- **Causa:** Predições oscilam rapidamente em torno da média
- Cruzam threshold constantemente sem convicção real

---

## 🎯 DECISÃO CRÍTICA

### ❌ **NÃO CONTINUAR com 75 épocas!**

**Razões:**
1. Backtest catastrófico (-34% vs +6.93%)
2. Over-trading extremo (320 trades)
3. Sharpe negativo (-1.44 vs +0.29)
4. Drawdown inaceitável (-39.57%)

### ✅ **REVERTER para 50 épocas**

**Ações imediatas:**
1. Restaurar modelo de 50 épocas
2. NÃO treinar mais épocas (overfitting confirmado)
3. Focar em outras otimizações:
   - **Threshold optimization** (testar 30, 50, 100 bps)
   - **Feature engineering** (adicionar RSI, ATR)
   - **Ensemble** (múltiplos modelos)

---

## 📈 CURVA DE TREINAMENTO - ANÁLISE

### **Loss Progression (Últimas 25 Épocas)**

**Train Loss:**
- Época 50: 0.000464
- Época 60: 0.000456
- Época 70: 0.000454
- Época 75: 0.000451
- **Tendência:** Convergindo lentamente (ganho marginal)

**Val Loss:**
- Época 50: 0.000327
- Época 60: 0.000274
- Época 70: 0.000144
- Época 75: 0.000092
- **Tendência:** Caindo rápido (sinal de overfitting!)

**Gap Train-Val:**
- Época 50: 0.000464 - 0.000327 = 0.000137 (30% gap)
- Época 75: 0.000451 - 0.000092 = 0.000359 (390% gap!)
- **Interpretação:** Val loss artificialmente baixo = overfitting no validation set

---

## 🧠 LIÇÕES APRENDIDAS

### **1. Val Loss Baixo ≠ Bom Modelo**
- Val loss de 0.000092 parece excelente
- Mas backtest mostra overfitting
- **Conclusão:** Validation set não representa test set

### **2. Over-training Mata Trading**
- Mais épocas = mais overfitting
- Modelo "decora" padrões que não se repetem
- Fica overconfident → trada muito → custos explodem

### **3. Threshold Sozinho Não Basta**
- 20 bps deveria filtrar trades
- Mas predições oscilam rápido → cruza threshold sempre
- **Solução:** Adicionar smoothing (média móvel das predições)

### **4. Early Stopping Falhou**
- Patience de 10 épocas não detectou overfitting
- **Razão:** Val loss continuou caindo (enganoso)
- **Solução:** Monitorar backtest a cada N épocas!

---

## 🚀 PRÓXIMOS PASSOS RECOMENDADOS

### **PARAR TREINAMENTO**
❌ NÃO treinar até 200 épocas
✅ 50 épocas é o sweet spot

### **PRIORIDADE 1: Threshold Optimization**
Testar thresholds maiores para reduzir over-trading:
```bash
# Threshold 30 bps
uv run python -m src.ml_v3_arch.cli backtest --threshold-bps 30

# Threshold 50 bps
uv run python -m src.ml_v3_arch.cli backtest --threshold-bps 50

# Threshold 100 bps
uv run python -m src.ml_v3_arch.cli backtest --threshold-bps 100
```

**Meta:** Reduzir trades de 320 para 20-50

### **PRIORIDADE 2: Prediction Smoothing**
Adicionar média móvel nas predições (3-5 candles):
```python
# Evitar oscilações rápidas
predictions_smoothed = predictions.rolling(window=3).mean()
```

### **PRIORIDADE 3: Feature Engineering**
- RSI(14): detectar overbought/oversold
- ATR: volatilidade adaptativa
- Volume Profile: confirmação de trades

**Meta:** MAE < $18k, Sharpe > 1.0 com 50 épocas

---

## ✅ CONCLUSÃO

**Status Final:**
- ✅ 50 épocas: **MELHOR MODELO** (+6.93%, Sharpe 0.29, 18 trades)
- ❌ 75 épocas: **OVERFITTING** (-34.70%, Sharpe -1.44, 320 trades)

**Decisão:**
- Reverter para 50 épocas
- Parar treinamento de épocas adicionais
- Focar em threshold optimization e feature engineering

**Próxima sessão:**
- Testar thresholds: 30, 50, 100 bps
- Implementar prediction smoothing
- Adicionar features avançadas (RSI, ATR)

---

**Data:** 20/10/2025 10:35 BRT  
**Autor:** Copilot + Silvino Miranda  
**Status:** 🚨 **ALERTA DE OVERFITTING - TREINAMENTO SUSPENSO**
