# Arquitetura SOLID do ML v2

## 📐 Visão Geral

Este projeto implementa uma arquitetura **SOLID** para sistemas de Machine Learning aplicados a trading de criptomoedas. A estrutura foi projetada para ser **manutenível**, **extensível** e **testável**.

## 🏗️ Princípios SOLID Aplicados

### **S - Single Responsibility Principle (SRP)**

Cada classe tem **uma única responsabilidade**:

```
✅ DataPreprocessor       → Apenas preprocessamento
✅ ModelFactory           → Apenas criação de modelos
✅ DirectionalBacktester  → Apenas simulação de trading
✅ MetricsCalculator      → Apenas cálculo de métricas
```

**Antes (❌ Viola SRP):**
```python
class MLTradingSystem:
    def load_data(self): ...
    def create_features(self): ...
    def train_model(self): ...
    def backtest(self): ...
    def send_email(self): ...  # Muitas responsabilidades!
```

**Depois (✅ Respeita SRP):**
```python
class DataLoader: ...
class FeatureEngineer: ...
class ModelTrainer: ...
class BacktestEngine: ...
class NotificationService: ...
```

---

### **O - Open/Closed Principle (OCP)**

Classes são **abertas para extensão**, mas **fechadas para modificação**:

```python
# ✅ Extensível: adicionar novos modelos sem modificar ModelFactory
class ModelFactory:
    @staticmethod
    def create_model(config: ModelConfig) -> keras.Model:
        if config.model_type == 'lstm':
            return ModelFactory._create_lstm_regression(config)
        elif config.model_type == 'gru':
            return ModelFactory._create_gru_regression(config)
        # Adicionar novos tipos aqui sem quebrar código existente
```

**Padrões usados:**
- **Factory Method**: `ModelFactory` cria diferentes tipos de modelos
- **Strategy Pattern**: Diferentes estratégias de trading sem modificar core

---

### **L - Liskov Substitution Principle (LSP)**

Subclasses podem **substituir** suas superclasses sem quebrar o código:

```python
# ✅ Qualquer implementação de BaseModel pode ser usada
def train_and_evaluate(model: BaseModel, data):
    model.fit(data.X_train, data.y_train)
    return model.evaluate(data.X_val, data.y_val)

# Funciona com qualquer modelo:
lstm_model = LSTMModel()
gru_model = GRUModel()
directional_model = DirectionalModel()

train_and_evaluate(lstm_model, data)      # ✅
train_and_evaluate(gru_model, data)       # ✅
train_and_evaluate(directional_model, data)  # ✅
```

---

### **I - Interface Segregation Principle (ISP)**

Interfaces **específicas** ao invés de uma interface gigante:

```python
# ✅ Interfaces segregadas
class Trainable(Protocol):
    def fit(self, X, y): ...

class Predictable(Protocol):
    def predict(self, X): ...

class Evaluable(Protocol):
    def evaluate(self, X, y): ...

# Classes implementam apenas o que precisam
class PretrainedModel(Predictable):
    # Não precisa de fit()
    def predict(self, X): ...
```

**Ao invés de:**
```python
# ❌ Interface monolítica
class Model(ABC):
    def fit(self, X, y): ...
    def predict(self, X): ...
    def evaluate(self, X, y): ...
    def save(self, path): ...
    def load(self, path): ...
    # Todos obrigados a implementar tudo!
```

---

### **D - Dependency Inversion Principle (DIP)**

Módulos dependem de **abstrações**, não de implementações concretas:

```python
# ✅ Depende de abstração (BasePreprocessor)
class TradingPipeline:
    def __init__(
        self,
        preprocessor: BasePreprocessor,  # Abstração!
        model: BaseModel,                # Abstração!
        backtester: BaseBacktester       # Abstração!
    ):
        self.preprocessor = preprocessor
        self.model = model
        self.backtester = backtester
    
    def run(self, data):
        X, y = self.preprocessor.transform(data)
        predictions = self.model.predict(X)
        results = self.backtester.run_backtest(data, predictions)
        return results

# Injeção de dependência: passa as implementações concretas
pipeline = TradingPipeline(
    preprocessor=DirectionalPreprocessor(...),
    model=ModelFactory.create_model(config),
    backtester=DirectionalBacktester(...)
)
```

