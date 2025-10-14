# Sistema de Estratégias Configuráveis

## 📋 Visão Geral

Criamos um sistema completo para gerenciar e testar múltiplas estratégias de trading sem modificar o código. Os parâmetros são armazenados em JSON (simulando um banco de dados).

## 🏗️ Arquitetura

```
src/ml/backtesting/
├── strategies.json          # Banco de dados simulado de estratégias
├── strategy_config.py       # Gerenciador de configurações
├── my_strategy.py           # Estratégia refatorada para usar config
└── compare_strategies.py    # Comparador automático de estratégias

run_compare_strategies.py    # Script principal na raiz
```

## 📊 Arquivo strategies.json

Estrutura simulando tabela de banco de dados:

```json
{
  "strategies": [
    {
      "id": 1,
      "name": "Conservadora TP 1.5%",
      "description": "Estratégia conservadora...",
      "active": true,
      "parameters": {
        "profit_target": 0.015,
        "stop_loss": 0.01,
        "stake_percentage": 0.95,
        "prediction_threshold": 0.005,
        "hold_periods": 48
      },
      "created_at": "2025-10-14T10:00:00",
      "updated_at": "2025-10-14T10:00:00"
    }
  ],
  "metadata": {
    "version": "1.0.0",
    "parameter_definitions": { ... }
  }
}
```

## 🎯 Estratégias Cadastradas

### 1. **Conservadora TP 1.5%** (ID: 1)
- Take Profit: 1.5%
- Stop Loss: 1.0%
- Threshold: 0.5%
- Hold: 48 períodos (24h)
- Perfil: Risco baixo, lucros pequenos e frequentes

### 2. **Moderada TP 2%** (ID: 2) ⭐ MELHOR RESULTADO
- Take Profit: 2.0%
- Stop Loss: 1.5%
- Threshold: 0.5%
- Hold: 48 períodos (24h)
- Perfil: Equilibrada, melhor performance nos testes (26.21% retorno)

### 3. **Agressiva TP 3%** (ID: 3)
- Take Profit: 3.0%
- Stop Loss: 1.5%
- Threshold: 0.5%
- Hold: 48 períodos (24h)
- Perfil: Risco maior, busca lucros maiores (23.86% retorno nos testes)

### 4. **Moderada Plus TP 2.5%** (ID: 4)
- Take Profit: 2.5%
- Stop Loss: 1.5%
- Threshold: 0.5%
- Hold: 48 períodos (24h)
- Perfil: Intermediária entre moderada e agressiva

### 5. **Day Trade TP 1%** (ID: 5)
- Take Profit: 1.0%
- Stop Loss: 0.8%
- Threshold: 0.3%
- Hold: 24 períodos (12h)
- Perfil: Alta frequência, lucros pequenos

### 6. **Swing Trade TP 5%** (ID: 6)
- Take Profit: 5.0%
- Stop Loss: 2.0%
- Threshold: 0.8%
- Hold: 96 períodos (48h)
- Perfil: Baixa frequência, lucros grandes

### 7. **Teste Experimental** (ID: 7) ❌ INATIVA
- Status: Inativa (não será testada)
- Para experimentações

## 🔧 Classes Principais

### StrategyParameters
Dataclass que armazena e valida os parâmetros:
- `profit_target`: % de lucro alvo (0.1% - 20%)
- `stop_loss`: % de stop loss (0.1% - 10%)
- `stake_percentage`: % do capital por trade (10% - 100%)
- `prediction_threshold`: % de diferença para sinal (0.1% - 5%)
- `hold_periods`: Períodos mínimos para manter (1 - 200)

### Strategy
Representa uma estratégia completa:
- `id`: Identificador único
- `name`: Nome da estratégia
- `description`: Descrição detalhada
- `active`: Se está ativa para backtesting
- `parameters`: Objeto StrategyParameters
- `created_at`: Data de criação
- `updated_at`: Data de atualização

### StrategyConfig
Gerenciador de estratégias:
```python
config = StrategyConfig()

# Buscar estratégia
strategy = config.get_strategy(2)  # Por ID
strategy = config.get_strategy_by_name("Moderada TP 2%")  # Por nome

# Listar estratégias
all_strategies = config.get_all_strategies()
active_strategies = config.get_active_strategies()

# CRUD
config.add_strategy(strategy)
config.update_strategy(2, name="Novo Nome")
config.delete_strategy(7)
config.save_strategies()
```

## 🚀 Como Usar

### 1. Testar UMA estratégia específica

```python
from src.ml.backtesting.strategy_config import StrategyConfig
from src.ml.backtesting.my_strategy import MyStrategy

# Carregar estratégia
config = StrategyConfig()
strategy = config.get_strategy_by_name("Moderada TP 2%")

# Criar classe estratégia configurada
strategy_class = MyStrategy.from_strategy_config(strategy)

# Usar no backtester
backtester = Backtester(df, model, strategy=strategy_class)
final_capital = backtester.run()
```

### 2. Comparar TODAS as estratégias ativas

