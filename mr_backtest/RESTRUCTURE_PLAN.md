# 🏗️ Reestruturação do Projeto - Plano de Implementação

## 📊 Estrutura Atual (BAGUNÇADA)

```
mr_backtest/
├── src/
│   ├── analyze_checkpoint.py     # Duplicado
│   ├── analyze_results.py        # Mal organizado
│   ├── config.py                 # Config management
│   ├── download_btc_csv.py       # Download
│   ├── genetic_optimizer.py      # AG
│   ├── grid_search_1h.py         # Scripts soltos
│   ├── mr_backtest.py            # Core backtesting
│   ├── optimize_daily_trader.py  # Scripts soltos
│   ├── optimize_roi.py           # Scripts soltos
│   └── quick_test_1h.py          # Scripts soltos
├── analyze_checkpoint.py         # ❌ Duplicado na raiz
├── grid_search_1h.py             # ❌ Duplicado na raiz
├── quick_test_1h.py              # ❌ Duplicado na raiz
├── config/, data/, report/       # OK
└── Vários README.md              # Documentação espalhada
```

## 🎯 Estrutura Nova (PROFISSIONAL)

```
mr_backtest/
├── src/
│   ├── __init__.py
│   │
│   ├── download/                 # 📥 Módulo de Download
│   │   ├── __init__.py
│   │   ├── downloader.py         # Classe principal
│   │   └── utils.py              # Helpers
│   │
│   ├── backtest/                 # 🔬 Módulo de Backtesting
│   │   ├── __init__.py
│   │   ├── engine.py             # Core backtesting engine
│   │   ├── strategies.py         # Strategy classes
│   │   ├── indicators.py         # Technical indicators
│   │   └── utils.py              # Helpers
│   │
│   ├── analysis/                 # 📊 Módulo de Análise
│   │   ├── __init__.py
│   │   ├── metrics.py            # Performance metrics
│   │   ├── visualizer.py         # Plots e gráficos
│   │   ├── reporter.py           # Reports generation
│   │   └── utils.py              # Helpers
│   │
│   ├── optimization/             # 🧬 Módulo de Otimização
│   │   ├── __init__.py
│   │   ├── genetic.py            # Genetic Algorithm
│   │   ├── grid.py               # Grid Search
│   │   ├── neural.py             # Neural Network (futuro)
│   │   └── utils.py              # Helpers
│   │
│   ├── config/                   # ⚙️ Módulo de Configuração
│   │   ├── __init__.py
│   │   ├── manager.py            # Config management
│   │   ├── params.py             # Parameter classes
│   │   └── utils.py              # Helpers
│   │
│   └── utils/                    # 🛠️ Utilities Globais
│       ├── __init__.py
│       ├── file_io.py            # File operations
│       ├── logger.py             # Logging
│       └── constants.py          # Constants
│
├── scripts/                      # 🚀 Scripts de Execução
│   ├── download_data.py          # Download datasets
│   ├── run_backtest.py           # Run backtests
│   ├── run_grid_search.py        # Grid search
│   ├── run_genetic_optimizer.py  # GA optimization
│   └── analyze_results.py        # Analyze results
│
├── tests/                        # 🧪 Testes
│   ├── test_backtest.py
│   ├── test_optimization.py
│   └── test_download.py
│
├── config/                       # ⚙️ Configs (data files)
│   └── params.csv
│
├── data/                         # 📁 Data files
│   ├── raw/                      # Downloaded data
│   └── processed/                # Processed results
│
├── report/                       # 📊 Reports
│   └── ...
│
├── docs/                         # 📚 Documentação
│   ├── README.md
│   ├── GUIDE.md
│   └── API.md
│
├── notebooks/                    # 📓 Jupyter notebooks (opcional)
│   └── exploration.ipynb
│
├── .env                          # Environment vars
├── .gitignore
├── pyproject.toml
├── README.md                     # Main README
└── setup.py                      # Package setup
```

## 📋 Plano de Migração

### Fase 1: Criar Estrutura de Diretórios
```bash
mkdir -p src/{download,backtest,analysis,optimization,config,utils}
mkdir -p scripts tests docs notebooks data/{raw,processed}
touch src/{download,backtest,analysis,optimization,config,utils}/__init__.py
```

### Fase 2: Migrar e Refatorar Arquivos

#### 📥 Download Module
- `src/download_btc_csv.py` → `src/download/downloader.py`
- Criar `src/download/utils.py`

#### 🔬 Backtest Module  
- `src/mr_backtest.py` → Dividir em:
  - `src/backtest/engine.py` (core backtesting)
  - `src/backtest/strategies.py` (Strategy classes)
  - `src/backtest/indicators.py` (RSI, ATR, MA)

#### 📊 Analysis Module
- `src/analyze_results.py` → `src/analysis/reporter.py`
- `src/analyze_checkpoint.py` → `src/analysis/checkpoint_analyzer.py`
- Criar `src/analysis/metrics.py`
- Criar `src/analysis/visualizer.py`

#### 🧬 Optimization Module
- `src/genetic_optimizer.py` → `src/optimization/genetic.py`
- `src/grid_search_1h.py` → `scripts/run_grid_search.py`
- `src/optimize_roi.py` → `scripts/run_genetic_optimizer.py`
- `src/optimize_daily_trader.py` → `scripts/run_genetic_optimizer.py`

#### ⚙️ Config Module
- `src/config.py` → Dividir em:
  - `src/config/manager.py` (ConfigManager)
  - `src/config/params.py` (Params, StrategyConfig, ParamRange)

#### 🚀 Scripts
- Mover scripts de execução para `scripts/`
- Scripts devem importar de `src.module`

### Fase 3: Atualizar Imports
- Atualizar todos imports para nova estrutura
- Ex: `from src.backtest.engine import Backtest`

### Fase 4: Limpeza
- Remover arquivos duplicados na raiz
- Consolidar documentação em `docs/`

## 🎯 Benefícios

✅ **Organização Clara**: Cada módulo tem responsabilidade definida
✅ **Escalabilidade**: Fácil adicionar novos módulos (RN, etc)
✅ **Testabilidade**: Estrutura facilita testes unitários
✅ **Manutenibilidade**: Código organizado por funcionalidade
✅ **Profissional**: Estrutura padrão da indústria
✅ **Reutilização**: Classes utils em cada módulo

## 🚀 Próximos Passos

1. ✅ Criar estrutura de diretórios
2. ✅ Migrar arquivos com refatoração
3. ✅ Atualizar imports
4. ✅ Criar testes básicos
5. ✅ Consolidar documentação
6. ✅ Remover duplicados
7. ✅ Validar funcionamento

**Deseja prosseguir com a reestruturação?**