---

## 📁 Estrutura de Diretórios

```
src/ml_v2/
├── domain/                   # 🎯 Core Business (Entities, Value Objects)
│   ├── __init__.py
│   └── entities.py          # TradeSignal, Trade, MarketData, ModelConfig, etc
│
├── interfaces/               # 📐 Contratos (Abstrações)
│   ├── __init__.py
│   ├── base_model.py        # BaseModel, Trainable, Predictable, Evaluable
│   ├── base_preprocessor.py # BasePreprocessor, DataScaler, DataTransformer
│   ├── base_backtester.py   # BaseBacktester, TradingStrategy
│   └── base_evaluator.py    # BaseEvaluator, MetricsCalculator
│
├── factories/                # 🏭 Criação de Objetos Complexos
│   ├── __init__.py
│   └── model_factory.py     # ModelFactory (cria LSTM, GRU, Directional)
│
├── services/                 # 💼 Lógica de Negócio
│   ├── __init__.py
│   ├── training_service.py  # Serviço de treinamento
│   └── backtest_service.py  # Serviço de backtesting
│
├── infrastructure/           # 🔧 Implementações Concretas
│   ├── __init__.py
│   ├── data_loader.py       # Carregamento de dados
│   └── persistence.py       # Salvamento de modelos/resultados
│
├── models/                   # 🤖 Implementações de Modelos (legado)
│   ├── lstm_model.py
│   ├── directional_model.py
│   └── improved_directional_model.py
│
├── backtest/                 # 📊 Engines de Backtest (legado)
│   ├── engine.py
│   └── directional_backtester.py
│
├── preprocess/               # 🔄 Preprocessadores (legado)
│   ├── preprocess.py
│   └── preprocess_classification.py
│
└── cli.py                    # 🖥️ Interface de linha de comando
```

---

## 🎯 Padrões de Design Implementados

### **1. Factory Pattern**

**Onde:** `factories/model_factory.py`

**Propósito:** Centralizar criação de modelos complexos

```python
from ml_v2.factories import ModelFactory
from ml_v2.domain import ModelConfig

config = ModelConfig(
    model_type='lstm',
    lookback=60,
    lstm_units=64,
    dropout=0.3
)

model = ModelFactory.create_model(config)
```

**Benefícios:**
- ✅ Adicion ar novos modelos sem modificar código existente (OCP)
- ✅ Configuração centralizada
- ✅ Fácil de testar

---

### **2. Strategy Pattern**

**Onde:** `interfaces/base_backtester.py`

**Propósito:** Diferentes estratégias de trading intercambiáveis

```python
class TradingStrategy(Protocol):
    def generate_signals(self, predictions, prices): ...
    def calculate_position_size(self, capital, price, signal): ...

class RegressionStrategy(TradingStrategy):
    # Estratégia baseada em previsão de preço
    ...

class DirectionalStrategy(TradingStrategy):
    # Estratégia baseada em classificação
    ...
```

---

### **3. Observer Pattern**

**Uso futuro:** Callbacks de treinamento

```python
class TrainingObserver(ABC):
    @abstractmethod
    def on_epoch_end(self, epoch: int, metrics: dict): ...

class MetricsLogger(TrainingObserver):
    def on_epoch_end(self, epoch, metrics):
        self.log(f"Epoch {epoch}: {metrics}")

class EarlyStoppingCallback(TrainingObserver):
    def on_epoch_end(self, epoch, metrics):
        if self.should_stop(metrics):
            raise StopTraining()
```

---

## 🔄 Fluxo de Dados

