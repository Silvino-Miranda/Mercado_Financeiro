# Mean-Reversion Backtester (BTCUSDT Daily)

Um sistema de backtesting avançado para estratégias de reversão à média no par BTCUSDT usando dados diários, implementando três variantes de estratégia com gestão rigorosa de risco.

## 🎯 Visão Geral

Este backtester implementa três estratégias de reversão à média para Bitcoin (BTCUSDT) com características comuns:
- **Entrada**: Quando o preço está abaixo da média móvel de 200 períodos
- **Saída**: Stop-loss, take-profit, stop de tempo ou breakeven
- **Gestão de Risco**: ATR-based stop loss, breakeven automático e custos de transação

## 📊 Estratégias Implementadas

### 1. MR-Base (Filtro de Inclinação)
- **Condição de Entrada**: Preço ≤ (1 - dist_below_ma_pct) × MA200 **E** MA200 hoje > MA200 há 5 dias
- **Lógica**: Compra quando o preço está abaixo da MA200 mas a tendência de longo prazo é ascendente

### 2. MR-RSI (Cruzamento do RSI)
- **Condição de Entrada**: Preço ≤ (1 - dist_below_ma_pct) × MA200 **E** RSI(14) cruza acima de 30
- **Lógica**: Compra quando o preço está abaixo da MA200 e o RSI sai da zona de sobrevenda

### 3. MR-Reclaim (Reconquista da MA200)
- **Condição de Entrada**: Preço anterior ≤ 0.95 × MA200 **E** preço atual ≥ MA200
- **Lógica**: Compra quando o preço reconquista a MA200 após estar significativamente abaixo

## ⚙️ Parâmetros de Configuração

### Parâmetros de Estratégia
- **`variant`**: Tipo de estratégia (`base`, `rsi`, `reclaim`)
- **`ma_len`**: Período da média móvel (padrão: 200)
- **`dist_below_ma_pct`**: Distância percentual abaixo da MA para entrada (padrão: 5%)
- **`slope_lookback`**: Período para cálculo da inclinação da MA (padrão: 5)
- **`rsi_period`**: Período do RSI (padrão: 14)
- **`rsi_cross_level`**: Nível de cruzamento do RSI (padrão: 30)

### Parâmetros de Gestão de Risco
- **`tp_pct`**: Take profit percentual (padrão: 10%)
- **`sl_pct`**: Stop loss percentual (padrão: 8%)
- **`atr_mult`**: Multiplicador do ATR para stop dinâmico (padrão: 2.0)
- **`time_stop`**: Número máximo de barras em posição (padrão: 30)
- **`be_trigger_pct`**: Trigger para breakeven (padrão: 6%)
- **`allow_breakeven`**: Habilitar breakeven automático (padrão: True)

### Parâmetros de Custos
- **`fees_bps`**: Taxas de corretagem em basis points (padrão: 10 = 0.10%)
- **`slip_bps`**: Slippage em basis points (padrão: 5 = 0.05%)
- **`capital_per_trade`**: Capital por operação (padrão: $1000)

## 🚀 Como Usar

### Instalação de Dependências
```bash
pip install pandas numpy argparse
```

### Formato do CSV Requerido
O arquivo CSV deve conter as seguintes colunas (case-insensitive):
- **Date**: Data (formato compatível com pandas datetime)
- **Open**: Preço de abertura
- **High**: Preço máximo
- **Low**: Preço mínimo
- **Close**: Preço de fechamento

### Execução Simples
```bash
python mr_backtest.py --csv dados/BTCUSDT_1d.csv --variant base --capital_per_trade 1000
```

### Execução com Parâmetros Customizados
```bash
python mr_backtest.py --csv dados/BTCUSDT_1d.csv --variant rsi \
  --capital_per_trade 5000 --fees_bps 15 --slip_bps 3 \
  --tp_pct 0.12 --sl_pct 0.06 --atr_mult 1.5 --time_stop 25 \
  --be_trigger_pct 0.05 --ma_len 180 --dist_below_ma_pct 0.07
```

### Grid Search (Recomendado)
```bash
python mr_backtest.py --csv dados/BTCUSDT_1d.csv --grid
```

## 📈 Métricas de Performance

O sistema calcula automaticamente as seguintes métricas:

### Métricas Básicas
- **Número de Trades**: Total de operações executadas
- **Taxa de Acerto**: Percentual de trades lucrativos
- **Profit Factor**: Razão entre lucros e perdas brutas
- **Expectativa por Trade**: Ganho/perda média esperada por operação

