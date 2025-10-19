# 🎯 Recomendações para Treino Production

## 📋 Checklist Pré-Treino

Antes de iniciar treino de 50+ épocas (que levará ~3 horas), verifique:

- [ ] ✅ Pipeline testado com 2 épocas (funcionou?)
- [ ] ✅ Preprocessor sendo salvo corretamente
- [ ] ✅ Evaluate mostrando métricas realistas (MAE ~$20k)
- [ ] ✅ Backtest executando trades (mesmo que perdendo)
- [ ] ✅ CSV com 142,665 linhas carregando sem erros
- [ ] ✅ Espaço em disco (modelo ~50MB, artifacts ~200MB)
- [ ] ✅ Máquina não vai desligar/hibernar nas próximas 3h

---

## 🚀 Comando Recomendado

### **Configuração Ótima (baseada em testes)**
```bash
uv run python -m src.ml_v3_arch.cli train \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 50 \
  --units 128 \
  --lookback 60 \
  --batch-size 64 \
  --lr 0.001 \
  --model-type lstm
```

### **Por quê esses parâmetros?**

**Epochs: 50**
- 2 épocas: loss 0.0011 → 0.0016 (ainda aprendendo)
- 50 épocas: esperado < 0.0005 (convergência)
- Trade-off: 10 épocas = pouco, 100 épocas = overfitting

**Units: 128**
- 64 units: rápido mas capacidade limitada
- 128 units: sweet spot (complexidade vs generalização)
- 256 units: risco de overfitting com apenas 100k amostras

**Lookback: 60**
- 60 candles × 30min = 30 horas de histórico
- Captura ciclos intraday + interday
- Menos que 30: muito pouco contexto
- Mais que 90: muito ruído

**Batch Size: 64**
- 32: muito lento
- 64: equilíbrio perfeito
- 128: pode perder detalhes (gradientes muito agregados)

**Learning Rate: 0.001**
- 0.0001: muito lento (não converge em 50 épocas)
- 0.001: padrão e eficaz
- 0.01: muito rápido (pode oscilar)

---

## 📊 Expectativas Realistas

### **Durante o Treino (monitorar):**

**Epoch 1:**
```
loss: 0.0020 - mae: 0.0269 - val_loss: 0.0010 - val_mae: 0.0247
```

**Epoch 10:**
```
loss: 0.0008 - mae: 0.0180 - val_loss: 0.0009 - val_mae: 0.0195
```

**Epoch 30:**
```
loss: 0.0004 - mae: 0.0120 - val_loss: 0.0006 - val_mae: 0.0145
```

**Epoch 50 (esperado):**
```
loss: 0.0003 - mae: 0.0095 - val_loss: 0.0005 - val_mae: 0.0130
```

### **Métricas Finais (Evaluate):**

| Métrica | Atual (2 épocas) | Meta (50 épocas) |
|---------|------------------|------------------|
| MAE | $20,945 | **< $15,000** |
| MAPE | 20.50% | **< 15%** |
| R² Score | -0.58 | **> 0.60** |
| Hit Rate | 49.29% | **> 55%** |

### **Backtest:**

| Métrica | Atual (2 épocas) | Meta (50 épocas) |
|---------|------------------|------------------|
| Retorno | -4.98% | **> +10%** |
| Sharpe | -0.40 | **> 1.0** |
| Trades | 4 | **> 20** |
| Win Rate | 25% | **> 50%** |

---

## ⏱️ Tempo Estimado

**Baseado em hardware:**
- **CPU (sem GPU):** ~3-4 horas
- **GPU (NVIDIA):** ~1-2 horas
- **M1/M2 Mac:** ~2-3 horas

**Breakdown:**
```
Época 1-10:  ~40min  (mais lento - warm up)
Época 11-30: ~60min  (velocidade constante)
Época 31-50: ~60min  (mesma velocidade)
Total:       ~160min (~2h40min)
```

**Dica:** Rode durante a noite ou enquanto trabalha em outra coisa.

---

## 📈 Monitoramento Durante Treino

### **Bons Sinais:**
✅ `loss` caindo constantemente  
✅ `val_loss` próximo de `loss` (diff < 30%)  
✅ `mae` diminuindo  
✅ Epochs progredindo sem errors  

### **Red Flags:**
❌ `val_loss` > 2× `loss` (overfitting severo)  
❌ `loss` oscilando muito (learning rate muito alta)  
❌ `loss` não caindo (underfitting ou bug)  
❌ `loss > 1.0` (normalização errada - BUG GRAVE)  

### **Quando Interromper:**

**Ctrl+C é seguro!**
- Checkpoint salvo a cada época
- Pode retomar com `--resume`

**Cenários para interromper:**
1. `val_loss` aumentando por 5+ épocas seguidas
2. `loss` não mudando por 10+ épocas
3. Erro de memória (reduzir batch_size)

---

## 🔄 Continue Training (se necessário)

Se treino foi interrompido ou quer mais épocas:

```bash
# Modelo atual: 50 épocas
# Quer adicionar: +20 épocas

uv run python -m src.ml_v3_arch.cli train \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 20 \
  --resume
```

