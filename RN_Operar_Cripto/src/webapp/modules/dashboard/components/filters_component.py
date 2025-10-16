"""
Filters Component
Componente reutilizável para filtros e controles
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


def date_range_filter(
    start_id: str,
    end_id: str,
    default_days: int = 30,
    label: str = "Período"
) -> html.Div:
    """
    Cria um filtro de intervalo de datas
    
    Args:
        start_id: ID do DatePickerSingle de início
        end_id: ID do DatePickerSingle de fim
        default_days: Dias padrão do período
        label: Label do filtro
        
    Returns:
        html.Div: Container com date pickers
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=default_days)
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                    id=start_id,
                    date=start_date,
                    display_format='DD/MM/YYYY',
                    className="form-control"
                )
            ], width=6),
            dbc.Col([
                dcc.DatePickerSingle(
                    id=end_id,
                    date=end_date,
                    display_format='DD/MM/YYYY',
                    className="form-control"
                )
            ], width=6)
        ])
    ], className="mb-3")


def dropdown_filter(
    filter_id: str,
    options: List[Dict[str, Any]],
    label: str,
    default_value: Optional[Any] = None,
    multi: bool = False,
    placeholder: str = "Selecione..."
) -> html.Div:
    """
    Cria um filtro dropdown
    
    Args:
        filter_id: ID do dropdown
        options: Lista de opções [{'label': 'X', 'value': 1}, ...]
        label: Label do filtro
        default_value: Valor padrão
        multi: Permitir múltipla seleção
        placeholder: Texto placeholder
        
    Returns:
        html.Div: Container com dropdown
    """
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Dropdown(
            id=filter_id,
            options=options,
            value=default_value,
            multi=multi,
            placeholder=placeholder,
            className="mb-2"
        )
    ], className="mb-3")


def slider_filter(
    filter_id: str,
    label: str,
    min_value: float,
    max_value: float,
    step: float,
    default_value: Optional[float] = None,
    marks: Optional[Dict[float, str]] = None
) -> html.Div:
    """
    Cria um filtro slider
    
    Args:
        filter_id: ID do slider
        label: Label do filtro
        min_value: Valor mínimo
        max_value: Valor máximo
        step: Incremento
        default_value: Valor padrão
        marks: Marcações customizadas
        
    Returns:
        html.Div: Container com slider
    """
    value = default_value if default_value is not None else min_value
    
    if marks is None:
        marks = {
            min_value: str(min_value),
            max_value: str(max_value)
        }
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.Slider(
            id=filter_id,
            min=min_value,
            max=max_value,
            step=step,
            value=value,
            marks=marks,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], className="mb-4")


def range_slider_filter(
    filter_id: str,
    label: str,
    min_value: float,
    max_value: float,
    step: float,
    default_range: Optional[List[float]] = None
) -> html.Div:
    """
    Cria um filtro de intervalo (range slider)
    
    Args:
        filter_id: ID do range slider
        label: Label do filtro
        min_value: Valor mínimo
        max_value: Valor máximo
        step: Incremento
        default_range: Intervalo padrão [min, max]
        
    Returns:
        html.Div: Container com range slider
    """
    value = default_range if default_range else [min_value, max_value]
    
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dcc.RangeSlider(
            id=filter_id,
            min=min_value,
            max=max_value,
            step=step,
            value=value,
            marks={
                min_value: str(min_value),
                max_value: str(max_value)
            },
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], className="mb-4")


def radio_filter(
    filter_id: str,
    options: List[Dict[str, Any]],
    label: str,
    default_value: Optional[Any] = None,
    inline: bool = True
) -> html.Div:
    """
    Cria um filtro de radio buttons
    
    Args:
        filter_id: ID do radio
        options: Lista de opções [{'label': 'X', 'value': 1}, ...]
        label: Label do filtro
        default_value: Valor padrão
        inline: Exibir inline
        
    Returns:
        html.Div: Container com radio buttons
    """
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dbc.RadioItems(
            id=filter_id,
            options=options,
            value=default_value,
            inline=inline
        )
    ], className="mb-3")


def checklist_filter(
    filter_id: str,
    options: List[Dict[str, Any]],
    label: str,
    default_values: Optional[List[Any]] = None,
    inline: bool = False
) -> html.Div:
    """
    Cria um filtro de checklist
    
    Args:
        filter_id: ID do checklist
        options: Lista de opções [{'label': 'X', 'value': 1}, ...]
        label: Label do filtro
        default_values: Valores padrão selecionados
        inline: Exibir inline
        
    Returns:
        html.Div: Container com checklist
    """
    return html.Div([
        html.Label(label, className="form-label fw-bold"),
        dbc.Checklist(
            id=filter_id,
            options=options,
            value=default_values or [],
            inline=inline
        )
    ], className="mb-3")


def filter_panel(
    filters: List[html.Div],
    title: str = "Filtros",
    show_apply_button: bool = True,
    apply_button_id: str = "apply-filters"
) -> dbc.Card:
    """
    Cria um painel com múltiplos filtros
    
    Args:
        filters: Lista de componentes de filtro
        title: Título do painel
        show_apply_button: Mostrar botão "Aplicar"
        apply_button_id: ID do botão aplicar
        
    Returns:
        dbc.Card: Card com painel de filtros
    """
    content = [
        dbc.CardHeader(html.H5(title, className="mb-0")),
        dbc.CardBody(filters)
    ]
    
    if show_apply_button:
        content.append(
            dbc.CardFooter([
                dbc.Button(
                    "Aplicar Filtros",
                    id=apply_button_id,
                    color="primary",
                    className="w-100"
                )
            ])
        )
    
    return dbc.Card(content, className="shadow-sm mb-4")


def search_box(
    search_id: str,
    placeholder: str = "Buscar...",
    button_id: Optional[str] = None
) -> html.Div:
    """
    Cria uma caixa de busca
    
    Args:
        search_id: ID do input de busca
        placeholder: Texto placeholder
        button_id: ID do botão de busca (opcional)
        
    Returns:
        html.Div: Container com search box
    """
    components = [
        dbc.Input(
            id=search_id,
            type="text",
            placeholder=placeholder,
            className="me-2"
        )
    ]
    
    if button_id:
        components.append(
            dbc.Button(
                "🔍",
                id=button_id,
                color="primary"
            )
        )
    
    return dbc.InputGroup(components, className="mb-3")
