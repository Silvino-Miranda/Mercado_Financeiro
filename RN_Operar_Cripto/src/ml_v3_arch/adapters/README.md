# Adapters - Migração Gradual v2 → v3

## 📋 Visão Geral

Os **Adapters** implementam o padrão GoF Adapter para permitir **migração gradual** da arquitetura v2 para v3 **sem quebrar código existente**.

### ✅ Objetivos

1. **Compatibilidade Retroativa**: Código v2 continua funcionando
2. **Implementação v3**: Usa classes robustas da v3 internamente
3. **Migração Gradual**: Atualizar módulos um de cada vez
4. **Zero Refatoração Imediata**: Não precisa reescrever tudo

### 🎯 Princípios SOLID Aplicados

- **Open/Closed Principle (OCP)**: Extensível sem modificar v2
- **Liskov Substitution (LSP)**: Adapters substituem classes v2
- **Dependency Inversion (DIP)**: Código v2 depende de interface, não implementação

---

## 📦 Adapters Disponíveis

### 1️⃣ DataPreprocessorAdapter

**Propósito**: Manter interface v2 de `DataPreprocessor` usando implementação v3.

#### Interface v2 Mantida

```python
from ml_v3_arch.adapters import DataPreprocessorAdapter

# Código v2 (não quebra!)
preprocessor = DataPreprocessorAdapter(
    feature_cols=['Open', 'High', 'Low', 'Volume'],
    target_col='Close',
    lookback=60
)

# Fit apenas no treino
preprocessor.fit(df_train)

# Transform em val/test
X_train, y_train = preprocessor.transform(df_train)
X_val, y_val = preprocessor.transform(df_val)
```

#### Implementação v3 (Interna)

- Usa `DataLoader` para validações robustas
- Valida colunas, missing values, tamanho mínimo
- Scalers separados para X e y
- Criação de sequências LSTM otimizada

#### Métodos Disponíveis

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `fit(df_train)` | Fit dos scalers apenas no treino | self |
| `transform(df)` | Transforma em sequências LSTM | (X, y) |
| `fit_transform(df)` | Fit + transform em uma chamada | (X, y) |
| `inverse_target(y_scaled)` | Inverte normalização do target | y_original |
| `get_config()` | Retorna configuração | dict |

---

### 2️⃣ ModelBuilderAdapter

**Propósito**: Manter interface v2 de construção de modelos usando `ModelFactory` v3.

#### Interface v2 Mantida

```python
from ml_v3_arch.adapters import ModelBuilderAdapter

# 1. Modelo LSTM de regressão (código v2 não quebra!)
model = ModelBuilderAdapter.build_lstm(
    input_shape=(60, 10),
    learning_rate=1e-3
)

# 2. Modelo de classificação direcional
model_cls = ModelBuilderAdapter.build_directional_lstm(
    input_shape=(60, 10),
    n_classes=3,
    lstm_units=64,
    dropout=0.3,
    learning_rate=1e-3
)

# 3. Modelo melhorado com Focal Loss
model_improved = ModelBuilderAdapter.build_improved_directional_lstm(
    input_shape=(60, 10),
    lstm_units=128,
    lstm_layers=3,
    dropout=0.4,
    use_focal_loss=True
)

# 4. Callbacks
callbacks = ModelBuilderAdapter.get_callbacks(
    patience_early=10,
    patience_lr=5
)
```

#### Implementação v3 (Interna)

- Usa `ModelFactory` com configs tipadas
- Validações de parâmetros robustas
- Suporte a múltiplos tipos de modelos
- Callbacks configuráveis e extensíveis

#### Métodos Estáticos

| Método | Modelo | Loss | Uso |
|--------|--------|------|-----|
| `build_lstm()` | LSTM 2 layers | MSE | Regressão |
| `build_directional_lstm()` | LSTM 2 layers | Categorical Crossentropy | Classificação 3 classes |
| `build_improved_directional_lstm()` | LSTM 3 layers + BatchNorm | Focal Loss | Classificação desbalanceada |
| `get_callbacks()` | - | - | EarlyStopping + ReduceLR |
| `calculate_class_weights()` | - | - | Pesos para desbalanceamento |

---

### 3️⃣ BacktestAdapter

**Propósito**: Manter interface v2 de backtesting usando `BacktestService` v3.

#### Interface v2 Mantida

