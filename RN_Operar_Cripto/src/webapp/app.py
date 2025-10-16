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
                    dcc.Tab(
                        label='📉 Análise Avançada',
                        value='tab-analise-avancada',
                        style={'padding': '10px', 'fontWeight': 'bold'},
                        selected_style={'padding': '10px', 'fontWeight': 'bold',
                                      'backgroundColor': '#9b59b6', 'color': 'white'}
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
    print(f"\n🔍 [DEBUG Callback] render_tab_content chamado com tab='{tab}'\n")
    
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
        # Obter gráficos dinamicamente dentro do callback
        fig_capital, fig_previsao, fig_trades = controller.get_charts()
        
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
    
    elif tab == 'tab-analise-avancada':
        # TAB 4: ANÁLISE AVANÇADA
        # Obter gráficos avançados dinamicamente
        advanced_charts = controller.get_advanced_charts()
        
        return html.Div([
            html.H2('📉 Análise Avançada de Performance', 
                    style={'color': '#9b59b6', 'marginBottom': '20px'}),
            
            html.P([
                '🔍 Esta seção oferece análises aprofundadas para diagnosticar problemas ',
                'e identificar oportunidades de melhoria no modelo e na estratégia.'
            ], style={'fontSize': '16px', 'marginBottom': '30px', 'color': '#7f8c8d'}),
            
            # Seção 1: Análise de Risco
            html.Div([
                html.H3('💀 Análise de Risco', style={'color': '#e74c3c', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Drawdown: '), 
                    'Mede o quanto o capital caiu desde o pico anterior. ',
                    'Drawdowns profundos (>20%) indicam risco elevado. ',
                    'Meta: Manter abaixo de 15%.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('1. Drawdown - Queda desde o Pico'),
                dcc.Graph(
                    id='grafico-drawdown',
                    figure=advanced_charts['drawdown']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Seção 2: Qualidade das Previsões
            html.Div([
                html.H3('🎯 Qualidade das Previsões do LSTM', style={'color': '#3498db', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Erro de Previsão: '), 
                    'Se o modelo sempre prevê valores ACIMA do real (erro positivo), ',
                    'há BIAS de otimismo. Se sempre prevê ABAIXO (erro negativo), é pessimista. ',
                    'Meta: Erro próximo de zero com baixa dispersão.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('2. Erro de Previsão (Previsão - Real)'),
                dcc.Graph(
                    id='grafico-prediction-error',
                    figure=advanced_charts['prediction_error']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Seção 3: Distribuição de Resultados
            html.Div([
                html.H3('📊 Distribuição de Ganhos e Perdas', style={'color': '#27ae60', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Win/Loss Distribution: '), 
                    'Mostra quantos trades tiveram X% de lucro/prejuízo. ',
                    'Ideal: Ganhos maiores que perdas (assimetria positiva). ',
                    'Problemas: Se perdas são maiores que ganhos em média.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('3. Histograma de Ganhos vs Perdas'),
                dcc.Graph(
                    id='grafico-win-loss',
                    figure=advanced_charts['win_loss_dist']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Seção 4: Retornos Cumulativos
            html.Div([
                html.H3('📈 Retornos Cumulativos', style={'color': '#16a085', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Retorno Acumulado (%): '), 
                    'Visualiza o crescimento percentual do capital desde o início. ',
                    'Ideal: Curva suave ascendente. ',
                    'Problemas: Longos períodos planos ou quedas acentuadas.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('4. Evolução do Retorno Percentual'),
                dcc.Graph(
                    id='grafico-cumulative-returns',
                    figure=advanced_charts['cumulative_returns']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Seção 5: Sharpe Ratio Móvel
            html.Div([
                html.H3('⚡ Sharpe Ratio Móvel', style={'color': '#9b59b6', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Sharpe Ratio: '), 
                    'Mede retorno ajustado ao risco. Sharpe > 1 = Bom, > 2 = Excelente, < 0 = Ruim. ',
                    'Se oscila muito, a estratégia é inconsistente. ',
                    'Meta: Manter acima de 1.0 consistentemente.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('5. Sharpe Ratio ao Longo do Tempo'),
                dcc.Graph(
                    id='grafico-rolling-sharpe',
                    figure=advanced_charts['rolling_sharpe']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
            
            # Seção 6: Heatmap Mensal
            html.Div([
                html.H3('🔥 Performance Mensal', style={'color': '#e67e22', 'marginTop': '30px'}),
                html.P([
                    html.Strong('Heatmap Mensal: '), 
                    'Identifica meses problemáticos (vermelho) e lucrativos (verde). ',
                    'Útil para detectar sazonalidade ou períodos de mercado desfavoráveis.'
                ], style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                
                controller.create_section_title('6. Retornos por Mês/Ano'),
                dcc.Graph(
                    id='grafico-monthly-heatmap',
                    figure=advanced_charts['monthly_heatmap']
                ),
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                     'borderRadius': '10px', 'marginBottom': '30px'}),
        ])


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR DASH")
    print("="*70)
    print("📊 Dashboard disponível em: http://127.0.0.1:8050/")
    print("="*70 + "\n")
    
    app.run(debug=True)
