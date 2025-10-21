# 🔄 Guia de Migração: ml_v2 → ml_v3_arch

**Data:** 2025-10-18  
**Status:** 📘 Guia Oficial de Migração

---

## 🎯 Visão Geral

Este guia ajuda a **migrar gradualmente** do `ml_v2` (código funcional) para o `ml_v3_arch` (arquitetura SOLID).

**Estratégia:** Coexistência pacífica - ambos funcionam simultaneamente.

---

## 📊 Comparação de Estruturas

### ml_v2 (Funcional)
```
ml_v2/
├── cli.py (monolítico)
├── preprocess.py
├── models/
├── backtest/
└── validation/
```

### ml_v3_arch (SOLID)
```
ml_v3_arch/
├── domain/          # Core business
├── interfaces/      # Contratos
├── factories/       # Criação
├── services/        # Lógica
├── infrastructure/  # I/O
└── adapters/        # Bridge para v2
```

---

## 🚀 Estratégias de Migração

### **Estratégia 1: Paralela (Recomendada)**

Mantenha ambos rodando lado a lado:

```python
# Projeto existente continua com v2
from ml_v2.cli import cmd_train

# Novos features usam v3
from ml_v3_arch.services import TrainingService
```

**Vantagens:**
- ✅ Zero downtime
- ✅ Comparação de resultados
- ✅ Rollback fácil
- ✅ Aprendizado sem pressão

---

### **Estratégia 2: Gradual (Componente por Componente)**

Migre uma funcionalidade por vez:

**Fase 1:** Migrar preprocessamento
```python
# Antes (v2)
from ml_v2.preprocess import DataPreprocessor

# Depois (v3)
from ml_v3_arch.infrastructure import DataPreprocessor  # Nova implementação
```

**Fase 2:** Migrar criação de modelos
```python
# Antes (v2)
from ml_v2.models.lstm_model import build_lstm
model = build_lstm(input_shape, lr=0.001)

# Depois (v3)
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.domain import ModelConfig

config = ModelConfig(model_type='lstm', lookback=60)
model = ModelFactory.create_model(config)
```

**Fase 3:** Migrar backtesting
```python
# Antes (v2)
from ml_v2.backtest.engine import backtest_regression

# Depois (v3)
from ml_v3_arch.services import BacktestService
service = BacktestService(strategy, config)
```

---

## 📋 Checklist de Migração

### Pré-Migração
- [ ] Backup completo do ml_v2
- [ ] Testes do ml_v2 passando
- [ ] Documentar funcionalidades atuais
- [ ] Identificar dependências

### Durante Migração
- [ ] Criar adapter para compatibilidade
- [ ] Migrar configurações para Value Objects
- [ ] Refatorar para usar Dependency Injection
- [ ] Adicionar testes unitários (v3)
- [ ] Comparar resultados v2 vs v3

### Pós-Migração
- [ ] Todos os testes passando
- [ ] Performance igual ou melhor
- [ ] Documentação atualizada
- [ ] Code review aprovado
- [ ] Deploy em staging

---

## 🔌 Usando Adapters

### Adapter: ml_v2 → ml_v3_arch

```python
from ml_v3_arch.adapters import MLv2Adapter

adapter = MLv2Adapter()

# Converter dados v2 para v3
v2_data = load_v2_format("data.csv")
v3_data = adapter.convert_data(v2_data)

# Usar serviço v3
service = TrainingService()
service.train(v3_data)
```

### Adapter: ml_v3_arch → ml_v2

```python
# Usar modelo v3 no pipeline v2
v3_model = ModelFactory.create_model(config)
v2_compatible_model = adapter.wrap_as_v2(v3_model)

# Agora funciona com código v2
backtest_regression(df, v2_compatible_model)
```

---

## 📝 Exemplos Práticos

### Exemplo 1: Migrar Treino

**Antes (v2):**
```python
import argparse
from ml_v2.preprocess import DataPreprocessor
from ml_v2.models.lstm_model import build_lstm

# Hardcoded params
df = load_data("data.csv")
preprocessor = DataPreprocessor(feature_cols, "Close", lookback=60)
X, y = preprocessor.fit_transform(df)

model = build_lstm((60, 10), learning_rate=0.001)
model.fit(X, y, epochs=100)
```

