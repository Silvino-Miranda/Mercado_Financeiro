#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis Types
--------------
Data structures for analysis module.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..optimization.types import Individual


@dataclass
class CheckpointData:
    """Checkpoint data structure."""
    generation: int
    total_generations: int
    population: List['Individual']
    best_individual: Optional['Individual'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Analysis result structure."""
    total_configs: int
    valid_configs: int
    invalid_configs: int
    best_config: Optional[Dict[str, Any]] = None
    top_configs: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, float] = field(default_factory=dict)
    parameter_sensitivity: Dict[str, Dict[str, float]] = field(default_factory=dict)
    variant_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class ComparisonResult:
    """Comparison result structure."""
    configs: List[Dict[str, Any]] = field(default_factory=list)
    winner: Optional[Dict[str, Any]] = None
    comparison_matrix: Dict[str, List[float]] = field(default_factory=dict)
    rankings: Dict[str, int] = field(default_factory=dict)
