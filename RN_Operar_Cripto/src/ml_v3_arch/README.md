# ML v3 - Arquitetura SOLID para Trading com Deep Learning

**Versão:** 3.0.0  
**Status:** 🚧 Em Desenvolvimento (Clean Architecture)  
**Última atualização:** 2025-10-18

---

## 🎯 Objetivo

Este é o **módulo v3** do pipeline de ML para trading, completamente refatorado usando **princípios SOLID** e **Clean Architecture**. 

**Diferencial do v2:**
- ✅ Arquitetura 100% SOLID desde o início
- ✅ Zero código legado - fresh start
- ✅ Dependency Injection em todos os níveis
- ✅ Testável por design
- ✅ Extensível sem modificar código existente

---

## 🏗️ Arquitetura

### **Clean Architecture + SOLID + DDD**

```
ml_v3_arch/
├── domain/              # 🎯 Core Business Logic
│   ├── entities.py      # Trade, TradeSignal, MarketData
│   └── value_objects.py # ModelConfig, BacktestConfig, Metrics
│
├── interfaces/          # 📐 Contratos (Abstrações)
│   ├── base_model.py    # Trainable, Predictable, Evaluable
│   ├── base_preprocessor.py
│   ├── base_backtester.py
│   └── base_evaluator.py
│
├── factories/           # 🏭 Object Creation
│   ├── model_factory.py
│   └── strategy_factory.py
│
├── services/            # 💼 Business Logic
│   ├── training_service.py
│   ├── evaluation_service.py
│   └── backtest_service.py
│
├── infrastructure/      # 🔧 External Concerns
│   ├── data_loader.py
│   ├── model_persistence.py
│   └── metrics_storage.py
│
├── adapters/            # 🔌 Bridge para ml_v2
│   └── ml_v2_adapter.py
│
└── examples/            # 📚 Usage Examples
    ├── basic_usage.py
    └── advanced_patterns.py
```

---

## 🚀 Princípios Aplicados

### **SOLID**
- ✅ **S**RP: Cada classe uma responsabilidade
- ✅ **O**CP: Extensível sem modificação
- ✅ **L**SP: Subclasses substituíveis
- ✅ **I**SP: Interfaces segregadas
- ✅ **D**IP: Depende de abstrações

### **Clean Architecture**
- ✅ Independente de frameworks
- ✅ Testável
- ✅ Independente de UI
- ✅ Independente de banco de dados
- ✅ Independente de agentes externos

### **Domain-Driven Design (DDD)**
- ✅ Entities: Trade, Position
- ✅ Value Objects: TradeSignal, ModelConfig
- ✅ Aggregates: Portfolio
- ✅ Domain Services: RiskManager
- ✅ Repositories: ModelRepository

---

## 📦 Instalação

```bash
# Clone o repositório (se ainda não fez)
git clone <repo-url>
cd RN_Operar_Cripto

# Instalar dependências com UV
uv sync

# Ou ativar ambiente
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

---

## 🎓 Quick Start

### **Exemplo 1: Criar e Treinar Modelo**

```python
from ml_v3_arch.domain import ModelConfig
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.services import TrainingService
from ml_v3_arch.infrastructure import DataLoader

# 1. Configurar (Value Object com validações)
config = ModelConfig(
    model_type='directional',
    lookback=60,
    lstm_units=128,
    dropout=0.4,
    learning_rate=1e-3
)

# 2. Carregar dados
loader = DataLoader()
data = loader.load_csv("data/BTCUSDT_30m_full.csv")

# 3. Criar modelo via Factory
model = ModelFactory.create_model(config)

# 4. Treinar via Service (Dependency Injection)
service = TrainingService(
    model=model,
    data_loader=loader,
    config=config
)

history = service.train(data)
```

### **Exemplo 2: Backtest com Strategy Pattern**

```python
from ml_v3_arch.domain import BacktestConfig
from ml_v3_arch.factories import StrategyFactory
from ml_v3_arch.services import BacktestService

# Configurar
config = BacktestConfig(
    initial_capital=100000,
    fee_bps=10.0,
    position_size=0.95
)

# Criar estratégia
strategy = StrategyFactory.create_strategy(
    strategy_type='directional',
    min_confidence=0.6
)

# Executar backtest
service = BacktestService(
    strategy=strategy,
    config=config
)

results = service.run(data, predictions)
```

---

## 🔄 Coexistência com ml_v2

O `ml_v3_arch` **coexiste** com o `ml_v2`:

```python
# Usar ml_v2 (código legado)
from src.ml_v2.cli import cmd_train

