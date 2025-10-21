"""
Backtest Service
Serviço para simulação e backtesting de estratégias
"""
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
from src.webapp.modules.strategies.repositories import StrategyRepository
from src.webapp.modules.dashboard.repositories import TradingHistoryRepository
from src.webapp.shared.models import Strategy, Trade
from src.webapp.shared.config import Constants


class BacktestService:
    """Serviço para backtesting de estratégias"""
    
    def __init__(self):
        """Inicializa repositórios"""
        self.strategy_repo = StrategyRepository()
        self.history_repo = TradingHistoryRepository()
    
    def run_backtest(
        self,
        strategy_id: int,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Executa backtest para período específico
        
        Args:
            strategy_id: ID da estratégia
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            initial_capital: Capital inicial
            
        Returns:
            Dict com resultados do backtest
        """
        # Carregar trades do período
        trades_data = self.history_repo.find_by_date_range(
            strategy_id=strategy_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not trades_data:
            return {
                'success': False,
                'message': 'Nenhum trade encontrado para o período'
            }
        
        # Converter para modelos
        trades = [Trade.from_dict(t) for t in trades_data]
        
        # Simular execução
        results = self._simulate_trades(trades, initial_capital)
        
        # Calcular métricas
        metrics = self._calculate_backtest_metrics(results)
        
        return {
            'success': True,
            'strategy_id': strategy_id,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'capital': {
                'initial': initial_capital,
                'final': results['final_capital'],
                'peak': results['peak_capital']
            },
            'metrics': metrics,
            'trades': results['trades']
        }
    
    def _simulate_trades(
        self,
        trades: List[Trade],
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Simula execução dos trades
        
        Args:
            trades: Lista de trades
            initial_capital: Capital inicial
            
        Returns:
            Dict com resultados da simulação
        """
        capital = initial_capital
        peak_capital = initial_capital
        position = None  # None, 'long', 'short'
        entry_price = 0.0
        entry_amount = 0.0
        simulated_trades = []
        
        for trade in trades:
            if trade.is_buy():
                # Entrada - compra BTC
                if position is None:
                    entry_price = trade.preco
                    entry_amount = capital / trade.preco
                    position = 'long'
                    
                    simulated_trades.append({
                        'date': trade.data,
                        'operation': 'BUY',
                        'price': trade.preco,
                        'amount': entry_amount,
                        'capital': capital,
                        'position': 'OPEN'
                    })
            
            elif trade.is_sell():
                # Saída - vende BTC
                if position == 'long':
                    exit_price = trade.preco
                    capital = entry_amount * exit_price
                    profit = capital - (entry_amount * entry_price)
                    profit_pct = (profit / (entry_amount * entry_price)) * 100
                    
                    simulated_trades.append({
                        'date': trade.data,
                        'operation': 'SELL',
                        'price': trade.preco,
                        'amount': entry_amount,
                        'capital': capital,
                        'position': 'CLOSED',
                        'profit': profit,
                        'profit_pct': profit_pct
                    })
                    
                    # Atualizar peak
                    if capital > peak_capital:
                        peak_capital = capital
                    
                    # Reset posição
                    position = None
                    entry_price = 0.0
                    entry_amount = 0.0
        
        return {
            'final_capital': capital,
            'peak_capital': peak_capital,
            'trades': simulated_trades
        }
    
    def _calculate_backtest_metrics(
        self,
        simulation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula métricas do backtest
        
        Args:
            simulation_results: Resultados da simulação
            
        Returns:
            Dict com métricas
        """
        trades = simulation_results['trades']
        df = pd.DataFrame(trades)
        
        # Apenas operações de fechamento
        closed_trades = df[df['position'] == 'CLOSED']
        
        if len(closed_trades) == 0:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0
            }
        
        # Estatísticas
        total_trades = len(closed_trades)
        profitable = closed_trades[closed_trades['profit'] > 0]
        losing = closed_trades[closed_trades['profit'] <= 0]
        
        profitable_trades = len(profitable)
        losing_trades = len(losing)
        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        
        avg_profit = profitable['profit'].mean() if len(profitable) > 0 else 0
        avg_loss = losing['profit'].mean() if len(losing) > 0 else 0
        
        total_profit = profitable['profit'].sum() if len(profitable) > 0 else 0
        total_loss = abs(losing['profit'].sum()) if len(losing) > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Drawdown
        df['peak'] = df['capital'].cummax()
        df['drawdown'] = ((df['capital'] - df['peak']) / df['peak']) * 100
        max_drawdown = df['drawdown'].min()
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2)
        }
    
    def get_monthly_performance(self, strategy_id: int) -> List[Dict[str, Any]]:
        """
        Retorna performance mensal
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            Lista com performance por mês
        """
        return self.history_repo.get_monthly_performance(strategy_id)
    
    def get_equity_curve(self, strategy_id: int) -> pd.DataFrame:
        """
        Retorna curva de equity
        
        Args:
            strategy_id: ID da estratégia
            
        Returns:
            DataFrame com data e capital
        """
        trades_data = self.history_repo.find_by_strategy(strategy_id)
        
        if not trades_data:
            return pd.DataFrame(columns=['data', 'capital'])
        
        df = pd.DataFrame(trades_data)
        df['data'] = pd.to_datetime(df['data'])
        
        return df[['data', 'capital']].sort_values('data')
    
    def compare_periods(
        self,
        strategy_id: int,
        periods: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Compara performance em diferentes períodos
        
        Args:
            strategy_id: ID da estratégia
            periods: Lista de períodos [{'start': '2024-01-01', 'end': '2024-06-01'}, ...]
            
        Returns:
            Lista com resultados de cada período
        """
        results = []
        
        for period in periods:
            backtest = self.run_backtest(
                strategy_id=strategy_id,
                start_date=period['start'],
                end_date=period['end']
            )
            
            if backtest['success']:
                results.append({
                    'period': period,
                    'metrics': backtest['metrics'],
                    'capital': backtest['capital']
                })
        
        return results
