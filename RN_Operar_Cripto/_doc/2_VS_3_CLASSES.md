# 🎯 COMPARAÇÃO: 2 CLASSES vs 3 CLASSES

## 📊 VISÃO GERAL

### **2 Classes (Binário)**
- **Classes:** Sobe (1) / Não Sobe (0)
- **Estratégia:** Comprar quando prevê "Sobe", Hold quando prevê "Não Sobe"
- **Problema:** "Não Sobe" mistura movimento lateral + queda

### **3 Classes (Multiclasse)** ⭐ **RECOMENDADO**
- **Classes:** ALTA (2) / LATERAL (1) / BAIXA (0)
- **Estratégia:** Comprar (ALTA), Esperar (LATERAL), Vender/Short (BAIXA)
- **Vantagem:** Identifica consolidação e permite estratégias de venda

---

## 🆚 COMPARAÇÃO DETALHADA

| Aspecto | 2 Classes | 3 Classes |
|---------|-----------|-----------|
| **Classes** | Sobe / Não Sobe | ALTA / LATERAL / BAIXA |
| **Accuracy esperada** | 65-70% | 55-60% (mais difícil) |
| **Random guess** | 50% | 33.3% |
| **Estratégias possíveis** | Long apenas | Long + Short + Hold |
| **Identifica consolidação** | ❌ Não | ✅ Sim (classe LATERAL) |
| **Permite venda/short** | ❌ Não | ✅ Sim (classe BAIXA) |
| **Útil para trading real** | ⚠️ Limitado | ✅ Muito útil |
| **Complexidade** | Mais simples | Um pouco mais complexo |
| **Tempo de treino** | 45-60 min | 45-60 min (igual) |

---

## 📈 MODELO ATUAL (2 CLASSES)

### **Resultados:**
```
Accuracy Test: 65.46%
Melhoria: +13.3% vs baseline (52.2%)

PROBLEMA DETECTADO:
- Recall "Sobe": 3% (muito baixo!)
- Recall "Não Sobe": 99% (muito alto)
- Modelo conservador demais
```

### **Por que isso aconteceu?**
A classe "Não Sobe" inclui:
- 🔴 Movimentos de **BAIXA** (cai muito)
- 🟡 Movimentos **LATERAIS** (fica parado)

O modelo aprendeu que é "seguro" prever "Não Sobe" sempre, pois:
- Lateral + Baixa = maioria dos casos
- Accuracy fica alta mesmo prevendo errado nas subidas

---

## 🎯 MODELO PROPOSTO (3 CLASSES)

### **Definição das classes:**

```python
# Threshold: 0.5%
retorno_futuro = (preço_futuro - preço_atual) / preço_atual * 100

if retorno_futuro < -0.5%:
    classe = 0  # BAIXA (cai > 0.5%)
    
elif -0.5% <= retorno_futuro <= +0.5%:
    classe = 1  # LATERAL (movimento pequeno)
    
else:  # retorno_futuro > +0.5%
    classe = 2  # ALTA (sobe > 0.5%)
```

### **Vantagens:**

1. ✅ **Identifica consolidação**
   - Classe LATERAL = mercado de lado
   - Evita entrar em falsos breakouts

2. ✅ **Permite estratégias de venda**
   - Classe BAIXA = oportunidade de short
   - Mais lucro em mercado de baixa

3. ✅ **Mais realista**
   - Reflete melhor o comportamento real do mercado
   - 3 estados distintos e acionáveis

4. ✅ **Resolve problema do recall baixo**
   - Modelo não pode mais "esconder" tudo em "Não Sobe"
   - Forçado a diferenciar LATERAL de BAIXA

### **Distribuição esperada dos dados:**

```
Classe 0 (BAIXA):    ~30-35% (quedas significativas)
Classe 1 (LATERAL):  ~35-40% (maioria - consolidação)
Classe 2 (ALTA):     ~30-35% (subidas significativas)
```

### **Estratégia de trading:**

```python
if pred_class == 2 and confidence > 0.6:
    # ALTA com alta confiança
    acao = "COMPRAR (Long)"
    
elif pred_class == 0 and confidence > 0.6:
    # BAIXA com alta confiança
    acao = "VENDER / SHORT"
    
elif pred_class == 1 or confidence < 0.6:
    # LATERAL ou baixa confiança
    acao = "NÃO OPERAR (esperar)"
```

---

## 🚀 SCRIPTS DISPONÍVEIS

### **OPÇÃO 1: Melhorar modelo binário (2 classes)**

```powershell
# Com class_weight para balancear
.venv\Scripts\python.exe src\ml\train_balanced.py
```

