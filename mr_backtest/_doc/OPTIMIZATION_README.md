# 🧬 Sistema de Otimização de Parâmetros

Sistema modular para otimização de estratégias de trading usando Algoritmos Genéticos (AG), preparado para extensão com Redes Neurais (RN) e outros métodos.

---

## 🎯 Objetivos

1. **Aumentar ROI** (Return on Investment)
2. **Aumentar frequência de trades** (trades/ano)
3. **Manter alto profit factor**
4. **Minimizar drawdown**
5. **Otimização multi-objetivo**

---

## 📦 Módulos Criados

### 1. `config.py` - Gerenciador de Parâmetros
**Funcionalidades:**
- Carrega/salva parâmetros de CSV
- Validação de parâmetros
- Definição de ranges para otimização
- Suporte a múltiplos conjuntos de parâmetros

**Uso:**
```python
from config import load_params_from_csv, save_params_to_csv

# Carregar parâmetros
config = load_params_from_csv('params.csv')

# Validar
is_valid, errors = config.validate()

# Salvar
save_params_to_csv(config, 'my_params.csv')
```

### 2. `params.csv` - Template de Parâmetros
CSV com 5 conjuntos pré-configurados:
- **champion** - Melhor do grid search
- **runner_up** - Segundo melhor
- **aggressive** - Mais trades, maior risco
- **conservative** - Menos risco
- **default** - Parâmetros padrão

### 3. `genetic_optimizer.py` - Algoritmo Genético
**Funcionalidades:**
- Otimização multi-objetivo
- Elitismo (melhores sempre sobrevivem)
- Mutação adaptativa (diminui com gerações)
- Crossover uniforme
- Suporte futuro para paralelização

**Uso:**
```python
from genetic_optimizer import GeneticOptimizer, OptimizationObjective

optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    population_size=50,
    generations=30,
    objective=OptimizationObjective.MULTI
)

best_config = optimizer.run()
```

---

## 🚀 Como Usar

### 1. Otimização Básica (Quick Start)

```bash
python genetic_optimizer.py
```

Isso vai:
- Carregar dados de `BTCUSDT_daily.csv`
- Executar 20 gerações com população de 50
- Otimizar para objetivo multi-objetivo
- Salvar resultado em `optimized_params.csv`

### 2. Otimização Customizada

```python
from genetic_optimizer import GeneticOptimizer, OptimizationObjective
from config import create_narrow_ranges

# Criar otimizador
optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    population_size=100,      # População maior = mais diversidade
    generations=50,           # Mais gerações = melhor convergência
    objective=OptimizationObjective.MULTI,
    param_ranges=create_narrow_ranges(),  # Ranges focados
    mutation_rate=0.2,        # Taxa de mutação inicial
    crossover_rate=0.7,       # Taxa de crossover
    elitism_rate=0.1,         # 10% dos melhores sobrevivem
    min_trades=10             # Mínimo de trades por config
)

# Executar
best_config = optimizer.run()

# Salvar
from config import save_params_to_csv
save_params_to_csv(best_config, 'best_params.csv')

# Salvar histórico de evolução
optimizer.save_history('evolution.csv')
```

### 3. Objetivos de Otimização Disponíveis

```python
# 1. Profit Factor (padrão do grid search)
objective=OptimizationObjective.PROFIT_FACTOR

# 2. Total PnL (maximizar lucro absoluto)
objective=OptimizationObjective.TOTAL_PNL

# 3. Sharpe Ratio (retorno ajustado a risco)
objective=OptimizationObjective.SHARPE

# 4. Trades per Year (mais operações)
objective=OptimizationObjective.TRADES_PER_YEAR

# 5. ROI (PnL / Drawdown)
objective=OptimizationObjective.ROI

# 6. Multi-objetivo (RECOMENDADO)
objective=OptimizationObjective.MULTI
```

### 4. Definir Ranges Customizados

```python
from config import ParamRange

custom_ranges = {
    'ma_len': ParamRange(
        name='ma_len',
        min_val=180,
        max_val=250,
        step=10,
        param_type='int'
    ),
    'tp_pct': ParamRange(
        name='tp_pct',
        min_val=0.05,
        max_val=0.20,
        step=0.01,
        param_type='float'
    ),
    'variant': ParamRange(
        name='variant',
        min_val=0,
        max_val=0,
        values=['base'],  # Só BASE (melhor variante)
        param_type='str'
    )
}

optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    param_ranges=custom_ranges,
    ...
)
```

---

## 📊 Entendendo o Objetivo Multi-Objetivo

O objetivo `MULTI` combina 4 métricas:

```python
fitness = (
    profit_factor * 0.30 +           # 30% - Qualidade das operações
    (trades_per_year / 20) * 100 * 0.25 +  # 25% - Frequência
    win_rate * 100 * 0.25 +          # 25% - Taxa de acerto
    (total_pnl / 1000) * 0.20        # 20% - Lucro absoluto
)
```

