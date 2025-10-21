"""
Dashboard Components
Componentes reutilizáveis para UI do dashboard
"""
from .metrics_card_component import (
    metrics_card,
    metrics_row,
    stat_card,
    info_alert,
    progress_card
)
from .chart_container_component import (
    chart_container,
    dual_chart_container,
    tabbed_charts,
    mini_chart,
    comparison_chart_grid
)
from .filters_component import (
    date_range_filter,
    dropdown_filter,
    slider_filter,
    range_slider_filter,
    radio_filter,
    checklist_filter,
    filter_panel,
    search_box
)

__all__ = [
    # Metrics
    'metrics_card',
    'metrics_row',
    'stat_card',
    'info_alert',
    'progress_card',
    
    # Charts
    'chart_container',
    'dual_chart_container',
    'tabbed_charts',
    'mini_chart',
    'comparison_chart_grid',
    
    # Filters
    'date_range_filter',
    'dropdown_filter',
    'slider_filter',
    'range_slider_filter',
    'radio_filter',
    'checklist_filter',
    'filter_panel',
    'search_box'
]
