"""
Metrics Card Component
Componente reutilizável para exibir métricas em cards
"""
from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional


def metrics_card(
    title: str,
    value: str,
    icon: str = "📊",
    color: str = "primary",
    subtitle: Optional[str] = None,
    trend: Optional[Dict[str, Any]] = None
) -> dbc.Card:
    """
    Cria um card de métrica
    
    Args:
        title: Título do card
        value: Valor principal (formatado)
        icon: Emoji ou ícone
        color: Cor do card (primary, success, danger, warning, info)
        subtitle: Texto adicional abaixo do título
        trend: Dict com 'value' e 'direction' ('up', 'down', 'neutral')
        
    Returns:
        dbc.Card: Card com métrica formatada
    """
    # Trend icon
    trend_element = None
    if trend:
        trend_icon = "↑" if trend['direction'] == 'up' else "↓" if trend['direction'] == 'down' else "→"
        trend_color = "success" if trend['direction'] == 'up' else "danger" if trend['direction'] == 'down' else "secondary"
        trend_element = html.Span(
            f"{trend_icon} {trend['value']}",
            className=f"text-{trend_color} small ms-2"
        )
    
    # Card body
    card_body = [
        html.Div([
            html.Span(icon, className="fs-1 me-2"),
            html.Span(title, className="text-muted small")
        ], className="d-flex align-items-center mb-2"),
        html.H3(value, className=f"text-{color} mb-0"),
    ]
    
    if subtitle:
        card_body.append(
            html.P(subtitle, className="text-muted small mb-0 mt-1")
        )
    
    if trend_element:
        card_body.append(trend_element)
    
    return dbc.Card(
        dbc.CardBody(card_body),
        className="shadow-sm h-100"
    )


def metrics_row(metrics: list[Dict[str, Any]]) -> html.Div:
    """
    Cria uma linha com múltiplos cards de métricas
    
    Args:
        metrics: Lista de dicts com parâmetros para metrics_card
        
    Returns:
        html.Div: Container com row de cards
        
    Example:
        metrics_row([
            {'title': 'Capital Inicial', 'value': 'R$ 10.000', 'icon': '💰'},
            {'title': 'Capital Final', 'value': 'R$ 11.971', 'icon': '🎯'}
        ])
    """
    cols = [
        dbc.Col(
            metrics_card(**metric),
            width=12,
            md=6,
            lg=len(metrics) if len(metrics) <= 4 else 3,
            className="mb-3"
        )
        for metric in metrics
    ]
    
    return html.Div(
        dbc.Row(cols),
        className="metrics-row mb-4"
    )


def stat_card(
    label: str,
    value: str,
    color: str = "primary",
    size: str = "md"
) -> html.Div:
    """
    Cria um card simples de estatística (mais compacto)
    
    Args:
        label: Label da estatística
        value: Valor (formatado)
        color: Cor do texto (primary, success, danger, warning, info, secondary)
        size: Tamanho (sm, md, lg)
        
    Returns:
        html.Div: Card compacto com estatística
    """
    size_classes = {
        'sm': 'h6',
        'md': 'h5',
        'lg': 'h4'
    }
    
    return html.Div([
        html.Div(label, className="text-muted small text-uppercase"),
        html.Div(value, className=f"{size_classes[size]} text-{color} mb-0 fw-bold")
    ], className="stat-card p-3 border rounded")


def info_alert(
    message: str,
    alert_type: str = "info",
    title: Optional[str] = None,
    dismissible: bool = False
) -> dbc.Alert:
    """
    Cria um alerta informativo
    
    Args:
        message: Mensagem do alerta
        alert_type: Tipo (success, info, warning, danger)
        title: Título opcional
        dismissible: Se pode ser fechado
        
    Returns:
        dbc.Alert: Alerta Bootstrap
    """
    content = []
    
    if title:
        content.append(html.H5(title, className="alert-heading"))
    
    content.append(html.P(message, className="mb-0"))
    
    return dbc.Alert(
        content,
        color=alert_type,
        dismissible=dismissible,
        className="mb-3"
    )


def progress_card(
    title: str,
    current: float,
    target: float,
    format_fn=None
) -> dbc.Card:
    """
    Cria um card com barra de progresso
    
    Args:
        title: Título do card
        current: Valor atual
        target: Valor alvo
        format_fn: Função para formatar valores (ex: lambda x: f"R$ {x:,.2f}")
        
    Returns:
        dbc.Card: Card com progresso
    """
    percentage = min((current / target) * 100, 100) if target > 0 else 0
    
    format_fn = format_fn or (lambda x: f"{x:,.2f}")
    
    color = "success" if percentage >= 100 else "warning" if percentage >= 75 else "danger"
    
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="mb-3"),
            dbc.Progress(
                value=percentage,
                color=color,
                className="mb-2",
                style={"height": "20px"}
            ),
            html.Div([
                html.Span(f"Atual: {format_fn(current)}", className="text-muted small"),
                html.Span(f"Meta: {format_fn(target)}", className="text-muted small float-end")
            ])
        ]),
        className="shadow-sm"
    )
