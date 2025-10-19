# 🚀 QUICK START - ML_V3_ARCH

**Última atualização:** 18 de Outubro de 2025

---

## ⚡ Comandos Rápidos

### **Executar TODOS os testes**
```bash
uv run python -m pytest tests/ml_v3_arch/ -v
```

### **Executar testes sem coverage (mais rápido)**
```bash
uv run python -m pytest tests/ml_v3_arch/ --no-cov -q
```

### **Executar com coverage HTML**
```bash
uv run python -m pytest tests/ml_v3_arch/ --cov=src/ml_v3_arch --cov-report=html
# Abrir: coverage_html/index.html
```

### **Executar testes específicos**
```bash
# Domain
uv run python -m pytest tests/ml_v3_arch/test_domain.py -v

# Factories
uv run python -m pytest tests/ml_v3_arch/test_factories.py -v

# TrainingService
uv run python -m pytest tests/ml_v3_arch/test_services_training.py -v
```

### **Executar um teste específico**
```bash
uv run python -m pytest tests/ml_v3_arch/test_services_training.py::TestTrainingServiceTrain::test_no_data_leakage_in_preprocessing -v
```

---

## 📊 Status Atual

```
✅ Domain Tests:        38/38 passing
✅ Factories Tests:     36/36 passing
✅ TrainingService:     13/13 passing
⏳ EvaluationService:   0/15 pending
⏳ BacktestService:     0/15 pending
⏳ Infrastructure:      0/20 pending

TOTAL: 87/150+ (58%)
```

---

## 📁 Estrutura de Arquivos

```
src/ml_v3_arch/
├── domain/
│   └── entities.py              # ModelConfig, BacktestConfig, Trade
├── interfaces/
│   └── base.py                  # BaseModel, BasePreprocessor
├── factories/
│   └── model_factory.py         # 4 tipos de modelos
├── services/
│   ├── training_service.py      # ✅ 13 testes
│   ├── evaluation_service.py    # ⏳ 0 testes
│   └── backtest_service.py      # ⏳ 0 testes
├── infrastructure/
│   ├── data_loader.py           # ⏳ 0 testes
│   └── model_persistence.py     # ⏳ 0 testes
├── examples/
│   └── full_pipeline.py
└── docs/
    ├── PHASE3_FINAL_REPORT.md   # ✅ Relatório técnico completo
    ├── EXECUTIVE_SUMMARY.md     # ✅ Resumo executivo
    ├── PHASE3_TESTS_PROGRESS.md # ✅ Progresso detalhado
    └── QUICK_START.md           # ✅ Este arquivo

tests/ml_v3_arch/
├── conftest.py                  # 8 fixtures reutilizáveis
├── test_domain.py               # ✅ 38 testes (425 linhas)
├── test_factories.py            # ✅ 36 testes (470 linhas)
└── test_services_training.py    # ✅ 13 testes (490 linhas)
```

---

## 🔧 Configuração Inicial

### **1. Instalar dependências**
```bash
uv sync
```

### **2. Verificar instalação**
```bash
uv run python -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)"
uv run python -c "import pytest; print('pytest:', pytest.__version__)"
```

### **3. Executar testes**
```bash
uv run python -m pytest tests/ml_v3_arch/ --no-cov -q
```

**Esperado:** `87 passed in ~4s`

---

## 📚 Documentação

### **Relatórios Completos**
1. **PHASE3_FINAL_REPORT.md** - Relatório técnico detalhado (87 testes)
2. **EXECUTIVE_SUMMARY.md** - Resumo executivo do projeto
3. **PHASE3_TESTS_PROGRESS.md** - Progresso por componente

### **Arquitetura**
4. **PHASE1_ARCHITECTURE.md** - Domain, Interfaces, Factories
5. **PHASE2_SERVICES.md** - Services + Infrastructure

### **Guias**
6. **.github/copilot-instructions.md** - Instruções para Copilot

---

## 🎯 Exemplos de Uso

### **Criar e Treinar Modelo**
```python
from ml_v3_arch.domain import ModelConfig
from ml_v3_arch.factories import ModelFactory
from ml_v3_arch.services import TrainingService

# 1. Config
config = ModelConfig(
    model_type='lstm',
    lookback=60,
    lstm_units=64,
    lstm_layers=2,
    dropout=0.3,
    learning_rate=0.001,
    batch_size=32,
    epochs=50,
    patience=10
)

# 2. Criar modelo via Factory
model = ModelFactory.create_model(config)

# 3. Criar serviço de treino
training_service = TrainingService(
    model=model,
    preprocessor=preprocessor,
    config=config,
    artifacts_dir="artifacts"
)

# 4. Treinar
result = training_service.train(
    df_train=df_train,
    df_val=df_val,
    save_artifacts=True,
    verbose=1
)

print(f"✅ Treino concluído em {result['metadata']['total_time']:.2f}s")
```

