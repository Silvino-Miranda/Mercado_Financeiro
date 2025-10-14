# Sistema de Day Trade com IA

## 🤖 Descrição
Sistema automatizado de day trade que utiliza Inteligência Artificial (OpenAI GPT) para análise de indicadores técnicos e geração de sinais de trading. Combina análise técnica tradicional com insights de IA para tomada de decisões informadas.

## 🎯 Objetivo
Automatizar o processo de análise técnica utilizando IA para interpretar indicadores financeiros, gerando relatórios detalhados e sinais de trading com justificativas fundamentadas.

## 🛠️ Funcionalidades

### Análise Técnica Automatizada
- **Indicadores Técnicos**: SMA 50/200, RSI, MACD
- **Integração com IA**: Análise via OpenAI GPT-4o-mini
- **Sinais Inteligentes**: Recomendações baseadas em múltiplos fatores
- **Relatórios Detalhados**: Justificativas para cada sinal gerado

### Arquiteturas Disponíveis
- **main.py**: Versão base com LangChain
- **main_oop.py**: Implementação orientada a objetos
- **main_chain.py**: Versão com chains avançadas
- **Agentes Especializados**: Sistema multi-agente

### Processamento de Dados
- **Coleta Automática**: Dados via Yahoo Finance
- **Cálculo de Indicadores**: TA-Lib para análise técnica
- **Processamento JSON**: Estruturação de dados para IA
- **Histórico Configurável**: Períodos personalizáveis

## 📁 Estrutura do Projeto
```
daytrade/
├── src/
│   ├── main.py                 # Script principal
│   ├── main_oop.py            # Versão OOP
│   ├── main_chain.py          # Versão com chains
│   ├── agents/
│   │   ├── __init__.py
│   │   └── technical_agent.py  # Agente de análise técnica
│   ├── models/                # Modelos de dados
│   └── utils/                 # Utilitários
├── resultados/                # Relatórios gerados
│   ├── 2024-10-15_BTC-USD.md
│   ├── 2024-10-15_PENDLE-USD.md
│   └── 2024-10-17_DISB34.SA.md
├── _Arquivos/                 # Dependências especiais
│   └── TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
├── requirements.txt           # Dependências
├── READEME.md                # Documentação (typo original)
└── README.md                 # Este arquivo
```

## 🚀 Como Usar

### 1. Pré-requisitos
- Python 3.8+
- Chave API da OpenAI
- TA-Lib instalado

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt

# Para Windows, instalar TA-Lib manualmente:
pip install _Arquivos/TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

### 3. Configuração da API
Crie um arquivo `.env` com sua chave da OpenAI:
```env
OPENAI_API_KEY=sua_chave_api_aqui
```

### 4. Execução
```bash
cd src
python main.py
```

### 5. Análise dos Resultados
- Relatórios são salvos na pasta `resultados/`
- Formato Markdown para fácil leitura
- Inclui gráficos e recomendações detalhadas

## 📊 Exemplo de Uso

### Análise de Ativo
```python
# Configuração do ativo
ticker = "BTC-USD"
period = "1mo"
interval = "1d"

# Obter dados e calcular indicadores
data = get_historical_data(ticker)
indicators = calculate_indicators(data)

# Análise com IA
analysis = llm.invoke(prompt_template.format(
    ticker=ticker,
    indicators=indicators
))
```

### Saída do Sistema
```json
{
    "ticker": "BTC-USD",
    "timestamp": "2024-10-15",
    "signal": "COMPRA",
    "confidence": 85,
    "indicators": {
        "SMA_50": 67000,
        "SMA_200": 65000,
        "RSI": 55,
        "MACD": "Positivo"
    },
    "analysis": "Tendência de alta confirmada..."
}
```

## 🔧 Principais Dependências
- `yfinance`: Coleta de dados financeiros
- `talib`: Cálculo de indicadores técnicos
- `langchain`: Framework para IA
- `openai`: API da OpenAI
- `python-dotenv`: Gerenciamento de variáveis de ambiente

## 📈 Indicadores Implementados

### Médias Móveis
- **SMA 50**: Tendência de curto prazo
- **SMA 200**: Tendência de longo prazo
- **Cruzamentos**: Sinais de entrada/saída

### Osciladores
- **RSI**: Força relativa (sobrecompra/sobrevenda)
- **MACD**: Convergência/divergência de médias

### Volume
- **OBV**: Volume no balanço (em desenvolvimento)
- **Volume médio**: Confirmação de sinais

## 🤖 Integração com IA

### Modelo Utilizado
- **GPT-4o-mini**: Modelo otimizado da OpenAI
- **Temperature 0.5**: Equilibrio entre criatividade e precisão
- **Context Window**: Suporte a contextos extensos

### Prompt Engineering
```python
prompt_template = """
Dados históricos processados para {ticker}.
Indicadores calculados:
- SMA 50: {sma_50}
- SMA 200: {sma_200}
- RSI: {rsi}
- MACD: {macd}

Analise estes indicadores e forneça:
1. Sinal de trading (COMPRA/VENDA/ESPERA)
2. Nível de confiança (0-100)
3. Justificativa detalhada
4. Pontos de entrada e saída
"""
```

### Processamento de Resposta
- Parsing automático de JSON
- Validação de sinais
- Tratamento de erros
- Fallback para análise técnica tradicional

## ⚙️ Configurações Avançadas

### Parâmetros de Indicadores
```python
# RSI
rsi_period = 14
rsi_overbought = 70
rsi_oversold = 30

# MACD
macd_fast = 12
macd_slow = 26
macd_signal = 9
```

### Configurações de IA
```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    max_tokens=1000
)
```

## 📊 Relatórios Gerados

### Formato dos Relatórios
- **Header**: Ticker, data, timestamp
- **Resumo Executivo**: Sinal principal e confiança
- **Análise Técnica**: Detalhamento dos indicadores
- **Recomendações**: Pontos de entrada/saída
- **Riscos**: Cenários adversos
- **Conclusão**: Resumo final

### Exemplo de Relatório
```markdown
# Análise Técnica - BTC-USD
**Data**: 2024-10-15
**Sinal**: COMPRA (85% confiança)

## Indicadores
- SMA 50: $67,000 (acima da SMA 200)
- RSI: 55 (zona neutra)
- MACD: Positivo, linha acima do sinal

## Recomendação
Entrada: $66,500
Stop Loss: $65,000
Take Profit: $70,000
```

## ⚠️ Avisos Importantes
- **Não é Aconselhamento Financeiro**: Sistema para fins educacionais
- **Backtesting Necessário**: Teste estratégias antes de operar
- **Gestão de Risco**: Nunca arrisque mais do que pode perder
- **Monitoramento**: Acompanhe posições constantemente

## 🎯 Casos de Uso
- **Day Trading**: Sinais intraday automatizados
- **Swing Trading**: Análise de médio prazo
- **Educação**: Aprendizado de análise técnica
- **Pesquisa**: Desenvolvimento de estratégias

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novos indicadores técnicos
- Modelos de IA alternativos
- Interfaces web
- Backtesting automatizado
- Integração com brokers

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
