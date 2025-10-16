"""
Controller: DashboardController
Responsável por orquestrar Model e View, controlando o fluxo da aplicação
"""
from typing import Dict, Tuple, Optional
import pandas as pd
from src.webapp.models.trading_data_model import TradingDataModel
from src.webapp.views.chart_view import ChartView
from src.webapp.views.layout_view import LayoutView


class DashboardController:
    """Controller principal do dashboard"""
    
    def __init__(self, csv_path: str):
        """
        Inicializa o controller
        
        Args:
            csv_path: Caminho para o arquivo CSV de dados
        """
        self.model = TradingDataModel(csv_path)
        self.chart_view = ChartView()
        self.layout_view = LayoutView()
        self.advanced = None
        
        # Estado
        self.data_loaded = False
        self.metrics_calculated = False
    
    def initialize_data(self) -> bool:
        """
        Inicializa os dados (carrega e pré-processa)
        
        Returns:
            bool: True se inicializou com sucesso
        """
        print("="*70)
        print("INICIALIZANDO DASHBOARD")
        print("="*70)
        
        # Carregar dados
        if not self.model.load_data():
            print("❌ Falha ao carregar dados")
            return False
        
        self.data_loaded = True
        
        # Pré-processar
        if not self.model.preprocess_data():
            print("❌ Falha no pré-processamento")
            return False
        
        # Calcular métricas
        metricas = self.model.calculate_metrics()
        if not metricas:
            print("❌ Falha ao calcular métricas")
            return False
        
        self.metrics_calculated = True
        
        # Inicializar Advanced Analytics
        try:
            from src.webapp.models.advanced_analytics import AdvancedAnalytics
            self.advanced = AdvancedAnalytics(self.model.get_dataframe())
            print("✅ Advanced Analytics inicializado")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Advanced Analytics: {e}")
            self.advanced = None
        
        print("="*70)
        print("✅ DASHBOARD INICIALIZADO COM SUCESSO")
        print("="*70)
        return True
    
    def get_charts(self) -> Tuple:
        """
        Obtém todos os gráficos
        
        Returns:
            Tuple: (fig_capital, fig_previsao, fig_trades)
        """
        print(f"🔍 [DEBUG Controller] get_charts() chamado. data_loaded={self.data_loaded}")
        
        if not self.data_loaded:
            print("⚠️ [DEBUG Controller] Dados não carregados, retornando gráficos vazios")
            empty = self.chart_view.create_empty_chart()
            return (empty, empty, empty)
        
        df = self.model.get_dataframe()
        
        if df is None:
            print("❌ [DEBUG Controller] DataFrame é None!")
            empty = self.chart_view.create_empty_chart("DataFrame não encontrado")
            return (empty, empty, empty)
        
        print(f"🔍 [DEBUG Controller] Criando gráficos com {len(df)} linhas de dados")
        
        fig_capital = self.chart_view.create_capital_evolution_chart(df)
        fig_previsao = self.chart_view.create_prediction_vs_actual_chart(df)
        fig_trades = self.chart_view.create_trades_scatter_chart(df)
        
        # Garantir que não retorne None
        if fig_capital is None:
            fig_capital = self.chart_view.create_empty_chart("Erro no gráfico de capital")
        if fig_previsao is None:
            fig_previsao = self.chart_view.create_empty_chart("Erro no gráfico de previsão")
        if fig_trades is None:
            fig_trades = self.chart_view.create_empty_chart("Erro no gráfico de trades")
        
        print("✅ [DEBUG Controller] Gráficos criados com sucesso")
        return (fig_capital, fig_previsao, fig_trades)
    
    def get_advanced_charts(self) -> Dict:
        """
        Obtém gráficos avançados de análise
        
        Returns:
            Dict com todos os gráficos avançados
        """
        if not self.data_loaded:
            empty = self.chart_view.create_empty_chart()
            return {
                'drawdown': empty,
                'prediction_error': empty,
                'win_loss_dist': empty,
                'cumulative_returns': empty,
                'rolling_sharpe': empty,
                'monthly_heatmap': empty
            }
        
        df = self.model.get_dataframe()
        
        if df is None:
            empty = self.chart_view.create_empty_chart("DataFrame não encontrado")
            return {
                'drawdown': empty,
                'prediction_error': empty,
                'win_loss_dist': empty,
                'cumulative_returns': empty,
                'rolling_sharpe': empty,
                'monthly_heatmap': empty
            }
        
        print(f"🔍 [DEBUG Controller] Criando gráficos avançados...")
        
        return {
            'drawdown': self.chart_view.create_drawdown_chart(df) or 
                       self.chart_view.create_empty_chart("Erro no drawdown"),
            'prediction_error': self.chart_view.create_prediction_error_chart(df) or 
                               self.chart_view.create_empty_chart("Erro no erro de previsão"),
            'win_loss_dist': self.chart_view.create_win_loss_distribution(df) or 
                            self.chart_view.create_empty_chart("Erro na distribuição"),
            'cumulative_returns': self.chart_view.create_cumulative_returns_chart(df) or 
                                 self.chart_view.create_empty_chart("Erro nos retornos"),
            'rolling_sharpe': self.chart_view.create_rolling_sharpe_chart(df) or 
                             self.chart_view.create_empty_chart("Erro no Sharpe"),
            'monthly_heatmap': self.chart_view.create_monthly_returns_heatmap(df) or 
                              self.chart_view.create_empty_chart("Erro no heatmap")
        }
    
    def get_metrics(self) -> Optional[Dict]:
        """
        Obtém as métricas calculadas
        
        Returns:
            Dict com métricas ou None
        """
        return self.model.get_metrics() if self.metrics_calculated else None
    
    def get_insights(self) -> Dict:
        """
        Obtém insights automáticos baseados nos dados
        
        Returns:
            Dict com insights por categoria
        """
        if not self.data_loaded or not self.metrics_calculated:
            return {}
        return self.model.calculate_insights()
    
    def get_advanced_metrics(self) -> Dict:
        """
        Obtém métricas avançadas dos níveis 1-4
        
        Returns:
            Dict com todas as análises avançadas
        """
        if not self.advanced:
            return {}
        
        try:
            return {
                'hourly': self.advanced.calculate_hourly_performance(),
                'risk_reward': self.advanced.calculate_risk_reward_ratio(),
                'consecutive': self.advanced.calculate_consecutive_losses(),
                'confusion_matrix': self.advanced.calculate_confusion_matrix(),
                'monte_carlo': self.advanced.monte_carlo_simulation(n_simulations=1000, n_trades=100),
                'walk_forward': self.advanced.walk_forward_analysis(window_size=50, step_size=10),
                'sensitivity': self.advanced.sensitivity_analysis(
                    tp_range=[0.02, 0.03, 0.04, 0.05],
                    sl_range=[0.01, 0.015, 0.02, 0.025]
                ),
                'alerts': self.advanced.check_alerts({
                    'drawdown_max': -15,
                    'sharpe_min': 1.0,
                    'win_rate_min': 45
                }),
                'regime': self.advanced.detect_market_regime()
            }
        except Exception as e:
            print(f"❌ Erro ao calcular métricas avançadas: {e}")
            return {}
    
    def get_layout_components(self):
        """
        Obtém todos os componentes do layout
        
        Returns:
            Tuple: (header, description, metrics_panel)
        """
        metricas = self.get_metrics()
        
        header = self.layout_view.create_header()
        description = self.layout_view.create_description(metricas)
        metrics_panel = self.layout_view.create_metrics_panel(metricas)
        
        return (header, description, metrics_panel)
    
    def create_section_title(self, title: str):
        """
        Cria um título de seção
        
        Args:
            title: Texto do título
            
        Returns:
            Componente HTML do título
        """
        return self.layout_view.create_section_title(title)