**Depois (v3):**
```python
from ml_v3_arch.domain import ModelConfig
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.services import TrainingService
from ml_v3_arch.infrastructure import DataLoader

# Configuração validada
config = ModelConfig(
    model_type='lstm',
    lookback=60,
    learning_rate=1e-3,
    epochs=100
)

# Dependency Injection
loader = DataLoader()
model = ModelFactory.create_model(config)
service = TrainingService(model, loader, config)

# Service orquestra tudo
history = service.train("data.csv")
```

---

### Exemplo 2: Migrar Backtest

**Antes (v2):**
```python
from ml_v2.backtest.engine import backtest_regression

equity, metrics = backtest_regression(
    df, 
    predictions,
    fee_bps=10.0,
    slippage_bps=5.0,
    threshold_bps=20.0,
    initial_capital=10000
)
```

**Depois (v3):**
```python
from ml_v3_arch.domain import BacktestConfig
from ml_v3_arch.factories import StrategyFactory
from ml_v3_arch.services import BacktestService

# Config como Value Object
config = BacktestConfig(
    initial_capital=10000,
    fee_bps=10.0,
    slippage_bps=5.0,
    threshold_bps=20.0
)

# Strategy Pattern
strategy = StrategyFactory.create_strategy('regression', config)

# Service
service = BacktestService(strategy, config)
results = service.run(df, predictions)
```

---

## ⚠️ Armadilhas Comuns

### 1. **Não converter configs**
```python
# ❌ Errado - passar dict
model = ModelFactory.create_model({'model_type': 'lstm'})

# ✅ Correto - usar Value Object
config = ModelConfig(model_type='lstm')
model = ModelFactory.create_model(config)
```

### 2. **Ignorar Dependency Injection**
```python
# ❌ Errado - instanciar dentro
class TrainingService:
    def __init__(self):
        self.loader = DataLoader()  # Acoplado!

# ✅ Correto - injetar dependência
class TrainingService:
    def __init__(self, loader: DataLoader):
        self.loader = loader  # Desacoplado!
```

### 3. **Não usar interfaces**
```python
# ❌ Errado - depender de implementação
def train(model: LSTMModel):
    ...

# ✅ Correto - depender de abstração
def train(model: BaseModel):
    ...
```

---

## 📈 Cronograma Sugerido

### Semana 1-2: Preparação
- Estudar arquitetura v3
- Executar exemplos
- Identificar componentes a migrar

### Semana 3-4: Migração Básica
- Migrar configurações para Value Objects
- Usar Factory para criar modelos
- Testes comparativos v2 vs v3

### Semana 5-6: Migração Avançada
- Migrar serviços
- Implementar Dependency Injection
- Refatorar CLI

### Semana 7-8: Finalização
- Testes completos
- Documentação
- Code review
- Deploy

---

## 🧪 Validação

### Comparar Resultados

```python
# Treinar com ambas versões
v2_model = train_v2(data)
v3_model = train_v3(data)

# Comparar predições
v2_pred = v2_model.predict(X_test)
v3_pred = v3_model.predict(X_test)

# Devem ser próximas (seeds fixas)
assert np.allclose(v2_pred, v3_pred, rtol=0.01)
```

### Performance Benchmarks

```python
import time

# v2
start = time.time()
train_v2(data)
v2_time = time.time() - start

# v3
start = time.time()
train_v3(data)
v3_time = time.time() - start

print(f"v2: {v2_time:.2f}s")
print(f"v3: {v3_time:.2f}s")
print(f"Diferença: {(v3_time - v2_time) / v2_time * 100:.1f}%")
```

---

## 📚 Recursos

- **[v3 README](README.md)** - Visão geral do v3
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura detalhada
- **[examples/](examples/)** - Exemplos de uso
- **[ml_v2 README](../ml_v2/README.md)** - Referência do v2

---

## 🤝 Suporte

**Dúvidas?**
- Consulte os exemplos em `examples/`
- Revise a documentação
- Compare código v2 vs v3

**Problemas?**
- Abra uma issue
- Use o adapter para compatibilidade
- Mantenha v2 rodando até resolver

---

## ✅ Critérios de Sucesso

Migração bem-sucedida quando:
- ✅ Todos os testes passando
- ✅ Performance mantida ou melhorada
- ✅ Código mais legível e manutenível
- ✅ Fácil adicionar novos features
- ✅ Equipe confortável com nova arquitetura

---

**Boa migração! 🚀**

---

**Última atualização:** 2025-10-18
