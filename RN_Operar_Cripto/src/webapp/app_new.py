"""
Trading Bot Dashboard - Modular Architecture
Aplicação Dash com arquitetura modular (Angular-like)
"""
import sys
from pathlib import Path

# Adicionar raiz do projeto ao PATH
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Importar páginas e componentes
from src.webapp.modules.dashboard.pages import (
    overview_page, overview_component,
    backtest_page, backtest_component,
    comparison_page, comparison_component
)
from src.webapp.shared.config import AppConfig


# Configuração
config = AppConfig()

# Criar aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Trading Bot Dashboard"
)

# Layout principal
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🤖 Trading Bot Dashboard", className="display-4 mb-2"),
                html.P(
                    "Sistema de análise e monitoramento de estratégias de trading com Machine Learning",
                    className="lead text-muted"
                )
            ], className="text-center py-4 mb-4 border-bottom")
        ])
    ]),
    
    # Navigation Tabs
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(
                    overview_page.layout,
                    label="📊 Visão Geral",
                    tab_id="tab-overview",
                    active_label_class_name="fw-bold text-primary"
                ),
                dbc.Tab(
                    backtest_page.layout,
                    label="🔄 Backtest",
                    tab_id="tab-backtest",
                    active_label_class_name="fw-bold text-primary"
                ),
                dbc.Tab(
                    comparison_page.layout,
                    label="📊 Comparação",
                    tab_id="tab-comparison",
                    active_label_class_name="fw-bold text-primary"
                )
            ], id="main-tabs", active_tab="tab-overview")
        ])
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Div([
                html.P([
                    "💡 ",
                    html.Strong("Trading Bot Dashboard"),
                    " | Powered by LSTM Neural Networks | ",
                    html.Small("BTC/USDT 30min", className="text-muted")
                ], className="text-center text-muted mb-2"),
                html.P([
                    html.Small("Arquitetura Modular (Angular-like) | SQLite Database | Dash + Plotly", 
                              className="text-muted")
                ], className="text-center")
            ], className="py-3")
        ])
    ])
], fluid=True, className="bg-light min-vh-100")


# Registrar callbacks das páginas
overview_component.register_callbacks(app)
backtest_component.register_callbacks(app)
comparison_component.register_callbacks(app)


# Executar servidor
if __name__ == '__main__':
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║       🤖 TRADING BOT DASHBOARD - MODULAR ARCHITECTURE   ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Server: http://{config.HOST}:{config.PORT}                        ║
    ║  Debug Mode: {config.DEBUG}                                   ║
    ║  Database: data/trading_bot.db                           ║
    ║  Architecture: Modular (Angular-like)                    ║
    ╠══════════════════════════════════════════════════════════╣
    ║  📊 Pages:                                               ║
    ║     - Visão Geral (Overview) ✅                          ║
    ║     - Backtest ✅                                        ║
    ║     - Comparação ✅                                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
