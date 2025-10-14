"""
Main Application Entry Point
Aplicação Dash seguindo padrão MVC
"""
import sys
from pathlib import Path

# Adicionar raiz do projeto ao PATH se necessário
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import dash
from dash import dcc, html
from src.webapp.controllers.dashboard_controller import DashboardController


# Configurações - Caminho atualizado para outputs
CSV_PATH = 'src/ml/outputs/capital_history-BTCUSDT.csv'

# Inicializar Controller
controller = DashboardController(CSV_PATH)
controller.initialize_data()

# Obter componentes do layout
header, description, metrics_panel = controller.get_layout_components()

# Obter gráficos
fig_capital, fig_previsao, fig_trades = controller.get_charts()

# Criar aplicação Dash
app = dash.Dash(__name__)
app.title = "Trading Bot Dashboard"

# Definir layout com Tabs
app.layout = html.Div(
    children=[
        # Header
        header,
        
        # Descrição
        description,
        
        # Tabs Navigation
        html.Div([
            dcc.Tabs(
                id='tabs-navigation',
                value='tab-estrategia',
                children=[
                    dcc.Tab(
                        label='📊 Estratégia',
                        value='tab-estrategia',
                        style={'padding': '10px', 'fontWeight': 'bold'},
                        selected_style={'padding': '10px', 'fontWeight': 'bold', 
                                      'backgroundColor': '#3498db', 'color': 'white'}
                    ),
                    dcc.Tab(
                        label='💰 Resultados',
                        value='tab-resultados',
                        style={'padding': '10px', 'fontWeight': 'bold'},
                        selected_style={'padding': '10px', 'fontWeight': 'bold',
                                      'backgroundColor': '#27ae60', 'color': 'white'}
                    ),
                    dcc.Tab(
                        label='📈 Gráficos',
                        value='tab-graficos',
                        style={'padding': '10px', 'fontWeight': 'bold'},
                        selected_style={'padding': '10px', 'fontWeight': 'bold',
                                      'backgroundColor': '#e74c3c', 'color': 'white'}
                    ),
                ],
                style={'marginTop': '20px', 'marginBottom': '20px'}
            ),
            
            # Conteúdo das Tabs
            html.Div(id='tabs-content')
        ]),
        
        # Footer
        html.Div(
            children=[
                html.Hr(),
                html.P(
                    '🤖 Sistema de Trading Automatizado com LSTM Neural Network | '
                    'Desenvolvido seguindo padrão MVC (Model-View-Controller)',
                    style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '30px'}
                ),
            ]
        )
    ],
    style={'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'}
)


