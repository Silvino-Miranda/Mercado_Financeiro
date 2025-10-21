"""
Comparison Page Layout
Layout estático da página de comparação de estratégias
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def get_layout() -> html.Div:
    """
    Retorna o layout da página Comparison
    
    Returns:
        html.Div: Container com layout completo
    """
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("📊 Comparação de Estratégias", className="mb-1"),
                html.P(
                    "Compare performance e métricas de múltiplas estratégias lado a lado",
                    className="text-muted"
                )
            ])
        ], className="mb-4"),
        
        # Strategy Selection Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🎯 Selecione Estratégias para Comparar", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Estratégias (selecione 2-4):", className="fw-bold"),
                                dcc.Dropdown(
                                    id='comparison-strategy-selector',
                                    placeholder="Selecione estratégias...",
                                    multi=True,
                                    className="mb-3"
                                )
                            ], width=12, md=10),
                            dbc.Col([
                                dbc.Button(
                                    "🔄 Comparar",
                                    id="comparison-compare-button",
                                    color="primary",
                                    className="w-100"
                                )
                            ], width=12, md=2)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        
        # Loading Spinner
        dcc.Loading(
            id="comparison-loading",
            type="default",
            children=[
                # Summary Cards
                html.Div(id='comparison-summary-cards', className="mb-4"),
                
                # Comparison Table
                html.Div(id='comparison-metrics-table', className="mb-4"),
                
                # Charts Grid
                html.Div(id='comparison-charts-grid', className="mb-4"),
                
                # Performance Ranking
                html.Div(id='comparison-ranking', className="mb-4"),
                
                # Insights
                html.Div(id='comparison-insights')
            ]
        ),
        
        # Hidden stores
        dcc.Store(id='comparison-data-store')
        
    ], className="container-fluid p-4")


# Export layout
layout = get_layout()
