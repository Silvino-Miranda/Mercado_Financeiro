"""
View: ChartView
Responsável por criar visualizações (gráficos) com Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, List


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
            print(f"🔍 [DEBUG] DataFrame shape: {df.shape}")
            print(f"🔍 [DEBUG] Colunas disponíveis: {df.columns.tolist()}")
            print(f"🔍 [DEBUG] Primeiras 3 linhas:\n{df.head(3)}")
            
            fig = px.line(df, x='Data', y='Capital',
                         labels={'Capital': 'Capital ($)', 'Data': 'Data'},
                         title='Evolução do Capital ao Longo do Tempo')
            fig.update_traces(line_color='green', line_width=2)
            print(f"✅ [DEBUG] Gráfico de capital criado com sucesso")
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de capital: {e}")
            import traceback
            traceback.print_exc()
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
    def create_drawdown_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de drawdown (queda do pico)
        Mostra o quanto o capital caiu desde o pico anterior
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            # Calcular drawdown
            df_copy = df.copy()
            df_copy['Peak'] = df_copy['Capital'].cummax()
            df_copy['Drawdown'] = ((df_copy['Capital'] - df_copy['Peak']) / df_copy['Peak']) * 100
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_copy['Data'], 
                y=df_copy['Drawdown'],
                fill='tozeroy',
                name='Drawdown',
                line=dict(color='red', width=2)
            ))
            
            fig.update_layout(
                title='Drawdown - Queda Máxima desde o Pico',
                xaxis_title='Data',
                yaxis_title='Drawdown (%)',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de drawdown: {e}")
            return None
    
    @staticmethod
    def create_prediction_error_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de erro de previsão (Previsão - Valor Real)
        Identifica bias do modelo (prevê sempre alto ou sempre baixo)
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            df_copy = df.copy()
            df_copy['Erro'] = df_copy['Previsao'] - df_copy['Valor Atual']
            df_copy['Erro_Pct'] = (df_copy['Erro'] / df_copy['Valor Atual']) * 100
            
            fig = go.Figure()
            
            # Linha de erro percentual
            fig.add_trace(go.Scatter(
                x=df_copy['Data'],
                y=df_copy['Erro_Pct'],
                mode='lines+markers',
                name='Erro de Previsão (%)',
                line=dict(color='orange', width=1),
                marker=dict(size=4)
            ))
            
            # Linha zero (referência)
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         annotation_text="Zero (previsão perfeita)")
            
            fig.update_layout(
                title='Erro de Previsão do Modelo LSTM (%)',
                xaxis_title='Data',
                yaxis_title='Erro (%)',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de erro de previsão: {e}")
            return None
    
    @staticmethod
    def create_win_loss_distribution(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria histograma de distribuição de ganhos e perdas
        Mostra quantos trades tiveram X% de lucro/prejuízo
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            # Calcular variação de capital entre trades
            vendas = df[df['Operacao'] == 'Venda'].copy()
            vendas['Capital_Anterior'] = vendas['Capital'].shift(1)
            vendas['Variacao_Pct'] = ((vendas['Capital'] - vendas['Capital_Anterior']) / vendas['Capital_Anterior']) * 100
            vendas = vendas.dropna()
            
            fig = go.Figure()
            
            # Separar ganhos e perdas
            ganhos = vendas[vendas['Variacao_Pct'] > 0]['Variacao_Pct']
            perdas = vendas[vendas['Variacao_Pct'] <= 0]['Variacao_Pct']
            
            fig.add_trace(go.Histogram(
                x=ganhos,
                name='Ganhos',
                marker_color='green',
                opacity=0.7,
                nbinsx=20
            ))
            
            fig.add_trace(go.Histogram(
                x=perdas,
                name='Perdas',
                marker_color='red',
                opacity=0.7,
                nbinsx=20
            ))
            
            fig.update_layout(
                title='Distribuição de Ganhos e Perdas por Trade',
                xaxis_title='Variação de Capital (%)',
                yaxis_title='Número de Trades',
                barmode='overlay',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de distribuição: {e}")
            return None
    
    @staticmethod
    def create_cumulative_returns_chart(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria gráfico de retornos cumulativos (%)
        Mostra o retorno percentual acumulado desde o início
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            df_copy = df.copy()
            capital_inicial = df_copy['Capital'].iloc[0]
            df_copy['Retorno_Acumulado'] = ((df_copy['Capital'] - capital_inicial) / capital_inicial) * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_copy['Data'],
                y=df_copy['Retorno_Acumulado'],
                mode='lines',
                name='Retorno Acumulado',
                line=dict(color='#2ecc71', width=3),
                fill='tozeroy'
            ))
            
            # Linha de referência zero
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            fig.update_layout(
                title='Retorno Acumulado ao Longo do Tempo',
                xaxis_title='Data',
                yaxis_title='Retorno (%)',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de retornos cumulativos: {e}")
            return None
    
    @staticmethod
    def create_rolling_sharpe_chart(df: pd.DataFrame, window: int = 30) -> Optional[go.Figure]:
        """
        Cria gráfico de Sharpe Ratio móvel
        Mostra a qualidade dos retornos (retorno ajustado ao risco) ao longo do tempo
        
        Args:
            df: DataFrame com dados de trading
            window: Janela para cálculo móvel (padrão: 30 operações)
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            df_copy = df.copy()
            
            # Calcular retornos diários
            df_copy['Retorno'] = df_copy['Capital'].pct_change()
            
            # Sharpe Ratio móvel (simplificado, sem risk-free rate)
            df_copy['Sharpe_Movel'] = (
                df_copy['Retorno'].rolling(window=window).mean() / 
                df_copy['Retorno'].rolling(window=window).std()
            ) * (252 ** 0.5)  # Anualizado
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_copy['Data'],
                y=df_copy['Sharpe_Movel'],
                mode='lines',
                name=f'Sharpe Ratio (janela {window})',
                line=dict(color='purple', width=2)
            ))
            
            # Linha de referência (Sharpe > 1 é bom)
            fig.add_hline(y=1, line_dash="dash", line_color="green", 
                         annotation_text="Sharpe = 1 (Bom)")
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            
            fig.update_layout(
                title=f'Sharpe Ratio Móvel (Janela de {window} operações)',
                xaxis_title='Data',
                yaxis_title='Sharpe Ratio',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico de Sharpe móvel: {e}")
            return None
    
    @staticmethod
    def create_monthly_returns_heatmap(df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Cria heatmap de retornos mensais
        Visualiza performance por mês/ano
        
        Args:
            df: DataFrame com dados de trading
            
        Returns:
            Figure do Plotly ou None
        """
        try:
            df_copy = df.copy()
            df_copy['Ano'] = df_copy['Data'].dt.year
            df_copy['Mes'] = df_copy['Data'].dt.month
            
            # Retorno por período
            df_copy['Retorno'] = df_copy['Capital'].pct_change() * 100
            
            # Agrupar por mês
            monthly = df_copy.groupby(['Ano', 'Mes'])['Retorno'].sum().reset_index()
            
            # Pivot para heatmap
            pivot = monthly.pivot(index='Mes', columns='Ano', values='Retorno')
            
            # Nomes dos meses
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=[meses[i-1] for i in pivot.index],
                colorscale='RdYlGn',
                text=pivot.values.round(2),
                texttemplate='%{text}%',
                textfont={"size": 10},
                colorbar=dict(title="Retorno (%)")
            ))
            
            fig.update_layout(
                title='Retornos Mensais (%)',
                xaxis_title='Ano',
                yaxis_title='Mês',
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar heatmap mensal: {e}")
            return None
    
    # ============================================================================
    # NÍVEL 1: GRÁFICOS ADICIONAIS
    # ============================================================================
    
    @staticmethod
    def create_hourly_performance_chart(hourly_df: pd.DataFrame) -> go.Figure:
        """Cria gráfico de performance por hora"""
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=hourly_df['Hora'],
                y=hourly_df['Win_Rate'],
                name='Taxa de Acerto (%)',
                marker_color='lightblue',
                text=hourly_df['Win_Rate'].round(1),
                texttemplate='%{text}%',
                textposition='outside'
            ))
            
            fig.update_layout(
                title='Taxa de Acerto por Hora do Dia',
                xaxis_title='Hora',
                yaxis_title='Taxa de Acerto (%)',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico hourly: {e}")
            return None
    
    @staticmethod
    def create_monte_carlo_chart(mc_results: Dict) -> go.Figure:
        """Cria histograma de simulação Monte Carlo"""
        try:
            simulations = mc_results.get('simulations', [])
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=simulations,
                nbinsx=50,
                name='Distribuição de Retornos',
                marker_color='purple',
                opacity=0.7
            ))
            
            # Linhas de percentis
            fig.add_vline(x=mc_results['percentile_5'], line_dash="dash", line_color="red",
                         annotation_text=f"P5: {mc_results['percentile_5']:.1f}%")
            fig.add_vline(x=mc_results['median_return'], line_dash="solid", line_color="green",
                         annotation_text=f"Mediana: {mc_results['median_return']:.1f}%")
            fig.add_vline(x=mc_results['percentile_95'], line_dash="dash", line_color="blue",
                         annotation_text=f"P95: {mc_results['percentile_95']:.1f}%")
            
            fig.update_layout(
                title='Simulação Monte Carlo - Distribuição de Retornos Esperados (1000 simulações)',
                xaxis_title='Retorno (%)',
                yaxis_title='Frequência',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico Monte Carlo: {e}")
            return None
    
    @staticmethod
    def create_walk_forward_chart(wf_results: List[Dict]) -> go.Figure:
        """Cria gráfico de Walk-Forward Analysis"""
        try:
            if not wf_results:
                return None
            
            df_wf = pd.DataFrame(wf_results)
            
            fig = go.Figure()
            
            # Retorno por período
            fig.add_trace(go.Scatter(
                x=df_wf['periodo_fim'],
                y=df_wf['retorno'],
                mode='lines+markers',
                name='Retorno por Período (%)',
                line=dict(color='blue', width=2),
                marker=dict(size=8)
            ))
            
            # Linha zero
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            fig.update_layout(
                title='Walk-Forward Analysis - Retorno por Período de Validação',
                xaxis_title='Data Final do Período',
                yaxis_title='Retorno (%)',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar gráfico Walk-Forward: {e}")
            return None
    
    @staticmethod
    def create_sensitivity_heatmap(sens_results: List[Dict]) -> go.Figure:
        """Cria heatmap de análise de sensibilidade TP/SL"""
        try:
            if not sens_results:
                return None
            
            df_sens = pd.DataFrame(sens_results)
            
            # Pivot para heatmap
            pivot = df_sens.pivot(index='stop_loss', columns='take_profit', values='retorno_final')
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=[f'{tp:.1f}%' for tp in pivot.columns],
                y=[f'{sl:.1f}%' for sl in pivot.index],
                colorscale='RdYlGn',
                text=pivot.values.round(2),
                texttemplate='%{text}%',
                textfont={"size": 10},
                colorbar=dict(title="Retorno (%)")
            ))
            
            fig.update_layout(
                title='Análise de Sensibilidade - Retorno por Combinação TP/SL',
                xaxis_title='Take Profit (%)',
                yaxis_title='Stop Loss (%)',
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar heatmap de sensibilidade: {e}")
            return None
    
    @staticmethod
    def create_confusion_matrix_chart(cm: Dict) -> go.Figure:
        """Cria visualização de matriz de confusão"""
        try:
            # Matriz 2x2
            matrix = [
                [cm['true_negative'], cm['false_positive']],
                [cm['false_negative'], cm['true_positive']]
            ]
            
            labels = [
                [f"TN: {cm['true_negative']}", f"FP: {cm['false_positive']}"],
                [f"FN: {cm['false_negative']}", f"TP: {cm['true_positive']}"]
            ]
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['Previu BAIXA', 'Previu ALTA'],
                y=['Real BAIXA', 'Real ALTA'],
                text=labels,
                texttemplate='%{text}',
                textfont={"size": 16},
                colorscale='Blues',
                showscale=False
            ))
            
            fig.update_layout(
                title=f'Matriz de Confusão do Modelo LSTM<br>Accuracy: {cm["accuracy"]*100:.1f}% | F1-Score: {cm["f1_score"]*100:.1f}%',
                xaxis_title='Previsão do Modelo',
                yaxis_title='Realidade do Mercado',
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erro ao criar matriz de confusão: {e}")
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