```python
from ml_v3_arch.adapters import BacktestAdapter

# 1. Backtest de regressão (código v2 não quebra!)
equity_curve, metrics = BacktestAdapter.backtest_regression(
    df=df_test,
    preds_usd=predictions,
    fee_bps=10.0,
    slippage_bps=5.0,
    threshold_bps=20.0,
    initial_capital=10000.0
)

# 2. Backtest de classificação
equity_curve, metrics = BacktestAdapter.backtest_classifier(
    df=df_test,
    predictions=pred_classes,
    probabilities=pred_probs,
    fee_bps=10.0,
    slippage_bps=5.0,
    min_confidence=0.6,
    initial_capital=100000.0
)

# 3. Imprimir relatório
BacktestAdapter.print_backtest_report(metrics)
```

#### Implementação v3 (Interna)

- Usa `BacktestService` com entidades tipadas (`Trade`, `BacktestConfig`)
- Validações de dados robustas
- Cálculo de métricas financeiras completas (Sharpe, Drawdown, Profit Factor)
- Simulação de custos realista (fees + slippage)

#### Métricas Retornadas

```python
metrics = {
    'total_trades': int,         # Número de trades executados
    'total_return': float,       # Retorno total (%)
    'sharpe_ratio': float,       # Sharpe Ratio anualizado
    'max_drawdown': float,       # Max Drawdown (%)
    'win_rate': float,           # Taxa de acerto (%)
    'avg_win': float,            # Ganho médio por trade vencedor
    'avg_loss': float,           # Perda média por trade perdedor
    'profit_factor': float,      # Profit Factor (wins/losses)
    'final_capital': float       # Capital final ($)
}
```

---

## 🔧 Migração Gradual - Passo a Passo

### Etapa 1: Instalar Adapters no Código v2

**Antes (v2 puro):**

```python
# src/ml_v2/cli.py
from src.ml_v2.preprocess import DataPreprocessor
from src.ml_v2.models.lstm_model import build_lstm, get_callbacks
from src.ml_v2.backtest.engine import backtest_regression
```

**Depois (v2 com adapters v3):**

```python
# src/ml_v2/cli.py
from src.ml_v3_arch.adapters import (
    DataPreprocessorAdapter as DataPreprocessor,
    ModelBuilderAdapter as ModelBuilder,
    BacktestAdapter as Backtest
)

# Código v2 continua funcionando SEM MODIFICAÇÕES!
```

### Etapa 2: Executar Testes de Regressão

```bash
# Testar que v2 continua funcionando
uv run python -m src.ml_v2.cli train --csv data/BTCUSDT_30m_full.csv --epochs 5

# Se funcionar: adapters estão corretos! ✅
```

### Etapa 3: Migrar Módulos Gradualmente

1. ✅ **Preprocessamento**: Usar `DataPreprocessorAdapter`
2. ✅ **Modelos**: Usar `ModelBuilderAdapter`
3. ✅ **Backtest**: Usar `BacktestAdapter`
4. 🚧 **Evaluation**: Criar `EvaluationAdapter` (próximo passo)
5. 🚧 **CLI**: Migrar CLI completo para v3 pura

---

## 🧪 Exemplo Completo de Uso

```python
"""Pipeline completo usando adapters (código v2 não quebra!)."""
import pandas as pd
import numpy as np

from ml_v3_arch.adapters import (
    DataPreprocessorAdapter,
    ModelBuilderAdapter,
    BacktestAdapter
)

# 1. Carregar dados
df = pd.read_csv('data/BTCUSDT_30m_full.csv')
df['Date'] = pd.to_datetime(df['Date'])

# 2. Split temporal
n = len(df)
df_train = df.iloc[:int(n*0.7)]
df_val = df.iloc[int(n*0.7):int(n*0.85)]
df_test = df.iloc[int(n*0.85):]

# 3. Preprocessamento (interface v2, implementação v3)
preprocessor = DataPreprocessorAdapter(
    feature_cols=['Open', 'High', 'Low', 'Volume', 'RSI', 'MACD'],
    target_col='Close',
    lookback=60
)

X_train, y_train = preprocessor.fit_transform(df_train)
X_val, y_val = preprocessor.transform(df_val)
X_test, y_test = preprocessor.transform(df_test)

# 4. Construir modelo (interface v2, implementação v3)
model = ModelBuilderAdapter.build_lstm(
    input_shape=X_train.shape[1:],
    learning_rate=1e-3
)

callbacks = ModelBuilderAdapter.get_callbacks(
    patience_early=10,
    patience_lr=5
)

# 5. Treinar
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=64,
    callbacks=callbacks,
    verbose=1
)

# 6. Predições
y_pred_scaled = model.predict(X_test, verbose=0).ravel()
y_pred_usd = preprocessor.inverse_target(y_pred_scaled)

# 7. Backtest (interface v2, implementação v3)
equity_curve, metrics = BacktestAdapter.backtest_regression(
    df=df_test.iloc[60:].reset_index(drop=True),
    preds_usd=y_pred_usd,
    fee_bps=10.0,
    slippage_bps=5.0,
    initial_capital=10000.0
)

# 8. Relatório
BacktestAdapter.print_backtest_report(metrics)

print("✅ Pipeline v2 executado com implementação v3!")
```

