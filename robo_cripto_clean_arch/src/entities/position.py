# entities/position.py
from dataclasses import dataclass

@dataclass
class Position:
    entry_date: str
    exit_date: str
    ativo: str
    position: float
    entry_price: float
    exit_price: float