"""
Analytics Service
Serviço para análise de dados de trading e cálculo de métricas
"""
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from src.webapp.modules.strategies.repositories import StrategyRepository
from src.webapp.modules.dashboard.repositories import TradingHistoryRepository
from src.webapp.shared.models import Strategy, Trade
from src.webapp.shared.config import Constants


class AnalyticsService:
    """Serviço de análise de dados de trading"""
    
    def __init__(self):
        """Inicializa repositórios"""
        self.strategy_repo = StrategyRepository()
        self.history_repo = TradingHistoryRepository()
    
    def get_strategy_overview(self, strategy_id: int) -> Dict[str, Any]:
        """
        Retorna visão geral completa de uma estratégia
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Dict com strategy, trades, metrics, insights
        """
        # Carregar dados
        strategy_data = self.strategy_repo.find_by_id(strategy_id)
        if not strategy_data:
            raise ValueError(f"Estratégia {strategy_id} não encontrada")
        
        strategy = Strategy.from_dict(strategy_data)
        
        # Carregar histórico
        trades_data = self.history_repo.find_by_strategy(strategy_id)
        trades = [Trade.from_dict(t) for t in trades_data]
        
        # Calcular métricas
        metrics = self.calculate_metrics(trades)
        
        # Gerar insights
        insights = self.generate_insights(strategy, metrics)
        
        return {
            'strategy': strategy,
            'trades': trades,
            'metrics': metrics,
            'insights': insights
        }
    
    def calculate_metrics(self, trades: List[Trade]) -> Dict[str, Any]:
        """
        Calcula métricas de performance
        
        Args:
            trades: Lista de trades
            
        Returns:
            Dict com métricas calculadas
        """
        if not trades:
            return {}
        
        # Converter para DataFrame para cálculos
        df = pd.DataFrame([t.to_dict() for t in trades])
        
        # Capital
        capital_inicial = df['capital'].iloc[0]
        capital_final = df['capital'].iloc[-1]
        retorno_total = ((capital_final - capital_inicial) / capital_inicial) * 100
        
        # Período
        df['data'] = pd.to_datetime(df['data'])
        data_inicial = df['data'].min()
        data_final = df['data'].max()
        dias = (data_final - data_inicial).days
        anos = dias / 365.25 if dias > 0 else 1
        retorno_anual = ((capital_final / capital_inicial) ** (1 / anos) - 1) * 100 if anos > 0 else 0
        
        # Operações
        compras = len(df[df['operacao'] == 'Compra'])
        vendas = len(df[df['operacao'] == 'Venda'])
        
        # Win Rate
        df_vendas = df[df['operacao'] == 'Venda'].copy()
        if len(df_vendas) > 0:
            df_vendas['retorno'] = df_vendas['capital'].diff()
            trades_lucro = len(df_vendas[df_vendas['retorno'] > 0])
            win_rate = (trades_lucro / len(df_vendas)) * 100
        else:
            win_rate = 0
        
        # Drawdown
        df['peak'] = df['capital'].cummax()
        df['drawdown'] = ((df['capital'] - df['peak']) / df['peak']) * 100
        max_drawdown = df['drawdown'].min()
        
        # Sharpe Ratio
        df['return_pct'] = df['capital'].pct_change() * 100
        returns = df['return_pct'].dropna()
        sharpe_ratio = (returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        # Erro de previsão
        erro_medio = df['erro_previsao'].mean() if 'erro_previsao' in df.columns else 0
        erro_std = df['erro_previsao'].std() if 'erro_previsao' in df.columns else 0
        
        return {
            'capital_inicial': capital_inicial,
            'capital_final': capital_final,
            'retorno_total': round(retorno_total, 2),
            'retorno_anual': round(retorno_anual, 2),
            'data_inicial': data_inicial.strftime('%Y-%m-%d'),
            'data_final': data_final.strftime('%Y-%m-%d'),
            'dias_operacao': dias,
            'total_operacoes': len(df),
            'total_compras': compras,
            'total_vendas': vendas,
            'win_rate': round(win_rate, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'erro_previsao_medio': round(erro_medio, 2),
            'erro_previsao_std': round(erro_std, 2)
        }
    
    def generate_insights(
        self,
        strategy: Strategy,
        metrics: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Gera insights sobre a estratégia
        
        Args:
            strategy: Modelo da estratégia
            metrics: Métricas calculadas
            
        Returns:
            List de insights com tipo, título e mensagem
        """
        insights = []
        
        # Insight: Sharpe Ratio
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe >= Constants.EXCELLENT_SHARPE_RATIO:
            insights.append({
                'type': 'success',
                'title': '🎯 Excelente Sharpe Ratio',
                'message': f'Sharpe de {sharpe:.2f} indica retorno ajustado ao risco excepcional!'
            })
        elif sharpe >= Constants.GOOD_SHARPE_RATIO:
            insights.append({
                'type': 'success',
                'title': '✅ Bom Sharpe Ratio',
                'message': f'Sharpe de {sharpe:.2f} mostra boa relação risco/retorno.'
            })
        elif sharpe < 0.5:
            insights.append({
                'type': 'warning',
                'title': '⚠️ Sharpe Ratio Baixo',
                'message': f'Sharpe de {sharpe:.2f} sugere retorno insuficiente para o risco.'
            })
        
        # Insight: Drawdown
        drawdown = metrics.get('max_drawdown', 0)
        if drawdown <= Constants.ACCEPTABLE_DRAWDOWN:
            insights.append({
                'type': 'success',
                'title': '🛡️ Drawdown Controlado',
                'message': f'Drawdown de {drawdown:.2f}% está em nível aceitável.'
            })
        elif drawdown <= Constants.CRITICAL_DRAWDOWN:
            insights.append({
                'type': 'warning',
                'title': '⚠️ Drawdown Elevado',
                'message': f'Drawdown de {drawdown:.2f}% requer atenção. Considere ajustar stop loss.'
            })
        else:
            insights.append({
                'type': 'danger',
                'title': '🚨 Drawdown Crítico',
                'message': f'Drawdown de {drawdown:.2f}% é muito alto! Revisar urgentemente a estratégia.'
            })
        
        # Insight: Win Rate
        win_rate = metrics.get('win_rate', 0)
        if win_rate >= Constants.EXCELLENT_WIN_RATE:
            insights.append({
                'type': 'success',
                'title': '🏆 Excelente Win Rate',
                'message': f'{win_rate:.1f}% de acerto é excepcional!'
            })
        elif win_rate >= Constants.GOOD_WIN_RATE:
            insights.append({
                'type': 'success',
                'title': '✅ Bom Win Rate',
                'message': f'{win_rate:.1f}% de acerto está acima da média.'
            })
        elif win_rate < 40:
            insights.append({
                'type': 'warning',
                'title': '⚠️ Win Rate Baixo',
                'message': f'{win_rate:.1f}% de acerto está abaixo do esperado.'
            })
        
        # Insight: Retorno vs Drawdown
        retorno = metrics.get('retorno_total', 0)
        ratio_return_drawdown = abs(retorno / drawdown) if drawdown != 0 else 0
        if ratio_return_drawdown > 2:
            insights.append({
                'type': 'info',
                'title': '📊 Boa Relação Retorno/Drawdown',
                'message': f'Retorno de {retorno:.1f}% com drawdown de {drawdown:.1f}% é eficiente.'
            })
        elif ratio_return_drawdown < 1:
            insights.append({
                'type': 'warning',
                'title': '📉 Drawdown Desproporcional',
                'message': 'Risco muito alto em relação ao retorno obtido.'
            })
        
        return insights
    
    def get_trades_dataframe(self, strategy_id: int) -> pd.DataFrame:
        """
        Retorna trades como DataFrame
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            pd.DataFrame: DataFrame com trades
        """
        return self.history_repo.to_dataframe(
            query="SELECT * FROM trading_history WHERE strategy_id = ? ORDER BY data ASC",
            params=(strategy_id,)
        )
    
    def compare_strategies(self, strategy_ids: List[int]) -> Dict[str, Any]:
        """
        Compara múltiplas estratégias
        
        Args:
            strategy_ids: Lista de IDs de estratégias
            
        Returns:
            Dict com comparação
        """
        strategies = self.strategy_repo.get_comparison(strategy_ids)
        
        return {
            'strategies': [Strategy.from_dict(s) for s in strategies],
            'best_return': max(strategies, key=lambda x: x.get('total_return', 0)),
            'best_sharpe': max(strategies, key=lambda x: x.get('sharpe_ratio', 0)),
            'lowest_drawdown': min(strategies, key=lambda x: x.get('max_drawdown', 0))
        }
