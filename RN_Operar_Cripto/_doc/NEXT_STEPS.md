# 🎯 PRÓXIMOS PASSOS - RESUMO EXECUTIVO

## 📊 SITUAÇÃO ATUAL

**Modelo:** `quick_test_final.keras`
- ✅ **Accuracy Test:** 65.46% (era 52.2% baseline)
- ✅ **Melhoria:** +13.3%
- ✅ **Meta atingida:** >60% ✓

**PROBLEMA DETECTADO:**
- 🔴 **Recall "Sobe":** 3% (muito baixo!)
- ✅ **Recall "Não Sobe":** 99% (excelente)
- ⚠️ Modelo está **CONSERVADOR demais** - tem medo de prever "Sobe"

**Por que aconteceu:**
- Classes desbalanceadas no dataset (mais amostras de "Não Sobe")
- Modelo aprendeu a ser conservador para maximizar accuracy geral

---

## 🚀 SOLUÇÕES DISPONÍVEIS

### ⭐ OPÇÃO 1: TREINAR COM BALANCEAMENTO (RECOMENDADO)
```powershell
.venv\Scripts\python.exe src\ml\train_balanced.py
```

**O que faz:**
- ⚖️ Calcula `class_weight` automaticamente
- 🎯 Dá mais peso para classe "Sobe" (minoritária)
- 📈 Aumenta Dropout (0.2 → 0.3) para evitar overfitting
- 🔥 Usa mesma otimização CPU (AMD FX-8300)

**Tempo:** 45-60 minutos

**Resultado esperado:**
- Recall "Sobe": **15-30%** (era 3%)
- Accuracy: **62-67%** (pequena queda aceitável)
- **Modelo mais equilibrado!**

**Quando usar:**
- Você quer que o modelo **detecte mais oportunidades de compra**
- Não tem problema com alguns falsos positivos
- Quer modelo mais agressivo

---

### 🔍 OPÇÃO 2: TESTAR THRESHOLD CUSTOMIZADO
```powershell
.venv\Scripts\python.exe src\scripts\test_threshold.py
```

**O que faz:**
- Testa thresholds: 0.2, 0.3, 0.4, 0.5, 0.6, 0.7
- Mostra Precision, Recall, F1 para cada threshold
- **Descobre melhor threshold** para seus objetivos

**Tempo:** 2-3 minutos

**Resultado esperado:**
- Threshold ideal pode ser **0.3 ou 0.4** (não 0.5)
- Recall "Sobe" pode subir para **10-20%** sem retreinar!
- **Solução rápida sem retreinar**

**Quando usar:**
- Quer resultado RÁPIDO (2 min)
- Não quer esperar retreinamento
- Quer testar diferentes estratégias (agressiva vs conservadora)

---

### 📊 OPÇÃO 3: USAR MODELO ATUAL
**Não fazer nada** - Modelo atual é bom para estratégia conservadora!

**Quando usar:**
- Você prefere **poucos trades** mas com **alta confiança**
- Recall 99% em "Não Sobe" evita perdas
- Estratégia: Só compra quando modelo está MUITO confiante

**Vantagens:**
- ✅ Já está pronto
- ✅ Accuracy 65.46% é boa
- ✅ Evita muitos falsos positivos

**Desvantagens:**
- ❌ Perde muitas oportunidades (Recall 3%)
- ❌ Poucos trades podem não gerar lucro suficiente

---

## 🎯 RECOMENDAÇÃO FINAL

**Para MÁXIMO LUCRO:** Escolha **OPÇÃO 1** (Treinar com Balanceamento)
- Tempo: 45-60 min
- Detecta mais oportunidades
- Modelo mais equilibrado

**Para TESTE RÁPIDO:** Escolha **OPÇÃO 2** (Testar Threshold)
- Tempo: 2-3 min
- Descobre se threshold 0.3 resolve
- Sem retreinamento

**Para CONSERVADOR:** Use **OPÇÃO 3** (Modelo Atual)
- Tempo: 0 min (já pronto)
- Alta confiança, poucos trades
- Evita riscos

---

## 📝 COMANDOS RÁPIDOS

```powershell
# OPÇÃO 1: Treinar com balanceamento (45-60 min)
.venv\Scripts\python.exe src\ml\train_balanced.py

# OPÇÃO 2: Testar threshold (2-3 min)
.venv\Scripts\python.exe src\scripts\test_threshold.py

# OPÇÃO 3: Usar modelo atual
# Modelo já salvo: src/ml/checkpoints/quick_test_final.keras
```

---

## 🎓 PRÓXIMAS ITERAÇÕES (FUTURO)

Após resolver o recall baixo, próximas melhorias:

1. **Bidirectional LSTM** (Priority 3)
   - Melhora contexto temporal
   - +5-10% accuracy

2. **Attention Mechanism** (Priority 4)
   - Foca em partes importantes da sequência
   - +3-5% accuracy

3. **Ensemble (LSTM + GRU)** (Priority 5)
   - Combina múltiplos modelos
   - +5-8% accuracy

4. **Data Augmentation** (Priority 6)
   - Adiciona ruído, mixup temporal
   - Mais dados sintéticos

**Meta final:** 75-80% accuracy

---

## ❓ DÚVIDAS FREQUENTES

**Q: Por que não usar meu GPU AMD?**
A: TensorFlow só funciona com NVIDIA (CUDA). DirectML é experimental e pode ser mais lento que CPU otimizada.

**Q: Posso usar Google Colab?**
A: Sim! Colab tem GPU NVIDIA T4 grátis. Treinamento em 10-15 min. Veja `_doc/CPU_GPU_OPTIMIZATION.md`

**Q: Quanto tempo total para chegar a 75%?**
A: Iterativo. Cada melhoria: 1-2h. Total estimado: 1-2 semanas de experimentação.

**Q: Posso usar esse modelo em produção?**
A: Recomendado resolver recall baixo primeiro. Modelo atual é bom para backtesting conservador.

---

## 📞 SUPORTE

Documentação completa:
- `_doc/TRAINING_IMPROVEMENTS.md` - Guia completo de melhorias
- `_doc/IMPLEMENTATION_SUMMARY.md` - Resumo de implementações
- `_doc/CPU_GPU_OPTIMIZATION.md` - GPU AMD e otimização CPU
- `_doc/STRATEGIES_CONFIG.md` - Configuração de estratégias

**Última atualização:** 2025-10-14
