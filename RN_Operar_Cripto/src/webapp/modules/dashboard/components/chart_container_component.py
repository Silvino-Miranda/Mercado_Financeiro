"""
Chart Container Component
Componente reutilizável para gráficos
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Optional, Any
import plotly.graph_objects as go


def chart_container(
    figure: go.Figure,
    title: str,
    height: int = 400,
    show_controls: bool = False,
    subtitle: Optional[str] = None
) -> dbc.Card:
    """
    Cria um container para gráfico com título e controles
    
    Args:
        figure: Figura Plotly
        title: Título do gráfico
        height: Altura em pixels
        show_controls: Mostrar controles de zoom/pan
        subtitle: Subtítulo opcional
        
    Returns:
        dbc.Card: Card com gráfico
    """
    # Update figure layout
    figure.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode='x unified'
    )
    
    header = [html.H5(title, className="mb-0")]
    if subtitle:
        header.append(html.P(subtitle, className="text-muted small mb-0"))
    
    return dbc.Card([
        dbc.CardHeader(header),
        dbc.CardBody([
            dcc.Graph(
                figure=figure,
                config={
                    'displayModeBar': show_controls,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                }
            )
        ], className="p-0")
    ], className="shadow-sm mb-4")


def dual_chart_container(
    left_figure: go.Figure,
    right_figure: go.Figure,
    left_title: str,
    right_title: str,
    height: int = 400
) -> html.Div:
    """
    Cria um container com dois gráficos lado a lado
    
    Args:
        left_figure: Figura da esquerda
        right_figure: Figura da direita
        left_title: Título esquerdo
        right_title: Título direito
        height: Altura em pixels
        
    Returns:
        html.Div: Container com dois gráficos
    """
    return dbc.Row([
        dbc.Col([
            chart_container(
                figure=left_figure,
                title=left_title,
                height=height
            )
        ], width=12, md=6),
        dbc.Col([
            chart_container(
                figure=right_figure,
                title=right_title,
                height=height
            )
        ], width=12, md=6)
    ])


def tabbed_charts(
    charts: list[dict[str, Any]],
    default_active: int = 0
) -> dbc.Card:
    """
    Cria um container com múltiplos gráficos em abas
    
    Args:
        charts: Lista de dicts com 'id', 'label', 'figure'
        default_active: Índice da aba ativa por padrão
        
    Returns:
        dbc.Card: Card com abas de gráficos
        
    Example:
        tabbed_charts([
            {'id': 'equity', 'label': 'Equity Curve', 'figure': fig1},
            {'id': 'drawdown', 'label': 'Drawdown', 'figure': fig2}
        ])
    """
    tabs = []
    
    for i, chart in enumerate(charts):
        tab_content = dcc.Graph(
            figure=chart['figure'],
            config={'displaylogo': False}
        )
        
        tabs.append(
            dbc.Tab(
                tab_content,
                label=chart['label'],
                tab_id=chart['id'],
                active_tab_class_name="fw-bold"
            )
        )
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Tabs(
                tabs,
                id="chart-tabs",
                active_tab=charts[default_active]['id']
            )
        ], className="p-0")
    ], className="shadow-sm mb-4")


def mini_chart(
    figure: go.Figure,
    height: int = 150,
    sparkline: bool = False
) -> html.Div:
    """
    Cria um mini gráfico (para dashboards compactos)
    
    Args:
        figure: Figura Plotly
        height: Altura em pixels
        sparkline: Se True, remove eixos e grid (estilo sparkline)
        
    Returns:
        html.Div: Container com mini gráfico
    """
    if sparkline:
        figure.update_layout(
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            height=height,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    else:
        figure.update_layout(
            height=height,
            margin=dict(l=20, r=20, t=20, b=20)
        )
    
    return html.Div(
        dcc.Graph(
            figure=figure,
            config={'displayModeBar': False, 'staticPlot': sparkline}
        ),
        className="mini-chart"
    )


def comparison_chart_grid(
    charts: list[dict[str, Any]],
    columns: int = 2
) -> html.Div:
    """
    Cria uma grid de gráficos para comparação
    
    Args:
        charts: Lista de dicts com 'title', 'figure', 'description' (opcional)
        columns: Número de colunas (2, 3 ou 4)
        
    Returns:
        html.Div: Grid de gráficos
    """
    col_width = 12 // columns
    
    rows = []
    for i in range(0, len(charts), columns):
        row_charts = charts[i:i+columns]
        cols = []
        
        for chart in row_charts:
            card = dbc.Card([
                dbc.CardHeader(html.H6(chart['title'], className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(
                        figure=chart['figure'],
                        config={'displaylogo': False}
                    )
                ], className="p-2")
            ], className="shadow-sm mb-3")
            
            if 'description' in chart:
                card.children.append(
                    dbc.CardFooter(
                        html.Small(chart['description'], className="text-muted")
                    )
                )
            
            cols.append(
                dbc.Col(card, width=12, lg=col_width)
            )
        
        rows.append(dbc.Row(cols))
    
    return html.Div(rows, className="comparison-grid")
