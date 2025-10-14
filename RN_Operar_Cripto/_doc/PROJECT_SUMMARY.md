# 📊 Projeto RN_Operar_Cripto - Resumo Completo

## 🎯 Objetivo
Sistema de previsão de preços de criptomoedas utilizando **LSTM (Long Short-Term Memory)** para trading automatizado de BTC/USDT.

---

## 🧠 Tipo de Rede Neural
**LSTM (Long Short-Term Memory)** - Uma arquitetura especializada de Redes Neurais Recorrentes (RNN) projetada para:
- Capturar dependências temporais de longo prazo
- Aprender padrões sequenciais em séries temporais financeiras
- Evitar o problema de gradiente desvanecente comum em RNNs tradicionais

---

## 📁 Estrutura do Projeto

### 🗂️ Módulos Principais

#### 1. **Data (Dados)**
```
src/data/
├── data_loader.py      # Carregamento de dados históricos
├── data_save.py        # Salvamento de dados processados
└── indicator.py        # Cálculo de indicadores técnicos
```

**Funcionalidades:**
- Carregamento de dados do arquivo local `BTCUSDT_30m.csv`
- Cálculo automático de indicadores técnicos (SMA, EMA, RSI, MACD, etc.)
- Gerenciamento de dados históricos

#### 2. **Utils (Utilitários)**
```
src/utils/
└── data_preprocessing.py  # Pré-processamento e normalização
```

**Funcionalidades:**
- Normalização dos dados (MinMaxScaler)
- Criação de sequências temporais (janelas de 60 períodos)
- Divisão dos dados em treino/validação/teste

#### 3. **Models (Modelos)**
```
src/models/
└── lstm_model.py       # Implementação do modelo LSTM
```

**Arquitetura:**
- Camadas LSTM empilhadas
- Dropout para regularização
- Previsão de múltiplos valores: Close, High, Low

#### 4. **Backtesting**
```
src/backtesting/
├── backtester.py       # Engine de backtesting
└── my_strategy.py      # Estratégia de trading
```

**Funcionalidades:**
- Simulação de operações de compra/venda
- Cálculo de métricas de performance
- Análise de rentabilidade

---

## 📊 Dados Utilizados

### Série Temporal: **BTC/USDT (30 minutos)**
- **Arquivo:** `data/BTCUSDT_30m.csv`
- **Período:** 2023-10-13 até 2025-10-13
- **Total de registros:** 35.089 candles
- **Intervalo:** 30 minutos

### Colunas do Dataset:
```
Date            # Timestamp do candle
Open            # Preço de abertura
High            # Preço máximo
Low             # Preço mínimo
Close           # Preço de fechamento
SMA_20          # Média Móvel Simples (20 períodos)
EMA_20          # Média Móvel Exponencial (20 períodos)
RSI_14          # Índice de Força Relativa (14 períodos)
MACD            # Moving Average Convergence Divergence
MACD_Signal     # Linha de sinal do MACD
BB_High         # Banda de Bollinger Superior
BB_Low          # Banda de Bollinger Inferior
Stoch           # Oscilador Estocástico
OBV             # On-Balance Volume
```

---

## 🎓 Features do Modelo

### Entrada (Features):
```python
feature_columns = [
    "Open",           # Preço de abertura
    "High",           # Preço máximo
    "Low",            # Preço mínimo
    "SMA_20",         # Média móvel simples
    "EMA_20",         # Média móvel exponencial
    "RSI_14",         # Índice de força relativa
    "MACD",           # MACD
    "MACD_Signal",    # Linha de sinal MACD
    "BB_High",        # Bollinger Band superior
    "BB_Low",         # Bollinger Band inferior
    "Stoch",          # Estocástico
    "OBV",            # On-Balance Volume
]
```

### Saída (Targets):
```python
target_columns = [
    "Close",  # Preço de fechamento previsto
    "High",   # Preço máximo previsto
    "Low"     # Preço mínimo previsto
]
```

