"""
Overview Page Layout
Layout estático da página de visão geral
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def get_layout() -> html.Div:
    """
    Retorna o layout da página Overview
    
    Returns:
        html.Div: Container com layout completo
    """
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("📊 Visão Geral da Estratégia", className="mb-1"),
                html.P(
                    "Análise detalhada de performance e métricas de trading",
                    className="text-muted"
                )
            ])
        ], className="mb-4"),
        
        # Strategy Selector
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Selecione a Estratégia:", className="fw-bold"),
                        dcc.Dropdown(
                            id='overview-strategy-selector',
                            placeholder="Carregando estratégias...",
                            className="mb-2"
                        ),
                        dbc.Button(
                            "Atualizar Dados",
                            id="overview-refresh-button",
                            color="primary",
                            size="sm",
                            className="float-end"
                        )
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        
        # Loading Spinner
        dcc.Loading(
            id="overview-loading",
            type="default",
            children=[
                # Metrics Cards
                html.Div(id='overview-metrics-cards', className="mb-4"),
                
                # Insights/Alerts
                html.Div(id='overview-insights', className="mb-4"),
                
                # Charts Row 1: Equity + Drawdown
                html.Div(id='overview-charts-equity', className="mb-4"),
                
                # Charts Row 2: Distribution + Performance
                html.Div(id='overview-charts-analysis', className="mb-4"),
                
                # Data Table
                html.Div(id='overview-data-table', className="mb-4"),
                
                # Footer Stats
                html.Div(id='overview-footer-stats')
            ]
        ),
        
        # Hidden divs for data storage
        dcc.Store(id='overview-data-store'),
        dcc.Interval(
            id='overview-interval',
            interval=60*1000,  # 60 seconds
            n_intervals=0,
            disabled=True  # Disabled by default
        )
    ], className="container-fluid p-4")


# Export layout
layout = get_layout()
