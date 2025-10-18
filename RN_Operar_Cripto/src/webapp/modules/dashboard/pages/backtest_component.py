"""
Backtest Component
Lógica de negócio e callbacks da página Backtest
"""
from dash import Output, Input, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.webapp.modules.dashboard.services import BacktestService
from src.webapp.modules.dashboard.components import (
    metrics_row, chart_container, info_alert
)
from src.webapp.modules.strategies.repositories import StrategyRepository
from src.webapp.shared.config import Constants


class BacktestComponent:
    """Componente de lógica para página Backtest"""
    
    def __init__(self):
        """Inicializa serviços"""
        self.backtest_service = BacktestService()
        self.strategy_repo = StrategyRepository()
    
    def register_callbacks(self, app):
        """
        Registra todos os callbacks da página
        
        Args:
            app: Instância do Dash app
        """
        
        @app.callback(
            Output('backtest-strategy-selector', 'options'),
            Output('backtest-strategy-selector', 'value'),
            Output('backtest-start-date', 'date'),
            Output('backtest-end-date', 'date'),
            Input('backtest-strategy-selector', 'id')
        )
        def initialize_backtest(_):
            """Inicializa seletores e datas padrão"""
            strategies = self.strategy_repo.find_active()
            
            if not strategies:
                return [], None, None, None
            
            options = [
                {'label': f"{s['name']} ({s['model_type']})", 'value': s['id']}
                for s in strategies
            ]
            
            # Datas padrão: últimos 30 dias
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            return options, strategies[0]['id'], start_date.date(), end_date.date()
        
        @app.callback(
            Output('backtest-summary', 'children'),
            Output('backtest-metrics', 'children'),
            Output('backtest-charts', 'children'),
            Output('backtest-trade-details', 'children'),
            Output('backtest-results-store', 'data'),
            Input('backtest-run-button', 'n_clicks'),
            Input('backtest-strategy-selector', 'value'),
            Input('backtest-start-date', 'date'),
            Input('backtest-end-date', 'date'),
            Input('backtest-initial-capital', 'value'),
            prevent_initial_call=True
        )
        def run_backtest(
            n_clicks: int,
            strategy_id: Optional[int],
            start_date: str,
            end_date: str,
            initial_capital: float
        ):
            """
            Executa backtest e atualiza resultados
            
            Args:
                n_clicks: Cliques no botão
                strategy_id: ID da estratégia
                start_date: Data inicial
                end_date: Data final
                initial_capital: Capital inicial
                
            Returns:
                Tuple com componentes atualizados
            """
            if not strategy_id or not start_date or not end_date:
                empty = info_alert(
                    "Configure todos os parâmetros e clique em 'Executar Backtest'",
                    alert_type="info",
                    title="ℹ️ Aguardando Configuração"
                )
                return empty, None, None, None, None
            
            try:
                # Executar backtest
                results = self.backtest_service.run_backtest(
                    strategy_id=strategy_id,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital
                )
                
                if not results['success']:
                    error = info_alert(
                        results.get('message', 'Erro ao executar backtest'),
                        alert_type="warning",
                        title="⚠️ Sem Dados"
                    )
                    return error, None, None, None, None
                
                # Criar componentes
                summary = self._create_summary(results)
                metrics = self._create_metrics(results['metrics'], results['capital'])
                charts = self._create_charts(results['trades'])
                trade_details = self._create_trade_details(results['trades'])
                
                return summary, metrics, charts, trade_details, results
                
            except Exception as e:
                error = info_alert(
                    f"Erro ao executar backtest: {str(e)}",
                    alert_type="danger",
                    title="❌ Erro"
                )
                return error, None, None, None, None
    
    def _create_summary(self, results: Dict[str, Any]) -> dbc.Alert:
        """Cria resumo do backtest"""
        capital = results['capital']
        period = results['period']
        
        profit = capital['final'] - capital['initial']
        profit_pct = (profit / capital['initial']) * 100
        
        color = "success" if profit > 0 else "danger"
        icon = "📈" if profit > 0 else "📉"
        
        return dbc.Alert([
            html.H4(f"{icon} Backtest Executado com Sucesso!", className="alert-heading"),
            html.Hr(),
            html.P([
                html.Strong("Período: "),
                f"{period['start']} até {period['end']}"
            ]),
            html.P([
                html.Strong("Resultado: "),
                f"{Constants.format_currency(profit)} ({Constants.format_percentage(profit_pct)})"
            ], className="mb-0")
        ], color=color, className="mb-4")
    
    def _create_metrics(
        self,
        metrics: Dict[str, Any],
        capital: Dict[str, float]
    ) -> html.Div:
        """Cria cards de métricas do backtest"""
        cards_data = [
            {
                'title': 'Capital Inicial',
                'value': Constants.format_currency(capital['initial']),
                'icon': '💰',
                'color': 'secondary'
            },
            {
                'title': 'Capital Final',
                'value': Constants.format_currency(capital['final']),
                'icon': '🎯',
                'color': 'success' if capital['final'] > capital['initial'] else 'danger'
            },
            {
                'title': 'Capital Pico',
                'value': Constants.format_currency(capital['peak']),
                'icon': '⚡',
                'color': 'info'
            },
            {
                'title': 'Total Trades',
                'value': str(metrics.get('total_trades', 0)),
                'icon': '🔄',
                'color': 'primary'
            },
            {
                'title': 'Trades Lucrativos',
                'value': f"{metrics.get('profitable_trades', 0)} ({Constants.format_percentage(metrics.get('win_rate', 0))})",
                'icon': '✅',
                'color': 'success'
            },
            {
                'title': 'Trades Perdedores',
                'value': str(metrics.get('losing_trades', 0)),
                'icon': '❌',
                'color': 'danger'
            },
            {
                'title': 'Lucro Médio',
                'value': Constants.format_currency(metrics.get('avg_profit', 0)),
                'icon': '📊',
                'color': 'success'
            },
            {
                'title': 'Max Drawdown',
                'value': Constants.format_percentage(metrics.get('max_drawdown', 0)),
                'icon': '📉',
                'color': 'danger'
            }
        ]
        
        return metrics_row(cards_data)
    
    def _create_charts(self, trades: list) -> html.Div:
        """Cria gráficos do backtest"""
        if not trades:
            return None
        
        # Equity Curve
        dates = [t['date'] for t in trades]
        capitals = [t['capital'] for t in trades]
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=dates,
            y=capitals,
            mode='lines+markers',
            name='Capital',
            line=dict(color=Constants.COLOR_PROFIT, width=2),
            marker=dict(size=4)
        ))
        fig_equity.update_layout(
            title="Evolução do Capital no Backtest",
            xaxis_title="Data",
            yaxis_title="Capital (USDT)",
            hovermode='x unified'
        )
        
        # Trade Results Distribution
        closed_trades = [t for t in trades if t.get('position') == 'CLOSED']
        if closed_trades:
            profits = [t.get('profit', 0) for t in closed_trades]
            
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(
                x=profits,
                nbinsx=20,
                marker=dict(
                    color=profits,
                    colorscale=[[0, Constants.COLOR_LOSS], [1, Constants.COLOR_PROFIT]],
                    line=dict(width=1, color='white')
                ),
                name='Distribuição de Lucros'
            ))
            fig_dist.update_layout(
                title="Distribuição de Resultados por Trade",
                xaxis_title="Lucro/Prejuízo (USDT)",
                yaxis_title="Quantidade de Trades",
                showlegend=False
            )
        else:
            fig_dist = go.Figure()
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    chart_container(fig_equity, "📈 Curva de Equity", height=400)
                ], width=12, md=6),
                dbc.Col([
                    chart_container(fig_dist, "📊 Distribuição de Resultados", height=400)
                ], width=12, md=6)
            ])
        ])
    
    def _create_trade_details(self, trades: list) -> dbc.Card:
        """Cria tabela de detalhes dos trades"""
        if not trades:
            return None
        
        # Filtrar apenas fechamentos
        closed_trades = [t for t in trades if t.get('position') == 'CLOSED']
        
        if not closed_trades:
            return info_alert(
                "Nenhum trade fechado no período",
                alert_type="info"
            )
        
        # Limitar a 20 mais recentes
        recent = closed_trades[-20:] if len(closed_trades) > 20 else closed_trades
        
        table_header = [
            html.Thead(html.Tr([
                html.Th("Data"),
                html.Th("Operação"),
                html.Th("Preço"),
                html.Th("Quantidade"),
                html.Th("Lucro/Prejuízo"),
                html.Th("Capital")
            ]))
        ]
        
        rows = []
        for trade in recent:
            profit = trade.get('profit', 0)
            profit_pct = trade.get('profit_pct', 0)
            
            rows.append(html.Tr([
                html.Td(trade['date'].strftime('%d/%m/%Y %H:%M') if hasattr(trade['date'], 'strftime') else str(trade['date'])),
                html.Td(
                    trade['operation'],
                    className="fw-bold " + ("text-success" if trade['operation'] == 'BUY' else "text-danger")
                ),
                html.Td(f"${trade['price']:,.2f}"),
                html.Td(f"{trade['amount']:.6f}"),
                html.Td(
                    f"${profit:,.2f} ({profit_pct:+.2f}%)",
                    className="fw-bold " + ("text-success" if profit > 0 else "text-danger")
                ),
                html.Td(f"${trade['capital']:,.2f}")
            ]))
        
        table_body = [html.Tbody(rows)]
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5("📋 Detalhes dos Trades", className="mb-0"),
                html.Small(f" (Últimos {len(recent)} trades fechados)", className="text-muted")
            ]),
            dbc.CardBody([
                dbc.Table(
                    table_header + table_body,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    striped=True,
                    size='sm'
                )
            ])
        ], className="shadow-sm")


# Instância global
backtest_component = BacktestComponent()


def register_callbacks(app):
    """Função helper para registrar callbacks"""
    backtest_component.register_callbacks(app)
