#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Configuration Manager
--------------------------------
Gerencia parâmetros de estratégias de trading com suporte a:
- Carregamento/salvamento de CSV
- Validação de parâmetros
- Definição de ranges para otimização
- Múltiplos conjuntos de parâmetros (portfolios)

Usage:
    from config import StrategyConfig, load_params_from_csv
    
    # Carregar do CSV
    config = load_params_from_csv('params.csv')
    
    # Usar parâmetros
    params = config.to_params()
    
    # Criar config programaticamente
    config = StrategyConfig(
        variant='base',
        ma_len=220,
        dist_below_ma_pct=0.05,
        ...
    )
"""

import csv
import json
from dataclasses import dataclass, asdict, fields
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd


@dataclass
class StrategyConfig:
    """Configuração de parâmetros de estratégia"""
    
    # Strategy selection
    variant: str = "base"  # base | rsi | reclaim
    
    # Technical indicators
    ma_len: int = 200
    rsi_period: int = 14
    slope_lookback: int = 5
    
    # Entry conditions
    dist_below_ma_pct: float = 0.05  # 5%
    rsi_cross_level: float = 30.0
    
    # Exit management
    tp_pct: float = 0.10  # 10% take profit
    sl_pct: float = 0.08  # 8% stop loss
    atr_mult: float = 2.0
    time_stop: int = 30  # bars
    
    # Risk management
    be_trigger_pct: float = 0.06
    allow_breakeven: bool = True
    
    # Trading costs
    fees_bps: float = 10.0  # 0.10% per side
    slip_bps: float = 5.0   # 0.05% per side
    
    # Position sizing
    capital_per_trade: float = 1000.0
    
    # Metadata
    name: str = "default"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_params(self):
        """Convert to Params dataclass for backtest"""
        from mr_backtest import Params
        return Params(
            variant=self.variant,
            ma_len=self.ma_len,
            dist_below_ma_pct=self.dist_below_ma_pct,
            slope_lookback=self.slope_lookback,
            rsi_period=self.rsi_period,
            rsi_cross_level=self.rsi_cross_level,
            tp_pct=self.tp_pct,
            sl_pct=self.sl_pct,
            atr_mult=self.atr_mult,
            time_stop=self.time_stop,
            be_trigger_pct=self.be_trigger_pct,
            fees_bps=self.fees_bps,
            slip_bps=self.slip_bps,
            capital_per_trade=self.capital_per_trade,
            allow_breakeven=self.allow_breakeven
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyConfig':
        """Create from dictionary"""
        # Filter only valid fields
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate parameter values"""
        errors = []
        
        # Variant check
        if self.variant not in ['base', 'rsi', 'reclaim']:
            errors.append(f"Invalid variant: {self.variant}")
        
        # Positive integers
        if self.ma_len <= 0:
            errors.append(f"ma_len must be > 0: {self.ma_len}")
        if self.time_stop <= 0:
            errors.append(f"time_stop must be > 0: {self.time_stop}")
        
        # Percentages (0-1 range)
        if not 0 < self.dist_below_ma_pct < 1:
            errors.append(f"dist_below_ma_pct must be in (0, 1): {self.dist_below_ma_pct}")
        if not 0 < self.tp_pct < 1:
            errors.append(f"tp_pct must be in (0, 1): {self.tp_pct}")
        if not 0 < self.sl_pct < 1:
            errors.append(f"sl_pct must be in (0, 1): {self.sl_pct}")
        
        # Positive values
        if self.atr_mult <= 0:
            errors.append(f"atr_mult must be > 0: {self.atr_mult}")
        if self.capital_per_trade <= 0:
            errors.append(f"capital_per_trade must be > 0: {self.capital_per_trade}")
        
        return len(errors) == 0, errors


@dataclass
class ParamRange:
    """Define o range de um parâmetro para otimização"""
    name: str
    min_val: float
    max_val: float
    step: Optional[float] = None
    values: Optional[List[Any]] = None  # Para valores discretos
    param_type: str = "float"  # float | int | str | bool
    
    def get_values(self) -> List[Any]:
        """Retorna lista de valores possíveis"""
        if self.values is not None:
            return self.values
        
        if self.param_type == "int":
            if self.step:
                return list(range(int(self.min_val), int(self.max_val) + 1, int(self.step)))
            return list(range(int(self.min_val), int(self.max_val) + 1))
        
        if self.param_type == "float":
            if self.step:
                import numpy as np
                return np.arange(self.min_val, self.max_val + self.step, self.step).tolist()
            return [self.min_val, self.max_val]
        
        return []