# Usar ml_v3_arch (nova arquitetura)
from ml_v3_arch.services import TrainingService

# Ou usar adapter para integrar
from ml_v3_arch.adapters import MLv2Adapter

adapter = MLv2Adapter()
adapter.train_using_v2_data(config)
```

**Benefícios:**
- ✅ Migração gradual
- ✅ Comparação de resultados
- ✅ Rollback fácil se necessário
- ✅ Aprendizado sem pressão

---

## 📐 Design Patterns Implementados

### **1. Factory Pattern**
```python
ModelFactory.create_model(config)
StrategyFactory.create_strategy(type, params)
```

### **2. Strategy Pattern**
```python
class TradingStrategy(Protocol):
    def generate_signals(predictions): ...

class DirectionalStrategy(TradingStrategy): ...
class RegressionStrategy(TradingStrategy): ...
```

### **3. Observer Pattern** (WIP)
```python
class TrainingObserver(Protocol):
    def on_epoch_end(metrics): ...

class MetricsLogger(TrainingObserver): ...
class EarlyStoppingCallback(TrainingObserver): ...
```

### **4. Repository Pattern** (WIP)
```python
class ModelRepository(Protocol):
    def save(model): ...
    def load(model_id): ...
    def list_all(): ...
```

### **5. Adapter Pattern**
```python
class MLv2Adapter:
    def convert_to_v3(v2_data): ...
    def convert_to_v2(v3_result): ...
```

---

## ✅ Vantagens sobre ml_v2

| Aspecto | ml_v2 | ml_v3_arch |
|---------|-------|------------|
| **Arquitetura** | Funcional, mas monolítico | SOLID + Clean Architecture |
| **Testabilidade** | Difícil (acoplado) | Fácil (desacoplado) |
| **Extensibilidade** | Requer modificar código | Apenas adicionar classes |
| **Manutenibilidade** | Média | Alta |
| **Documentação** | Boa | Excelente |
| **Dependency Injection** | Parcial | Completa |
| **Código Legado** | Sim | Zero |

---

## 🧪 Testes

```bash
# Rodar testes unitários
pytest src/ml_v3_arch/tests/ -v

# Testes de integração
pytest src/ml_v3_arch/tests/integration/ -v

# Cobertura
pytest --cov=ml_v3_arch --cov-report=html
```

---

## 📚 Documentação

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura completa SOLID
- **[SOLID_SUMMARY.md](SOLID_SUMMARY.md)** - Resumo executivo
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Como migrar de v2 para v3
- **[API_REFERENCE.md](API_REFERENCE.md)** - Referência completa da API

---

## 🎯 Roadmap

### Fase 1: Fundação ✅
- [x] Estrutura de diretórios
- [x] Domain model
- [x] Interfaces abstratas
- [x] Factory Pattern
- [x] Documentação básica

### Fase 2: Core Services 🚧
- [ ] TrainingService completo
- [ ] EvaluationService
- [ ] BacktestService
- [ ] Strategy Pattern completo

### Fase 3: Infrastructure 📋
- [ ] Data loaders robustos
- [ ] Model persistence
- [ ] Metrics storage
- [ ] Logging system

### Fase 4: Advanced Patterns 📋
- [ ] Observer Pattern
- [ ] Repository Pattern
- [ ] Command Pattern
- [ ] Chain of Responsibility

### Fase 5: Production Ready 📋
- [ ] Testes completos (>80% cobertura)
- [ ] CI/CD pipeline
- [ ] Performance benchmarks
- [ ] Documentação completa

---

## 🤝 Contribuindo

Para contribuir:

1. **Siga SOLID:** Todo código deve respeitar os princípios
2. **Use interfaces:** Dependa de abstrações, não implementações
3. **Teste tudo:** Cobertura mínima de 80%
4. **Documente:** Docstrings + type hints obrigatórios
5. **Exemplos:** Adicione em `examples/`

---

## 📄 Licença

MIT License - Mesmo do projeto principal

---

## 🎓 Aprendizado

Este módulo é uma **referência** de como aplicar:
- SOLID Principles
- Clean Architecture
- Domain-Driven Design
- Design Patterns

Use como base para outros projetos! 🚀

---

**Status:** 🚧 Em Desenvolvimento Ativo  
**Versão Estável:** Use `ml_v2` para produção  
**Versão Experimental:** Use `ml_v3_arch` para aprender

---

**Mantido por:** Silvino Miranda  
**Última atualização:** 2025-10-18
