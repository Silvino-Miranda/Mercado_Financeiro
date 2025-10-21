"""
Database Schema and ORM for Trading Bot
Modelo de dados SQLite para histórico de trading e estratégias
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd


class TradingDatabase:
    """Gerenciador do banco de dados de trading"""
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        """
        Inicializa conexão com banco SQLite
        
        Args:
            db_path: Caminho relativo ou absoluto do arquivo .db
        """
        # Garantir que o diretório existe
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_file)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Estabelece conexão com o banco"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permitir acesso por nome de coluna
        print(f"✅ Conectado ao banco: {self.db_path}")
    
    def _create_tables(self):
        """Cria tabelas se não existirem"""
        cursor = self.conn.cursor()
        
        # TABELA 1: STRATEGIES (Master)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                model_type TEXT NOT NULL,
                take_profit REAL NOT NULL,
                stop_loss REAL NOT NULL,
                threshold REAL,
                position_size REAL DEFAULT 0.95,
                min_holding_periods INTEGER DEFAULT 48,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                
                -- Metadados do modelo LSTM
                lstm_layers INTEGER,
                lstm_units INTEGER,
                sequence_length INTEGER,
                features_count INTEGER,
                
                -- Métricas de Performance
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                total_trades INTEGER,
                
                -- Configuração JSON (features, targets, etc)
                config_json TEXT
            )
        """)
        
        # TABELA 2: TRADING_HISTORY (Detalhe)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id INTEGER NOT NULL,
                
                -- Dados da operação
                data TIMESTAMP NOT NULL,
                operacao TEXT NOT NULL CHECK(operacao IN ('Compra', 'Venda')),
                status TEXT NOT NULL CHECK(status IN ('Entrada', 'Saida')),
                
                -- Valores
                previsao REAL NOT NULL,
                valor_atual REAL NOT NULL,
                preco REAL NOT NULL,
                quantidade REAL NOT NULL,
                custo REAL DEFAULT 0.0,
                capital REAL NOT NULL,
                
                -- Métricas derivadas (calculadas)
                retorno_percentual REAL,
                retorno_absoluto REAL,
                drawdown REAL,
                erro_previsao REAL,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
            )
        """)
        
        # ÍNDICES para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_history_strategy 
            ON trading_history(strategy_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_history_data 
            ON trading_history(data)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trading_history_operacao 
            ON trading_history(operacao, status)
        """)
        
        self.conn.commit()
        print("✅ Tabelas criadas/verificadas com sucesso")
    
    # ==================== CRUD - STRATEGIES ====================
    
    def insert_strategy(self, **kwargs) -> int:
        """
        Insere nova estratégia
        
        Args:
            name: Nome único da estratégia
            description: Descrição textual
            model_type: Tipo do modelo (LSTM, GRU, etc)
            take_profit: % de lucro para saída
            stop_loss: % de perda para stop
            **kwargs: Outros campos opcionais
            
        Returns:
            ID da estratégia inserida
        """
        required = ['name', 'model_type', 'take_profit', 'stop_loss']
        for field in required:
            if field not in kwargs:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        kwargs['updated_at'] = datetime.now().isoformat()
        
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO strategies ({columns}) VALUES ({placeholders})",
            list(kwargs.values())
        )
        self.conn.commit()
        
        strategy_id = cursor.lastrowid
        print(f"✅ Estratégia '{kwargs['name']}' criada com ID={strategy_id}")
        return strategy_id
    
    def get_strategy(self, strategy_id: int = None, name: str = None) -> Optional[Dict]:
        """Busca estratégia por ID ou nome"""
        cursor = self.conn.cursor()
        
        if strategy_id:
            cursor.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
        elif name:
            cursor.execute("SELECT * FROM strategies WHERE name = ?", (name,))
        else:
            raise ValueError("Informe strategy_id ou name")
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_strategies(self, active_only: bool = True) -> List[Dict]:
        """Lista todas as estratégias"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM strategies"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_strategy_metrics(self, strategy_id: int, **metrics):
        """Atualiza métricas de performance da estratégia"""
        metrics['updated_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in metrics.keys()])
        values = list(metrics.values()) + [strategy_id]
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE strategies SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        print(f"✅ Métricas da estratégia ID={strategy_id} atualizadas")
    
    # ==================== CRUD - TRADING HISTORY ====================
    
    def insert_trade(self, strategy_id: int, **kwargs) -> int:
        """
        Insere operação de trading
        
        Args:
            strategy_id: ID da estratégia
            data: Data da operação (string ou datetime)
            operacao: 'Compra' ou 'Venda'
            status: 'Entrada' ou 'Saida'
            previsao: Valor previsto pelo modelo
            valor_atual: Valor real do ativo
            preco: Preço de execução
            quantidade: Quantidade negociada
            capital: Capital total após operação
            **kwargs: Campos opcionais (retorno_percentual, etc)
            
        Returns:
            ID do trade inserido
        """
        kwargs['strategy_id'] = strategy_id
        
        required = ['data', 'operacao', 'status', 'previsao', 
                   'valor_atual', 'preco', 'quantidade', 'capital']
        for field in required:
            if field not in kwargs:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Calcular erro de previsão se não fornecido
        if 'erro_previsao' not in kwargs:
            kwargs['erro_previsao'] = kwargs['previsao'] - kwargs['valor_atual']
        
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO trading_history ({columns}) VALUES ({placeholders})",
            list(kwargs.values())
        )
        self.conn.commit()
        
        return cursor.lastrowid
    
    def bulk_insert_trades(self, strategy_id: int, trades: List[Dict]):
        """
        Insere múltiplos trades de uma vez (mais eficiente)
        
        Args:
            strategy_id: ID da estratégia
            trades: Lista de dicts com dados dos trades
        """
        if not trades:
            return
        
        # Adicionar strategy_id a todos
        for trade in trades:
            trade['strategy_id'] = strategy_id
            if 'erro_previsao' not in trade:
                trade['erro_previsao'] = trade['previsao'] - trade['valor_atual']
        
        # Pegar colunas do primeiro trade (assumir todos têm mesmas colunas)
        columns = list(trades[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        
        cursor = self.conn.cursor()
        cursor.executemany(
            f"INSERT INTO trading_history ({', '.join(columns)}) VALUES ({placeholders})",
            [tuple(trade[col] for col in columns) for trade in trades]
        )
        self.conn.commit()
        print(f"✅ {len(trades)} trades inseridos para estratégia ID={strategy_id}")
    
    def get_trades_by_strategy(self, strategy_id: int) -> pd.DataFrame:
        """Retorna todos os trades de uma estratégia como DataFrame"""
        query = """
            SELECT * FROM trading_history 
            WHERE strategy_id = ? 
            ORDER BY data ASC
        """
        return pd.read_sql_query(query, self.conn, params=(strategy_id,))
    
    def get_trades_summary(self, strategy_id: int) -> Dict[str, Any]:
        """Retorna resumo estatístico dos trades"""
        cursor = self.conn.cursor()
        
        # SQLite não tem STDEV nativo, calcular manualmente ou usar pandas
        query = """
            SELECT 
                COUNT(*) as total_trades,
                MIN(data) as first_trade,
                MAX(data) as last_trade,
                MIN(capital) as min_capital,
                MAX(capital) as max_capital,
                AVG(erro_previsao) as avg_prediction_error
            FROM trading_history
            WHERE strategy_id = ?
        """
        
        cursor.execute(query, (strategy_id,))
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    # ==================== UTILITÁRIOS ====================
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Executa query SQL customizada"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def to_dataframe(self, table_name: str) -> pd.DataFrame:
        """Converte tabela inteira para DataFrame"""
        return pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
    
    def close(self):
        """Fecha conexão com o banco"""
        if self.conn:
            self.conn.close()
            print("❌ Conexão com banco encerrada")
    
    def __enter__(self):
        """Context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - fecha conexão ao sair"""
        self.close()


# ==================== FUNÇÃO AUXILIAR ====================

def calculate_strategy_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula métricas de performance a partir do histórico de trades
    
    Args:
        df: DataFrame com colunas: data, capital, operacao, preco
        
    Returns:
        Dict com métricas calculadas
    """
    if df.empty:
        return {}
    
    # Capital inicial e final
    initial_capital = df['capital'].iloc[0]
    final_capital = df['capital'].iloc[-1]
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    
    # Drawdown máximo
    df['peak'] = df['capital'].cummax()
    df['drawdown'] = ((df['capital'] - df['peak']) / df['peak']) * 100
    max_drawdown = df['drawdown'].min()
    
    # Win Rate (trades lucrativos)
    df['return_pct'] = df['capital'].pct_change() * 100
    winning_trades = len(df[df['return_pct'] > 0])
    total_trades = len(df[df['operacao'] == 'Venda'])  # Contar apenas saídas
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Sharpe Ratio (simplificado - assumir risk-free rate = 0)
    returns = df['return_pct'].dropna()
    sharpe_ratio = (returns.mean() / returns.std()) if returns.std() > 0 else 0
    
    return {
        'total_return': round(total_return, 2),
        'max_drawdown': round(max_drawdown, 2),
        'win_rate': round(win_rate, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'total_trades': total_trades
    }
