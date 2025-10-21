"""
Script de Migração de Dados CSV → SQLite
Popula o banco de dados com histórico de trading existente
"""
import sys
from pathlib import Path

# Adicionar raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import csv
from datetime import datetime
import pandas as pd
from src.webapp.models.database import TradingDatabase, calculate_strategy_metrics


def migrate_csv_to_sqlite(
    csv_path: str = 'src/ml/outputs/capital_history-BTCUSDT.csv',
    db_path: str = 'data/trading_bot.db'
):
    """
    Migra dados do CSV para o banco SQLite
    
    Args:
        csv_path: Caminho do arquivo CSV
        db_path: Caminho do banco de dados
    """
    print("\n" + "="*70)
    print("🔄 INICIANDO MIGRAÇÃO DE DADOS CSV → SQLite")
    print("="*70)
    
    # 1. Ler CSV com módulo csv nativo (mais robusto)
    print(f"\n📂 Lendo CSV: {csv_path}")
    trades_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            trades_data.append(row)
    
    print(f"✅ {len(trades_data)} registros encontrados")
    
    # 2. Conectar ao banco
    print(f"\n💾 Conectando ao banco: {db_path}")
    db = TradingDatabase(db_path)
    
    # 4. Criar/Verificar estratégia
    print("\n🎯 Criando estratégia 'Agressiva TP 3%'")
    
    strategy_name = "Agressiva TP 3%"
    existing = db.get_strategy(name=strategy_name)
    
    if existing:
        print(f"⚠️  Estratégia já existe (ID={existing['id']}). Pulando criação.")
        strategy_id = existing['id']
    else:
        strategy_id = db.insert_strategy(
            name=strategy_name,
            description="Estratégia vencedora: TP 3%, SL 1.5%, holding 48 períodos (24h)",
            model_type="LSTM",
            take_profit=3.0,
            stop_loss=1.5,
            threshold=0.5,
            position_size=0.95,
            min_holding_periods=48,
            
            # Metadados do modelo
            lstm_layers=2,
            lstm_units=64,
            sequence_length=60,
            features_count=6,
            
            # Config JSON (features e targets)
            config_json='{"features": ["Open", "High", "Low", "Close", "SMA_20", "EMA_20"], "targets": ["Close", "High", "Low"]}'
        )
    
    # 5. Preparar trades para inserção
    print("\n📊 Preparando trades para inserção...")
    trades = []
    
    for row in trades_data:
        trade = {
            'data': datetime.strptime(row['Data'], '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S'),
            'operacao': row['Operacao'],
            'status': row['Status'],
            'previsao': float(row['Previsao']),
            'valor_atual': float(row['Valor Atual']),
            'preco': float(row['Preco']),
            'quantidade': float(row['Quantidade']),
            'custo': float(row['Custo']),
            'capital': float(row['Capital']),
        }
        trades.append(trade)
    
    # 6. Inserir trades em batch
    print(f"\n💾 Inserindo {len(trades)} trades no banco...")
    db.bulk_insert_trades(strategy_id, trades)
    
    # 7. Calcular e atualizar métricas da estratégia
    print("\n📈 Calculando métricas de performance...")
    df_trades = db.get_trades_by_strategy(strategy_id)
    metrics = calculate_strategy_metrics(df_trades)
    
    print(f"\n📊 Métricas calculadas:")
    for key, value in metrics.items():
        print(f"   • {key}: {value}")
    
    db.update_strategy_metrics(strategy_id, **metrics)
    
    # 8. Validar migração
    print("\n✅ Validando migração...")
    summary = db.get_trades_summary(strategy_id)
    print(f"\n📋 Resumo da migração:")
    print(f"   • Total de trades: {summary.get('total_trades', 0)}")
    print(f"   • Primeiro trade: {summary.get('first_trade', 'N/A')}")
    print(f"   • Último trade: {summary.get('last_trade', 'N/A')}")
    print(f"   • Capital mínimo: ${summary.get('min_capital', 0):,.2f}")
    print(f"   • Capital máximo: ${summary.get('max_capital', 0):,.2f}")
    
    # 9. Fechar conexão
    db.close()
    
    print("\n" + "="*70)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70 + "\n")


def show_database_stats(db_path: str = 'data/trading_bot.db'):
    """Exibe estatísticas do banco de dados"""
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("="*70)
    
    db = TradingDatabase(db_path)
    
    # Listar estratégias
    strategies = db.list_strategies(active_only=False)
    print(f"\n🎯 Total de estratégias: {len(strategies)}")
    
    for strat in strategies:
        print(f"\n┌─ Estratégia: {strat['name']} (ID={strat['id']})")
        print(f"│  ├─ Tipo: {strat['model_type']}")
        print(f"│  ├─ TP: {strat['take_profit']}% | SL: {strat['stop_loss']}%")
        print(f"│  ├─ Total Return: {strat.get('total_return', 'N/A')}%")
        print(f"│  ├─ Sharpe Ratio: {strat.get('sharpe_ratio', 'N/A')}")
        print(f"│  ├─ Max Drawdown: {strat.get('max_drawdown', 'N/A')}%")
        print(f"│  ├─ Win Rate: {strat.get('win_rate', 'N/A')}%")
        print(f"│  └─ Total Trades: {strat.get('total_trades', 'N/A')}")
    
    db.close()
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    # Executar migração
    migrate_csv_to_sqlite()
    
    # Exibir estatísticas
    show_database_stats()