**Output esperado:**
```
🔄 MODO RESUME: Carregando modelo e histórico anteriores...
✅ Modelo carregado: artifacts\v3\models\lstm_v3.keras
✅ Histórico carregado: 50 épocas anteriores

Épocas TOTAIS: 50 (anteriores) + 20 (novas) = 70
```

---

## 🎯 Otimização Pós-Treino

### **1. Se R² Score ainda < 0.50:**

**Possíveis causas:**
- Modelo muito simples (aumentar units para 256)
- Lookback inadequado (testar 90)
- Features insuficientes (adicionar RSI, ATR, etc.)

**Ação:**
```bash
# Retreinar com mais capacidade
uv run python -m src.ml_v3_arch.cli train \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 50 \
  --units 256 \
  --lookback 90
```

### **2. Se Backtest não opera (< 10 trades):**

**Causa:** Threshold muito conservador

**Ação:**
```bash
# Reduzir threshold para 10 bps
uv run python -m src.ml_v3_arch.cli backtest \
  --csv data/BTCUSDT_30m_full.csv \
  --capital 10000 \
  --threshold-bps 10
```

### **3. Se Overfitting (val_loss >> loss):**

**Ações:**
1. Adicionar Dropout:
   ```bash
   # Não implementado ainda, mas é o próximo passo
   # Dropout atual: 0.3 (fixo no código)
   # Ideal: 0.4-0.5 para overfitting
   ```

2. Usar EarlyStopping:
   ```python
   # Já implementado! Patience = 10 épocas
   # Para automaticamente se val_loss não melhorar
   ```

3. Regularização L2:
   ```python
   # A implementar no futuro
   ```

---

## 📁 Backup Antes de Retreinar

**IMPORTANTE:** Treinar sobrescreve modelo anterior!

```powershell
# Backup manual
Copy-Item artifacts\v3\models\lstm_v3.keras artifacts\v3\models\lstm_v3_backup.keras
Copy-Item artifacts\v3\preprocessors\preprocessor_lstm_v3.pkl artifacts\v3\preprocessors\preprocessor_backup.pkl
Copy-Item artifacts\v3\logs\history_lstm_v3.json artifacts\v3\logs\history_backup.json
```

Ou usar timestamps (configurar `add_timestamp=True` no código).

---

## 🎓 Próximos Experimentos

Após treino production bem-sucedido (R² > 0.60):

### **1. Feature Engineering:**
- RSI (14)
- Stochastic Oscillator
- ATR (Average True Range)
- Volume analysis
- Order book features

### **2. Arquiteturas Alternativas:**
- GRU (mais rápido, pode ser melhor)
- Bidirectional LSTM
- Attention mechanisms
- Transformer-based

### **3. Ensemble:**
- Treinar 3-5 modelos com seeds diferentes
- Média das predições
- Tipicamente melhora 5-10% nas métricas

### **4. Walk-Forward Optimization:**
- Retreinar modelo a cada N semanas
- Adapta a mudanças de regime de mercado
- Mais realista que treino fixo

---

## 🚨 Troubleshooting Production

### **Erro de Memória:**
```
OOM (Out of Memory) during training
```
**Solução:**
```bash
# Reduzir batch_size
--batch-size 32

# Ou reduzir units
--units 64
```

### **Treino muito lento (> 6h):**
**Causas possíveis:**
- CPU fraco (sem GPU)
- Antivírus escaneando arquivos
- Background processes

**Solução:**
- Fechar programas pesados
- Desabilitar antivírus temporariamente
- Usar GPU se disponível

### **Loss explodindo (NaN):**
```
Epoch 5: loss: nan
```
**Causa:** Learning rate muito alta ou gradients exploding

**Solução:**
```bash
# Reduzir learning rate
--lr 0.0001
```

---

## ✅ Checklist Pós-Treino

Após treino completo, verificar:

- [ ] ✅ Loss final < 0.0005
- [ ] ✅ Val_loss < 2× loss
- [ ] ✅ MAE < $15,000
- [ ] ✅ R² Score > 0.50
- [ ] ✅ Hit Rate > 52%
- [ ] ✅ Backtest com > 10 trades
- [ ] ✅ Sharpe Ratio > 0
- [ ] ✅ Artifacts salvos corretamente
- [ ] ✅ Documentação atualizada

**Se tudo OK:** 🎉 **Modelo production ready!**

**Se algum item falhar:** Revisar seção "Otimização Pós-Treino" acima.

---

## 🎯 Comando Final (Copy & Paste)

```bash
# Windows PowerShell
uv run python -m src.ml_v3_arch.cli train --csv data/BTCUSDT_30m_full.csv --epochs 50 --units 128 --lookback 60

# Após treino, avaliar:
uv run python -m src.ml_v3_arch.cli evaluate --csv data/BTCUSDT_30m_full.csv

# E backtesting:
uv run python -m src.ml_v3_arch.cli backtest --csv data/BTCUSDT_30m_full.csv --capital 10000
```

**Boa sorte! 🚀**

---

**Criado em:** 19/10/2025  
**Versão:** v3.1.0  
**Tempo estimado:** ~3 horas  
**Meta:** R² > 0.60, Sharpe > 1.0