```
1. Data Loading (Infrastructure)
   └─> DataLoader.load_csv()

2. Preprocessing (Domain + Interfaces)
   └─> BasePreprocessor.fit_transform()
       ├─> DataScaler.fit()
       ├─> DataTransformer.transform()
       └─> SequenceBuilder.create_sequences()

3. Model Creation (Factory)
   └─> ModelFactory.create_model(ModelConfig)

4. Training (Services)
   └─> TrainingService.train(model, X, y)

5. Evaluation (Services)
   └─> EvaluationService.evaluate(model, X_test, y_test)

6. Backtesting (Infrastructure)
   └─> BaseBacktester.run_backtest(data, predictions)
       ├─> TradingStrategy.generate_signals()
       └─> calculate_metrics()
```

---

## ✅ Benefícios da Arquitetura SOLID

### **1. Manutenibilidade**
- Código organizado e fácil de navegar
- Responsabilidades claras
- Mudanças localizadas (não afetam todo o sistema)

### **2. Testabilidade**
- Componentes isolados
- Fácil de mockar dependências
- Testes unitários independentes

### **3. Extensibilidade**
- Adicionar novos modelos: criar nova classe que herda de `BaseModel`
- Adicionar nova estratégia: implementar `TradingStrategy`
- Adicionar novo preprocessador: herdar de `BasePreprocessor`

### **4. Reusabilidade**
- Componentes independentes podem ser reutilizados
- Factories podem ser usadas em outros projetos
- Interfaces definem contratos claros

---

## 🚀 Como Usar a Nova Arquitetura

### **Exemplo 1: Treinar modelo usando Factory**

```python
from ml_v2.domain import ModelConfig
from ml_v2.factories import ModelFactory
from ml_v2.infrastructure import DataLoader
from ml_v2.preprocess import DataPreprocessor

# Configurar modelo
config = ModelConfig(
    model_type='directional',
    lookback=60,
    lstm_units=128,
    lstm_layers=3,
    dropout=0.4,
    learning_rate=1e-3,
    batch_size=64,
    epochs=100
)

# Criar modelo via factory
model = ModelFactory.create_model(config)
callbacks = ModelFactory.get_callbacks(config)

# Carregar e preprocessar dados
loader = DataLoader()
df = loader.load_csv("data/BTCUSDT_30m_full.csv")

preprocessor = DataPreprocessor(...)
X_train, y_train = preprocessor.fit_transform(df_train)
X_val, y_val = preprocessor.transform(df_val)

# Treinar
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=config.epochs,
    batch_size=config.batch_size,
    callbacks=callbacks
)
```

### **Exemplo 2: Backtest com injeção de dependência**

```python
from ml_v2.domain import BacktestConfig
from ml_v2.backtest import DirectionalBacktester

# Configurar backtest
config = BacktestConfig(
    initial_capital=100000,
    fee_bps=10.0,
    slippage_bps=5.0,
    position_size=0.95,
    min_confidence=0.6
)

# Criar backtester (implementa BaseBacktester)
backtester = DirectionalBacktester(**config.__dict__)

# Executar (depende de abstração, não implementação)
history = backtester.run_backtest(df_test, predictions, probabilities)
metrics = backtester.calculate_metrics()
```

---

## 📚 Referências

- **Clean Code** - Robert C. Martin
- **Design Patterns** - Gang of Four
- **Domain-Driven Design** - Eric Evans
- **Python Type Hints** - PEP 544 (Protocols)

---

## 🎯 Próximos Passos

1. ✅ Migrar código legado para usar factories
2. ✅ Implementar Strategy Pattern completo para backtesting
3. ⏳ Adicionar Observer Pattern para callbacks personalizados
4. ⏳ Criar testes unitários para todas as interfaces
5. ⏳ Documentar exemplos de uso avançados

---

**✨ Esta arquitetura garante que o código seja profissional, escalável e fácil de manter!**