### Parâmetros do Modelo:
- **Sequence Length:** 60 períodos (30 horas de dados)
- **Epochs:** 10 (ajustável)
- **Batch Size:** 64
- **Split:** 70% treino, 15% validação, 15% teste

---

## 🚀 Scripts de Execução

### 1. **Preparação dos Dados**
```bash
python prepare_data.py
```
**Função:**
- Carrega o arquivo CSV
- Verifica e adiciona indicadores técnicos faltantes
- Cria backup automático
- Valida a integridade dos dados

### 2. **Treinamento do Modelo**
```bash
python src/main_train.py
```
**Função:**
- Carrega dados pré-processados
- Treina o modelo LSTM
- Salva o modelo treinado como `lstm_model.keras`
- Gera histórico de treinamento

### 3. **Previsões**
```bash
python src/main_predict.py
```
**Função:**
- Carrega modelo treinado
- Gera previsões para os dados de teste
- Calcula métricas de erro (MAE, RMSE, etc.)
- Salva resultados

### 4. **Dashboard de Visualização**
```bash
python src/app.py
```
**Função:**
- Interface web interativa (Dash)
- Visualização de previsões vs valores reais
- Gráficos comparativos
- Acesso via http://localhost:8050

---

## 📦 Dependências Principais

```
tensorflow          # Framework de deep learning
keras               # API de alto nível para TensorFlow
pandas              # Manipulação de dados
numpy               # Computação numérica
scikit-learn        # Pré-processamento e métricas
ta                  # Indicadores técnicos
matplotlib          # Visualização de dados
yfinance            # Download de dados financeiros
dash                # Dashboard web interativo
plotly              # Gráficos interativos
backtrader          # Framework de backtesting
```

---

## 🔧 Configuração

### Arquivo: `config.py`
```python
# Configurações centralizadas do projeto
SYMBOL = "BTCUSDT"
INTERVAL = "30m"
DATA_FILE = "data/BTCUSDT_30m.csv"
SEQUENCE_LENGTH = 60
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15
```

---

## 📈 Workflow Completo

```
1. Preparação
   └─> prepare_data.py
       └─> Carrega CSV
       └─> Adiciona indicadores
       └─> Valida dados

2. Treinamento
   └─> main_train.py
       └─> Pré-processa dados
       └─> Treina LSTM
       └─> Salva modelo

3. Previsão
   └─> main_predict.py
       └─> Carrega modelo
       └─> Gera previsões
       └─> Calcula métricas

4. Visualização
   └─> app.py
       └─> Dashboard interativo
       └─> Análise visual
```

---

## ✅ Status Atual do Projeto

✔️ Dados preparados com indicadores técnicos  
✔️ Estrutura modular organizada  
✔️ Scripts de treinamento e previsão  
✔️ Dashboard de visualização  
✔️ Configuração centralizada  
✔️ Documentação completa  

---

## 🎯 Próximos Passos Sugeridos

1. **Otimização do Modelo**
   - Ajustar hiperparâmetros (epochs, batch_size, layers)
   - Testar diferentes arquiteturas LSTM
   - Implementar early stopping

2. **Melhorias na Estratégia**
   - Refinar regras de entrada/saída
   - Adicionar stop-loss e take-profit
   - Implementar gestão de risco

3. **Análise de Performance**
   - Backtesting extensivo
   - Análise de drawdown
   - Comparação com buy-and-hold

4. **Integração em Tempo Real**
   - Conectar com API da Binance
   - Trading automatizado
   - Sistema de alertas

5. **Monitoramento**
   - Logs de operações
   - Métricas de performance
   - Dashboard de acompanhamento

---

## 📝 Observações Importantes

⚠️ **AVISO:** Este projeto é para fins educacionais e de pesquisa. Trading de criptomoedas envolve riscos significativos. Sempre faça backtesting extensivo antes de usar em ambiente real.

📚 **Documentação Adicional:**
- Ver `README.md` para instruções de instalação
- Ver comentários no código para detalhes técnicos
- Ver notebooks Jupyter para análises exploratórias

---

**Última Atualização:** 13 de Outubro de 2025  
**Versão:** 1.0  
**Autor:** Silvino Miranda