### **Avaliar Modelo**
```python
from ml_v3_arch.services import EvaluationService

# Criar avaliador
evaluator = EvaluationService(model=model, preprocessor=preprocessor)

# Avaliar
metrics = evaluator.evaluate(df_test)

print(f"MAE: {metrics['mae']:.4f}")
print(f"RMSE: {metrics['rmse']:.4f}")
print(f"Hit Rate: {metrics['hit_rate']:.2%}")
```

### **Backtest**
```python
from ml_v3_arch.domain import BacktestConfig
from ml_v3_arch.services import BacktestService

# Config
backtest_config = BacktestConfig(
    initial_capital=10000.0,
    fee_bps=10.0,
    slippage_bps=5.0,
    position_size=0.95,
    min_confidence=0.6
)

# Criar serviço
backtest_service = BacktestService(config=backtest_config)

# Executar backtest
result = backtest_service.run(signals=signals, prices=prices)

print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {result['max_drawdown']:.2%}")
print(f"Win Rate: {result['win_rate']:.2%}")
```

---

## 🧪 Fixtures Disponíveis (conftest.py)

### **Configs**
```python
def test_something(sample_model_config):
    # ModelConfig já configurado
    assert sample_model_config.model_type == 'lstm'

def test_backtest(sample_backtest_config):
    # BacktestConfig já configurado
    assert sample_backtest_config.initial_capital == 10000.0
```

### **Dados**
```python
def test_training(sample_data):
    X_train, y_train, X_val, y_val, X_test, y_test = sample_data
    # Dados sintéticos prontos para uso

def test_backtest(sample_prices):
    # pd.Series com 1000 preços

def test_dataloader(sample_dataframe):
    # pd.DataFrame OHLC com 1000 candles
```

### **Mocks**
```python
def test_service(mock_keras_model, mock_preprocessor):
    # Mocks já configurados
    # mock_keras_model.fit retorna histórico
    # mock_preprocessor.fit_transform retorna (X, y)
```

### **Temporários**
```python
def test_save_artifacts(tmp_path):
    # Diretório temporário
    # Limpo automaticamente após o teste
```

---

## 🐛 Debugging

### **Executar teste com output detalhado**
```bash
uv run python -m pytest tests/ml_v3_arch/test_services_training.py::TestTrainingServiceVerbosity::test_verbose_1_prints_progress -vv -s
```

### **Executar com breakpoint**
```python
def test_something():
    # ...
    import pdb; pdb.set_trace()  # Breakpoint
    # ...
```

### **Ver fixtures disponíveis**
```bash
uv run python -m pytest tests/ml_v3_arch/ --fixtures
```

---

## 📈 Métricas de Qualidade

```bash
# Coverage report
uv run python -m pytest tests/ml_v3_arch/ --cov=src/ml_v3_arch --cov-report=term-missing

# Slow tests
uv run python -m pytest tests/ml_v3_arch/ --durations=10

# Failed tests only
uv run python -m pytest tests/ml_v3_arch/ --lf

# Stop on first failure
uv run python -m pytest tests/ml_v3_arch/ -x
```

---

## 🎯 Próximos Passos

### **Para Desenvolvedores**

1. **Completar Phase 3:**
   ```bash
   # Criar test_services_evaluation.py
   # Criar test_services_backtest.py
   # Criar test_infrastructure.py
   ```

2. **Atingir 80% coverage:**
   ```bash
   uv run python -m pytest tests/ml_v3_arch/ --cov=src/ml_v3_arch --cov-fail-under=80
   ```

3. **Integration Tests:**
   ```bash
   # Criar tests/integration/
   # Testar pipeline completo end-to-end
   ```

### **Para Usuários**

1. **Ver exemplos:**
   ```python
   # Abrir: src/ml_v3_arch/examples/full_pipeline.py
   ```

2. **Ler documentação:**
   ```bash
   # Abrir: src/ml_v3_arch/docs/EXECUTIVE_SUMMARY.md
   ```

3. **Executar pipeline:**
   ```bash
   uv run python src/ml_v3_arch/examples/full_pipeline.py
   ```

---

## 🔗 Links Úteis

- **pytest docs**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-mock**: https://pytest-mock.readthedocs.io/
- **uv**: https://docs.astral.sh/uv/

---

## 📞 Suporte

**Dúvidas?** Consulte:
1. `PHASE3_FINAL_REPORT.md` - Relatório técnico completo
2. `EXECUTIVE_SUMMARY.md` - Resumo executivo
3. `.github/copilot-instructions.md` - Para usar com Copilot

---

**Criado por:** GitHub Copilot  
**Versão:** 1.0  
**Status:** ✅ 87/87 testes passando
