# Sistema de Backtest Média Móvel 200 (MA200)

## 📈 Descrição
Sistema de backtest para estratégia baseada na Média Móvel de 200 períodos em criptomoedas. Implementa uma das estratégias mais populares do mercado, testando sua eficácia em múltiplos ativos digitais com análise estatística detalhada.

## 🎯 Objetivo
Validar a eficácia da estratégia MA200 em criptomoedas, fornecendo métricas de performance detalhadas para auxiliar na tomada de decisões de investimento baseadas em análise técnica.

## 🛠️ Funcionalidades

### Estratégia MA200
- **Sinal de Compra**: Preço acima da MA200
- **Sinal de Venda**: Preço abaixo da MA200
- **Filtro de Tendência**: Identificação de mercados bull/bear
- **Backtesting Sistemático**: Teste em múltiplos ativos

### Análise Abrangente
- **16 Criptomoedas**: Portfólio diversificado de testes
- **Métricas Detalhadas**: Lucro, drawdown, win rate
- **Comparação Visual**: Gráficos de performance
- **Ranking Automático**: Ordenação por rentabilidade

### Processamento de Dados
- **Dados Históricos**: Arquivos CSV locais
- **Indicadores Técnicos**: Cálculo automático da MA200
- **Tratamento de Erros**: Validação de dados
- **Relatórios Estruturados**: Saída organizada

## 📁 Estrutura do Projeto
```
MA200/
├── src/
│   ├── main.py                 # Script principal
│   ├── backtest_ma200.py       # Classe de backtest MA200
│   ├── DataHandler.py          # Manipulação de dados
│   ├── __init__.py
│   └── data/
│       ├── data_loader.py      # Carregamento de dados
│       ├── data_save.py        # Salvamento de dados
│       ├── indicator.py        # Cálculo de indicadores
│       └── __init__.py
├── data/                       # Dados históricos
│   ├── BTC-USD_2010-01-01_to_2024-10-31_1d.csv
│   ├── ETH-USD_2010-01-01_to_2024-10-31_1d.csv
│   ├── ADA-USD_2010-01-01_to_2024-10-31_1d.csv
│   └── ... (mais 13 ativos)
├── load.ipynb                  # Notebook de carregamento
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Verificação dos Dados
Os dados históricos estão incluídos na pasta `data/`. Formato esperado:
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,42000,43000,41500,42500,1234567
```

### 3. Configuração dos Ativos
No arquivo `main.py`, você pode modificar a lista de ativos:
```python
tickers = [
    "BTC-USD", "SOL-USD", "NMR-USD", "FET-USD",
    "AVAX-USD", "ADA-USD", "LINK-USD", "SNX-USD",
    # ... adicione ou remova conforme necessário
]
```

### 4. Execução do Backtest
```bash
cd src
python main.py
```

### 5. Análise dos Resultados
- Tabela ordenada por performance
- Gráfico comparativo de lucros
- Métricas individuais por ativo

## 📊 Exemplo de Saída
```
Resultados do Backtest MA200
============================
    ticker  profit_percent  total_trades  win_rate
0   BTC-USD          245.7%            23     65.2%
1   ETH-USD          189.3%            31     58.1%
2   SOL-USD          156.8%            18     72.2%
...
```

## 🔧 Principais Dependências
- `pandas`: Manipulação de dados financeiros
- `matplotlib`: Visualização de resultados
- `numpy`: Cálculos numéricos
- Módulos customizados para backtesting

## 📈 Classe BacktestMA200

### Inicialização
```python
class BacktestMA200:
    def __init__(self, ticker, file_path=None):
        self.ticker = ticker
        self.file_path = file_path
        self.data = None
        self.results = {}
```

### Métodos Principais
- **load_data()**: Carregamento e preparação dos dados
- **calculate_ma200()**: Cálculo da média móvel de 200 períodos
- **generate_signals()**: Geração de sinais de compra/venda
- **run_backtest()**: Execução da simulação completa
- **get_results()**: Compilação de métricas finais