**Por quê?**
- **Profit Factor**: Garante qualidade (ganhos > perdas)
- **Trades/Ano**: Aumenta oportunidades (objetivo principal)
- **Win Rate**: Mantém consistência
- **Total PnL**: Maximiza retorno absoluto

---

## 🔧 Configuração de Ranges

### Ranges Padrão (Amplos)
```python
from config import create_default_ranges
ranges = create_default_ranges()
```

- **ma_len**: 150-250 (step 10)
- **dist_below_ma_pct**: 0.02-0.15 (step 0.01)
- **tp_pct**: 0.05-0.20 (step 0.01)
- **sl_pct**: 0.04-0.15 (step 0.01)
- **time_stop**: 10-60 (step 5)

### Ranges Estreitos (Focados)
```python
from config import create_narrow_ranges
ranges = create_narrow_ranges()
```

Baseados nos melhores resultados do grid search:
- **variant**: ['base'] apenas
- **ma_len**: 200-230 (step 5)
- **dist_below_ma_pct**: 0.03-0.10
- **tp_pct**: 0.08-0.15
- **sl_pct**: 0.06-0.12
- **allow_breakeven**: [False] apenas

**Recomendação**: Use ranges estreitos para convergência mais rápida.

---

## 📈 Exemplo Completo: Otimizar para Mais Trades

```python
from genetic_optimizer import GeneticOptimizer, OptimizationObjective

# Objetivo: Aumentar trades/ano mantendo qualidade
optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    population_size=80,
    generations=40,
    objective=OptimizationObjective.MULTI,  # Balancea frequência com qualidade
    min_trades=15,  # Exige mínimo de 15 trades
    mutation_rate=0.25,  # Mutação um pouco maior para exploração
    elitism_rate=0.15   # Mantém top 15%
)

print("Starting optimization for more trades per year...")
best = optimizer.run()

# Ver top 10
top10 = optimizer.get_top_n(10)
for i, ind in enumerate(top10, 1):
    m = ind.metrics
    print(f"\n#{i} - Fitness: {ind.fitness:.2f}")
    print(f"  Trades/Year: {m['trades_per_year']:.2f}")
    print(f"  PF: {m['profit_factor']:.2f}, WR: {m['win_rate']:.1%}")
    print(f"  PnL: ${m['total_pnl']:.2f}")
```

---

## 🧪 Workflow Recomendado

### Fase 1: Exploração (Ranges Amplos)
```python
# 1. Use ranges amplos para explorar espaço
optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    population_size=100,
    generations=30,
    param_ranges=create_default_ranges(),  # AMPLO
    objective=OptimizationObjective.MULTI
)

best1 = optimizer.run()
save_params_to_csv(best1, 'phase1_best.csv')
```

### Fase 2: Refinamento (Ranges Estreitos)
```python
# 2. Refine ao redor dos melhores resultados
optimizer = GeneticOptimizer(
    csv_data_path='BTCUSDT_daily.csv',
    population_size=60,
    generations=50,
    param_ranges=create_narrow_ranges(),  # ESTREITO
    objective=OptimizationObjective.MULTI
)

best2 = optimizer.run()
save_params_to_csv(best2, 'phase2_best.csv')
```

### Fase 3: Validação
```python
# 3. Testar melhor config com backtest individual
from mr_backtest import backtest, analyze, load_ohlc_csv

df = load_ohlc_csv('BTCUSDT_daily.csv')
params = best2.to_params()
trades, ec = backtest(df, params)
metrics = analyze(trades, ec, df)

print(f"Final validation:")
print(f"  Trades: {metrics['trades']}")
print(f"  Trades/Year: {metrics['trades_per_year']:.2f}")
print(f"  Profit Factor: {metrics['profit_factor']:.4f}")
print(f"  Win Rate: {metrics['win_rate']:.2%}")
print(f"  Total PnL: ${metrics['total_pnl']:.2f}")
```

---

## 📊 Análise dos Resultados

### Ver Evolução do Fitness
```python
import pandas as pd
import matplotlib.pyplot as plt

# Carregar histórico
hist = pd.DataFrame(optimizer.history)

plt.figure(figsize=(10, 6))
plt.plot(hist['generation'], hist['best_fitness'], label='Best', linewidth=2)
plt.plot(hist['generation'], hist['avg_fitness'], label='Average', alpha=0.7)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Fitness Evolution')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('fitness_evolution.png')
plt.show()
```

### Comparar Top Configurations
```python
top10 = optimizer.get_top_n(10)

# Criar DataFrame
data = []
for ind in top10:
    row = {
        'fitness': ind.fitness,
        'pf': ind.metrics['profit_factor'],
        'wr': ind.metrics['win_rate'],
        'tpy': ind.metrics['trades_per_year'],
        'pnl': ind.metrics['total_pnl'],
        'ma_len': ind.config.ma_len,
        'tp_pct': ind.config.tp_pct,
        'sl_pct': ind.config.sl_pct
    }
    data.append(row)

df = pd.DataFrame(data)
print(df.to_string(index=False))
```

