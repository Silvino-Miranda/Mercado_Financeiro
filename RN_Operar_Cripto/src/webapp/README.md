# 📊 WebApp - Trading Dashboard

Dashboard de análise de trading automatizado seguindo padrão **MVC (Model-View-Controller)**.

## 🏗️ Estrutura do Projeto

```
webapp/
├── __init__.py                          # Package initialization
├── app.py                               # 🚀 MAIN - Ponto de entrada da aplicação
│
├── models/                              # 📊 MODEL - Lógica de dados
│   ├── __init__.py
│   └── trading_data_model.py           # Carregamento e processamento de dados
│
├── views/                               # 🎨 VIEW - Componentes visuais
│   ├── __init__.py
│   ├── chart_view.py                   # Gráficos Plotly
│   └── layout_view.py                  # Componentes HTML/Dash
│
└── controllers/                         # 🎮 CONTROLLER - Lógica de controle
    ├── __init__.py
    └── dashboard_controller.py         # Orquestração Model-View
```

---

## 🎯 Padrão MVC Implementado

### 📊 **MODEL** (`models/`)
**Responsabilidade:** Gerenciar dados e lógica de negócio

- **`TradingDataModel`**: 
  - Carrega dados do CSV
  - Pré-processa dados (conversões, datas)
  - Calcula métricas (retorno, taxa de acerto, etc)
  - Retorna dados processados

**Exemplo:**
```python
model = TradingDataModel('capital_history.csv')
model.load_data()
model.preprocess_data()
metricas = model.calculate_metrics()
```

---

### 🎨 **VIEW** (`views/`)
**Responsabilidade:** Criar componentes visuais (sem lógica de negócio)

- **`ChartView`**: 
  - Cria gráficos Plotly
  - Evolução do capital
  - Previsão vs Real
  - Scatter de trades

- **`LayoutView`**: 
  - Cria componentes HTML/Dash
  - Header, descrição, métricas
  - Seções e títulos

**Exemplo:**
```python
chart_view = ChartView()
fig = chart_view.create_capital_evolution_chart(df)

layout_view = LayoutView()
metrics_panel = layout_view.create_metrics_panel(metricas)
```

---

### 🎮 **CONTROLLER** (`controllers/`)
**Responsabilidade:** Orquestrar Model e View, controlar fluxo

- **`DashboardController`**: 
  - Inicializa Model e Views
  - Orquestra carregamento de dados
  - Coordena criação de componentes
  - Fornece interface unificada

**Exemplo:**
```python
controller = DashboardController('capital_history.csv')
controller.initialize_data()

# Obter tudo de forma coordenada
header, description, metrics = controller.get_layout_components()
charts = controller.get_charts()
```

---

## 🚀 Como Executar

### Opção 1: Via webapp/app.py (Recomendado)
```bash
cd c:\_Dev\Github\Python\Mercado_Financeiro\RN_Operar_Cripto
.venv\Scripts\python.exe webapp\app.py
```

### Opção 2: Via módulo Python
```bash
python -m webapp.app
```

Acesse: **http://127.0.0.1:8050/**

---

## 📈 Funcionalidades

### ✅ Métricas Dinâmicas
Todas as métricas são calculadas automaticamente do CSV:
- Capital inicial e final
- Retorno total e anualizado
- Período de teste
- Total de operações

### 🎯 Análise de Acurácia
Calcula automaticamente:
- ✅ Trades lucrativos
- ❌ Trades com prejuízo  
- 📊 Taxa de acerto (%)

### 📊 Visualizações
1. **Evolução do Capital**: Linha mostrando crescimento
2. **Previsão vs Real**: Comparação das previsões LSTM
3. **Pontos de Entrada/Saída**: Scatter de compras (azul) e vendas (vermelho)

---

## 🔧 Vantagens do Padrão MVC

### ✅ Separação de Responsabilidades
- **Model**: Só cuida dos dados
- **View**: Só cuida da apresentação
- **Controller**: Só cuida da orquestração

### ✅ Manutenibilidade
- Mudanças em gráficos? → Edite apenas `views/chart_view.py`
- Mudanças em cálculos? → Edite apenas `models/trading_data_model.py`
- Mudanças no fluxo? → Edite apenas `controllers/dashboard_controller.py`

### ✅ Testabilidade
Cada componente pode ser testado independentemente:
```python
# Testar model
model = TradingDataModel('test.csv')
assert model.load_data() == True

# Testar view
view = ChartView()
fig = view.create_capital_evolution_chart(df)
assert fig is not None

# Testar controller
controller = DashboardController('test.csv')
assert controller.initialize_data() == True
```

### ✅ Reusabilidade
Componentes podem ser reutilizados em outros projetos:
```python
# Usar o model em outro contexto
from webapp.models import TradingDataModel
model = TradingDataModel('outro_arquivo.csv')

# Usar as views em outro dashboard
from webapp.views import ChartView
chart = ChartView.create_capital_evolution_chart(df)
```

---

## 📝 Exemplo de Fluxo Completo

```python
# 1. Controller inicializa tudo
controller = DashboardController('capital_history.csv')
controller.initialize_data()

# 2. Controller pede dados ao Model
metricas = controller.get_metrics()  # Model calcula e retorna

# 3. Controller pede componentes à View
metrics_panel = controller.layout_view.create_metrics_panel(metricas)

# 4. Controller fornece tudo pronto para o Dash
app.layout = html.Div([metrics_panel, ...])
```

---

## 🎓 Padrão de Design

```
┌─────────────────────────────────────────────────┐
│                   DASH APP                      │
│              (Ponto de entrada)                 │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│              CONTROLLER                         │
│       (Orquestra Model e View)                  │
└──────────┬──────────────────┬───────────────────┘
           │                  │
           ▼                  ▼
    ┌──────────────┐   ┌──────────────┐
    │    MODEL     │   │     VIEW     │
    │   (Dados)    │   │   (Visual)   │
    └──────────────┘   └──────────────┘
```

---

## 📚 Referências

- **MVC Pattern**: https://en.wikipedia.org/wiki/Model–view–controller
- **Dash Framework**: https://dash.plotly.com/
- **Plotly**: https://plotly.com/python/

---

*Desenvolvido seguindo boas práticas de Software Engineering* 🚀