class ConfigManager:
    """Gerencia múltiplas configurações e ranges de otimização"""
    
    def __init__(self):
        self.configs: List[StrategyConfig] = []
        self.param_ranges: Dict[str, ParamRange] = {}
    
    def add_config(self, config: StrategyConfig):
        """Adiciona configuração"""
        self.configs.append(config)
    
    def add_param_range(self, param_range: ParamRange):
        """Define range para um parâmetro"""
        self.param_ranges[param_range.name] = param_range
    
    def load_from_csv(self, csv_path: str):
        """Carrega configurações de CSV"""
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            data = row.to_dict()
            
            # Convert boolean strings
            for key, val in data.items():
                if isinstance(val, str):
                    if val.lower() in ['true', 'false']:
                        data[key] = val.lower() == 'true'
            
            config = StrategyConfig.from_dict(data)
            self.add_config(config)
    
    def save_to_csv(self, csv_path: str):
        """Salva configurações para CSV"""
        if not self.configs:
            raise ValueError("No configurations to save")
        
        data = [config.to_dict() for config in self.configs]
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
    
    def get_best_config(self, results: pd.DataFrame, metric: str = 'profit_factor') -> StrategyConfig:
        """Retorna melhor configuração baseada em métrica"""
        if results.empty:
            raise ValueError("No results provided")
        
        best_idx = results[metric].idxmax()
        best_row = results.loc[best_idx]
        
        return StrategyConfig.from_dict(best_row.to_dict())


# Helper functions

def load_params_from_csv(csv_path: str) -> StrategyConfig:
    """Carrega parâmetros de CSV (primeira linha)"""
    manager = ConfigManager()
    manager.load_from_csv(csv_path)
    
    if not manager.configs:
        raise ValueError(f"No configurations found in {csv_path}")
    
    return manager.configs[0]


def load_all_params_from_csv(csv_path: str) -> List[StrategyConfig]:
    """Carrega todos os conjuntos de parâmetros de CSV"""
    manager = ConfigManager()
    manager.load_from_csv(csv_path)
    return manager.configs


def save_params_to_csv(config: StrategyConfig, csv_path: str):
    """Salva parâmetros para CSV"""
    df = pd.DataFrame([config.to_dict()])
    df.to_csv(csv_path, index=False)


def create_default_ranges() -> Dict[str, ParamRange]:
    """Cria ranges padrão para otimização"""
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=2,
            values=['base', 'rsi', 'reclaim'],
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=150, max_val=250,
            step=10,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.02, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.05, max_val=0.20,
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.04, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.0, max_val=3.0,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=10, max_val=60,
            step=5,
            param_type='int'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=1,
            values=[True, False],
            param_type='bool'
        )
    }


def create_narrow_ranges() -> Dict[str, ParamRange]:
    """Cria ranges estreitos baseados nos melhores resultados do grid search"""
    return {
        'variant': ParamRange(
            name='variant',
            min_val=0, max_val=0,
            values=['base'],  # Apenas BASE
            param_type='str'
        ),
        'ma_len': ParamRange(
            name='ma_len',
            min_val=200, max_val=230,
            step=5,
            param_type='int'
        ),
        'dist_below_ma_pct': ParamRange(
            name='dist_below_ma_pct',
            min_val=0.03, max_val=0.10,
            step=0.01,
            param_type='float'
        ),
        'tp_pct': ParamRange(
            name='tp_pct',
            min_val=0.08, max_val=0.15,
            step=0.01,
            param_type='float'
        ),
        'sl_pct': ParamRange(
            name='sl_pct',
            min_val=0.06, max_val=0.12,
            step=0.01,
            param_type='float'
        ),
        'atr_mult': ParamRange(
            name='atr_mult',
            min_val=1.0, max_val=2.5,
            step=0.25,
            param_type='float'
        ),
        'time_stop': ParamRange(
            name='time_stop',
            min_val=15, max_val=45,
            step=5,
            param_type='int'
        ),
        'allow_breakeven': ParamRange(
            name='allow_breakeven',
            min_val=0, max_val=0,
            values=[False],  # Sempre False (melhor resultado)
            param_type='bool'
        )
    }


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("Config Manager Demo")
    print("=" * 60)
    
    # Create config
    config = StrategyConfig(
        variant='base',
        ma_len=220,
        dist_below_ma_pct=0.05,
        tp_pct=0.10,
        sl_pct=0.10,
        allow_breakeven=False,
        name="champion",
        description="Best config from grid search"
    )
    
    print("\n1. Configuration created:")
    print(json.dumps(config.to_dict(), indent=2))
    
    # Validate
    is_valid, errors = config.validate()
    print(f"\n2. Validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    if errors:
        for err in errors:
            print(f"   - {err}")
    
    # Save to CSV
    save_params_to_csv(config, "test_params.csv")
    print("\n3. Saved to: test_params.csv")
    
    # Load back
    loaded = load_params_from_csv("test_params.csv")
    print("\n4. Loaded from CSV:")
    print(f"   variant={loaded.variant}, ma_len={loaded.ma_len}, tp_pct={loaded.tp_pct}")
    
    # Show ranges
    print("\n5. Default optimization ranges:")
    ranges = create_default_ranges()
    for name, r in list(ranges.items())[:3]:
        vals = r.get_values()
        print(f"   {name}: {len(vals)} values from {r.min_val} to {r.max_val}")
    
    print("\n✅ Config module working correctly!")
