# 🐛 Troubleshooting: RecursionError no CLI v3

## ❌ Problema

Ao executar o CLI v3, você está encontrando este erro:

```
RecursionError: maximum recursion depth exceeded
  File "numpy\core\_dtype.py", line 143, in _scalar_str
  File "numpy\core\numertypes.py", line 417, in issubdtype
```

## 🔍 Causa Raiz

Este é um **bug conhecido** causado por incompatibilidade entre versões de:
- NumPy
- TensorFlow
- Pandas

O erro ocorre quando há imports circulares ou conflitos de inicialização entre essas bibliotecas.

## ✅ Soluções

### Solução 1: Usar CLI v2 (Funcionando)

O CLI v2 já está testado e funcionando perfeitamente:

```bash
# CLI v2 funciona normalmente
python -m src.ml_v2.cli train --csv data/BTCUSDT_30m_full.csv --epochs 10
python -m src.ml_v2.cli train_classifier --csv data/BTCUSDT_30m_full.csv
python -m src.ml_v2.cli backtest --csv data/BTCUSDT_30m_full.csv
```

**Recomendação**: Use a v2 para produção até resolvermos o problema de ambiente da v3.

---

### Solução 2: Atualizar Dependências

Tente atualizar as bibliotecas para versões compatíveis:

```bash
pip install --upgrade numpy tensorflow pandas scikit-learn
```

**Versões recomendadas:**
- NumPy: 1.26.4
- TensorFlow: 2.15.0 ou 2.16.0
- Pandas: 2.2.2
- scikit-learn: 1.4.2

---

### Solução 3: Ambiente Virtual Limpo

Crie um novo ambiente virtual do zero:

```bash
# PowerShell
python -m venv venv_v3
.\venv_v3\Scripts\Activate.ps1

# Instalar dependências limpas
pip install --upgrade pip
pip install tensorflow==2.15.0 numpy==1.26.4 pandas==2.2.2 scikit-learn==1.4.2
```

---

### Solução 4: Usar Adapters v2→v3 (Alternativa)

Os **Adapters** permitem usar a arquitetura v3 através da interface v2:

```python
from src.ml_v3_arch.adapters import (
    DataPreprocessorAdapter,
    ModelBuilderAdapter,
    BacktestAdapter
)

# Interface v2, implementação v3!
preprocessor = DataPreprocessorAdapter(feature_cols, "Close", 60)
preprocessor.fit(df_train)
X_train, y_train = preprocessor.transform(df_train)

model = ModelBuilderAdapter.build_lstm(
    input_shape=(60, 5),
    learning_rate=1e-3
)

# Continua com v2 API...
```

**Vantagens**:
- Usa arquitetura v3 por baixo
- Sem problemas de imports
- Testado (12/21 testes passando)

---

## 🎯 Workaround Temporário: Usar v2

Enquanto não resolvermos o bug de ambiente, **use a v2 que está 100% funcional**:

### Treinar LSTM (Regressão)
```bash
python -m src.ml_v2.cli train \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 50 \
  --lookback 60 \
  --units 64 \
  --dropout 0.3
```

### Treinar Classificador
```bash
python -m src.ml_v2.cli train_classifier \
  --csv data/BTCUSDT_30m_full.csv \
  --epochs 100 \
  --lookback 60
```

### Backtest
```bash
python -m src.ml_v2.cli backtest_classifier \
  --csv data/BTCUSDT_30m_full.csv \
  --capital 100000 \
  --fee-bps 10
```

---

## 📊 Comparação v2 vs v3

| Aspecto | v2 (Procedural) | v3 (Clean Arch) |
|---------|----------------|-----------------|
| **Status** | ✅ Funcionando | ⚠️ Bug de ambiente |
| **CLI** | 100% funcional | RecursionError |
| **Arquitetura** | Procedural | Clean Architecture |
| **Testes** | Funcionais | 87 testes unitários |
| **Produção** | ✅ Pronto | ⏳ Aguardando fix |

---

## 🔧 Debug: Verificar Versões

Para verificar suas versões atuais:

```python
import numpy as np
import tensorflow as tf
import pandas as pd
import sklearn

print(f"NumPy: {np.__version__}")
print(f"TensorFlow: {tf.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"scikit-learn: {sklearn.__version__}")
```

**Saída esperada (compatível):**
```
NumPy: 1.26.4
TensorFlow: 2.15.0
Pandas: 2.2.2
scikit-learn: 1.4.2
```

---

## 🆘 Se Nada Funcionar

1. **Use v2 em produção** (100% confiável)
2. **Crie issue no GitHub** com logs completos
3. **Teste em outro ambiente** (Google Colab, container Docker)

---

## 📚 Referências

- **Issue similar no TensorFlow**: https://github.com/tensorflow/tensorflow/issues/62003
- **NumPy dtype recursion**: https://github.com/numpy/numpy/issues/24002
- **Workaround conhecidos**: Usar imports locais (dentro de funções)

---

## ✅ Próximos Passos

1. **Atualizar dependências** (Solução 2)
2. **Se não resolver**: Usar v2 em produção
3. **Reportar problema** com suas versões específicas

**Para agora**: Use `python -m src.ml_v2.cli` que está 100% funcional! 🚀
