# 📁 Estrutura do Projeto - Mean Reversion Backtest

## 📂 Organização de Pastas

```
mr_backtest/
├── 📄 README.md                    # Documentação principal do projeto
├── 📄 OPTIMIZATION_README.md       # Guia de otimização com AG
├── 📄 ANALYZE_README.md            # Guia de análise de resultados
├── 📄 STRUCTURE.md                 # Este arquivo - estrutura do projeto
├── 📄 pyproject.toml               # Configuração do projeto e dependências
├── 📄 uv.lock                      # Lock file de dependências (uv)
├── 📄 .python-version              # Versão do Python (3.12+)
├── 📄 .env                         # Variáveis de ambiente
│
├── 📁 src/                         # 🔧 Código fonte
│   ├── mr_backtest.py              # Motor de backtesting principal
│   ├── config.py                   # Gerenciador de parâmetros
│   ├── genetic_optimizer.py        # Otimizador com algoritmo genético
│   └── download_btc_csv.py         # Download de dados da Binance
│
├── 📁 config/                      # ⚙️ Arquivos de configuração
│   └── params.csv                  # Parâmetros de estratégias (5 presets)
│
├── 📁 data/                        # 📊 Dados e resultados
│   ├── BTCUSDT_daily.csv           # Dados históricos BTC (principal)
│   ├── BTCUSDT_daily_sample.csv    # Sample de dados para testes
│   ├── grid_results.csv            # Resultados completos do grid search
│   ├── best_robust_configs.csv     # Top configurações robustas
│   └── trades.csv                  # Trades individuais do último backtest
│
├── 📁 report/                      # 📈 Análises e relatórios
│   ├── analyze_results.py          # Script de análise de resultados
│   ├── EXECUTIVE_REPORT.md         # Relatório executivo
│   ├── SUMMARY.md                  # Resumo das análises
│   ├── grid_results_analysis.png   # Gráficos de análise
│   └── optimization_history.csv    # Histórico de otimização AG
│
└── 📁 .venv/                       # Ambiente virtual Python
```

---

## 🎯 Convenções de Paths

### Paths Relativos Automáticos

Todos os módulos agora suportam **paths relativos** e resolvem automaticamente para as pastas corretas:

#### 1. **CSV de Dados** → `data/`
```python
# Ao usar mr_backtest.py ou genetic_optimizer.py
python src/mr_backtest.py --csv BTCUSDT_daily.csv
# Resolve para: data/BTCUSDT_daily.csv

# OU path absoluto
python src/mr_backtest.py --csv C:\full\path\to\my_data.csv
```

#### 2. **Arquivos de Config** → `config/`
```python
# Ao usar config.py
from config import load_params_from_csv
config = load_params_from_csv('params.csv')
# Resolve para: config/params.csv

# OU path absoluto
config = load_params_from_csv('C:\full\path\to\my_params.csv')
```

#### 3. **Relatórios e Análises** → `report/`
```python
# Ao usar analyze_results.py
python report/analyze_results.py --csv grid_results.csv
# Resolve para: data/grid_results.csv (entrada)
# Gráficos salvos em: report/grid_results_analysis.png (saída)

# Ao salvar histórico de otimização
optimizer.save_history('optimization_history.csv')
# Resolve para: report/optimization_history.csv
```

#### 4. **Resultados de Grid Search** → `data/`
```python
# Grid search sempre salva em data/
python src/mr_backtest.py --csv BTCUSDT_daily.csv --grid
# Salva: data/grid_results.csv
```

---

## 🚀 Workflows Principais

### 1. Download de Dados
```bash
# Baixar dados atualizados da Binance
cd src
python download_btc_csv.py --start 2020-01-01 --out BTCUSDT_daily.csv
# Salva em: data/BTCUSDT_daily.csv
```

### 2. Backtest Individual
```bash
# Testar uma configuração específica
cd src
python mr_backtest.py --csv BTCUSDT_daily.csv \
  --variant base --ma_len 220 --dist_below_ma_pct 0.05 \
  --tp_pct 0.10 --sl_pct 0.10 --no_breakeven
# Salva trades em: data/trades.csv
```

### 3. Backtest com Config File
```bash
# Usar parâmetros de config/params.csv
cd src
python mr_backtest.py --config params.csv --csv BTCUSDT_daily.csv
# Lê: config/params.csv
# Salva: data/trades.csv
```

