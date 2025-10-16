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
                🎯 Taxa de Acerto Geral: {metricas["taxa_acerto_geral"]:.1f}% ({metricas["trades_lucro"]} trades lucrativos)
                📊 Compras: {metricas["taxa_acerto_compra"]:.1f}% | Vendas: {metricas["taxa_acerto_venda"]:.1f}%
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
            
            # Análise de Acurácia Geral
            html.H4('🎯 Análise de Acurácia dos Trades:', 
                    style={'marginTop': '20px', 'color': '#34495e'}),
            html.Div([
                html.P(f'✅ Trades Lucrativos: {metricas["trades_lucro"]} ({metricas["taxa_acerto_geral"]:.1f}%)', 
                       style={'color': '#27ae60', 'fontWeight': 'bold', 'fontSize': '18px'}),
                html.P(f'❌ Trades com Prejuízo: {metricas["trades_prejuizo"]} ({100-metricas["taxa_acerto_geral"]:.1f}%)', 
                       style={'color': '#e74c3c', 'fontWeight': 'bold', 'fontSize': '18px'}),
                html.P(f'📊 Taxa de Acerto Geral: {metricas["taxa_acerto_geral"]:.1f}%', 
                       style={'color': '#3498db', 'fontWeight': 'bold', 'fontSize': '22px', 
                              'backgroundColor': '#ecf0f1', 'padding': '10px', 'borderRadius': '5px',
                              'textAlign': 'center', 'marginTop': '10px'}),
            ]),
            
            html.Hr(),
            
            # Nova seção: Análise de Acurácia por Operação
            html.H4('📊 Análise Detalhada: Acertos por Tipo de Operação', 
                    style={'marginTop': '20px', 'color': '#2c3e50'}),
            
            html.Div([
                # Acertos nas COMPRAS
                html.Div([
                    html.H5('🟢 DECISÕES DE COMPRA:', 
                            style={'color': '#16a085', 'marginBottom': '10px'}),
                    html.P(f'✅ Compras Acertadas: {metricas["acertos_compra"]}', 
                           style={'color': '#27ae60', 'fontSize': '16px', 'marginLeft': '20px'}),
                    html.P(f'   (Comprou e o preço subiu)', 
                           style={'color': '#7f8c8d', 'fontSize': '14px', 'marginLeft': '20px', 'fontStyle': 'italic'}),
                    html.P(f'❌ Compras Erradas: {metricas["erros_compra"]}', 
                           style={'color': '#e74c3c', 'fontSize': '16px', 'marginLeft': '20px'}),
                    html.P(f'   (Comprou mas o preço caiu)', 
                           style={'color': '#7f8c8d', 'fontSize': '14px', 'marginLeft': '20px', 'fontStyle': 'italic'}),
                    html.P(f'🎯 Taxa de Acerto nas Compras: {metricas["taxa_acerto_compra"]:.1f}%', 
                           style={'color': '#16a085', 'fontWeight': 'bold', 'fontSize': '18px',
                                  'backgroundColor': '#d5f4e6', 'padding': '8px', 'borderRadius': '5px',
                                  'marginLeft': '20px', 'marginTop': '10px'}),
                ], style={'marginBottom': '20px', 'padding': '15px', 
                         'border': '2px solid #16a085', 'borderRadius': '8px',
                         'backgroundColor': '#f0fdf7'}),
                
                # Acertos nas VENDAS
                html.Div([
                    html.H5('🔴 DECISÕES DE VENDA:', 
                            style={'color': '#c0392b', 'marginBottom': '10px'}),
                    html.P(f'✅ Vendas Acertadas: {metricas["acertos_venda"]}', 
                           style={'color': '#27ae60', 'fontSize': '16px', 'marginLeft': '20px'}),
                    html.P(f'   (Vendeu e o preço caiu depois)', 
                           style={'color': '#7f8c8d', 'fontSize': '14px', 'marginLeft': '20px', 'fontStyle': 'italic'}),
                    html.P(f'❌ Vendas Erradas: {metricas["erros_venda"]}', 
                           style={'color': '#e74c3c', 'fontSize': '16px', 'marginLeft': '20px'}),
                    html.P(f'   (Vendeu mas o preço continuou subindo)', 
                           style={'color': '#7f8c8d', 'fontSize': '14px', 'marginLeft': '20px', 'fontStyle': 'italic'}),
                    html.P(f'🎯 Taxa de Acerto nas Vendas: {metricas["taxa_acerto_venda"]:.1f}%', 
                           style={'color': '#c0392b', 'fontWeight': 'bold', 'fontSize': '18px',
                                  'backgroundColor': '#fadbd8', 'padding': '8px', 'borderRadius': '5px',
                                  'marginLeft': '20px', 'marginTop': '10px'}),
                ], style={'marginBottom': '20px', 'padding': '15px',
                         'border': '2px solid #c0392b', 'borderRadius': '8px',
                         'backgroundColor': '#fef5f4'}),
                
                # Conclusão
                html.Div([
                    html.H5('🎓 CONCLUSÃO:', 
                            style={'color': '#8e44ad', 'marginBottom': '10px'}),
                    html.P(
                        f"O modelo acertou mais nas {'COMPRAS' if metricas['taxa_acerto_compra'] > metricas['taxa_acerto_venda'] else 'VENDAS'} "
                        f"({max(metricas['taxa_acerto_compra'], metricas['taxa_acerto_venda']):.1f}% vs "
                        f"{min(metricas['taxa_acerto_compra'], metricas['taxa_acerto_venda']):.1f}%)",
                        style={'fontSize': '16px', 'fontWeight': 'bold', 'color': '#2c3e50',
                               'backgroundColor': '#f4ecf7', 'padding': '10px', 'borderRadius': '5px',
                               'marginLeft': '20px'}
                    ),
                ], style={'padding': '15px', 'border': '2px solid #8e44ad', 
                         'borderRadius': '8px', 'backgroundColor': '#faf5ff'}),
            ]),
            
            html.Hr(),
            
            html.P('✅ Modelo testado APENAS com dados nunca vistos no treinamento', 
                   style={'color': '#27ae60', 'fontWeight': 'bold', 'marginTop': '15px'}),
                   
        ], style={'padding': '25px', 'backgroundColor': '#e8f5e9', 
                 'borderRadius': '10px', 'margin': '20px 0', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    
    @staticmethod
    def create_insight_card(title: str, message: str, card_type: str = 'info') -> html.Div:
        """
        Cria um card de insight/alerta
        
        Args:
            title: Título do insight
            message: Mensagem do insight
            card_type: Tipo do card ('success', 'warning', 'danger', 'info')
            
        Returns:
            Componente HTML do card
        """
        # Cores por tipo
        colors = {
            'success': {'bg': '#d4edda', 'border': '#28a745', 'text': '#155724', 'icon': '✅'},
            'warning': {'bg': '#fff3cd', 'border': '#ffc107', 'text': '#856404', 'icon': '⚠️'},
            'danger': {'bg': '#f8d7da', 'border': '#dc3545', 'text': '#721c24', 'icon': '❌'},
            'info': {'bg': '#d1ecf1', 'border': '#17a2b8', 'text': '#0c5460', 'icon': '💡'}
        }
        
        color = colors.get(card_type, colors['info'])
        
        return html.Div([
            html.Div([
                html.Span(color['icon'], style={'fontSize': '24px', 'marginRight': '10px'}),
                html.Strong(title, style={'fontSize': '18px'})
            ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'}),
            html.P(message, style={'margin': '0', 'lineHeight': '1.6'})
        ], style={
            'padding': '15px 20px',
            'backgroundColor': color['bg'],
            'border': f'2px solid {color["border"]}',
            'borderRadius': '8px',
            'marginBottom': '15px',
            'color': color['text']
        })
    
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
