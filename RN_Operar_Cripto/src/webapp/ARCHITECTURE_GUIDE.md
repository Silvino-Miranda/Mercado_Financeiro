# 🏗️ Guia de Arquitetura Modular - Trading Bot Dashboard

## ✅ O Que Foi Criado

### 📁 Estrutura de Diretórios
```
src/webapp/
├── modules/                        ✅ CRIADO
│   ├── dashboard/                  
│   │   ├── pages/                  ✅ CRIADO
│   │   ├── components/             ✅ CRIADO
│   │   ├── services/               ✅ CRIADO
│   │   └── repositories/           ✅ CRIADO
│   └── strategies/                 
│       ├── pages/                  ✅ CRIADO
│       ├── components/             ✅ CRIADO
│       ├── services/               ✅ CRIADO
│       └── repositories/           ✅ CRIADO
├── shared/                         ✅ CRIADO
│   ├── config/                     ✅ CRIADO + IMPLEMENTADO
│   │   ├── database_config.py      ✅
│   │   ├── app_config.py           ✅
│   │   └── constants.py            ✅
│   ├── core/                       ✅ CRIADO + IMPLEMENTADO
│   │   ├── database.py             ✅ Singleton DB Connection
│   │   └── base_repository.py     ✅ CRUD Genérico
│   ├── models/                     ✅ CRIADO (vazio)
│   └── utils/                      ✅ CRIADO (vazio)
└── assets/                         ✅ CRIADO
```

### ✅ Arquivos Implementados

1. **shared/config/database_config.py** - Config de banco
2. **shared/config/app_config.py** - Config geral da app
3. **shared/config/constants.py** - Constantes e Enums
4. **shared/core/database.py** - Singleton de conexão SQLite
5. **shared/core/base_repository.py** - Repositório base com CRUD
6. **modules/strategies/repositories/strategy_repository.py** - Repository de estratégias

---

## 🎯 Padrão de Arquitetura

### 📄 Pages vs Components

```python
# ✅ PATTERN: Separar lógica do layout

# overview.component.py (LÓGICA)
class OverviewComponent:
    def __init__(self, strategy_id: int):
        self.strategy_id = strategy_id
        self.service = AnalyticsService()
    
    def load_data(self):
        """Carrega dados da estratégia"""
        return self.service.get_strategy_analytics(self.strategy_id)
    
    def calculate_metrics(self):
        """Calcula métricas"""
        pass

# overview.page.py (LAYOUT/HTML)
from dash import html, dcc
from .overview.component import OverviewComponent

def render(strategy_id: int):
    component = OverviewComponent(strategy_id)
    data = component.load_data()
    
    return html.Div([
        html.H1("Dashboard"),
        dcc.Graph(figure=data['chart']),
        # ... mais layout
    ])
```

### 🧩 Components (Reutilizáveis)

```python
# metrics_card.component.py
def render_metrics_card(title: str, value: str, color: str):
    return html.Div([
        html.H3(title),
        html.P(value, style={'color': color})
    ])
```

### 🔌 Services (APIs Externas)

```python
# backtest.service.py
class BacktestService:
    """Serviço para APIs externas de backtest"""
    
    def __init__(self):
        self.base_url = "https://api.backtest.com"
        self.timeout = 30
    
    def run_backtest(self, strategy_config: dict):
        """Chama API externa para rodar backtest"""
        response = requests.post(
            f"{self.base_url}/backtest",
            json=strategy_config,
            timeout=self.timeout
        )
        return response.json()
```

### 🗄️ Repositories (Banco de Dados)

```python
# trading_history_repository.py
from src.webapp.shared.core.base_repository import BaseRepository

class TradingHistoryRepository(BaseRepository):
    def __init__(self):
        super().__init__('trading_history')
    
    def get_columns(self):
        return ['id', 'strategy_id', 'data', 'operacao', ...]
    
    def find_by_strategy(self, strategy_id: int):
        return self.find_where({'strategy_id': strategy_id})
    
    def get_profitable_trades(self, strategy_id: int):
        query = """
            SELECT * FROM trading_history
            WHERE strategy_id = ? 
            AND retorno_percentual > 0
        """
        return self.execute_raw(query, (strategy_id,))
```

---

## 📋 Plano de Migração

### FASE 1: Repositórios ✅ (EM ANDAMENTO)
- [x] StrategyRepository criado
- [ ] TradingHistoryRepository
- [ ] Migrar database.py antigo → usar novos repositories

### FASE 2: Modelos (Data Classes)
```python
# shared/models/strategy.model.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Strategy:
    id: int
    name: str
    model_type: str
    take_profit: float
    stop_loss: float
    total_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
```

### FASE 3: Services (APIs)
```python
# modules/dashboard/services/analytics.service.py
class AnalyticsService:
    """Processa dados para o dashboard"""
    
    def __init__(self):
        self.strategy_repo = StrategyRepository()
        self.history_repo = TradingHistoryRepository()
    
    def get_strategy_analytics(self, strategy_id: int):
        strategy = self.strategy_repo.find_by_id(strategy_id)
        trades = self.history_repo.find_by_strategy(strategy_id)
        
        return {
            'strategy': strategy,
            'trades': trades,
            'metrics': self._calculate_metrics(trades)
        }
```

