# Backtest de Criptomoedas e Portfólio

## 🚀 Descrição
Sistema de backtest para análise de performance de criptomoedas e criação de portfólios diversificados. Compara diferentes estratégias de investimento e calcula métricas de risco-retorno para otimização de carteiras.

## 🎯 Objetivo
Avaliar a performance histórica de criptomoedas individuais e portfólios diversificados, fornecendo métricas fundamentais para tomada de decisões de investimento em ativos digitais.

## 🛠️ Funcionalidades

### Análise de Ativos
- **Múltiplas Criptomoedas**: Suporte para principais criptomoedas do mercado
- **Dados Históricos**: Coleta automática via Yahoo Finance
- **Comparação com Bovespa**: Benchmark com mercado tradicional brasileiro
- **Portfólio Equiponderado**: Distribuição igual entre ativos selecionados

### Métricas de Performance
- **Retorno Cumulativo**: Performance total do período
- **Volatilidade Anualizada**: Medida de risco dos ativos
- **Índice Sharpe**: Relação risco-retorno ajustada
- **Ranking de Performance**: Classificação dos melhores ativos

## 📁 Estrutura do Projeto
```
Backtest-Cripto/
├── main.py                     # Script principal de análise
├── main2.py                    # Versão alternativa
├── main3.py                    # Análise expandida
├── main4.py                    # Versão com melhorias
├── main5.py                    # Versão mais recente
├── main5-silvino.py           # Versão personalizada
├── modified_main5.py          # Versão modificada
├── assets.py                  # Definição de ativos
├── requirements.txt           # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração dos Ativos
No arquivo `assets.py`, configure os ativos desejados:
```python
asset_names = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "ADA-USD": "Cardano",
    # Adicione mais criptomoedas conforme necessário
}
```

### 3. Execução do Backtest
```bash
python main.py
```

### 4. Análise dos Resultados
O sistema exibirá:
- Ranking dos ativos por Índice Sharpe
- Métricas de performance individuais
- Comparação com benchmark (Bovespa)
- Gráficos de evolução dos portfólios

## 📊 Exemplo de Saída
```
Backtest Results
================
                    Cumulative Return  Annualized Volatility  Sharpe Ratio
BTC-USD                        15.45                   0.85          2.34
ETH-USD                         8.92                   0.92          1.87
ADA-USD                         4.56                   1.12          1.23
^BVSP                           1.23                   0.35          0.89
```

## 🔧 Principais Dependências
- `pandas`: Manipulação e análise de dados
- `numpy`: Cálculos numéricos e estatísticos
- `yfinance`: Coleta de dados financeiros
- `matplotlib`: Visualização de gráficos

## 📈 Funcionalidades Técnicas

### Coleta de Dados
- Período configurável de análise
- Preenchimento automático de valores ausentes
- Sincronização de dados entre diferentes mercados
- Ajuste para feriados e fins de semana

### Cálculos Financeiros
- **Retornos Diários**: Cálculo percentual dia a dia
- **Retornos Cumulativos**: Performance acumulada
- **Volatilidade**: Desvio padrão anualizado
- **Sharpe Ratio**: (Retorno - Taxa Livre de Risco) / Volatilidade

### Gestão de Portfólio
- Alocação equiponderada automática
- Rebalanceamento implícito
- Cálculo de métricas agregadas
- Comparação com benchmarks

## ⚙️ Configurações Avançadas

### Período de Análise
```python
start_date = "2013-01-01"
end_date = "2024-07-21"
```

### Investimento Inicial
```python
initial_investment = 10000  # R$ 10.000
```

### Alocação de Portfólio
```python
allocation = 1 / len(data.columns)  # Equiponderado
```

## 📊 Interpretação dos Resultados

### Retorno Cumulativo
- Valores > 1: Ganho no período
- Valores < 1: Perda no período
- Comparar com benchmark para avaliar performance relativa

### Volatilidade Anualizada
- Menor volatilidade: Menor risco
- Maior volatilidade: Maior risco (e potencial retorno)

### Índice Sharpe
- Valores > 1: Boa relação risco-retorno
- Valores > 2: Excelente performance ajustada ao risco
- Valores negativos: Performance inferior à taxa livre de risco

## ⚠️ Avisos Importantes
- **Dados Históricos**: Performance passada não garante resultados futuros
- **Volatilidade**: Criptomoedas são ativos de alta volatilidade
- **Diversificação**: Considere diversificação além de criptomoedas
- **Gestão de Risco**: Nunca invista mais do que pode perder

## 🎯 Casos de Uso
- **Seleção de Ativos**: Identificar criptomoedas com melhor performance
- **Construção de Portfólio**: Otimizar alocação de ativos
- **Análise de Risco**: Avaliar volatilidade e correlações
- **Benchmarking**: Comparar com mercados tradicionais

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novos indicadores técnicos
- Estratégias de rebalanceamento
- Visualizações avançadas
- Integração com mais exchanges

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.