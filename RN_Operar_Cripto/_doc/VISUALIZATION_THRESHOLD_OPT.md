# 📊 VISUALIZAÇÃO - THRESHOLD OPTIMIZATION

## 🎯 Resultados em Gráfico ASCII

### **Retorno vs Threshold (75 Épocas)**

```
Retorno (%)
    +10 ┤
        │
      0 ┤────────────────────────────────────────o (150 bps: -1.70%)
        │                                        │
    -10 ┤                                    o (100 bps: -4.39%)
        │                                    │
    -20 ┤                            o (50 bps: -19.76%)
        │                            │
    -30 ┤                    o (30 bps: -29.88%)
        │                    │
    -40 ┤            o (20 bps: -34.70%)
        └────────────┴────────────┴────────────┴────────────┴──────> Threshold (bps)
             20         50        100       150       200
```

**Tendência:** Threshold maior = Retorno menos negativo

---

### **Trades vs Threshold (75 Épocas)**

```
Trades
   350 ┤
       │ o (20 bps: 320 trades)
   300 ┤ │
       │ │
   250 ┤ │ o (30 bps: 244)
       │ │ │
   200 ┤ │ │
       │ │ │
   150 ┤ │ │ o (50 bps: 124)
       │ │ │ │
   100 ┤ │ │ │
       │ │ │ │     o (100 bps: 54)
    50 ┤ │ │ │     │
       │ │ │ │     │           o (150 bps: 26)
     0 └─┴─┴─┴─────┴───────────┴──────────────────> Threshold (bps)
         20  30    50        100         150
```

**Tendência:** Threshold maior = Menos trades (exponencial)

---

### **Sharpe Ratio vs Threshold**

```
Sharpe
   0.5 ┤
       │
   0.0 ┤────────────────────────────────────────o (150 bps: 0.01)
       │                                        │
  -0.5 ┤                                    o (100 bps: -0.08)
       │                            o (50 bps: -0.69)
  -1.0 ┤                    o (30 bps: -1.19)
       │
  -1.5 ┤            o (20 bps: -1.44)
       └────────────┴────────────┴────────────┴────────────┴──────> Threshold (bps)
             20         50        100       150       200
```

**Tendência:** Sharpe melhora drasticamente com threshold maior

---

## 🆚 Comparação: 50 vs 75 Épocas

### **Retorno Total**

```
Retorno (%)
   +10 ┤
       │     🥇
    +5 ┤     │ 50 ÉPOCAS (+6.93%)
       │     │
     0 ┤─────┼─────────────────────o─────────────> Threshold (bps)
       │     │                     │ 75 épocas (150 bps: -1.70%)
    -5 ┤     │                     │
       │     │                     │
   -10 ┤     │                     │
       └─────┴─────────────────────┴──────────────
            20                   150
```

**Diferença:** 8.63 pontos percentuais a favor de 50 épocas!

---

### **Sharpe Ratio Comparison**

```
Sharpe
   0.5 ┤
       │     🥇
   0.3 ┤     │ 50 ÉPOCAS (0.29)
       │     │
   0.1 ┤─────┼─────────────────────o─────────────> Threshold (bps)
       │     │                     │ 75 épocas (0.01)
  -0.1 ┤     │                     │
       └─────┴─────────────────────┴──────────────
            20                   150
```

**Diferença:** 0.28 pontos (50 épocas 28x melhor!)

---

### **Número de Trades**

```
Trades
    50 ┤
       │
    40 ┤                     o 75 épocas (26 trades)
       │
    30 ┤     🥇
       │     │ 50 ÉPOCAS (18 trades)
    20 ┤     │
       │     │
    10 ┤     │
       └─────┴─────────────────────┴──────────────> Threshold (bps)
            20                   150
```

**Diferença:** 8 trades a menos (50 épocas mais seletivo!)

---

## 📈 Curva de Custos vs Threshold

```
Custos Estimados (% do Capital)
   50% ┤ o 20 bps: ~48%
       │ │
   40% ┤ │ o 30 bps: ~37%
       │ │ │
   30% ┤ │ │
       │ │ │
   20% ┤ │ │ o 50 bps: ~19%
       │ │ │ │
   10% ┤ │ │ │     o 100 bps: ~8%
       │ │ │ │     │
    0% ┤─┴─┴─┴─────┴────o 150 bps: ~4%──────────> Threshold (bps)
         20  30   50   100        150
```

**Insight:** Custos caem exponencialmente com threshold!

---

## 🎯 Zonas de Performance (75 Épocas)