### 4. Grid Search
```bash
# Executar grid search completo
cd src
python mr_backtest.py --csv BTCUSDT_daily.csv --grid
# Lê: data/BTCUSDT_daily.csv
# Salva: data/grid_results.csv
# Tempo: ~35-40 minutos (3,888 combinações)
```

### 5. Análise de Resultados
```bash
# Analisar resultados do grid search
cd report
python analyze_results.py --csv grid_results.csv --top 20 --plot
# Lê: data/grid_results.csv
# Salva: report/grid_results_analysis.png
```

### 6. Otimização com AG
```bash
# Otimizar parâmetros com algoritmo genético
cd src
python genetic_optimizer.py
# Lê: data/BTCUSDT_daily.csv
# Salva: config/optimized_params.csv
# Salva: report/optimization_history.csv
```

---

## 📝 Arquivos Importantes

### Código Fonte (`src/`)

#### `mr_backtest.py` (21.7 KB)
- Motor principal de backtesting
- 3 variantes de estratégia: BASE, RSI, RECLAIM
- Suporte a grid search
- CLI completo com argparse
- **Novo**: Suporta `--config` parameter

**Uso:**
```bash
python src/mr_backtest.py --csv BTCUSDT_daily.csv --grid
python src/mr_backtest.py --config champion.csv
```

#### `config.py` (~370 linhas)
- Gerenciador de parâmetros com dataclass
- Load/save de CSV
- Validação de parâmetros
- Ranges para otimização
- **Novo**: Resolve paths automaticamente para `config/`

**Uso:**
```python
from config import load_params_from_csv, save_params_to_csv

config = load_params_from_csv('params.csv')  # config/params.csv
params = config.to_params()
```

#### `genetic_optimizer.py` (~425 linhas)
- Algoritmo genético para otimização
- 6 objetivos: PROFIT_FACTOR, MULTI, ROI, etc.
- Elitismo, mutação adaptativa
- Multi-objetivo com pesos configuráveis
- **Novo**: Resolve paths para `data/` e `report/`

**Uso:**
```python
from genetic_optimizer import GeneticOptimizer, OptimizationObjective

optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',  # data/BTCUSDT_daily.csv
    population_size=50,
    generations=30
)
best = optimizer.run()
optimizer.save_history('evolution.csv')  # report/evolution.csv
```

#### `download_btc_csv.py` (108 linhas)
- Download de dados históricos da Binance API
- **Novo**: Salva automaticamente em `data/`

**Uso:**
```bash
python src/download_btc_csv.py --start 2020-01-01
# Salva: data/BTCUSDT_daily.csv
```

### Configuração (`config/`)

#### `params.csv`
CSV com 5 conjuntos de parâmetros:
- **champion**: Melhor do grid search (PF=2.63, WR=73%)
- **runner_up**: Segundo melhor (PF=2.32)
- **aggressive**: Mais trades, maior risco
- **conservative**: Menos risco, mais conservador
- **default**: Parâmetros padrão

**Colunas:**
```
name,description,variant,ma_len,dist_below_ma_pct,tp_pct,sl_pct,
atr_mult,time_stop,be_trigger_pct,allow_breakeven,capital_per_trade,
fees_bps,slip_bps,rsi_period,slope_lookback,rsi_cross_level
```

### Dados (`data/`)

#### `BTCUSDT_daily.csv`
Dados históricos principais (2020-2025):
- Date, Open, High, Low, Close
- Timeframe: Daily (1d)
- Par: BTC/USDT (Binance Spot)

#### `grid_results.csv` (808 KB)
Resultados do grid search:
- 3,888 combinações testadas
- 12 métricas por combinação
- Sorted by profit_factor desc

#### `best_robust_configs.csv` (59 KB)
Top 244 configurações:
- PF >= 1.01
- Trades >= 5
- Sorted by profit_factor

### Relatórios (`report/`)

#### `analyze_results.py` (344 linhas)
Script de análise com 6 funções:
1. basic_stats() - Estatísticas gerais
2. variant_comparison() - Comparar BASE vs RSI vs RECLAIM
3. top_configurations() - Top N configs
4. parameter_sensitivity() - Sensibilidade de parâmetros
5. robust_configurations() - Configs robustas
6. plot_results() - Visualizações

**Uso:**
```bash
python report/analyze_results.py --csv grid_results.csv --top 20 --plot
```

#### `EXECUTIVE_REPORT.md` (10.0 KB)
Relatório executivo com:
- Resumo dos resultados
- Champion config
- Comparação de variantes
- Recomendações

