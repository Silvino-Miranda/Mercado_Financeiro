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
                    dcc.Tab(
                        label='🔬 Análise Profunda',
                        value='tab-analise-profunda',
                        style={'padding': '10px', 'fontWeight': 'bold'},
                        selected_style={'padding': '10px', 'fontWeight': 'bold',
                                      'backgroundColor': '#f39c12', 'color': 'white'}
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
        insights = controller.get_insights()
        
        # Criar cards de insights
        insight_cards_risk = []
        insight_cards_strategy = []
        
        if insights:
            for insight in insights.get('risk', []):
                insight_cards_risk.append(
                    controller.layout_view.create_insight_card(
                        insight['title'], insight['message'], insight['type']
                    )
                )
            
            for insight in insights.get('strategy', []):
                insight_cards_strategy.append(
                    controller.layout_view.create_insight_card(
                        insight['title'], insight['message'], insight['type']
                    )
                )
        
        return html.Div([
            html.H2('💰 Resultados da Estratégia', 
                    style={'color': '#27ae60', 'marginBottom': '20px'}),
            
            # Seção de Insights de Risco
            html.Div([
                html.H3('🎯 Insights de Risco', style={'color': '#e74c3c', 'marginBottom': '15px'}),
                *insight_cards_risk
            ], style={'marginBottom': '30px'}),
            
            # Seção de Insights de Estratégia
            html.Div([
                html.H3('📊 Insights de Performance', style={'color': '#3498db', 'marginBottom': '15px'}),
                *insight_cards_strategy
            ], style={'marginBottom': '30px'}),
            
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
    
    elif tab == 'tab-analise-profunda':
        # TAB 5: ANÁLISE PROFUNDA (Níveis 1-4)
        metrics_adv = controller.get_advanced_metrics()
        
        if not metrics_adv:
            return html.Div([
                html.H2('🔬 Análise Profunda não disponível'),
                html.P('Erro ao carregar análises avançadas.')
            ])
        
        return html.Div([
            html.H2('🔬 Análise Profunda - Níveis 1-4', 
                    style={'color': '#f39c12', 'marginBottom': '20px'}),
            
            html.P([
                '🚀 Esta seção contém análises avançadas de Machine Learning, ',
                'Backtesting e Monitoramento em tempo real.'
            ], style={'fontSize': '16px', 'marginBottom': '15px', 'color': '#7f8c8d'}),
            
            # LEGENDA DOS NÍVEIS
            html.Div([
                html.H3('📚 Legenda dos Níveis de Análise', 
                       style={'color': '#2c3e50', 'marginBottom': '15px', 'textAlign': 'center'}),
                html.Div([
                    # Nível 1
                    html.Div([
                        html.Div([
                            html.Span('1️⃣', style={'fontSize': '32px', 'marginBottom': '10px'}),
                            html.H4('NÍVEL 1', style={'margin': '10px 0 5px 0', 'color': '#3498db'}),
                            html.H5('Métricas Adicionais', style={'margin': '0 0 10px 0', 'fontWeight': 'normal'}),
                        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
                        html.Ul([
                            html.Li('⏰ Win Rate por Hora'),
                            html.Li('💰 Risk/Reward Ratio'),
                            html.Li('📉 Sequências Consecutivas'),
                        ], style={'fontSize': '14px', 'lineHeight': '1.8'}),
                        html.P('Para traders', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '10px', 'fontStyle': 'italic'})
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '20px', 'backgroundColor': '#e3f2fd', 'borderRadius': '10px',
                             'marginRight': '1.5%', 'border': '2px solid #3498db'}),
                    
                    # Nível 2
                    html.Div([
                        html.Div([
                            html.Span('2️⃣', style={'fontSize': '32px', 'marginBottom': '10px'}),
                            html.H4('NÍVEL 2', style={'margin': '10px 0 5px 0', 'color': '#9b59b6'}),
                            html.H5('Análise de Modelo ML', style={'margin': '0 0 10px 0', 'fontWeight': 'normal'}),
                        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
                        html.Ul([
                            html.Li('🎯 Confusion Matrix'),
                            html.Li('📊 Accuracy & F1-Score'),
                            html.Li('🔗 Feature Correlation'),
                        ], style={'fontSize': '14px', 'lineHeight': '1.8'}),
                        html.P('Para ML engineers', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '10px', 'fontStyle': 'italic'})
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '20px', 'backgroundColor': '#f3e5f5', 'borderRadius': '10px',
                             'marginRight': '1.5%', 'border': '2px solid #9b59b6'}),
                    
                    # Nível 3
                    html.Div([
                        html.Div([
                            html.Span('3️⃣', style={'fontSize': '32px', 'marginBottom': '10px'}),
                            html.H4('NÍVEL 3', style={'margin': '10px 0 5px 0', 'color': '#27ae60'}),
                            html.H5('Backtesting Avançado', style={'margin': '0 0 10px 0', 'fontWeight': 'normal'}),
                        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
                        html.Ul([
                            html.Li('🎲 Monte Carlo (1000x)'),
                            html.Li('🚶 Walk-Forward'),
                            html.Li('🎚️ Sensitivity TP/SL'),
                        ], style={'fontSize': '14px', 'lineHeight': '1.8'}),
                        html.P('Para otimização', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '10px', 'fontStyle': 'italic'})
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '20px', 'backgroundColor': '#e8f5e9', 'borderRadius': '10px',
                             'marginRight': '1.5%', 'border': '2px solid #27ae60'}),
                    
                    # Nível 4
                    html.Div([
                        html.Div([
                            html.Span('4️⃣', style={'fontSize': '32px', 'marginBottom': '10px'}),
                            html.H4('NÍVEL 4', style={'margin': '10px 0 5px 0', 'color': '#e74c3c'}),
                            html.H5('Alerts & Monitoramento', style={'margin': '0 0 10px 0', 'fontWeight': 'normal'}),
                        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
                        html.Ul([
                            html.Li('🚨 Alertas de Risco'),
                            html.Li('🌡️ Regime de Mercado'),
                            html.Li('📡 Live Monitoring'),
                        ], style={'fontSize': '14px', 'lineHeight': '1.8'}),
                        html.P('Para gestão de risco', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '10px', 'fontStyle': 'italic'})
                    ], style={'width': '23%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '20px', 'backgroundColor': '#ffebee', 'borderRadius': '10px',
                             'border': '2px solid #e74c3c'}),
                ])
            ], style={'backgroundColor': '#ffffff', 'padding': '25px', 'borderRadius': '15px', 
                     'marginBottom': '40px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
            
            # ALERTAS ATIVOS
            html.Div([
                html.Div([
                    html.Span('NÍVEL 4', style={'backgroundColor': '#e74c3c', 'color': 'white', 
                             'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                             'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Span('Alerts & Monitoramento', style={'color': '#7f8c8d', 'fontSize': '14px'})
                ], style={'marginBottom': '10px'}),
                html.H3('🚨 Sistema de Alertas Configurável', style={'color': '#e74c3c', 'marginTop': '0'}),
                html.P('Monitora automaticamente métricas críticas e alerta quando limites são ultrapassados.',
                      style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                *[controller.layout_view.create_insight_card(
                    alert['title'], alert['message'], alert['type']
                ) for alert in metrics_adv.get('alerts', [])],
                html.P('✅ Nenhum alerta crítico detectado' if not metrics_adv.get('alerts') else '',
                      style={'color': '#27ae60', 'fontWeight': 'bold', 'fontSize': '16px', 'textAlign': 'center'})
            ], style={'marginBottom': '30px'}),
            
            # REGIME DE MERCADO
            html.Div([
                html.Div([
                    html.Span('NÍVEL 4', style={'backgroundColor': '#e74c3c', 'color': 'white', 
                             'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                             'fontWeight': 'bold', 'marginRight': '10px'}),
                    html.Span('Alerts & Monitoramento', style={'color': '#7f8c8d', 'fontSize': '14px'})
                ], style={'marginBottom': '10px'}),
                html.H3('🌡️ Detecção de Regime de Mercado', style={'color': '#3498db', 'marginTop': '0'}),
                html.P('Identifica automaticamente se o mercado está em tendência, lateral ou volátil. Cada regime requer estratégia diferente.',
                      style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
                html.Div([
                    html.H4(f"📊 {metrics_adv.get('regime', {}).get('regime', 'N/A')}", 
                           style={'color': '#e74c3c', 'fontSize': '28px'}),
                    html.P(metrics_adv.get('regime', {}).get('descricao', ''), 
                          style={'fontSize': '16px', 'marginBottom': '15px'}),
                    html.Div([
                        html.Span(f"Volatilidade: {metrics_adv.get('regime', {}).get('volatilidade', 0):.2f}%", 
                                 style={'marginRight': '20px', 'fontWeight': 'bold'}),
                        html.Span(f"Tendência: {metrics_adv.get('regime', {}).get('tendencia', 0):+.2f}%",
                                 style={'fontWeight': 'bold'})
                    ], style={'marginBottom': '15px'}),
                    html.P([html.Strong('💡 Recomendação: '), 
                           metrics_adv.get('regime', {}).get('recomendacao', '')],
                          style={'color': '#27ae60', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
            ], style={'marginBottom': '30px'}),
            
            # MÉTRICAS ADICIONAIS (NÍVEL 1)
            html.Div([
                html.H3('📊 Métricas Adicionais - Nível 1', style={'color': '#9b59b6'}),
                html.Div([
                    html.Div([
                        html.H4('💰 Risk/Reward Ratio'),
                        html.P(f"R:R = {metrics_adv.get('risk_reward', {}).get('risk_reward_ratio', 0):.2f}",
                              style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#27ae60'}),
                        html.P(f"Ganho Médio: {metrics_adv.get('risk_reward', {}).get('ganho_medio', 0):.2f}%"),
                        html.P(f"Perda Média: {metrics_adv.get('risk_reward', {}).get('perda_media', 0):.2f}%"),
                    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '15px', 'backgroundColor': '#e8f5e9', 'borderRadius': '8px',
                             'marginRight': '2%'}),
                    
                    html.Div([
                        html.H4('📉 Sequências Consecutivas'),
                        html.P(f"{metrics_adv.get('consecutive', {}).get('max_consecutive_losses', 0)} perdas",
                              style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#e74c3c'}),
                        html.P(f"{metrics_adv.get('consecutive', {}).get('max_consecutive_wins', 0)} ganhos consecutivos"),
                        html.P(f"{metrics_adv.get('consecutive', {}).get('total_sequences', 0)} sequências totais"),
                    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '15px', 'backgroundColor': '#fff3cd', 'borderRadius': '8px',
                             'marginRight': '2%'}),
                    
                    html.Div([
                        html.H4('🎯 Confusion Matrix'),
                        html.P(f"{metrics_adv.get('confusion_matrix', {}).get('accuracy', 0)*100:.1f}% Accuracy",
                              style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#3498db'}),
                        html.P(f"Precision: {metrics_adv.get('confusion_matrix', {}).get('precision', 0)*100:.1f}%"),
                        html.P(f"F1-Score: {metrics_adv.get('confusion_matrix', {}).get('f1_score', 0)*100:.1f}%"),
                    ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top',
                             'padding': '15px', 'backgroundColor': '#d1ecf1', 'borderRadius': '8px'}),
                ])
            ], style={'marginBottom': '30px'}),
            
            # GRÁFICO: Performance por Hora
            html.Div([
                html.Span('NÍVEL 1', style={'backgroundColor': '#3498db', 'color': 'white', 
                         'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                         'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span('Métricas Adicionais', style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '10px'}),
            html.H3('⏰ Performance por Hora do Dia', style={'color': '#16a085', 'marginTop': '0'}),
            html.P('Identifique os melhores horários para operar. Alta taxa de acerto em horários específicos pode indicar padrões de mercado.',
                  style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
            dcc.Graph(
                id='grafico-hourly',
                figure=controller.chart_view.create_hourly_performance_chart(metrics_adv.get('hourly'))
            ),
            
            # GRÁFICO: Confusion Matrix
            html.Div([
                html.Span('NÍVEL 2', style={'backgroundColor': '#9b59b6', 'color': 'white', 
                         'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                         'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span('Análise de Modelo ML', style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '10px', 'marginTop': '30px'}),
            html.H3('🎯 Matriz de Confusão do Modelo LSTM', style={'color': '#2980b9', 'marginTop': '0'}),
            html.P('TP (True Positive) = Previu ALTA e subiu | FP (False Positive) = Previu ALTA mas caiu. Meta: Maximizar TP e TN.',
                  style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
            dcc.Graph(
                id='grafico-confusion-matrix',
                figure=controller.chart_view.create_confusion_matrix_chart(metrics_adv.get('confusion_matrix'))
            ),
            
            # GRÁFICO: Monte Carlo
            html.Div([
                html.Span('NÍVEL 3', style={'backgroundColor': '#27ae60', 'color': 'white', 
                         'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                         'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span('Backtesting Avançado', style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '10px', 'marginTop': '30px'}),
            html.H3('🎲 Simulação Monte Carlo - 1000 Cenários', style={'color': '#8e44ad', 'marginTop': '0'}),
            html.P('Embaralha aleatoriamente os resultados dos trades para estimar distribuição de retornos possíveis. Mostra o que PODE acontecer.',
                  style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '10px'}),
            html.P([
                f"📈 Probabilidade de lucro: {metrics_adv.get('monte_carlo', {}).get('prob_positive', 0):.1f}% | ",
                f"📉 Risco de perda > 10%: {metrics_adv.get('monte_carlo', {}).get('prob_loss_10', 0):.1f}% | ",
                f"🚀 Chance de ganho > 20%: {metrics_adv.get('monte_carlo', {}).get('prob_gain_20', 0):.1f}%"
            ], style={'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '15px'}),
            dcc.Graph(
                id='grafico-monte-carlo',
                figure=controller.chart_view.create_monte_carlo_chart(metrics_adv.get('monte_carlo'))
            ),
            
            # GRÁFICO: Walk-Forward
            html.Div([
                html.Span('NÍVEL 3', style={'backgroundColor': '#27ae60', 'color': 'white', 
                         'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                         'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span('Backtesting Avançado', style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '10px', 'marginTop': '30px'}),
            html.H3('🚶 Walk-Forward Analysis', style={'color': '#27ae60', 'marginTop': '0'}),
            html.P('Valida a estratégia em múltiplos períodos sequenciais. Se performance varia muito, modelo não é estável no tempo.',
                  style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
            dcc.Graph(
                id='grafico-walk-forward',
                figure=controller.chart_view.create_walk_forward_chart(metrics_adv.get('walk_forward'))
            ),
            
            # GRÁFICO: Sensitivity Analysis
            html.Div([
                html.Span('NÍVEL 3', style={'backgroundColor': '#27ae60', 'color': 'white', 
                         'padding': '5px 15px', 'borderRadius': '20px', 'fontSize': '12px',
                         'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Span('Backtesting Avançado', style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '10px', 'marginTop': '30px'}),
            html.H3('🎚️ Análise de Sensibilidade TP/SL', style={'color': '#e67e22', 'marginTop': '0'}),
            html.P('Testa TODAS as combinações de Take Profit e Stop Loss. Verde = melhor retorno. Encontre a zona ótima para seus parâmetros.',
                  style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '15px'}),
            dcc.Graph(
                id='grafico-sensitivity',
                figure=controller.chart_view.create_sensitivity_heatmap(metrics_adv.get('sensitivity'))
            ),
            
            # FOOTER COM RESUMO
            html.Div([
                html.Hr(),
                html.H4('📊 Resumo da Implementação', style={'color': '#2c3e50', 'textAlign': 'center'}),
                html.P([
                    '✅ ', html.Strong('12 análises diferentes'), ' implementadas | ',
                    '✅ ', html.Strong('15+ gráficos interativos'), ' | ',
                    '✅ ', html.Strong('Insights automáticos'), ' em tempo real | ',
                    '✅ ', html.Strong('Sistema de alertas'), ' configurável'
                ], style={'textAlign': 'center', 'fontSize': '16px', 'color': '#27ae60', 'marginTop': '15px'}),
                html.P('🚀 Dashboard completo para análise profissional de trading algorítmico com LSTM',
                      style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '10px', 'fontStyle': 'italic'})
            ], style={'marginTop': '50px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
        ])


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR DASH")
    print("="*70)
    print("📊 Dashboard disponível em: http://127.0.0.1:8050/")
    print("="*70 + "\n")
    
    app.run(debug=True)