```
ZONA VERMELHA (Over-trading):
  Threshold: 20-30 bps
  Retorno: -35% a -25%
  Trades: 240-320
  Status: ❌ EVITAR

ZONA AMARELA (Aceitável):
  Threshold: 50-100 bps
  Retorno: -20% a -5%
  Trades: 54-124
  Status: ⚠️ SUBÓTIMO

ZONA VERDE (Quase neutro):
  Threshold: 150+ bps
  Retorno: -2% a 0%
  Trades: 10-26
  Status: ✅ OK (mas 50 épocas melhor)
```

---

## 🏆 Ranking Final - Visual

```
    🥇 1º Lugar
    ┌──────────────────────────────┐
    │ 50 ÉPOCAS + 20 BPS           │
    │ Retorno: +6.93%              │
    │ Sharpe: 0.29                 │
    │ Trades: 18                   │
    └──────────────────────────────┘

    🥈 2º Lugar
    ┌──────────────────────────────┐
    │ 75 ÉPOCAS + 150 BPS          │
    │ Retorno: -1.70%              │
    │ Sharpe: 0.01                 │
    │ Trades: 26                   │
    └──────────────────────────────┘

    🥉 3º Lugar
    ┌──────────────────────────────┐
    │ 75 ÉPOCAS + 100 BPS          │
    │ Retorno: -4.39%              │
    │ Sharpe: -0.08                │
    │ Trades: 54                   │
    └──────────────────────────────┘
```

**Gap entre 1º e 2º:** +8.63 p.p. de retorno!

---

## 📊 Matriz de Decisão

```
                      THRESHOLD
                 20    50    100   150
              ┌─────┬─────┬─────┬─────┐
              │ 🔴  │ 🔴  │ 🟡  │ 🟢  │
       75     │-35% │-20% │ -4% │ -2% │
     ÉPOCAS   │ ❌  │ ❌  │ ⚠️  │ ⚠️  │
              ├─────┴─────┴─────┴─────┤
              │ 🟢  │ ❓  │ ❓  │ ❓  │
       50     │ +7% │  ?  │  ?  │  ?  │
     ÉPOCAS   │ ✅  │  ?  │  ?  │  ?  │
              └─────┴─────┴─────┴─────┘

Legenda:
  🟢 Bom (retorno positivo)
  🟡 Neutro (-5% a 0%)
  🔴 Ruim (< -5%)
  ❓ Não testado ainda
```

**Próximo passo:** Testar threshold 30/50/100 bps no modelo de 50 épocas!

---

## 🎨 Performance Heatmap

```
         RETORNO (%)
      -40  -30  -20  -10   0  +10
       ┌────────────────────────┐
20 bps │ ████████████████████   │ 75 épocas: -34.70%
       ├────────────────────────┤
20 bps │                    ████│ 50 épocas: +6.93% 🏆
       ├────────────────────────┤
150bps │                  ██    │ 75 épocas: -1.70%
       └────────────────────────┘

Cores:
  ████ = Posição atual
  Comprimento da barra = Magnitude do retorno
```

---

## 💡 Insights Visuais

### **1. Relação Não-Linear**
```
Threshold ↑ 50%  → Trades ↓ 24%  → Retorno ↑ 14%
Threshold ↑ 100% → Trades ↓ 61%  → Retorno ↑ 44%
Threshold ↑ 400% → Trades ↓ 92%  → Retorno ↑ 95%
```
**Conclusão:** Benefício marginal decrescente após 100 bps

### **2. Curva de Custos**
```
Custos = Trades × 0.15% × 2

320 trades → 96 bps → MATA performance
 54 trades → 16 bps → Ainda pesado
 26 trades →  8 bps → Aceitável
 18 trades →  5 bps → ÓTIMO (50 épocas)
```

### **3. Sweet Spot Visualizado**
```
         THRESHOLD (bps)
         0   50  100  150  200
Retorno  │   │   │    │    │
    +10% ┤───┼───┼────┼────┤ 🎯 Meta
         │   │   │    │    │
      0% ┤───┼───┼────o────┤ 150 bps
         │   │   o    │    │ 100 bps
    -10% ┤───o───┼────┼────┤ 50 bps
         │   │   │    │    │
    -20% ┤───┼───┼────┼────┤
         │   │   │    │    │
    -30% ┤───┼───┼────┼────┤
         │ o │   │    │    │ 20 bps
    -40% └───┴───┴────┴────┘

Sweet spot: 100-150 bps (mas 50 épocas melhor!)
```

---

**Autor:** Copilot + Silvino Miranda  
**Data:** 20/10/2025 10:52 BRT  
**Tipo:** Visualização ASCII de resultados
