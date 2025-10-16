# 🗄️ Sistema de Banco de Dados SQLite - Trading Bot

## 📋 Visão Geral

O sistema agora utiliza **SQLite** como fonte de dados dinâmica, substituindo a dependência exclusiva de arquivos CSV. Isso permite:

- ✅ Gerenciamento de múltiplas estratégias
- ✅ Consultas SQL eficientes
- ✅ Relacionamento Master/Detail (Estratégias ↔ Histórico)
- ✅ Cálculo automático de métricas
- ✅ Fallback para CSV se banco não disponível

---

## 📂 Estrutura do Banco de Dados

### Localização
```
data/trading_bot.db
```

### Tabelas

#### 1. `strategies` (Master)
Armazena informações das estratégias de trading.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER PK | ID único da estratégia |
| `name` | TEXT UNIQUE | Nome da estratégia |
| `description` | TEXT | Descrição detalhada |
| `model_type` | TEXT | Tipo do modelo (LSTM, GRU, etc) |
| `take_profit` | REAL | % de lucro para saída |
| `stop_loss` | REAL | % de perda para stop |
| `threshold` | REAL | Threshold de decisão |
| `position_size` | REAL | % do capital por trade (padrão: 0.95) |
| `min_holding_periods` | INTEGER | Períodos mínimos de holding |
| `lstm_layers` | INTEGER | Número de camadas LSTM |
| `lstm_units` | INTEGER | Unidades por camada |
| `sequence_length` | INTEGER | Tamanho da sequência |
| `features_count` | INTEGER | Número de features |
| `total_return` | REAL | Retorno total (%) |
| `sharpe_ratio` | REAL | Sharpe Ratio |
| `max_drawdown` | REAL | Máximo drawdown (%) |
| `win_rate` | REAL | Taxa de acerto (%) |
| `total_trades` | INTEGER | Total de operações |
| `config_json` | TEXT | Configuração em JSON |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Data de atualização |
| `is_active` | BOOLEAN | Estratégia ativa? |

#### 2. `trading_history` (Detail)
Armazena o histórico de operações de cada estratégia.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER PK | ID único do trade |
| `strategy_id` | INTEGER FK | ID da estratégia |
| `data` | TIMESTAMP | Data/hora da operação |
| `operacao` | TEXT | 'Compra' ou 'Venda' |
| `status` | TEXT | 'Entrada' ou 'Saida' |
| `previsao` | REAL | Valor previsto pelo modelo |
| `valor_atual` | REAL | Valor real do ativo |
| `preco` | REAL | Preço de execução |
| `quantidade` | REAL | Quantidade negociada |
| `custo` | REAL | Custo da operação |
| `capital` | REAL | Capital total após operação |
| `retorno_percentual` | REAL | Retorno % do trade |
| `retorno_absoluto` | REAL | Retorno absoluto ($) |
| `drawdown` | REAL | Drawdown no momento |
| `erro_previsao` | REAL | Erro de previsão (previsto - real) |
| `created_at` | TIMESTAMP | Data de inserção |

---

## 🚀 Como Usar

### 1. Migração Inicial (CSV → SQLite)

```bash
# Executar script de migração
uv run src/webapp/migrate_data.py
```

Este script:
- ✅ Cria o banco `data/trading_bot.db`
- ✅ Cria as tabelas `strategies` e `trading_history`
- ✅ Migra dados do CSV para o banco
- ✅ Calcula métricas da estratégia
- ✅ Exibe estatísticas

### 2. Usando o Banco no Código

```python
from src.webapp.models.database import TradingDatabase

# Conectar ao banco
db = TradingDatabase("data/trading_bot.db")

# Listar estratégias
strategies = db.list_strategies()
for s in strategies:
    print(f"{s['name']}: {s['total_return']}% retorno")

# Buscar trades de uma estratégia
df = db.get_trades_by_strategy(strategy_id=1)
print(df.head())

# Fechar conexão
db.close()
```

### 3. Dashboard Web (Automático)

O dashboard agora carrega automaticamente do banco SQLite:

```bash
uv run src/webapp/app.py
```