```bash
# Executa backtesting para todas as estratégias ativas
python run_compare_strategies.py
```

Isso irá:
1. Carregar todas as estratégias ativas do JSON
2. Executar backtesting para cada uma
3. Salvar histórico individual: `capital_history-{nome_estrategia}.csv`
4. Gerar comparação: `strategies_comparison.csv`
5. Exibir ranking de performance

### 3. Adicionar nova estratégia

#### Opção A: Editar o JSON diretamente
Adicione um novo objeto no array `strategies` em `strategies.json`.

#### Opção B: Usar código Python
```python
from src.ml.backtesting.strategy_config import Strategy, StrategyParameters, StrategyConfig

# Criar nova estratégia
new_strategy = Strategy(
    id=8,
    name="Minha Nova Estratégia",
    description="Descrição aqui",
    active=True,
    parameters=StrategyParameters(
        profit_target=0.035,  # 3.5%
        stop_loss=0.02,       # 2%
        stake_percentage=0.90,
        prediction_threshold=0.006,
        hold_periods=36
    )
)

# Adicionar ao gerenciador
config = StrategyConfig()
config.add_strategy(new_strategy)
config.save_strategies()  # Salva no JSON
```

### 4. Ativar/Desativar estratégias

```python
config = StrategyConfig()
config.update_strategy(7, active=True)  # Ativar
config.save_strategies()
```

## 📈 Saídas Geradas

### Individual por Estratégia
```
src/ml/outputs/capital_history-Conservadora_TP_1.5%.csv
src/ml/outputs/capital_history-Moderada_TP_2%.csv
src/ml/outputs/capital_history-Agressiva_TP_3%.csv
...
```

### Comparação Consolidada
```
src/ml/outputs/strategies_comparison.csv
```

Contém:
- strategy_id, strategy_name
- initial_capital, final_capital
- return_pct, annual_return
- total_trades, compras, vendas, days
- Todos os parâmetros da estratégia

## 🎯 Resultados Esperados

O comparador exibe:

```
🏆 RANKING DE ESTRATÉGIAS (Por Capital Final)
======================================================================

🥇 Moderada TP 2%
   Capital Final: $126,207.00
   Retorno: 26.21% (126.47% ao ano)
   Trades: 232 em 104 dias
   Parâmetros: TP=2.0% | SL=1.5% | Threshold=0.50%

🥈 Moderada Plus TP 2.5%
   Capital Final: $124,500.00
   ...

🥉 Agressiva TP 3%
   Capital Final: $123,864.00
   ...
```

## 🔄 Fluxo de Trabalho

1. **Criar/Editar** estratégias no `strategies.json`
2. **Testar** manualmente uma estratégia específica
3. **Comparar** todas as ativas automaticamente
4. **Analisar** resultados no CSV de comparação
5. **Selecionar** a melhor estratégia
6. **Usar** no webapp ou trading ao vivo

## 💡 Vantagens

✅ **Sem alteração de código** - Apenas edita JSON
✅ **Versionamento** - Histórico de estratégias
✅ **Facilidade** - Adiciona quantas estratégias quiser
✅ **Comparação** - Testa todas automaticamente
✅ **Simulação de BD** - Estrutura pronta para migrar para banco real
✅ **Validação** - Parâmetros são validados automaticamente
✅ **Documentação** - Metadata no JSON documenta cada parâmetro

## 🔮 Próximos Passos

1. **Migração para Banco de Dados**
   - Criar tabela `strategies` no PostgreSQL/MySQL
   - Adapter pattern para trocar JSON por DB

2. **Interface Web**
   - CRUD de estratégias no webapp
   - Visualização de comparações
   - Seleção de estratégia ativa

3. **Backtesting Avançado**
   - Walk-forward optimization
   - Monte Carlo simulation
   - Análise de drawdown

4. **Machine Learning nos Parâmetros**
   - Otimização automática de parâmetros
   - Grid search / Bayesian optimization

## 📝 Exemplo de Uso Completo

```python
# 1. Carregar configuração
from src.ml.backtesting.strategy_config import StrategyConfig
config = StrategyConfig()

# 2. Listar estratégias
config.list_strategies(active_only=True)

# 3. Selecionar a melhor
best_strategy = config.get_strategy_by_name("Moderada TP 2%")
print(best_strategy)

# 4. Usar no trading
strategy_class = MyStrategy.from_strategy_config(best_strategy)

# 5. Ou comparar todas
# python run_compare_strategies.py
```

## 🛠️ Manutenção

### Backup
Sempre faça backup do `strategies.json` antes de modificar:
```bash
cp src/ml/backtesting/strategies.json src/ml/backtesting/strategies.json.bak
```

### Validação
O StrategyConfig valida automaticamente:
- IDs únicos
- Parâmetros dentro dos limites
- Estrutura JSON correta

### Logs
O compare_strategies.py registra todo o processo de execução.

---

**Criado em:** 2025-10-14  
**Versão:** 1.0.0  
**Status:** ✅ Implementado e Testado