**Quando usar:**
- Você só quer estratégia de compra (long)
- Não tem interesse em vender/short
- Quer manter simplicidade

**Resultado esperado:**
- Recall "Sobe": 15-30% (melhora do 3%)
- Accuracy: 62-67% (pequena queda aceitável)

---

### **OPÇÃO 2: Modelo multiclasse (3 classes)** ⭐ **RECOMENDADO**

```powershell
# Classificação em 3 classes
.venv\Scripts\python.exe src\ml\train_multiclass.py
```

**Quando usar:**
- Você quer estratégias completas (long + short + hold)
- Quer identificar consolidação (lateral)
- Quer modelo mais realista para trading

**Resultado esperado:**
- Accuracy: 55-60% (55% é excelente para 3 classes!)
- Recall balanceado entre as 3 classes
- Modelo mais útil para trading real

**Por que accuracy menor é OK:**
- Random guess = 33.3% (vs 50% em binário)
- 55% = **65% melhor** que random (55/33.3 = 1.65x)
- Em binário: 65% = **30% melhor** que random (65/50 = 1.30x)
- **Conclusão: 55% em 3 classes é MELHOR que 65% em 2 classes!**

---

## 📝 RECOMENDAÇÃO FINAL

### 🥇 **MELHOR OPÇÃO: 3 Classes (Multiclasse)**

**Razões:**
1. ✅ Mais útil para trading real
2. ✅ Permite long + short
3. ✅ Identifica consolidação
4. ✅ Resolve problema de recall baixo
5. ✅ Mesma complexidade de treino

**Execute:**
```powershell
.venv\Scripts\python.exe src\ml\train_multiclass.py
```

**Tempo:** 45-60 minutos (mesmo que binário)

---

### 🥈 **OPÇÃO ALTERNATIVA: 2 Classes Balanceado**

**Razões:**
1. ✅ Mais simples de interpretar
2. ✅ Accuracy pode ser maior
3. ✅ Bom para estratégia conservadora (só long)

**Execute:**
```powershell
.venv\Scripts\python.exe src\ml\train_balanced.py
```

**Tempo:** 45-60 minutos

---

## 🎓 PRÓXIMOS PASSOS (APÓS TREINO)

Independente da escolha:

1. **Avaliar resultados**
   - Confusion matrix
   - Precision/Recall por classe
   - F1-Score

2. **Testar threshold customizado**
   - Usar probabilidades ao invés de classes hard
   - Encontrar melhor threshold de confiança

3. **Backtesting**
   - Simular estratégia em dados históricos
   - Calcular retorno, Sharpe ratio, drawdown

4. **Melhorar modelo (se necessário)**
   - Bidirectional LSTM
   - Attention mechanism
   - Ensemble (LSTM + GRU)

---

## ❓ PERGUNTAS FREQUENTES

**Q: Por que accuracy menor em 3 classes é aceitável?**
A: Random guess = 33.3%. Qualquer accuracy > 40% já é útil. 55% é EXCELENTE!

**Q: E se eu quiser testar ambos?**
A: Pode! Execute os dois (90-120 min total) e compare resultados.

**Q: Posso ajustar os thresholds (0.5%)?**
A: Sim! No script, altere `threshold_up` e `threshold_down`. Sugestões:
- Mais agressivo: 0.3% (mais trades)
- Mais conservador: 1.0% (menos trades, movimentos maiores)

**Q: Como sei qual classe o modelo prevê?**
A: Modelo retorna probabilidades para cada classe:
```python
y_pred_proba = model.predict(X_new)
# Exemplo: [0.15, 0.25, 0.60] = 60% ALTA, 25% LATERAL, 15% BAIXA
y_pred_class = np.argmax(y_pred_proba)  # = 2 (ALTA)
```

**Q: Posso usar probabilidades ao invés de classes?**
A: SIM! Recomendado:
```python
if y_pred_proba[2] > 0.6:  # 60% confiança em ALTA
    comprar()
elif y_pred_proba[0] > 0.6:  # 60% confiança em BAIXA
    vender()
else:  # Baixa confiança ou LATERAL
    não_operar()
```

---

## 📞 COMANDOS RÁPIDOS

```powershell
# RECOMENDADO: 3 classes (ALTA/LATERAL/BAIXA)
.venv\Scripts\python.exe src\ml\train_multiclass.py

# ALTERNATIVA: 2 classes balanceado
.venv\Scripts\python.exe src\ml\train_balanced.py

# Testar threshold (depois do treino)
.venv\Scripts\python.exe src\scripts\test_threshold.py
```

**Última atualização:** 2025-10-14
