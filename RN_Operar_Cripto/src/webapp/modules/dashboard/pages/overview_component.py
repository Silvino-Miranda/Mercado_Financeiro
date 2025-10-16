"""
Overview Component
Lógica de negócio e callbacks da página Overview
"""
from dash import callback, Output, Input, State, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any, List

from src.webapp.modules.dashboard.services import AnalyticsService
from src.webapp.modules.dashboard.components import (
    metrics_row, chart_container, dual_chart_container, info_alert
)
from src.webapp.modules.strategies.repositories import StrategyRepository
from src.webapp.shared.config import Constants


class OverviewComponent:
    """Componente de lógica para página Overview"""
    
    def __init__(self):
        """Inicializa serviços"""
        self.analytics_service = AnalyticsService()
        self.strategy_repo = StrategyRepository()
    
    def register_callbacks(self, app):
        """
        Registra todos os callbacks da página
        
        Args:
            app: Instância do Dash app
        """
        
        @app.callback(
            Output('overview-strategy-selector', 'options'),
            Output('overview-strategy-selector', 'value'),
            Input('overview-strategy-selector', 'id')
        )
        def load_strategies(_):
            """Carrega lista de estratégias"""
            strategies = self.strategy_repo.find_active()
            
            if not strategies:
                return [], None
            
            options = [
                {'label': f"{s['name']} ({s['model_type']})", 'value': s['id']}
                for s in strategies
            ]
            
            # Seleciona a primeira por padrão
            default_value = strategies[0]['id'] if strategies else None
            
            return options, default_value
        
        @app.callback(
            Output('overview-metrics-cards', 'children'),
            Output('overview-insights', 'children'),
            Output('overview-charts-equity', 'children'),
            Output('overview-charts-analysis', 'children'),
            Output('overview-data-table', 'children'),
            Output('overview-footer-stats', 'children'),
            Input('overview-strategy-selector', 'value'),
            Input('overview-refresh-button', 'n_clicks'),
            prevent_initial_call=False
        )
        def update_overview(strategy_id: Optional[int], n_clicks: int):
            """
            Atualiza todos os componentes da página
            
            Args:
                strategy_id: ID da estratégia selecionada
                n_clicks: Cliques no botão refresh
                
            Returns:
                Tuple com todos os componentes atualizados
            """
            if not strategy_id:
                empty = html.Div("Selecione uma estratégia", className="text-muted text-center p-5")
                return empty, None, None, None, None, None
            
            try:
                # Carregar dados completos
                overview = self.analytics_service.get_strategy_overview(strategy_id)
                strategy = overview['strategy']
                trades = overview['trades']
                metrics = overview['metrics']
                insights = overview['insights']
                
                # 1. Metrics Cards
                metrics_cards = self._create_metrics_cards(metrics)
                
                # 2. Insights/Alerts
                insights_div = self._create_insights(insights)
                
                # 3. Equity & Drawdown Charts
                equity_charts = self._create_equity_charts(trades)
                
                # 4. Analysis Charts (Distribution + Performance)
                analysis_charts = self._create_analysis_charts(trades, metrics)
                
                # 5. Data Table
                data_table = self._create_data_table(trades)
                
                # 6. Footer Stats
                footer_stats = self._create_footer_stats(strategy, metrics)
                
                return (
                    metrics_cards,
                    insights_div,
                    equity_charts,
                    analysis_charts,
                    data_table,
                    footer_stats
                )
                
            except Exception as e:
                error_msg = info_alert(
                    message=f"Erro ao carregar dados: {str(e)}",
                    alert_type="danger",
                    title="❌ Erro"
                )
                return error_msg, None, None, None, None, None
    
    def _create_metrics_cards(self, metrics: Dict[str, Any]) -> html.Div:
        """Cria cards de métricas principais"""
        cards_data = [
            {
                'title': 'Capital Inicial',
                'value': Constants.format_currency(metrics.get('capital_inicial', 0)),
                'icon': '💰',
                'color': 'secondary'
            },
            {
                'title': 'Capital Final',
                'value': Constants.format_currency(metrics.get('capital_final', 0)),
                'icon': '🎯',
                'color': 'success' if metrics.get('retorno_total', 0) > 0 else 'danger'
            },
            {
                'title': 'Retorno Total',
                'value': Constants.format_percentage(metrics.get('retorno_total', 0)),
                'icon': '📈',
                'color': 'success' if metrics.get('retorno_total', 0) > 0 else 'danger',
                'subtitle': f"Retorno Anual: {Constants.format_percentage(metrics.get('retorno_anual', 0))}"
            },
            {
                'title': 'Win Rate',
                'value': Constants.format_percentage(metrics.get('win_rate', 0)),
                'icon': '🎲',
                'color': 'success' if metrics.get('win_rate', 0) >= Constants.GOOD_WIN_RATE else 'warning'
            },
            {
                'title': 'Sharpe Ratio',
                'value': f"{metrics.get('sharpe_ratio', 0):.2f}",
                'icon': '📊',
                'color': 'success' if metrics.get('sharpe_ratio', 0) >= Constants.GOOD_SHARPE_RATIO else 'warning'
            },
            {
                'title': 'Max Drawdown',
                'value': Constants.format_percentage(metrics.get('max_drawdown', 0)),
                'icon': '📉',
                'color': 'danger' if abs(metrics.get('max_drawdown', 0)) > 20 else 'warning'
            },
            {
                'title': 'Total Operações',
                'value': str(metrics.get('total_operacoes', 0)),
                'icon': '🔄',
                'color': 'info',
                'subtitle': f"{metrics.get('total_compras', 0)} compras | {metrics.get('total_vendas', 0)} vendas"
            },
            {
                'title': 'Período',
                'value': f"{metrics.get('dias_operacao', 0)} dias",
                'icon': '📅',
                'color': 'info',
                'subtitle': f"{metrics.get('data_inicial', '')} até {metrics.get('data_final', '')}"
            }
        ]
        
        return metrics_row(cards_data)
    
    def _create_insights(self, insights: List[Dict[str, str]]) -> html.Div:
        """Cria alertas de insights"""
        if not insights:
            return None
        
        type_map = {
            'success': 'success',
            'warning': 'warning',
            'danger': 'danger',
            'info': 'info'
        }
        
        alerts = [
            info_alert(
                message=insight['message'],
                alert_type=type_map.get(insight['type'], 'info'),
                title=insight['title'],
                dismissible=True
            )
            for insight in insights
        ]
        
        return html.Div(alerts)
    
    def _create_equity_charts(self, trades: List) -> html.Div:
        """Cria gráficos de Equity Curve e Drawdown"""
        if not trades:
            return None
        
        df = pd.DataFrame([t.to_dict() for t in trades])
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        
        # Equity Curve
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=df['data'],
            y=df['capital'],
            mode='lines',
            name='Capital',
            line=dict(color=Constants.COLOR_PROFIT, width=2),
            fill='tozeroy',
            fillcolor='rgba(39, 174, 96, 0.1)'
        ))
        fig_equity.update_layout(
            title="Curva de Equity",
            xaxis_title="Data",
            yaxis_title="Capital (USDT)",
            hovermode='x unified'
        )
        
        # Drawdown
        df['peak'] = df['capital'].cummax()
        df['drawdown'] = ((df['capital'] - df['peak']) / df['peak']) * 100
        
        fig_drawdown = go.Figure()
        fig_drawdown.add_trace(go.Scatter(
            x=df['data'],
            y=df['drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color=Constants.COLOR_LOSS, width=2),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
        fig_drawdown.update_layout(
            title="Drawdown",
            xaxis_title="Data",
            yaxis_title="Drawdown (%)",
            hovermode='x unified'
        )
        
        return dual_chart_container(
            left_figure=fig_equity,
            right_figure=fig_drawdown,
            left_title="📈 Evolução do Capital",
            right_title="📉 Análise de Drawdown",
            height=400
        )
    
    def _create_analysis_charts(self, trades: List, metrics: Dict[str, Any]) -> html.Div:
        """Cria gráficos de análise (distribuição e performance)"""
        if not trades:
            return None
        
        df = pd.DataFrame([t.to_dict() for t in trades])
        
        # Distribuição de Operações
        ops_count = df['operacao'].value_counts()
        fig_ops = go.Figure(data=[
            go.Pie(
                labels=ops_count.index,
                values=ops_count.values,
                marker=dict(colors=[Constants.COLOR_PROFIT, Constants.COLOR_LOSS])
            )
        ])
        fig_ops.update_layout(title="Distribuição de Operações")
        
        # Performance Mensal (simplificado)
        df['data'] = pd.to_datetime(df['data'])
        df['mes'] = df['data'].dt.to_period('M').astype(str)
        monthly = df.groupby('mes')['capital'].last().pct_change() * 100
        
        fig_monthly = go.Figure(data=[
            go.Bar(
                x=monthly.index,
                y=monthly.values,
                marker=dict(
                    color=monthly.values,
                    colorscale=[[0, Constants.COLOR_LOSS], [1, Constants.COLOR_PROFIT]],
                    cmin=-10,
                    cmax=10
                )
            )
        ])
        fig_monthly.update_layout(
            title="Retorno Mensal (%)",
            xaxis_title="Mês",
            yaxis_title="Retorno (%)"
        )
        
        return dual_chart_container(
            left_figure=fig_ops,
            right_figure=fig_monthly,
            left_title="📊 Distribuição de Operações",
            right_title="📅 Performance Mensal",
            height=350
        )
    
    def _create_data_table(self, trades: List) -> dbc.Card:
        """Cria tabela de dados recentes"""
        if not trades:
            return None
        
        # Últimas 10 operações
        recent_trades = trades[-10:]
        
        table_header = [
            html.Thead(html.Tr([
                html.Th("Data"),
                html.Th("Operação"),
                html.Th("Preço"),
                html.Th("Capital"),
                html.Th("Predição")
            ]))
        ]
        
        rows = []
        for trade in recent_trades:
            rows.append(html.Tr([
                html.Td(trade.data.strftime('%d/%m/%Y %H:%M') if hasattr(trade.data, 'strftime') else str(trade.data)),
                html.Td(
                    trade.operacao,
                    className="text-success" if trade.is_buy() else "text-danger"
                ),
                html.Td(f"${trade.preco:,.2f}"),
                html.Td(f"${trade.capital:,.2f}"),
                html.Td(trade.predicao)
            ]))
        
        table_body = [html.Tbody(rows)]
        
        return dbc.Card([
            dbc.CardHeader(html.H5("📋 Últimas Operações", className="mb-0")),
            dbc.CardBody([
                dbc.Table(
                    table_header + table_body,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    striped=True
                )
            ])
        ], className="shadow-sm")
    
    def _create_footer_stats(self, strategy, metrics: Dict[str, Any]) -> dbc.Card:
        """Cria estatísticas do rodapé"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Small("Estratégia:", className="text-muted d-block"),
                        html.Strong(strategy.name)
                    ], width=3),
                    dbc.Col([
                        html.Small("Modelo:", className="text-muted d-block"),
                        html.Strong(strategy.model_type)
                    ], width=2),
                    dbc.Col([
                        html.Small("Take Profit:", className="text-muted d-block"),
                        html.Strong(f"{strategy.take_profit:.2f}%")
                    ], width=2),
                    dbc.Col([
                        html.Small("Stop Loss:", className="text-muted d-block"),
                        html.Strong(f"{strategy.stop_loss:.2f}%")
                    ], width=2),
                    dbc.Col([
                        html.Small("Nível de Risco:", className="text-muted d-block"),
                        html.Strong(
                            strategy.get_risk_level(),
                            className="text-danger" if strategy.get_risk_level() == "Alto" else "text-warning"
                        )
                    ], width=3)
                ])
            ])
        ], className="shadow-sm bg-light")


# Instância global para registro de callbacks
overview_component = OverviewComponent()


def register_callbacks(app):
    """Função helper para registrar callbacks"""
    overview_component.register_callbacks(app)
