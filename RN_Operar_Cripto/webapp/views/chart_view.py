"""
View: ChartView
Responsável por criar visualizações (gráficos) com Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


class ChartView:
    """Classe para criar gráficos do dashboard"""
    
    @staticmethod
    def create_capital_evolution_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de evolução do capital
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            fig = px.line(df, x='Data', y='Capital',
                         labels={'Capital': 'Capital ($)', 'Data': 'Data'},
                         title='Evolução do Capital ao Longo do Tempo')
            fig.update_traces(line_color='green', line_width=2)
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de capital: {e}")
            return None
    
    @staticmethod
    def create_prediction_vs_actual_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de previsão vs valor real
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            fig = px.line(df, x='Data', y=['Valor Atual', 'Previsao'],
                         labels={'value': 'Preço BTC ($)', 'variable': 'Série', 'Data': 'Data'},
                         title='Previsão do Modelo LSTM vs. Valor Real do Bitcoin')
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de previsão: {e}")
            return None
    
    @staticmethod
    def create_trades_scatter_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de pontos de compra/venda
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            fig = px.scatter(df, x='Data', y='Preco', color='Operacao',
                           labels={'Preco': 'Preço de Execução ($)', 'Data': 'Data'},
                           title='Preços de Compra e Venda ao Longo do Tempo',
                           color_discrete_map={'Compra': 'blue', 'Venda': 'red'})
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de trades: {e}")
            return None
    
    @staticmethod
    def create_empty_chart(title: str = "Erro ao carregar dados") -> go.Figure:
        """
        Cria um gráfico vazio para casos de erro
        
        Args:
            title: Título do gráfico
            
        Returns:
            Figure vazia do Plotly
        """
        return px.line(title=title)