### Métricas de Risco
- **Maximum Drawdown**: Maior queda do capital
- **Sharpe-like Ratio**: Retorno ajustado ao risco
- **Sortino-like Ratio**: Retorno ajustado ao downside risk

### Métricas Operacionais
- **Tempo em Mercado**: Percentual do tempo em posição
- **Trades por Ano**: Frequência de operações
- **PnL Total**: Lucro/prejuízo total realizado

## 🔧 Lógica de Execução

### Sinais e Entradas
1. **Avaliação**: Sinais são avaliados no fechamento do dia T
2. **Execução**: Entradas são executadas na abertura do dia T+1
3. **Limitação**: Apenas 1 posição por vez

### Gestão de Saídas (Ordem Conservadora)
1. **Time Stop**: Saída no fechamento após X barras
2. **Gap Down**: Saída na abertura se gap através do stop
3. **Gap Up**: Saída na abertura se gap através do target
4. **Ambos Atingidos**: Se TP e SL tocam na mesma barra, SL tem prioridade
5. **Stop Loss**: Saída no nível de stop
6. **Take Profit**: Saída no nível de target
7. **Breakeven**: Stop movido para entrada após trigger

### Cálculo de Custos
- **Compra**: `Preço × (1 + fees_bps/10000) × (1 + slip_bps/10000)`
- **Venda**: `Preço × (1 - slip_bps/10000) / (1 + fees_bps/10000)`

## 📊 Outputs

### Execução Simples
- Sumário detalhado na tela com parâmetros e métricas
- Arquivo `trades.csv` com detalhes de cada operação

### Grid Search
- Arquivo `grid_results.csv` com todas as combinações testadas
- Top 10 melhores resultados ordenados por Profit Factor

## 🔍 Indicadores Técnicos Implementados

### RSI de Wilder
- Implementação com suavização exponencial (RMA)
- Período padrão: 14 barras
- Valores neutros (50) para barras iniciais

### ATR de Wilder
- True Range com suavização exponencial
- Período padrão: 14 barras
- Usado para stop loss dinâmico

### Média Móvel Simples
- Janela móvel com mínimo de períodos
- Padrão: 200 períodos
- Base para sinais de entrada

## 🧪 Grid Search Configurado

O grid search testa sistematicamente:
- **Variantes**: base, rsi, reclaim
- **Distância MA**: 3%, 5%, 7%, 10%
- **Take Profit**: 8%, 10%, 12%
- **Stop Loss**: 6%, 8%, 10%
- **ATR Multiplicador**: 1.5, 2.0
- **Time Stop**: 20, 30, 45 barras
- **MA Length**: 180, 200, 220
- **Breakeven**: Habilitado/Desabilitado

**Total**: 3 × 4 × 3 × 3 × 2 × 3 × 3 × 2 = **1,296 combinações**

## 📋 Exemplo de Saída

```
Strategy Summary
  variant: base
  ma_len: 200
  dist_below_ma_pct: 0.05
  tp_pct: 0.10
  sl_pct: 0.08
  capital_per_trade: 1000.0
----------------------------------------
trades: 45.0000
win_rate: 0.6222
profit_factor: 1.8945
expectancy_per_trade: 23.45
avg_win: 67.89
avg_loss: 42.12
max_drawdown: -234.56
sharpe_like: 0.8934
sortino_like: 1.2456
time_in_market: 0.3567
trades_per_year: 12.4500
total_pnl: 1055.25
```

## ⚠️ Considerações Importantes

1. **Dados Históricos**: Resultados passados não garantem performance futura
2. **Custos Realistas**: Inclui taxas e slippage para simulação mais precisa
3. **Ordem Conservadora**: Em caso de ambiguidade, assume o pior cenário
4. **Capital Fixo**: Cada trade usa capital fixo (não compounding)
5. **Timeframe**: Otimizado para dados diários

## 🛠️ Possíveis Melhorias

- [ ] Implementação de trailing stop
- [ ] Suporte para múltiplos ativos
- [ ] Visualizações gráficas dos resultados
- [ ] Análise de Monte Carlo
- [ ] Walk-forward optimization
- [ ] Compounding de capital

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais e de pesquisa.

---

**Autor**: Desenvolvido para análise quantitativa de estratégias de trading
**Versão**: 1.0
**Data**: Outubro 2025