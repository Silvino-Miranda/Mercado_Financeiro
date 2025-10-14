"""
Compare All Trading Strategies
Wrapper script para executar comparação de estratégias
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importa e executa o main do compare_strategies
from src.ml.compare_strategies import main

if __name__ == "__main__":
    main()
