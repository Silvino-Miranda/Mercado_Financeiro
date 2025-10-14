"""
View: LayoutView
Responsável por criar o layout HTML do dashboard
"""
from dash import html
from typing import Dict, Optional


class LayoutView:
    """Classe para criar componentes HTML do layout"""
    
    @staticmethod
    def create_header() -> html.Div:
        """
        Cria o cabeçalho do dashboard
        
        Returns:
            Componente HTML do cabeçalho
        """
        return html.H1(
            children='Análise de Previsões - BTC/USDT (30min)',
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}
        )
    
    @staticmethod
    def create_description(metricas: Optional[Dict] = None) -> html.Div:
        """
        Cria a descrição do sistema
        
        Args:
            metricas: Dicionário com métricas calculadas
            
        Returns:
            Componente HTML da descrição
        """
        if metricas:
            texto = f'''
                Sistema de Trading Automatizado com LSTM Neural Network
                Intervalo: 30 minutos | Par: BTC/USDT | Teste: {metricas["data_inicial"]} a {metricas["data_final"]}
                ✅ Retorno de {metricas["retorno_total"]:.2f}% em {metricas["dias"]} dias ({metricas["retorno_anual"]:.2f}% ao ano)
                🎯 Taxa de Acerto: {metricas["taxa_acerto"]:.1f}% ({metricas["trades_lucro"]} trades lucrativos)
            '''
        else:
            texto = 'Sistema de Trading Automatizado com LSTM Neural Network - Carregando dados...'
        
        return html.Div(
            children=texto,
            style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#ecf0f1', 
                   'borderRadius': '10px', 'marginBottom': '20px'}
        )
    
    @staticmethod
    def create_metrics_panel(metricas: Optional[Dict] = None) -> html.Div:
        """
        Cria o painel de métricas
        
        Args:
            metricas: Dicionário com métricas calculadas
            
        Returns:
            Componente HTML do painel de métricas
        """
        if not metricas:
            return html.Div([
                html.H3('⚠️ Erro ao carregar métricas'),
                html.P('Não foi possível calcular as métricas. Verifique o arquivo CSV.'),
            ], style={'padding': '20px', 'backgroundColor': '#ffebee', 
                     'borderRadius': '10px', 'margin': '20px 0'})
        
        return html.Div([
            html.H3('📊 Métricas de Performance (Calculadas Dinamicamente do CSV)'),
            
            # Métricas de Capital
            html.Div([
                html.P(f'💰 Capital Inicial: ${metricas["capital_inicial"]:,.2f}', 
                       style={'fontSize': '16px'}),
                html.P(f'💵 Capital Final: ${metricas["capital_final"]:,.2f}', 
                       style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#27ae60'}),
                html.P(f'📈 Retorno Total: {metricas["retorno_total"]:.2f}%', 
                       style={'fontSize': '16px'}),
                html.P(f'📅 Retorno Anualizado: {metricas["retorno_anual"]:.2f}% ao ano', 
                       style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#2980b9'}),
            ], style={'marginBottom': '15px'}),
            
            # Métricas de Operações
            html.Div([
                html.P(f'🔄 Total de Operações: {metricas["total_ops"]} trades ({metricas["compras"]} compras + {metricas["vendas"]} vendas)', 
                       style={'fontSize': '16px'}),
                html.P(f'⏱️ Período: {metricas["dias"]} dias ({metricas["data_inicial"]} a {metricas["data_final"]})', 
                       style={'fontSize': '16px'}),
            ], style={'marginBottom': '15px'}),
            
            html.Hr(),
            
            # Análise de Acurácia
            html.H4('🎯 Análise de Acurácia dos Trades:', 
                    style={'marginTop': '20px', 'color': '#34495e'}),
            html.Div([
                html.P(f'✅ Trades Lucrativos: {metricas["trades_lucro"]} ({metricas["taxa_acerto"]:.1f}%)', 
                       style={'color': '#27ae60', 'fontWeight': 'bold', 'fontSize': '18px'}),
                html.P(f'❌ Trades com Prejuízo: {metricas["trades_prejuizo"]} ({100-metricas["taxa_acerto"]:.1f}%)', 
                       style={'color': '#e74c3c', 'fontWeight': 'bold', 'fontSize': '18px'}),
                html.P(f'📊 Taxa de Acerto: {metricas["taxa_acerto"]:.1f}%', 
                       style={'color': '#3498db', 'fontWeight': 'bold', 'fontSize': '22px', 
                              'backgroundColor': '#ecf0f1', 'padding': '10px', 'borderRadius': '5px',
                              'textAlign': 'center', 'marginTop': '10px'}),
            ]),
            
            html.Hr(),
            
            html.P('✅ Modelo testado APENAS com dados nunca vistos no treinamento', 
                   style={'color': '#27ae60', 'fontWeight': 'bold', 'marginTop': '15px'}),
                   
        ], style={'padding': '25px', 'backgroundColor': '#e8f5e9', 
                 'borderRadius': '10px', 'margin': '20px 0', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    
    @staticmethod
    def create_section_title(title: str) -> html.H2:
        """
        Cria um título de seção
        
        Args:
            title: Texto do título
            
        Returns:
            Componente HTML do título
        """
        return html.H2(
            children=title,
            style={'color': '#2c3e50', 'marginTop': '30px', 'marginBottom': '15px'}
        )