---

## 🎛️ Tuning de Hiperparâmetros do AG

### Population Size
- **Pequena (20-30)**: Rápido, mas pode convergir prematuramente
- **Média (50-80)**: Balanço entre velocidade e diversidade
- **Grande (100+)**: Mais diversidade, mais lento

### Generations
- **Poucas (10-20)**: Testes rápidos
- **Médias (30-50)**: Produção normal
- **Muitas (50-100)**: Refinamento fino

### Mutation Rate
- **Baixa (0.1)**: Refinamento de soluções próximas
- **Média (0.2)**: Balanço
- **Alta (0.3+)**: Mais exploração

### Elitism Rate
- **Baixo (0.05)**: Mais mudança entre gerações
- **Médio (0.1-0.15)**: Recomendado
- **Alto (0.2+)**: Convergência mais rápida

---

## 🔮 Próximos Passos: Rede Neural

Para implementar otimização com RN:

```python
# neural_optimizer.py (estrutura futura)

class NeuralOptimizer:
    def __init__(self, ...):
        # Rede neural que aprende:
        # Input: parâmetros da estratégia
        # Output: métricas esperadas (PF, WR, TPY, etc)
        pass
    
    def train(self, historical_results):
        # Treina com resultados do grid search
        pass
    
    def predict_fitness(self, params):
        # Prediz fitness sem executar backtest
        pass
    
    def optimize(self):
        # Usa gradiente descendente ou bayesiano
        pass
```

---

## 💡 Dicas e Boas Práticas

### 1. Comece Pequeno
```bash
# Teste com população pequena primeiro
python -c "
from genetic_optimizer import GeneticOptimizer, OptimizationObjective
opt = GeneticOptimizer(
    'BTCUSDT_daily.csv',
    population_size=10,
    generations=3
)
opt.run()
"
```

### 2. Use Multi-Objetivo
O objetivo `MULTI` é melhor para aumentar trades mantendo qualidade.

### 3. Valide em Out-of-Sample
```python
# Split data
train_df = df[df['Date'] < '2024-01-01']
test_df = df[df['Date'] >= '2024-01-01']

# Optimize on train
# Test on test
```

### 4. Monitore Overfitting
Se fitness está muito alto mas poucos trades, pode ser overfitting.

### 5. Combine com Grid Search
Use grid search para mapear o espaço, depois AG para refinar.

---

## 📁 Estrutura de Arquivos

```
mr_backtest/
├── config.py                    # ✅ Gerenciador de parâmetros
├── params.csv                   # ✅ Templates de parâmetros
├── genetic_optimizer.py         # ✅ Algoritmo Genético
├── mr_backtest.py               # Backtester (existente)
├── analyze_results.py           # Analisador (existente)
├── OPTIMIZATION_README.md       # Esta documentação
├── optimized_params.csv         # Resultado da otimização
└── optimization_history.csv     # Histórico de evolução
```

---

## 🚀 Comandos Rápidos

```bash
# 1. Otimização padrão (rápida)
python genetic_optimizer.py

# 2. Otimização customizada
python -c "
from genetic_optimizer import GeneticOptimizer, OptimizationObjective
opt = GeneticOptimizer(
    'BTCUSDT_daily.csv',
    population_size=60,
    generations=40,
    objective=OptimizationObjective.MULTI,
    min_trades=10
)
best = opt.run()
"

# 3. Testar parâmetros otimizados
python mr_backtest.py --csv BTCUSDT_daily.csv \
  --variant base --ma_len 220 --dist_below_ma_pct 0.05 \
  --tp_pct 0.10 --sl_pct 0.10 --no_breakeven
```

---

## ⚙️ Dependências Adicionais

Já incluídas no projeto:
- `pandas`
- `numpy`
- `tqdm`

Para visualizações (opcional):
```bash
pip install matplotlib seaborn
```

---

## 📊 Benchmarks

Tempos típicos (i7, 8 cores):
- **População 50, 20 gerações**: ~10-15 minutos
- **População 100, 50 gerações**: ~45-60 minutos
- **População 200, 100 gerações**: ~3-4 horas

---

## 🎯 Meta: Aumentar Trades/Ano

Baseado no grid search:
- **Atual melhor**: 6-7 trades/ano (PF=2.63)
- **Meta otimização**: 15-20 trades/ano mantendo PF > 1.5

**Estratégias:**
1. Reduzir `dist_below_ma_pct` (mais sinais)
2. Aumentar `tp_pct` e `sl_pct` assimétricos
3. Reduzir `time_stop` para saídas mais rápidas
4. Testar `ma_len` menor (MA mais reativa)

---

**Desenvolvido para otimização avançada de estratégias de trading**  
**Versão**: 1.0 | **Data**: Outubro 2025  
**Status**: ✅ Pronto para Uso
