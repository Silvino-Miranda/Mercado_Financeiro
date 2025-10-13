# Optimization Module Documentation

## Overview
The optimization module provides sophisticated strategy parameter optimization using both genetic algorithms and exhaustive grid search.

## Architecture

```
src/optimization/
├── __init__.py          # Public API
├── __main__.py          # CLI interface
├── types.py             # Data structures
├── genetic.py           # Genetic algorithm
├── grid.py              # Grid search
└── utils.py             # Helper functions
```

## Components

### 1. Types (`types.py`)

**OptimizationObjective**
- `PROFIT_FACTOR`: Maximize profit factor
- `TOTAL_PNL`: Maximize total PnL
- `SHARPE`: Maximize Sharpe-like ratio
- `TRADES_PER_YEAR`: Maximize trading frequency
- `ROI`: Maximize return on investment
- `MULTI`: Multi-objective optimization (weighted combination)

**Individual**
- `config`: StrategyConfig instance
- `fitness`: Fitness score
- `metrics`: Performance metrics dict
- `generation`: Generation number

### 2. Genetic Algorithm (`genetic.py`)

#### GeneticOptimizer

**Algorithm Components:**
- **Selection**: Tournament selection (k=3)
- **Crossover**: Uniform crossover
- **Mutation**: Adaptive mutation rate (decays over generations)
- **Elitism**: Preserve top performers
- **Multi-objective**: Weighted fitness combining multiple metrics

**Key Methods:**
- `run()`: Execute optimization
- `save_history(filename)`: Export evolution history
- `get_top_n(n)`: Get best individuals
- `_create_random_config()`: Generate random configurations
- `_evaluate_fitness(config)`: Calculate fitness score
- `_selection(population)`: Tournament selection
- `_crossover(parent1, parent2)`: Breed new individual
- `_mutate(config)`: Mutate parameters
- `_evolve_generation(generation_num)`: Full evolution cycle

**Fitness Function:**
```python
# Multi-objective (default)
fitness = (
    0.35 * normalized_pf +      # Profit factor
    0.25 * normalized_wr +      # Win rate
    0.20 * normalized_trades +  # Trades/year
    0.20 * normalized_pnl       # Total PnL
)
```

**Parameters:**
- `csv_data_path`: OHLC data file
- `population_size`: Population size (default: 50)
- `generations`: Number of generations (default: 20)
- `objective`: OptimizationObjective (default: MULTI)
- `param_ranges`: Parameter search space
- `mutation_rate`: Initial mutation rate (default: 0.2)
- `crossover_rate`: Crossover probability (default: 0.7)
- `elitism_rate`: Elite preservation rate (default: 0.1)
- `min_trades`: Minimum trades required (default: 5)

### 3. Grid Search (`grid.py`)

#### GridSearchOptimizer

**Strategy:**
- Exhaustive search over parameter space
- Tests all parameter combinations
- Progress tracking with tqdm

**Key Methods:**
- `run(sort_by)`: Execute grid search
- `save_results(filename)`: Export to CSV
- `get_top_n(n, sort_by)`: Get best N configurations

**Parameters:**
- `csv_data_path`: OHLC data file
- `param_ranges`: Parameter ranges dictionary
- `min_trades`: Minimum trades required (default: 5)

### 4. Utilities (`utils.py`)

**Functions:**
- `save_optimization_results(individuals, filename)`: Export results
- `load_optimization_history(filename)`: Load previous results
- `save_best_config(config, filename)`: Save best configuration
- `calculate_diversity(population)`: Population diversity metric
- `print_population_summary(population)`: Display statistics

## CLI Usage

### Genetic Algorithm

```bash
# Basic usage
python -m src.optimization genetic \
    --csv data/BTCUSDT_daily.csv \
    --generations 20 \
    --objective multi

# Advanced usage
python -m src.optimization genetic \
    --csv data/BTCUSDT_daily.csv \
    --population 100 \
    --generations 50 \
    --objective profit_factor \
    --mutation_rate 0.3 \
    --crossover_rate 0.8 \
    --elitism_rate 0.15 \
    --ranges narrow \
    --save_best \
    --save_history \
    --show_top 10
```

