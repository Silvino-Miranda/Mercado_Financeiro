"""
Comparison Component
Lógica de negócio e callbacks da página Comparison
"""
from dash import Output, Input, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

from src.webapp.modules.dashboard.services import AnalyticsService
from src.webapp.modules.dashboard.components import info_alert, chart_container
from src.webapp.modules.strategies.repositories import StrategyRepository
from src.webapp.shared.config import Constants
from src.webapp.shared.models import Strategy


class ComparisonComponent:
    """Componente de lógica para página Comparison"""
    
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
            Output('comparison-strategy-selector', 'options'),
            Input('comparison-strategy-selector', 'id')
        )
        def load_strategies(_):
            """Carrega lista de estratégias"""
            strategies = self.strategy_repo.find_active()
            
            if not strategies:
                return []
            
            return [
                {'label': f"{s['name']} ({s['model_type']})", 'value': s['id']}
                for s in strategies
            ]
        
        @app.callback(
            Output('comparison-summary-cards', 'children'),
            Output('comparison-metrics-table', 'children'),
            Output('comparison-charts-grid', 'children'),
            Output('comparison-ranking', 'children'),
            Output('comparison-insights', 'children'),
            Input('comparison-compare-button', 'n_clicks'),
            Input('comparison-strategy-selector', 'value'),
            prevent_initial_call=True
        )
        def compare_strategies(n_clicks: int, strategy_ids: List[int]):
            """
            Compara estratégias selecionadas
            
            Args:
                n_clicks: Cliques no botão
                strategy_ids: Lista de IDs de estratégias
                
            Returns:
                Tuple com componentes de comparação
            """
            if not strategy_ids or len(strategy_ids) < 2:
                info = info_alert(
                    "Selecione pelo menos 2 estratégias para comparar",
                    alert_type="info",
                    title="ℹ️ Selecione Estratégias"
                )
                return info, None, None, None, None
            
            if len(strategy_ids) > 4:
                warning = info_alert(
                    "Selecione no máximo 4 estratégias para melhor visualização",
                    alert_type="warning",
                    title="⚠️ Muitas Estratégias"
                )
                return warning, None, None, None, None
            
            try:
                # Carregar dados de cada estratégia
                strategies_data = []
                for strategy_id in strategy_ids:
                    overview = self.analytics_service.get_strategy_overview(strategy_id)
                    strategies_data.append(overview)
                
                # Criar componentes
                summary_cards = self._create_summary_cards(strategies_data)
                metrics_table = self._create_metrics_table(strategies_data)
                charts_grid = self._create_charts_grid(strategies_data)
                ranking = self._create_ranking(strategies_data)
                insights = self._create_insights(strategies_data)
                
                return summary_cards, metrics_table, charts_grid, ranking, insights
                
            except Exception as e:
                error = info_alert(
                    f"Erro ao comparar estratégias: {str(e)}",
                    alert_type="danger",
                    title="❌ Erro"
                )
                return error, None, None, None, None
    
    def _create_summary_cards(self, strategies_data: List[Dict]) -> html.Div:
        """Cria cards resumo de cada estratégia"""
        cards = []
        
        for data in strategies_data:
            strategy = data['strategy']
            metrics = data['metrics']
            
            retorno = metrics.get('retorno_total', 0)
            color = "success" if retorno > 0 else "danger"
            
            card = dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5(strategy.name, className="mb-0"),
                        html.Small(strategy.model_type, className="text-muted")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            html.Small("Retorno Total", className="text-muted d-block"),
                            html.H4(
                                Constants.format_percentage(retorno),
                                className=f"text-{color} mb-2"
                            )
                        ]),
                        html.Hr(),
                        html.Div([
                            html.Small("Win Rate: ", className="text-muted"),
                            html.Strong(Constants.format_percentage(metrics.get('win_rate', 0)))
                        ], className="mb-1"),
                        html.Div([
                            html.Small("Sharpe: ", className="text-muted"),
                            html.Strong(f"{metrics.get('sharpe_ratio', 0):.2f}")
                        ], className="mb-1"),
                        html.Div([
                            html.Small("Max DD: ", className="text-muted"),
                            html.Strong(
                                Constants.format_percentage(metrics.get('max_drawdown', 0)),
                                className="text-danger"
                            )
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=3)
            
            cards.append(card)
        
        return dbc.Row(cards)
    
    def _create_metrics_table(self, strategies_data: List[Dict]) -> dbc.Card:
        """Cria tabela comparativa de métricas"""
        # Preparar dados
        rows_data = [
            ('Capital Inicial', 'capital_inicial', Constants.format_currency),
            ('Capital Final', 'capital_final', Constants.format_currency),
            ('Retorno Total', 'retorno_total', Constants.format_percentage),
            ('Retorno Anual', 'retorno_anual', Constants.format_percentage),
            ('Win Rate', 'win_rate', Constants.format_percentage),
            ('Sharpe Ratio', 'sharpe_ratio', lambda x: f"{x:.2f}"),
            ('Max Drawdown', 'max_drawdown', Constants.format_percentage),
            ('Total Operações', 'total_operacoes', str),
            ('Dias Operação', 'dias_operacao', str)
        ]
        
        # Header
        header_cols = [html.Th("Métrica", className="fw-bold")]
        for data in strategies_data:
            header_cols.append(
                html.Th(data['strategy'].name, className="text-center")
            )
        table_header = [html.Thead(html.Tr(header_cols))]
        
        # Rows
        rows = []
        for metric_name, metric_key, formatter in rows_data:
            cols = [html.Td(metric_name, className="fw-bold")]
            
            for data in strategies_data:
                value = data['metrics'].get(metric_key, 0)
                formatted = formatter(value)
                
                # Adicionar cor para métricas específicas
                css_class = "text-center"
                if metric_key in ['retorno_total', 'retorno_anual']:
                    css_class += " text-success" if value > 0 else " text-danger"
                elif metric_key == 'max_drawdown':
                    css_class += " text-danger"
                elif metric_key == 'sharpe_ratio':
                    css_class += " text-success" if value >= 1.5 else " text-warning"
                
                cols.append(html.Td(formatted, className=css_class))
            
            rows.append(html.Tr(cols))
        
        table_body = [html.Tbody(rows)]
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5("📋 Comparação de Métricas", className="mb-0")
            ]),
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
    
    def _create_charts_grid(self, strategies_data: List[Dict]) -> html.Div:
        """Cria grid de gráficos comparativos"""
        # Gráfico 1: Retorno Total
        fig_returns = go.Figure()
        
        strategies_names = [d['strategy'].name for d in strategies_data]
        returns = [d['metrics'].get('retorno_total', 0) for d in strategies_data]
        colors = [Constants.COLOR_PROFIT if r > 0 else Constants.COLOR_LOSS for r in returns]
        
        fig_returns.add_trace(go.Bar(
            x=strategies_names,
            y=returns,
            marker=dict(color=colors),
            text=[f"{r:.2f}%" for r in returns],
            textposition='outside'
        ))
        fig_returns.update_layout(
            title="Retorno Total (%)",
            xaxis_title="Estratégia",
            yaxis_title="Retorno (%)",
            showlegend=False
        )
        
        # Gráfico 2: Win Rate vs Sharpe
        fig_scatter = go.Figure()
        
        for data in strategies_data:
            strategy = data['strategy']
            metrics = data['metrics']
            
            fig_scatter.add_trace(go.Scatter(
                x=[metrics.get('win_rate', 0)],
                y=[metrics.get('sharpe_ratio', 0)],
                mode='markers+text',
                name=strategy.name,
                text=[strategy.name],
                textposition="top center",
                marker=dict(size=15)
            ))
        
        fig_scatter.update_layout(
            title="Win Rate vs Sharpe Ratio",
            xaxis_title="Win Rate (%)",
            yaxis_title="Sharpe Ratio",
            showlegend=True
        )
        
        # Gráfico 3: Drawdown Comparison
        fig_dd = go.Figure()
        
        drawdowns = [abs(d['metrics'].get('max_drawdown', 0)) for d in strategies_data]
        
        fig_dd.add_trace(go.Bar(
            x=strategies_names,
            y=drawdowns,
            marker=dict(color=Constants.COLOR_LOSS),
            text=[f"{dd:.2f}%" for dd in drawdowns],
            textposition='outside'
        ))
        fig_dd.update_layout(
            title="Max Drawdown (%)",
            xaxis_title="Estratégia",
            yaxis_title="Drawdown (%)",
            showlegend=False
        )
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    chart_container(fig_returns, "📈 Retorno Total", height=350)
                ], width=12, md=6),
                dbc.Col([
                    chart_container(fig_dd, "📉 Max Drawdown", height=350)
                ], width=12, md=6)
            ]),
            dbc.Row([
                dbc.Col([
                    chart_container(fig_scatter, "🎯 Win Rate vs Sharpe", height=400)
                ], width=12)
            ])
        ])
    
    def _create_ranking(self, strategies_data: List[Dict]) -> dbc.Card:
        """Cria ranking de estratégias"""
        # Critérios de ranking
        rankings = {
            'Melhor Retorno': max(strategies_data, key=lambda x: x['metrics'].get('retorno_total', 0)),
            'Melhor Sharpe': max(strategies_data, key=lambda x: x['metrics'].get('sharpe_ratio', 0)),
            'Melhor Win Rate': max(strategies_data, key=lambda x: x['metrics'].get('win_rate', 0)),
            'Menor Drawdown': min(strategies_data, key=lambda x: abs(x['metrics'].get('max_drawdown', 0)))
        }
        
        ranking_items = []
        icons = ['🥇', '🏆', '🎯', '🛡️']
        
        for (criteria, winner), icon in zip(rankings.items(), icons):
            strategy = winner['strategy']
            metrics = winner['metrics']
            
            if criteria == 'Melhor Retorno':
                value = Constants.format_percentage(metrics.get('retorno_total', 0))
            elif criteria == 'Melhor Sharpe':
                value = f"{metrics.get('sharpe_ratio', 0):.2f}"
            elif criteria == 'Melhor Win Rate':
                value = Constants.format_percentage(metrics.get('win_rate', 0))
            else:  # Menor Drawdown
                value = Constants.format_percentage(metrics.get('max_drawdown', 0))
            
            ranking_items.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.H5([icon, f" {criteria}"], className="mb-1"),
                        html.P([
                            html.Strong(strategy.name),
                            f" - {value}"
                        ], className="mb-0 text-muted")
                    ])
                ])
            )
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5("🏆 Rankings", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.ListGroup(ranking_items, flush=True)
            ])
        ], className="shadow-sm")
    
    def _create_insights(self, strategies_data: List[Dict]) -> html.Div:
        """Cria insights da comparação"""
        insights = []
        
        # Melhor estratégia geral (baseado em múltiplos critérios)
        best_overall = max(
            strategies_data,
            key=lambda x: (
                x['metrics'].get('retorno_total', 0) +
                x['metrics'].get('sharpe_ratio', 0) * 10 +
                abs(x['metrics'].get('max_drawdown', 0)) * -1
            )
        )
        
        insights.append(
            info_alert(
                f"A estratégia '{best_overall['strategy'].name}' apresenta o melhor balanço geral entre retorno, risco e consistência.",
                alert_type="success",
                title="🎯 Melhor Estratégia Geral"
            )
        )
        
        # Estratégia mais arriscada
        riskiest = max(strategies_data, key=lambda x: abs(x['metrics'].get('max_drawdown', 0)))
        if abs(riskiest['metrics'].get('max_drawdown', 0)) > 30:
            insights.append(
                info_alert(
                    f"A estratégia '{riskiest['strategy'].name}' apresenta drawdown elevado ({Constants.format_percentage(riskiest['metrics'].get('max_drawdown', 0))}). Considere reduzir exposição.",
                    alert_type="warning",
                    title="⚠️ Alerta de Risco"
                )
            )
        
        return html.Div(insights)


# Instância global
comparison_component = ComparisonComponent()


def register_callbacks(app):
    """Função helper para registrar callbacks"""
    comparison_component.register_callbacks(app)