### FASE 4: Components (UI)
```python
# modules/dashboard/components/metrics_card.component.py
def render(title: str, value: str, icon: str = "📊"):
    return html.Div([
        html.Span(icon, className="icon"),
        html.H4(title),
        html.P(value, className="metric-value")
    ], className="metrics-card")
```

### FASE 5: Pages (Páginas Completas)
```python
# modules/dashboard/pages/overview.page.py
from dash import html
from ..components import metrics_card, chart_container
from .overview.component import OverviewComponent

def render(strategy_id: int = 1):
    component = OverviewComponent(strategy_id)
    data = component.load_data()
    
    return html.Div([
        html.H1(f"📊 {data['strategy']['name']}"),
        
        html.Div([
            metrics_card.render("Retorno", f"{data['metrics']['return']}%"),
            metrics_card.render("Sharpe", f"{data['metrics']['sharpe']}"),
            metrics_card.render("Drawdown", f"{data['metrics']['drawdown']}%"),
        ], className="metrics-grid"),
        
        chart_container.render(data['charts']['capital']),
    ])
```

### FASE 6: App Principal
```python
# app.py (NOVO)
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from src.webapp.modules.dashboard.pages import overview
from src.webapp.modules.strategies.pages import list as strategies_list
from src.webapp.shared.config import AppConfig

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = AppConfig.SUPPRESS_CALLBACK_EXCEPTIONS

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return overview.render()
    elif pathname == '/strategies':
        return strategies_list.render()
    else:
        return overview.render()  # Default

if __name__ == '__main__':
    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )
```

---

## 🔧 Como Usar os Novos Componentes

### 1. Database Singleton
```python
from src.webapp.shared.core import db

# Executar query
results = db.execute_query("SELECT * FROM strategies")

# Com transação
with db.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
```

### 2. Repositórios
```python
from src.webapp.modules.strategies.repositories import StrategyRepository

repo = StrategyRepository()

# CRUD básico
strategies = repo.find_all()
strategy = repo.find_by_id(1)
new_id = repo.insert({'name': 'Nova', 'model_type': 'LSTM', ...})
repo.update(1, {'total_return': 25.0})
repo.delete(1)

# Métodos específicos
active = repo.find_active()
top = repo.get_top_performers(limit=5)
```

### 3. Configurações
```python
from src.webapp.shared.config import DatabaseConfig, AppConfig, Constants

# Database
db_path = DatabaseConfig.get_db_path()
DatabaseConfig.ensure_directories()

# App
print(f"Running on {AppConfig.HOST}:{AppConfig.PORT}")

# Constants
print(Constants.format_currency(1000))  # $1,000.00
print(Constants.COLOR_PROFIT)  # #27ae60
```

---

## 📝 Próximos Passos

### IMEDIATO
1. ✅ Criar `TradingHistoryRepository`
2. ✅ Criar modelos em `shared/models/`
3. ✅ Migrar lógica de `trading_data_model.py` → Services
4. ✅ Criar componentes de UI reutilizáveis

### CURTO PRAZO
5. ✅ Migrar páginas atuais → estrutura pages/components
6. ✅ Refatorar `app.py` para usar novo routing
7. ✅ Adicionar testes unitários por módulo

### MÉDIO PRAZO
8. ✅ Criar módulo de autenticação (users/)
9. ✅ API REST com FastAPI (opcional)
10. ✅ CI/CD com testes automáticos

---

## 🎨 Convenções de Nomenclatura

### Arquivos
- **Pages**: `nome.page.py` (layout Dash)
- **Components Logic**: `nome.component.py` (lógica)
- **Components UI**: `nome_component.py` (UI reutilizável)
- **Services**: `nome.service.py`
- **Repositories**: `nome_repository.py`
- **Models**: `nome.model.py`

### Classes
- **Components**: `OverviewComponent`
- **Services**: `BacktestService`
- **Repositories**: `StrategyRepository`
- **Models**: `Strategy`, `Trade`

### Funções
- **Render**: `render()`, `render_metrics_card()`
- **CRUD**: `find_all()`, `find_by_id()`, `create()`, `update()`, `delete()`
- **Business Logic**: `calculate_metrics()`, `process_data()`

---

## ⚠️ Importante

### SEMPRE use `uv run`
```bash
uv run src/webapp/app.py
```

### Imports Relativos
```python
# ✅ CORRETO
from src.webapp.shared.config import DatabaseConfig
from src.webapp.modules.strategies.repositories import StrategyRepository

# ❌ ERRADO
from shared.config import DatabaseConfig
from strategies.repositories import StrategyRepository
```

### Injeção de Dependência
```python
# ✅ BOM: Injetar dependências
class OverviewComponent:
    def __init__(self, service: AnalyticsService):
        self.service = service

# ❌ RUIM: Instanciar dentro
class OverviewComponent:
    def __init__(self):
        self.service = AnalyticsService()  # Tight coupling
```

---

## 📚 Referências

- **Arquitetura**: Inspirada em Angular (Modules → Components → Services)
- **Padrões**: Repository Pattern, Service Layer, Dependency Injection
- **Framework**: Dash (Plotly) para UI reativa

---

**Status**: 🚧 EM CONSTRUÇÃO  
**Próximo**: Criar `TradingHistoryRepository` e migrar lógica existente  
**Data**: 16/10/2025