**Options:**
- `--csv`: Path to OHLC CSV data (required)
- `--population`: Population size (default: 50)
- `--generations`: Number of generations (default: 20)
- `--objective`: Optimization objective (choices: profit_factor, total_pnl, sharpe, trades_per_year, roi, multi)
- `--ranges`: Parameter ranges (choices: default, narrow)
- `--mutation_rate`: Mutation rate (default: 0.2)
- `--crossover_rate`: Crossover rate (default: 0.7)
- `--elitism_rate`: Elitism rate (default: 0.1)
- `--min_trades`: Minimum trades required (default: 5)
- `--save_best`: Save best configuration to config/
- `--save_history`: Save evolution history
- `--output`: Custom output filename for best config
- `--history_output`: Custom output filename for history
- `--show_top`: Show top N individuals

### Grid Search

```bash
# Basic usage
python -m src.optimization grid \
    --csv data/BTCUSDT_daily.csv \
    --ranges narrow

# Advanced usage
python -m src.optimization grid \
    --csv data/BTCUSDT_daily.csv \
    --ranges default \
    --sort_by sharpe_like \
    --min_trades 10 \
    --save_all \
    --save_best \
    --show_top 20
```

**Options:**
- `--csv`: Path to OHLC CSV data (required)
- `--ranges`: Parameter ranges (choices: default, narrow)
- `--min_trades`: Minimum trades required (default: 5)
- `--sort_by`: Metric to sort by (default: profit_factor)
- `--save_all`: Save all results to CSV
- `--save_best`: Save best configuration
- `--output`: Custom output filename for all results
- `--best_output`: Custom output filename for best config
- `--show_top`: Show top N configurations

## Programmatic Usage

### Genetic Algorithm Example

```python
from src.optimization import GeneticOptimizer, OptimizationObjective
from src.config import create_narrow_ranges

# Configure optimizer
optimizer = GeneticOptimizer(
    csv_data_path="data/BTCUSDT_daily.csv",
    population_size=50,
    generations=20,
    objective=OptimizationObjective.MULTI,
    param_ranges=create_narrow_ranges(),
    mutation_rate=0.2,
    crossover_rate=0.7,
    elitism_rate=0.1,
    min_trades=5
)

# Run optimization
best_config = optimizer.run()

# Get top performers
top_10 = optimizer.get_top_n(10)

# Save results
optimizer.save_history("ga_evolution.csv")
```

### Grid Search Example

```python
from src.optimization import GridSearchOptimizer
from src.config import create_narrow_ranges

# Configure optimizer
optimizer = GridSearchOptimizer(
    csv_data_path="data/BTCUSDT_daily.csv",
    param_ranges=create_narrow_ranges(),
    min_trades=5
)

# Run optimization
best_config = optimizer.run(sort_by="profit_factor")

# Get top performers
top_20 = optimizer.get_top_n(20, sort_by="sharpe_like")

# Save results
optimizer.save_results("grid_search_results.csv")
```

## Parameter Ranges

### Default Ranges
Wide search space for exploration:
```python
{
    'variant': ['base', 'rsi'],
    'ma_len': range(50, 201, 10),
    'dist_below_ma_pct': [0.01, 0.02, 0.03, 0.05],
    'tp_pct': [0.05, 0.08, 0.10, 0.13, 0.15],
    'sl_pct': [0.03, 0.05, 0.08, 0.12, 0.15],
    'atr_mult': [1.0, 1.5, 2.0],
    'time_stop': [20, 30, 40, 50],
    'be_trigger_pct': [0.03, 0.05, 0.08],
    'allow_breakeven': [True, False]
}
```

