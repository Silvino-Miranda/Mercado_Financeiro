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
RN_Operar_Cripto/
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