# Callback para renderizar conteúdo das tabs
@app.callback(
    dash.dependencies.Output('tabs-content', 'children'),
    [dash.dependencies.Input('tabs-navigation', 'value')]
)
def render_tab_content(tab):
    """Renderiza o conteúdo de cada tab"""
    
    if tab == 'tab-estrategia':
        # TAB 1: ESTRATÉGIA
        return html.Div([
            html.H2('📊 Estratégia de Trading', 
                    style={'color': '#3498db', 'marginBottom': '20px'}),
            
            html.Div([
                # Descrição da Estratégia
                html.Div([
                    html.H3('🎯 Estratégia Vencedora: Agressiva TP 3% 🏆'),
                    html.Div([
                        html.P('🥇 Campeã entre 6 estratégias testadas com +27.90% de retorno!', 
                               style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#27ae60', 'marginBottom': '15px'}),
                    ]),
                    html.P([
                        html.Strong('Tipo: '), 'Trading Algorítmico com LSTM Neural Network',
                        html.Br(),
                        html.Strong('Modelo: '), 'Long Short-Term Memory (LSTM) - 2 camadas, 64 units',
                        html.Br(),
                        html.Strong('Features: '), '6 indicadores (Open, High, Low, Close, SMA_20, EMA_20)',
                        html.Br(),
                        html.Strong('Targets: '), 'Close, High, Low',
                        html.Br(),
                        html.Strong('Período de Análise: '), '60 períodos (30 horas)',
                        html.Br(),
                        html.Strong('Performance: '), 'Retorno de 27.90% em 104 dias (137.35% anualizado)',
                    ], style={'fontSize': '16px', 'lineHeight': '2'}),
                ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 
                         'borderRadius': '10px', 'marginBottom': '20px'}),
                
                # Sinais de Entrada/Saída
                html.Div([
                    html.H3('🎲 Sinais de Entrada e Saída'),
                    html.Div([
                        html.Div([
                            html.H4('🟢 COMPRA (Entrada)', style={'color': '#27ae60'}),
                            html.Ul([
                                html.Li('Previsão do modelo > Preço atual'),
                                html.Li('Desvio de previsão > 0.5% (threshold)'),
                                html.Li('Sem posição aberta'),
                                html.Li('Capital disponível suficiente'),
                            ]),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top',
                                 'backgroundColor': '#d5f4e6', 'padding': '15px', 'borderRadius': '8px'}),
                        
                        html.Div([
                            html.H4('🔴 VENDA (Saída)', style={'color': '#e74c3c'}),
                            html.Ul([
                                html.Li('Take Profit: +3% de lucro'),
                                html.Li('Stop Loss: -1.5% de prejuízo'),
                                html.Li('Holding mínimo: 48 períodos (24h)'),
                                html.Li('Sinal de reversão do modelo'),
                            ]),
                        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top',
                                 'backgroundColor': '#fadbd8', 'padding': '15px', 'borderRadius': '8px',
                                 'marginLeft': '4%'}),
                    ]),
                ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 
                         'borderRadius': '10px', 'marginBottom': '20px'}),
                
                # Gestão de Risco
                html.Div([
                    html.H3('🛡️ Gestão de Risco'),
                    html.Div([
                        html.Div([
                            html.H5('Capital por Trade:', style={'color': '#2c3e50'}),
                            html.P('95% do capital disponível', style={'fontSize': '18px', 'fontWeight': 'bold'}),
                        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center',
                                 'backgroundColor': '#e8f6f3', 'padding': '15px', 'borderRadius': '8px'}),
                        
                        html.Div([
                            html.H5('Stop Loss:', style={'color': '#e74c3c'}),
                            html.P('-1.5%', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#e74c3c'}),
                        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center',
                                 'backgroundColor': '#fadbd8', 'padding': '15px', 'borderRadius': '8px',
                                 'marginLeft': '3%'}),
                        
                        html.Div([
                            html.H5('Take Profit:', style={'color': '#27ae60'}),
                            html.P('+3.0%', style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#27ae60'}),
                        ], style={'width': '30%', 'display': 'inline-block', 'textAlign': 'center',
                                 'backgroundColor': '#d5f4e6', 'padding': '15px', 'borderRadius': '8px',
                                 'marginLeft': '3%'}),
                    ]),
                ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px'}),
            ])
        ])
    
    elif tab == 'tab-resultados':
        # TAB 2: RESULTADOS
        return html.Div([
            html.H2('💰 Resultados da Estratégia', 
                    style={'color': '#27ae60', 'marginBottom': '20px'}),
            
            # Painel de Métricas
            metrics_panel,
        ])
    
    elif tab == 'tab-graficos':
        # TAB 3: GRÁFICOS
        return html.Div([
            html.H2('📈 Análise Gráfica', 
                    style={'color': '#e74c3c', 'marginBottom': '20px'}),
            
            # Gráfico 1: Evolução do Capital
            controller.create_section_title('1. Evolução do Capital'),
            dcc.Graph(
                id='grafico-capital',
                figure=fig_capital
            ),
            
            # Gráfico 2: Previsão vs Valor Real
            controller.create_section_title('2. Previsões do Modelo vs Valor Real'),
            dcc.Graph(
                id='grafico-previsoes',
                figure=fig_previsao
            ),
            
            # Gráfico 3: Pontos de Entrada e Saída
            controller.create_section_title('3. Pontos de Entrada e Saída'),
            dcc.Graph(
                id='grafico-trades',
                figure=fig_trades
            ),
        ])


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR DASH")
    print("="*70)
    print("📊 Dashboard disponível em: http://127.0.0.1:8050/")
    print("="*70 + "\n")
    
    app.run(debug=True)