## ⚙️ Estratégia MA200 Detalhada

### Lógica de Trading
```python
# Sinais de compra e venda
if close_price > ma200:
    signal = "BUY"
elif close_price < ma200:
    signal = "SELL"
else:
    signal = "HOLD"
```

### Regras de Entrada/Saída
- **Entrada Long**: Preço cruza acima da MA200
- **Saída Long**: Preço cruza abaixo da MA200
- **Sem Short**: Estratégia apenas long
- **Confirmação**: Aguarda fechamento do período

### Características da Estratégia
- **Trend Following**: Segue a tendência principal
- **Simplicidade**: Apenas um indicador
- **Robustez**: Funciona em diferentes mercados
- **Disciplina**: Regras claras e objetivas

## 📊 Métricas Calculadas

### Performance Financeira
- **Lucro Total**: Percentual de ganho/perda
- **Número de Trades**: Quantidade de operações
- **Win Rate**: Percentual de trades vencedores
- **Profit Factor**: Razão entre lucros e perdas

### Análise de Risco
- **Maximum Drawdown**: Maior perda consecutiva
- **Volatilidade**: Desvio padrão dos retornos
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Calmar Ratio**: Retorno anual / Max Drawdown

## 📈 Ativos Analisados

### Criptomoedas Principais
- **BTC-USD**: Bitcoin
- **ETH-USD**: Ethereum
- **ADA-USD**: Cardano
- **LINK-USD**: Chainlink

### Altcoins Promissoras
- **SOL-USD**: Solana
- **AVAX-USD**: Avalanche
- **MATIC-USD**: Polygon
- **UNI-USD**: Uniswap

### Tokens Especializados
- **NMR-USD**: Numeraire
- **FET-USD**: Fetch.ai
- **SNX-USD**: Synthetix
- **Outros**: IMX, STX, PENDLE, MKR, RUNE

## 🔄 Fluxo de Execução
1. **Inicialização**: Carregamento de dados históricos
2. **Preparação**: Cálculo da MA200
3. **Sinalização**: Geração de sinais de trading
4. **Simulação**: Execução virtual das operações
5. **Análise**: Cálculo de métricas de performance
6. **Visualização**: Gráficos e relatórios

## 📊 Visualizações Disponíveis

### Gráfico Principal
```python
plt.figure(figsize=(12, 8))
plt.bar(results_df["ticker"], results_df["profit_percent"])
plt.xlabel("Ativo")
plt.ylabel("Lucro (%)")
plt.title("Comparação do Desempenho dos Ativos no Backtest MA200")
```

### Tipos de Gráficos
- **Barras**: Comparação de performance
- **Linhas**: Evolução temporal
- **Scatter**: Risco vs. Retorno
- **Heatmap**: Correlação entre ativos

## ⚠️ Considerações da Estratégia

### Vantagens
- **Simplicidade**: Fácil implementação
- **Robustez**: Funciona em diferentes condições
- **Disciplina**: Elimina subjetividade
- **Backtesting**: Facilmente testável

### Limitações
- **Whipsaws**: Falsos sinais em mercados laterais
- **Atraso**: Sinais com delay da tendência
- **Mercados Voláteis**: Performance reduzida
- **Custos**: Não considera taxas de transação

## 🎯 Casos de Uso
- **Investidores Iniciantes**: Estratégia simples e efetiva
- **Gestores de Portfolio**: Filtro de tendência
- **Traders Sistemáticos**: Base para sistemas automatizados
- **Educação**: Aprendizado de backtesting

## 🔮 Melhorias Futuras
- [ ] Incluir custos de transação
- [ ] Adicionar stop loss e take profit
- [ ] Implementar filtros adicionais
- [ ] Análise de correlação temporal
- [ ] Interface web interativa
- [ ] Otimização de parâmetros

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novos indicadores técnicos
- Métricas de risco avançadas
- Otimização de estratégias
- Visualizações interativas
- Integração com APIs

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.