Acesse: [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

---

## 📊 API do Database Model

### Criar Estratégia

```python
strategy_id = db.insert_strategy(
    name="Conservadora TP 2%",
    description="Estratégia com menor risco",
    model_type="LSTM",
    take_profit=2.0,
    stop_loss=1.0,
    threshold=0.7,
    position_size=0.80,
    lstm_layers=2,
    lstm_units=32
)
```

### Inserir Trades (Bulk)

```python
trades = [
    {
        'data': '2024-11-06 12:00:00',
        'operacao': 'Compra',
        'status': 'Entrada',
        'previsao': 69000.0,
        'valor_atual': 68500.0,
        'preco': 68500.0,
        'quantidade': 1.5,
        'custo': 0.0,
        'capital': 100000.0
    },
    # ... mais trades
]

db.bulk_insert_trades(strategy_id=1, trades=trades)
```

### Atualizar Métricas

```python
from src.webapp.models.database import calculate_strategy_metrics

df = db.get_trades_by_strategy(strategy_id=1)
metrics = calculate_strategy_metrics(df)

db.update_strategy_metrics(strategy_id=1, **metrics)
```

### Consultas SQL Customizadas

```python
# Trades lucrativos
results = db.execute_query("""
    SELECT data, capital, 
           (capital - LAG(capital) OVER (ORDER BY data)) as lucro
    FROM trading_history
    WHERE strategy_id = ? AND operacao = 'Venda'
""", (1,))

for row in results:
    print(row)
```

---

## 🔍 Verificar Banco de Dados

### Usando SQLite CLI

```bash
# Abrir banco
sqlite3 data/trading_bot.db

# Listar tabelas
.tables

# Ver schema
.schema strategies
.schema trading_history

# Consultar dados
SELECT name, total_return, sharpe_ratio FROM strategies;
SELECT COUNT(*) FROM trading_history WHERE strategy_id = 1;

# Sair
.quit
```

### Usando Python (Interactive)

```python
from src.webapp.models.database import TradingDatabase

db = TradingDatabase("data/trading_bot.db")

# Estatísticas
summary = db.get_trades_summary(strategy_id=1)
print(summary)

# DataFrame completo
df = db.to_dataframe('strategies')
print(df)
```

---

## 🛠️ Configuração no Dashboard

### Alterar Estratégia Exibida

Em `src/webapp/app.py`:

```python
# Configurações
DB_PATH = 'data/trading_bot.db'
STRATEGY_ID = 1  # Mudar para outra estratégia

controller = DashboardController(
    db_path=DB_PATH,
    strategy_id=STRATEGY_ID
)
```

### Fallback para CSV

Se o banco não estiver disponível, o sistema automaticamente usa o CSV:

```python
controller = DashboardController(
    csv_path='src/ml/outputs/capital_history-BTCUSDT.csv',
    db_path='data/trading_bot.db',  # Tentará este primeiro
    strategy_id=1
)
```

---

## 📈 Próximos Passos (Opcional)

1. **Interface de Gestão de Estratégias**
   - CRUD de estratégias no dashboard
   - Comparação lado-a-lado de múltiplas estratégias

2. **Sincronização Automática**
   - Script para atualizar banco com novos backtests
   - Trigger para recalcular métricas automaticamente

3. **API REST**
   - Endpoint para consultar estratégias
   - Webhook para novos trades

4. **Otimização**
   - Migrar para SQLAlchemy ORM
   - Adicionar índices compostos
   - Cache de queries frequentes

---

## 📝 Notas Importantes

⚠️ **SEMPRE use `uv run` para executar scripts Python neste projeto!**

```bash
# ✅ CORRETO
uv run src/webapp/migrate_data.py
uv run src/webapp/app.py

# ❌ ERRADO
python src/webapp/migrate_data.py
python src/webapp/app.py
```

⚠️ **Backup Automático**: O script de migração preserva o CSV original. Nunca deleta dados.

⚠️ **Compatibilidade**: O modelo `TradingDataModel` funciona tanto com SQLite quanto CSV (fallback).

---

## 🎯 Exemplo Completo: Adicionar Nova Estratégia

```python
from src.webapp.models.database import TradingDatabase, calculate_strategy_metrics
import pandas as pd

# 1. Conectar
db = TradingDatabase("data/trading_bot.db")

# 2. Criar nova estratégia
strategy_id = db.insert_strategy(
    name="Moderada TP 2.5%",
    description="Equilíbrio entre risco e retorno",
    model_type="LSTM",
    take_profit=2.5,
    stop_loss=1.2,
    threshold=0.6
)

# 3. Ler CSV com histórico da nova estratégia
df_csv = pd.read_csv('src/ml/outputs/capital_history-moderada.csv', sep=';')

# 4. Converter para formato de trades
trades = []
for _, row in df_csv.iterrows():
    trades.append({
        'data': row['Data'],
        'operacao': row['Operacao'],
        'status': row['Status'],
        'previsao': row['Previsao'],
        'valor_atual': row['Valor Atual'],
        'preco': row['Preco'],
        'quantidade': row['Quantidade'],
        'custo': row['Custo'],
        'capital': row['Capital']
    })

# 5. Inserir trades
db.bulk_insert_trades(strategy_id, trades)

# 6. Calcular e salvar métricas
df_trades = db.get_trades_by_strategy(strategy_id)
metrics = calculate_strategy_metrics(df_trades)
db.update_strategy_metrics(strategy_id, **metrics)

# 7. Verificar
strategy = db.get_strategy(strategy_id=strategy_id)
print(f"✅ Estratégia '{strategy['name']}' criada!")
print(f"   Retorno: {strategy['total_return']}%")
print(f"   Sharpe: {strategy['sharpe_ratio']}")

db.close()
```

---

## 📞 Suporte

Para dúvidas sobre o sistema de banco de dados:
- Consulte `src/webapp/models/database.py` (código documentado)
- Execute `uv run src/webapp/migrate_data.py` para ver exemplo de uso
- Verifique `src/webapp/models/trading_data_model.py` para integração

---

**Criado em**: 16/10/2025  
**Versão**: 1.0.0  
**Desenvolvedor**: Silvino Miranda