### Narrow Ranges
Focused search for refinement:
```python
{
    'variant': ['base'],
    'ma_len': range(100, 201, 25),
    'dist_below_ma_pct': [0.02, 0.03],
    'tp_pct': [0.08, 0.10, 0.13],
    'sl_pct': [0.05, 0.08, 0.12],
    'atr_mult': [1.0, 1.5],
    'time_stop': [30, 40],
    'be_trigger_pct': [0.05, 0.08],
    'allow_breakeven': [True, False]
}
```

## Performance Tips

### Genetic Algorithm
1. **Population Size**: Larger = better exploration, slower
   - Small problems: 30-50
   - Large problems: 100-200

2. **Generations**: More = better convergence
   - Quick test: 10-20
   - Production: 50-100

3. **Mutation Rate**: Higher = more exploration
   - Start: 0.2-0.3
   - Adaptive decay helps convergence

4. **Elitism**: Preserve best solutions
   - Recommended: 0.1-0.2 (10-20%)

5. **Parallel Processing**: Not yet implemented
   - Future: multiprocessing for fitness evaluation

### Grid Search
1. **Parameter Ranges**: Reduce combinations
   - Use narrow ranges after GA refinement
   - Focus on promising areas

2. **Minimum Trades**: Filter invalid configs
   - Typical: 5-10 trades

3. **Sort Metric**: Choose optimization goal
   - profit_factor: Risk-adjusted returns
   - sharpe_like: Volatility-adjusted
   - total_pnl: Absolute returns

## Output Files

### Genetic Algorithm History
CSV with columns:
- generation, variant, ma_len, dist_below_ma_pct, tp_pct, sl_pct
- atr_mult, time_stop, be_trigger_pct, allow_breakeven
- fitness, profit_factor, win_rate, trades_per_year, total_pnl

### Grid Search Results
CSV with all tested configurations and metrics

### Best Configuration
Standard params.csv format for direct use with backtest module

## Algorithm Details

### Adaptive Mutation Rate
```python
mutation_rate = initial_rate * (1 - generation / max_generations) ** 2
```
- High mutation early: Exploration
- Low mutation late: Exploitation

### Tournament Selection
```python
# Select k=3 random individuals
# Return the one with best fitness
```
- Balances selection pressure
- Maintains diversity

### Uniform Crossover
```python
# For each parameter:
#   50% chance from parent1
#   50% chance from parent2
```
- Good parameter mixing
- Preserves diversity

### Multi-Objective Fitness
```python
fitness = (
    0.35 * normalize(profit_factor) +
    0.25 * normalize(win_rate) +
    0.20 * normalize(trades_per_year) +
    0.20 * normalize(total_pnl)
)
```
- Weights tunable per strategy
- Normalization prevents dominance
- Penalty for insufficient trades

## Troubleshooting

### No Valid Configurations
**Problem**: All individuals have -999999 fitness
**Solutions**:
- Reduce `min_trades` threshold
- Expand parameter ranges
- Check data quality/length
- Verify strategy logic

### Slow Convergence
**Problem**: Fitness not improving
**Solutions**:
- Increase population size
- Increase mutation rate
- Expand parameter ranges
- Try different objective

### Premature Convergence
**Problem**: Population becomes identical too early
**Solutions**:
- Increase mutation rate
- Reduce elitism rate
- Increase population diversity penalty
- Use wider parameter ranges

## Future Enhancements

1. **Parallel Processing**: Multiprocessing for fitness evaluation
2. **Island Model**: Multiple populations with migration
3. **NSGA-II**: True multi-objective optimization
4. **Hyperparameter Tuning**: Auto-tune GA parameters
5. **Walk-Forward Optimization**: Time-series cross-validation
6. **Robustness Testing**: Monte Carlo parameter sensitivity
7. **Constraint Handling**: Custom constraints (e.g., max drawdown)
8. **Resume Capability**: Continue interrupted optimizations

## References

- DEAP: Distributed Evolutionary Algorithms in Python
- Holland, J. H. (1992). Genetic Algorithms
- Deb, K. et al. (2002). NSGA-II Multi-Objective Optimization
- Tharp, V. (1998). Trade Your Way to Financial Freedom
