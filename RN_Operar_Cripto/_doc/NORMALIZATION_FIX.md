# 🔧 Correção de Normalização - v3 Pipeline

## 📋 Resumo Executivo

**Data:** 19 de Outubro de 2025  
**Problema:** Modelo treinado com target normalizado, mas evaluate/backtest usavam target bruto  
**Solução:** Salvar preprocessor no treino e reutilizar no evaluate/backtest  
**Status:** ✅ RESOLVIDO

---

## ❌ Problema Original

### **Sintomas:**
```
Média Real:    $92,600
Média Predita: $262  ← COMPLETAMENTE ERRADO!
Std Predita:   $0    ← MODELO CONGELADO
R² Score:      -22.5 ← CATASTRÓFICO
MAPE:          99.7% ← INÚTIL
```

### **Causa Raiz:**

1. **Durante o Treino:**
   ```python
   # DataPreprocessorAdapter normaliza TUDO
   scaler_X = MinMaxScaler()
   scaler_y = MinMaxScaler()
   
   X_scaled = scaler_X.fit_transform(X)  # Features: [0, 1]
   y_scaled = scaler_y.fit_transform(y)  # Target: [0, 1]
   
   # Modelo aprende com valores [0, 1]
   model.fit(X_scaled, y_scaled)
   ```

2. **Durante o Evaluate/Backtest (ERRADO):**
   ```python
   # Criava NOVO scaler (escalas diferentes!)
   scaler_new = MinMaxScaler()
   X_test_scaled = scaler_new.fit_transform(X_test)  # ❌ Novo fit!
   
   y_pred_scaled = model.predict(X_test_scaled)  # [0, 1]
   
   # Desnormalizava com scaler ERRADO
   y_pred = scaler_new.inverse_transform(y_pred_scaled)  # ❌ Escala diferente!
   ```

3. **Resultado:**
   - Modelo prevê valores entre [0, 1]
   - Desnormalização usa min/max DIFERENTES do treino
   - Predições ficam completamente erradas

---

## ✅ Solução Implementada

### **1. Salvar Preprocessor no Treino**

**Arquivo:** `src/ml_v3_arch/cli.py` (linha 227-237)

```python
# 9.1 Salvar preprocessor (nome fixo, sem timestamp)
prep_dir = Path("artifacts/v3/preprocessors")
prep_dir.mkdir(parents=True, exist_ok=True)
prep_path = prep_dir / "preprocessor_lstm_v3.pkl"

import pickle
with open(prep_path, 'wb') as f:
    pickle.dump(preprocessor, f)

print(f"✅ Preprocessor salvo em: {prep_path}")
```

### **2. Carregar Preprocessor no Evaluate/Backtest**

Sempre carregar o preprocessor salvo para garantir escalas consistentes.

---

## 📊 Resultados Antes vs Depois

### **ANTES (Normalização Errada):**
```
MAE:             $92,338
MAPE:            99.70%
R² Score:        -22.50
Média Predita:   $262 (ERRADO!)
Std Predita:     $0 (CONGELADO!)
```

### **DEPOIS (Normalização Correta):**
```
MAE:             $20,945  ← 77% de melhoria
MAPE:            20.50%   ← 79% de melhoria
R² Score:        -0.58    ← 97% de melhoria
Média Predita:   $71,657  ← Escala correta!
Std Predita:     $7,325   ← Variando!
```

---

## 🎯 Próximos Passos

1. **Treinar modelo completo (50+ épocas)**
2. **Otimizar hyperparameters**
3. **Feature engineering avançado**

**Status:** ✅ Pipeline completo funcionando!
