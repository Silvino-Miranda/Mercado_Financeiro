# Dashboard de Sinais Financeiros

## 📊 Descrição
Dashboard interativo desenvolvido em Streamlit para análise em tempo real de sinais de compra e venda em criptomoedas e FIIs (Fundos de Investimento Imobiliário). Sistema modular com componentes reutilizáveis para visualização de dados financeiros.

## 🎯 Objetivo
Fornecer uma interface visual intuitiva para monitoramento de sinais de trading, permitindo aos usuários filtrar ativos, visualizar indicadores técnicos e tomar decisões informadas de investimento.

## 🛠️ Funcionalidades

### Interface Interativa
- **Seleção de Ativos**: Escolha múltipla de criptomoedas ou FIIs
- **Filtros de Sinal**: Compra, Venda ou Espera
- **Visualização em Tempo Real**: Atualização automática de dados
- **Layout Responsivo**: Interface adaptável a diferentes telas

### Análise de Sinais
- **Geração Automática**: Algoritmos de análise técnica
- **Múltiplos Timeframes**: Análise em diferentes períodos
- **Indicadores Técnicos**: RSI, MACD, Médias Móveis
- **Alertas Visuais**: Destaque para sinais importantes

### Componentes Modulares
- **Tabela Dinâmica**: Exibição organizada de dados
- **Gráficos Interativos**: Visualização com Plotly
- **Barra de Progresso**: Feedback visual do carregamento
- **Sidebar Configurável**: Controles laterais intuitivos

## 📁 Estrutura do Projeto
```
Dashboard/
├── src/
│   ├── app.py                  # Aplicação principal Streamlit
│   ├── assets_cryptos.py       # Lista de criptomoedas
│   ├── assets_fiis.py          # Lista de FIIs
│   ├── components/
│   │   ├── tabela.py           # Componente de tabela
│   │   └── grafico.py          # Componente de gráfico
│   └── utils/
│       ├── fetch_data.py       # Coleta de dados
│       └── generate_signal.py  # Geração de sinais
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração dos Ativos
Escolha entre criptomoedas ou FIIs editando o import em `app.py`:
```python
# Para criptomoedas
from assets_cryptos import stock, stock_names

# Para FIIs
# from assets_fiis import stock, stock_names
```

### 3. Execução do Dashboard
```bash
cd src
streamlit run app.py
```

### 4. Navegação na Interface
1. **Sidebar**: Selecione ativos e filtros
2. **Área Principal**: Visualize tabelas e gráficos
3. **Filtros**: Use os controles para personalizar a view
4. **Atualização**: Dados são atualizados automaticamente

## 📊 Funcionalidades do Dashboard

### Seleção de Ativos
```python
selected_cryptos = st.sidebar.multiselect(
    "Selecione os ativos", 
    options=stock, 
    default=stock
)
```

### Filtros de Sinal
```python
signal_filter = st.sidebar.multiselect(
    "Filtrar por sinal",
    options=["Compra", "Venda", "Espera"],
    default=["Compra", "Venda", "Espera"]
)
```

### Barra de Progresso
- Feedback visual durante carregamento
- Atualização em tempo real
- Indicação de progresso por ativo

## 🔧 Principais Dependências
- `streamlit`: Framework web para Python
- `pandas`: Manipulação de dados
- `plotly`: Gráficos interativos
- `yfinance`: Dados financeiros (implícito)

## 📈 Componentes Personalizados

### Componente Tabela (`components/tabela.py`)
- Exibição organizada de dados
- Formatação automática de valores
- Ordenação e filtros integrados
- Destaque para sinais importantes

### Componente Gráfico (`components/grafico.py`)
- Gráficos de candlestick
- Indicadores técnicos sobrepostos
- Zoom e pan interativos
- Múltiplos timeframes

### Utils de Dados (`utils/`)
- **fetch_data.py**: Coleta dados de diferentes fontes
- **generate_signal.py**: Algoritmos de geração de sinais

## ⚙️ Configurações

### Layout da Página
```python
st.set_page_config(
    page_title="Dashboard", 
    layout="wide"
)
```

### Títulos e Headers
```python
st.title("Dashboard de Sinais")
st.sidebar.header("Configurações")
```

## 📊 Sinais Disponíveis

### Tipos de Sinal
- **Compra**: Indicação de entrada long
- **Venda**: Indicação de entrada short
- **Espera**: Manter posição atual

### Algoritmos de Geração
- Análise de tendência
- Divergências de indicadores
- Padrões de candlestick
- Volume e momentum

## 🎨 Interface Visual

### Design Responsivo
- Layout adaptável
- Cores e temas configuráveis
- Ícones e indicadores visuais
- Feedback interativo

### Experiência do Usuário
- Navegação intuitiva
- Loading states claros
- Mensagens de erro amigáveis
- Tooltips explicativos

## 🔄 Fluxo de Dados
1. **Seleção**: Usuário escolhe ativos e filtros
2. **Coleta**: Sistema busca dados atualizados
3. **Processamento**: Geração de sinais automática
4. **Visualização**: Exibição em tabelas e gráficos
5. **Interação**: Usuário explora e analisa resultados

## ⚠️ Considerações
- **Dados em Tempo Real**: Dependem de conectividade
- **Performance**: Muitos ativos podem impactar velocidade
- **Sinais**: São indicativos, não recomendações financeiras
- **Atualização**: Recomenda-se refresh periódico

## 🎯 Casos de Uso
- **Day Trading**: Monitoramento de sinais intraday
- **Swing Trading**: Análise de tendências médio prazo
- **Portfolio Screening**: Varredura de oportunidades
- **Educação**: Aprendizado de análise técnica

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novos tipos de gráficos
- Indicadores técnicos adicionais
- Integração com APIs de exchanges
- Melhorias na UX/UI

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.