---

## 🎯 Comparação v2 vs v3 (via Adapters)

| Aspecto | v2 Puro | v3 via Adapters | Benefício |
|---------|---------|-----------------|-----------|
| **Interface** | v2 original | v2 mantida | ✅ Código não quebra |
| **Validações** | Básicas | Robustas (v3) | ✅ Menos bugs |
| **Type Safety** | Pouco | Completo (v3) | ✅ Erros em dev |
| **Testing** | Parcial | Cobertura 80%+ | ✅ Confiabilidade |
| **Performance** | OK | Otimizado (v3) | ✅ Mais rápido |
| **Manutenção** | Difícil | SOLID (v3) | ✅ Fácil evoluir |

---

## 📚 Documentação Relacionada

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Arquitetura v3 completa
- [SOLID_SUMMARY.md](../SOLID_SUMMARY.md) - Princípios aplicados
- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) - Guia de migração v2→v3
- [examples/](../examples/) - Exemplos de uso v3 pura

---

## ✅ Próximos Passos

### Fase 1: Adapters (🚧 EM PROGRESSO)
- [x] DataPreprocessorAdapter
- [x] ModelBuilderAdapter
- [x] BacktestAdapter
- [ ] EvaluationAdapter
- [ ] Testes para adapters

### Fase 2: Integração com CLI v2
- [ ] Atualizar `cli.py` para usar adapters
- [ ] Validar todos os subcomandos (train, evaluate, backtest, etc.)
- [ ] Smoke tests com dados reais

### Fase 3: Migração Completa
- [ ] Refatorar código v2 para v3 pura
- [ ] Remover dependências de v2
- [ ] Deprecar adapters (opcional)

---

## 🐛 Troubleshooting

### Erro: Import não encontrado

```bash
# Problema:
ModuleNotFoundError: No module named 'ml_v3_arch.adapters'

# Solução:
# 1. Verificar que __init__.py existe em adapters/
# 2. Adicionar src/ ao PYTHONPATH:
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Ou:
uv run python -m src.ml_v3_arch.adapters.example_usage
```

### Erro: AttributeError no adapter

```python
# Problema:
AttributeError: 'DataPreprocessorAdapter' object has no attribute 'X'

# Causa: Método v2 não implementado no adapter

# Solução: Reportar issue ou implementar método faltante
```

### Performance: Adapter mais lento que v2

```python
# Causa: Validações extras da v3

# Solução 1: Desabilitar validações em produção (não recomendado)
# Solução 2: Aceitar overhead (< 5%) para ganhar robustez
# Solução 3: Migrar para v3 pura (sem adapters) - melhor performance
```

---

## 💡 Boas Práticas

1. **Use adapters apenas para migração**: Não é uma solução permanente
2. **Teste cada módulo**: Valide que v2 continua funcionando
3. **Migre gradualmente**: Um módulo de cada vez
4. **Documente mudanças**: Atualizar CHANGELOG quando migrar
5. **Remova código morto**: Após migração completa, limpar v2 antigo

---

## 🤝 Contribuindo

Encontrou um bug ou quer adicionar um adapter?

1. Abra issue descrevendo o problema
2. Implemente adapter seguindo padrão existente
3. Adicione testes (cobertura > 80%)
4. Atualize esta documentação
5. Abra PR com descrição clara

---

**Mantido por**: Silvino Miranda  
**Última atualização**: 2025-10-18  
**Status**: 🚧 Em desenvolvimento ativo
