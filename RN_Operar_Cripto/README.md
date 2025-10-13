# Sistema de Trading com Rede Neural LSTM

## 🧠 Descrição
Sistema avançado de trading automatizado utilizando Redes Neurais LSTM (Long Short-Term Memory) para previsão de preços de criptomoedas. Combina machine learning, análise técnica e backtesting para operações automatizadas.

## 🎯 Objetivo
Desenvolver um sistema de trading inteligente que utiliza deep learning para prever movimentos de preços e executar operações automatizadas com base em padrões identificados em dados históricos.
- `main.py`: Script principal para rodar o projeto.
## 🛠️ Funcionalidades

### Machine Learning
- **LSTM Networks**: Redes neurais para séries temporais
- **Indicadores Técnicos**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Feature Engineering**: Criação de features avançadas
- **Treinamento Automático**: Pipeline completo de ML

### Trading Automatizado
- **Sinais de IA**: Decisões baseadas em previsões do modelo
- **Backtesting**: Validação de estratégias
- **Múltiplos Ativos**: Suporte para diferentes criptomoedas
- **Gestão de Risco**: Stop loss e take profit inteligentes

### Dashboard Interativo
- **Visualização em Tempo Real**: Gráficos dinâmicos
- **Métricas de Performance**: KPIs do modelo
- **Análise Técnica**: Indicadores sobrepostos
- **Interface Jupyter**: Notebooks interativos

## 📁 Estrutura do Projeto
```
# 🚀 RN_Operar_Cripto - Previsão de Bitcoin com LSTM

Sistema de previsão de preços de criptomoedas usando Redes Neurais LSTM (Long Short-Term Memory) com análise técnica e backtesting.

## 📊 Série Temporal

- **Par:** BTC/USDT (Bitcoin / Tether USD)
- **Intervalo:** 30 minutos
- **Arquivo:** `data/BTCUSDT_30m.csv`
- **Período:** 2023-10-13 até presente (~35.000 registros)

## 🧠 Tipo de Rede Neural

**LSTM (Long Short-Term Memory)** - Um tipo de Rede Neural Recorrente (RNN) especializada em:
- Capturar dependências temporais de longo prazo
- Aprender padrões em séries temporais
- Evitar o problema de gradientes desvanecentes
- Ideal para previsão de preços financeiros

## 📁 Estrutura do Projeto

```
RN_Operar_Cripto/
├── data/
│   └── BTCUSDT_30m.csv          # Série temporal principal
├── src/
│   ├── data/
│   │   ├── data_loader.py       # Carregamento de dados
│   │   ├── indicator.py         # Indicadores técnicos
│   │   └── data_save.py         # Salvamento de dados
│   ├── models/
│   │   └── lstm_model.py        # Modelo LSTM
│   ├── utils/
│   │   └── data_preprocessing.py # Pré-processamento
│   ├── backtesting/
│   │   ├── backtester.py        # Sistema de backtesting
│   │   └── my_strategy.py       # Estratégia de trading
│   ├── main_train.py            # Script de treinamento
│   ├── main_predict.py          # Script de previsão
│   └── app.py                   # Dashboard web (Dash)
├── config.py                    # Configurações centralizadas
├── prepare_data.py              # Preparação dos dados
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## 🎯 Features (Indicadores Técnicos)

O modelo usa os seguintes indicadores como features:

1. **Preços básicos:** Open, High, Low
2. **Médias Móveis:** SMA_20, EMA_20
3. **Momentum:** RSI_14 (Relative Strength Index)
4. **Tendência:** MACD, MACD_Signal
5. **Volatilidade:** BB_High, BB_Low (Bollinger Bands)
6. **Osciladores:** Stoch (Stochastic)
7. **Volume:** OBV (On-Balance Volume)

**Targets (Previsões):** Close, High, Low

## 🔧 Configuração e Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Preparar os dados

```bash
python prepare_data.py
```

Este script irá:
- Verificar o arquivo `BTCUSDT_30m.csv`
- Adicionar indicadores técnicos se necessário
- Criar backup dos dados originais

## 🚀 Uso

### 1. Treinar o Modelo

```bash
python src/main_train.py
```

Isso irá:
- Carregar os dados de `data/BTCUSDT_30m.csv`
- Pré-processar e normalizar os dados
- Criar sequências temporais (60 períodos)
- Treinar o modelo LSTM
- Salvar o modelo em `lstm_model.keras`

**Parâmetros de treinamento:**
- Sequência: 60 períodos (30 horas)
- Épocas: 10
- Batch size: 64
- Divisão: 70% treino, 15% validação, 15% teste

### 2. Fazer Previsões

```bash
python src/main_predict.py
```

Isso irá:
- Carregar o modelo treinado
- Fazer previsões para todos os dados
- Executar backtesting da estratégia
- Gerar arquivo `capital_history-BTCUSDT.csv`
- Plotar gráficos de previsão

### 3. Visualizar Dashboard

```bash
python src/app.py
```

Acesse: http://localhost:8050

O dashboard mostra:
- Comparação visual: Previsões vs Valores Reais
- Gráficos interativos (Plotly)
- Histórico de capital
- Performance da estratégia

