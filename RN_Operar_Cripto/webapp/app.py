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
from webapp.controllers.dashboard_controller import DashboardController


# Configurações
CSV_PATH = 'capital_history-BTCUSDT.csv'

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

# Definir layout
app.layout = html.Div(
    children=[
        # Header
        header,
        
        # Descrição
        description,
        
        # Painel de Métricas
        metrics_panel,
        
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


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR DASH")
    print("="*70)
    print("📊 Dashboard disponível em: http://127.0.0.1:8050/")
    print("="*70 + "\n")
    
    app.run(debug=True)
