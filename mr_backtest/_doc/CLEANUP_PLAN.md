# Cleanup & Migration Plan

## 📋 Files to Handle

### ✅ Completed Modules (Keep as-is)
- `src/download/` - ✅ Modular
- `src/backtest/` - ✅ Modular
- `src/config/` - ✅ Modular
- `src/optimization/` - ✅ Modular
- `src/analysis/` - ✅ Modular

### 🗑️ Legacy Files to Remove (Replaced by modules)
1. `src/config.py` → Replaced by `src/config/`
2. `src/mr_backtest.py` → Replaced by `src/backtest/`
3. `src/download_btc_csv.py` → Replaced by `src/download/`
4. `src/genetic_optimizer.py` → Replaced by `src/optimization/`
5. `src/analyze_checkpoint.py` → Replaced by `src/analysis/`
6. `src/analyze_results.py` → Replaced by `src/analysis/`

### 🔧 Scripts to Update (Use new imports)
1. `src/grid_search_1h.py` - Grid search script
2. `src/quick_test_1h.py` - Quick test script
3. `src/optimize_daily_trader.py` - Optimization script
4. `src/optimize_roi.py` - ROI optimization script

### 📁 Other Directories
- `src/utils/` - Check if still needed
- `src/__init__.py` - Update to export new modules

---

## 🎯 Action Plan

### Phase 1: Backup Legacy Files ✅
Move old files to `_archive/` for safety before deletion

### Phase 2: Update Scripts 🔧
Update imports in:
- grid_search_1h.py
- quick_test_1h.py
- optimize_daily_trader.py
- optimize_roi.py

### Phase 3: Update Root __init__.py 📦
Expose new modular structure

### Phase 4: Remove Legacy Files 🗑️
Delete old monolithic files

### Phase 5: Consolidate Documentation 📚
Organize all docs in docs/

### Phase 6: End-to-End Testing ✅
Validate complete workflow

---

## 📝 Migration Guide

### Old Import → New Import

**Config:**
```python
# Old
from config import StrategyConfig, load_params_from_csv

# New
from src.config import StrategyConfig, load_params_from_csv
```

**Backtest:**
```python
# Old
from mr_backtest import BacktestEngine, Params

# New
from src.backtest import BacktestEngine, Params
```

**Optimization:**
```python
# Old
from genetic_optimizer import GeneticOptimizer, Individual

# New
from src.optimization import GeneticOptimizer, Individual
```

**Analysis:**
```python
# Old
from analyze_results import analyze_results

# New
from src.analysis import ResultsAnalyzer, load_grid_results
```

**Download:**
```python
# Old
from download_btc_csv import download_data

# New
from src.download import DataDownloader
```

---

## ⚠️ Breaking Changes: NONE

All functionality is preserved. Old code will work with updated imports.

---

## 🚀 Next Steps

1. Create _archive/ directory
2. Move legacy files to archive
3. Update scripts with new imports
4. Test each script
5. Remove archived files after validation
6. Create final migration guide