## 📊 Módulos Principais

### 1. **data.data_loader**
Carrega dados do arquivo CSV local ou baixa via yfinance.

### 2. **data.indicator**
Calcula indicadores técnicos (SMA, EMA, RSI, MACD, etc.).

### 3. **utils.data_preprocessing**
Normaliza dados, cria sequências temporais, divide em treino/validação/teste.

### 4. **models.lstm_model**
Implementação do modelo LSTM com TensorFlow/Keras.

### 5. **backtesting.backtester**
Sistema de backtesting para avaliar estratégias de trading.

### 6. **backtesting.my_strategy**
Estratégia de trading baseada nas previsões do modelo.

## ⚙️ Configurações

Edite `config.py` para personalizar:

```python
DATA_CONFIG = {
    "symbol": "BTCUSDT",
    "interval": "30m",
    "local_filename": "BTCUSDT_30m.csv"
}

MODEL_CONFIG = {
    "sequence_length": 60,
    "epochs": 10,
    "batch_size": 64
}

BACKTEST_CONFIG = {
    "initial_capital": 10000.0,
    "commission": 0.001
}
```

## 📈 Arquitetura do Modelo LSTM

```
Input (60, 12) - Sequência de 60 períodos com 12 features
    ↓
LSTM Layer 1 (50 units) + Dropout(0.2)
    ↓
LSTM Layer 2 (50 units) + Dropout(0.2)
    ↓
Dense Layer (25 units, ReLU)
    ↓
Output (3 units) - Close, High, Low
```

## 🎯 Resultados

Os resultados são salvos em:
- `lstm_model.keras` - Modelo treinado
- `capital_history-BTCUSDT.csv` - Histórico de backtesting
- Gráficos de previsão (matplotlib)

## 🔍 Próximos Passos

- [ ] Otimização de hiperparâmetros
- [ ] Ensemble de modelos
- [ ] Trading em tempo real
- [ ] Análise de sentimento
- [ ] Mais pares de criptomoedas

## 📝 Notas

- O modelo foi treinado com dados históricos
- Resultados passados não garantem performance futura
- Use apenas para fins educacionais
- Não é conselho financeiro

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

**⚠️ Aviso:** Este projeto é apenas para fins educacionais. Trading de criptomoedas envolve riscos significativos. Sempre faça sua própria pesquisa e consulte profissionais antes de investir
├── src/
│   ├── main_train.py           # Treinamento do modelo
│   ├── main_predict.py         # Predições e trading
│   ├── app.py                  # Dashboard Streamlit
│   ├── app_test.py             # Testes da aplicação
│   ├── data/
│   │   ├── data_loader.py      # Carregamento de dados
│   │   ├── data_save.py        # Salvamento de dados
│   │   └── indicator.py        # Cálculo de indicadores
│   ├── models/
│   │   └── lstm_model.py       # Modelo LSTM
│   └── backtesting/
│       ├── backtester.py       # Engine de backtesting
│       └── my_strategy.py      # Estratégias de trading
├── data/                       # Datasets
├── _Arquivos/                  # Recursos adicionais
├── main.ipynb                  # Notebook principal
├── dash.ipynb                  # Dashboard notebook
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração do Ambiente
```bash
# Ativar ambiente virtual (Windows)
activate.bat

# Ou criar novo ambiente
python -m venv venv
venv\Scripts\activate
```

### 3. Treinamento do Modelo
```bash
cd src
python main_train.py
```

### 4. Execução de Predições
```bash
python main_predict.py
```

### 5. Dashboard Interativo
```bash
streamlit run app.py
```

## 📊 Pipeline de Machine Learning

### 1. Coleta de Dados
```python
# Exemplo de configuração
symbol = "BTC-USD"
start_date = "2024-01-01"
interval = "1d"

data_loader = DataLoader(symbol, start_date, interval)
df = data_loader.load_data()
```

### 2. Feature Engineering
```python
feature_columns = [
    "Open", "High", "Low", "Close",
    "SMA_20", "EMA_20", "RSI_14",
    "MACD", "MACD_Signal",
    "BB_High", "BB_Low",
    "Stoch", "OBV"
]
```

### 3. Modelo LSTM
```python
class LSTMModel:
    def __init__(self, input_shape, units=50):
        self.model = Sequential([
            LSTM(units, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
```

## 🔧 Principais Dependências
- `tensorflow`: Deep learning framework
- `pandas`: Manipulação de dados
- `numpy`: Cálculos numéricos
- `sklearn`: Pré-processamento e métricas
- `streamlit`: Dashboard web
- `plotly`: Visualizações interativas
- `yfinance`: Dados financeiros

## ⚠️ Considerações Importantes
- **Overfitting**: Monitore métricas de validação
- **Look-ahead Bias**: Evite vazamento de dados futuros
- **Custos de Transação**: Inclua taxas no backtesting
- **Regime Change**: Modelo pode precisar retreinamento

## 🎯 Casos de Uso
- **Trading Automatizado**: Operações baseadas em IA
- **Análise de Mercado**: Identificação de padrões
- **Gestão de Risco**: Otimização de portfólios
- **Pesquisa**: Desenvolvimento de estratégias

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
