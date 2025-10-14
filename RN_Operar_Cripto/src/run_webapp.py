"""
Run WebApp Dashboard
Script para executar o dashboard da raiz do projeto
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importar e executar o app
from src.webapp.app import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR DASH")
    print("="*70)
    print("📊 Dashboard disponível em: http://127.0.0.1:8050/")
    print("="*70 + "\n")
    
    app.run(debug=True)
