"""
Backtest Page Layout
Layout estático da página de backtesting
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def get_layout() -> html.Div:
    """
    Retorna o layout da página Backtest
    
    Returns:
        html.Div: Container com layout completo
    """
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("🔄 Backtesting de Estratégias", className="mb-1"),
                html.P(
                    "Simule e avalie estratégias em períodos históricos específicos",
                    className="text-muted"
                )
            ])
        ], className="mb-4"),
        
        # Configuration Panel
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("⚙️ Configuração do Backtest", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # Strategy Selector
                            dbc.Col([
                                html.Label("Estratégia:", className="fw-bold"),
                                dcc.Dropdown(
                                    id='backtest-strategy-selector',
                                    placeholder="Selecione uma estratégia...",
                                    className="mb-3"
                                )
                            ], width=12, md=4),
                            
                            # Date Range
                            dbc.Col([
                                html.Label("Data Inicial:", className="fw-bold"),
                                dcc.DatePickerSingle(
                                    id='backtest-start-date',
                                    display_format='DD/MM/YYYY',
                                    className="mb-3"
                                )
                            ], width=12, md=4),
                            
                            dbc.Col([
                                html.Label("Data Final:", className="fw-bold"),
                                dcc.DatePickerSingle(
                                    id='backtest-end-date',
                                    display_format='DD/MM/YYYY',
                                    className="mb-3"
                                )
                            ], width=12, md=4)
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Capital Inicial (USDT):", className="fw-bold"),
                                dbc.Input(
                                    id='backtest-initial-capital',
                                    type='number',
                                    value=10000,
                                    min=1000,
                                    step=1000,
                                    className="mb-3"
                                )
                            ], width=12, md=6),
                            
                            dbc.Col([
                                dbc.Button(
                                    "▶️ Executar Backtest",
                                    id="backtest-run-button",
                                    color="primary",
                                    size="lg",
                                    className="w-100 mt-4"
                                )
                            ], width=12, md=6)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        
        # Loading Spinner
        dcc.Loading(
            id="backtest-loading",
            type="default",
            children=[
                # Results Summary
                html.Div(id='backtest-summary', className="mb-4"),
                
                # Performance Metrics
                html.Div(id='backtest-metrics', className="mb-4"),
                
                # Charts
                html.Div(id='backtest-charts', className="mb-4"),
                
                # Trade Details Table
                html.Div(id='backtest-trade-details', className="mb-4"),
                
                # Period Comparison
                html.Div(id='backtest-period-comparison')
            ]
        ),
        
        # Hidden stores
        dcc.Store(id='backtest-results-store')
        
    ], className="container-fluid p-4")


# Export layout
layout = get_layout()