#### `SUMMARY.md` (9.1 KB)
Resumo detalhado:
- Top 10 configs
- Análise de parâmetros
- Insights e conclusões

---

## 🔄 Migrações e Compatibilidade

### ✅ Backwards Compatible

Todos os módulos mantêm **compatibilidade com paths absolutos**:

```python
# Funciona com paths absolutos
python src/mr_backtest.py --csv C:\full\path\BTCUSDT_daily.csv

# Funciona com paths relativos (resolve automaticamente)
python src/mr_backtest.py --csv BTCUSDT_daily.csv
```

### 🔧 Função Helper: `get_project_root()`

Todos os módulos usam a mesma função helper:

```python
def get_project_root() -> str:
    """Get the project root directory (parent of src/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

Isso garante que paths relativos sejam resolvidos corretamente independente de onde o script é executado.

---

## 📦 Dependências

Gerenciadas via `pyproject.toml`:

```toml
[project]
name = "mr-backtest"
version = "1.0.0"
requires-python = ">=3.12"

dependencies = [
    "pandas>=2.3.3",
    "numpy>=2.2.0",
    "tqdm>=4.66.0",       # Progress bar
    "requests>=2.32.3",   # Download de dados
]

[project.optional-dependencies]
viz = [
    "matplotlib>=3.9.0",
    "seaborn>=0.13.0"
]
```

**Instalar:**
```bash
# Dependências core
uv pip install -e .

# Com visualizações
uv pip install -e ".[viz]"
```

---

## 🎓 Guias de Uso

### Para Iniciantes
1. Ler `README.md` - Documentação principal
2. Executar backtest individual com `mr_backtest.py`
3. Analisar resultados com `analyze_results.py`

### Para Otimização
1. Ler `OPTIMIZATION_README.md` - Guia completo de otimização
2. Executar `genetic_optimizer.py` com população pequena (teste)
3. Aumentar population_size e generations para produção

### Para Análise Avançada
1. Ler `ANALYZE_README.md` - 40+ exemplos de análise
2. Usar funções Python diretamente
3. Criar análises customizadas com pandas

---

## 🧪 Testing

### Quick Test (5 min)
```bash
cd src
python genetic_optimizer.py
# Testa: data paths, config paths, report paths
# População: 20, Gerações: 5
```

### Full Test (30-45 min)
```bash
# 1. Grid search
cd src
python mr_backtest.py --csv BTCUSDT_daily.csv --grid

# 2. Análise
cd ../report
python analyze_results.py --csv grid_results.csv --plot

# 3. Otimização
cd ../src
python genetic_optimizer.py
```

---

## 📊 Métricas e Resultados

### Champion Configuration (Grid Search)
```
Variant: BASE
MA Length: 220
Distance: 5% below MA
TP: 10%, SL: 10%
Breakeven: False
Time Stop: 30 bars

Profit Factor: 2.63
Win Rate: 73%
Trades: 22
Trades/Year: 6.87
Total PnL: $3,589.97
Max Drawdown: -$498.88
```

### Objetivos de Otimização
- **Meta**: 15-20 trades/ano mantendo PF > 1.5
- **Atual**: 6-7 trades/ano com PF = 2.63
- **Estratégia**: Usar AG multi-objetivo (MULTI)

---

## 🔮 Próximos Passos

1. **Testar refatoração**: Executar todos workflows e validar paths
2. **Otimização AG**: Rodar com população 50-100, gerações 30-50
3. **Análise out-of-sample**: Split data train/test
4. **Walk-forward analysis**: Validação temporal
5. **Rede Neural**: Implementar `neural_optimizer.py`

---

## 💡 Dicas de Desenvolvimento

### Adicionar Novo Script em `src/`
```python
import os

def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths relativos
data_path = os.path.join(get_project_root(), "data", "file.csv")
config_path = os.path.join(get_project_root(), "config", "params.csv")
report_path = os.path.join(get_project_root(), "report", "output.csv")
```

### Adicionar Novo Preset em `config/params.csv`
1. Copiar linha existente (ex: champion)
2. Modificar valores de parâmetros
3. Mudar `name` e `description`
4. Salvar CSV

### Adicionar Nova Análise em `report/`
1. Criar script Python em `report/`
2. Importar: `from src.mr_backtest import ...`
3. Ler de: `data/grid_results.csv`
4. Salvar em: `report/my_analysis.csv`

---

**Estrutura organizada e pronta para produção!** 🚀  
**Versão**: 2.0 | **Data**: Outubro 2025
