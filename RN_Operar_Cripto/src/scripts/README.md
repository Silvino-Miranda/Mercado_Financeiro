# 📊 Scripts Auxiliares

Scripts para análise, debug e testes do sistema.

## 📝 Scripts Disponíveis

### Análise de Dados
- **`analyze_test_data.py`** - Análise de data leakage e distribuição de dados
- **`check_capital.py`** - Verifica histórico de capital das operações

### Análise de Previsões
- **`analyze_predictions.py`** - Debug de previsões do modelo LSTM

### Análise de Estratégias
- **`analyze_strategies_results.py`** - Ranking de estratégias de trading
- **`test_single_strategy.py`** - Testa uma estratégia específica
- **`run_compare_strategies.py`** - Compara múltiplas estratégias

## 🚀 Como Usar

### Executar com UV (recomendado)
```powershell
uv run python src/scripts/analyze_predictions.py
uv run python src/scripts/test_single_strategy.py
```

### Executar com Python direto
```powershell
python src/scripts/analyze_predictions.py
python src/scripts/test_single_strategy.py
```

## 📊 Descrição Detalhada

### analyze_test_data.py
Analisa o problema de data leakage identificado no treino/teste do modelo.
Mostra a distribuição de preços entre os períodos de treino e teste.

### check_capital.py
Lê o arquivo `capital_history-BTCUSDT.csv` e calcula:
- Capital inicial vs final
- Retorno total
- Retorno anualizado

### analyze_predictions.py
Analisa as previsões do modelo para entender:
- Por que a estratégia não está operando
- Qualidade das previsões
- Distribuição dos sinais

### analyze_strategies_results.py
Gera ranking das estratégias testadas com:
- Retorno total (%)
- Retorno anualizado (%)
- Capital final

### test_single_strategy.py
Testa uma estratégia específica do arquivo `strategies.json`:
- Carrega configuração
- Executa backtesting
- Gera relatório detalhado

### run_compare_strategies.py
Wrapper para executar `src/ml/compare_strategies.py`:
- Compara todas as estratégias
- Gera análise comparativa
- Identifica melhor estratégia

## 📁 Estrutura

```
src/scripts/
├── __init__.py
├── README.md (este arquivo)
├── analyze_predictions.py
├── analyze_strategies_results.py
├── analyze_test_data.py
├── check_capital.py
├── run_compare_strategies.py
└── test_single_strategy.py
```

## 💡 Quando Usar

- **Durante desenvolvimento**: Para debug e análise
- **Após treinamento**: Para validar previsões
- **Após backtesting**: Para analisar resultados
- **Para comparação**: Ao testar novas estratégias
