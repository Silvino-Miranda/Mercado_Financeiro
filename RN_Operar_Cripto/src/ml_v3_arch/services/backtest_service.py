"""
Backtest Service - Simula trading com modelos.

Princípios aplicados:
- SRP: Responsável apenas por backtesting
- DIP: Depende de abstrações
- Strategy Pattern: Diferentes estratégias de trading
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

import numpy as np
import pandas as pd

from ..domain.entities import (
    BacktestConfig,
    Trade,
    TradeDirection,
    MarketData
)
from ..interfaces import BaseModel


@dataclass
class BacktestResult:
    """Resultado de um backtest."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    trades: List[Trade]
    equity_curve: pd.DataFrame


class TradingStrategy:
    """Estratégia de trading baseada em predições."""
    
    def __init__(
        self,
        strategy_type: str = 'classification',
        threshold: float = 0.0
    ):
        """
        Args:
            strategy_type: 'regression' ou 'classification'
            threshold: Threshold para sinais (regression)
        """
        self.strategy_type = strategy_type
        self.threshold = threshold
    
    def generate_signals(
        self,
        predictions: np.ndarray,
        probabilities: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Gera sinais de trading a partir de predições.
        
        Args:
            predictions: Predições do modelo
            probabilities: Probabilidades (classification)
            
        Returns:
            Array com sinais: 1 (LONG), 0 (NEUTRAL), -1 (SHORT)
        """
        if self.strategy_type == 'regression':
            # Regression: threshold-based
            signals = np.zeros_like(predictions, dtype=int)
            signals[predictions > self.threshold] = 1
            signals[predictions < -self.threshold] = -1
            return signals
        
        elif self.strategy_type == 'classification':
            # Classification: direct mapping
            # Assume classes: 0=BAIXA, 1=LATERAL, 2=ALTA
            signals = predictions - 1  # [0,1,2] -> [-1,0,1]
            return signals.astype(int)
        
        else:
            raise ValueError(f"Unknown strategy_type: {self.strategy_type}")


class BacktestService:
    """
    Serviço de backtesting que:
    1. Simula trades com modelo
    2. Calcula métricas financeiras
    3. Gera equity curve
    4. Salva resultados
    """
    
    def __init__(
        self,
        model: BaseModel,
        config: BacktestConfig,
        strategy_type: str = 'classification'
    ):
        """
        Args:
            model: Modelo treinado
            config: Configuração de backtest
            strategy_type: 'regression' ou 'classification'
        """
        self.model = model
        self.config = config
        self.strategy = TradingStrategy(
            strategy_type=strategy_type,
            threshold=0.02  # 2% para regression
        )
    
    def run(
        self,
        X_test: np.ndarray,
        prices: np.ndarray,
        timestamps: Optional[np.ndarray] = None,
        verbose: int = 1
    ) -> BacktestResult:
        """
        Executa backtest.
        
        Args:
            X_test: Features de teste
            prices: Preços históricos (close prices)
            timestamps: Timestamps (opcional)
            verbose: Nível de verbosidade
            
        Returns:
            BacktestResult com métricas e trades
        """
        if verbose > 0:
            print("\n" + "="*80)
            print("💹 BACKTEST SERVICE - Simulando Trading")
            print("="*80)
            print(f"💰 Capital inicial: ${self.config.initial_capital:,.2f}")
            print(f"📊 Amostras: {len(X_test):,}")
            print(f"🎯 Estratégia: {self.strategy.strategy_type}")
            print()
        
        # Gerar predições
        predictions = self.model.predict(X_test)
        
        if self.strategy.strategy_type == 'classification':
            signals = self.strategy.generate_signals(np.argmax(predictions, axis=1))
        else:
            signals = self.strategy.generate_signals(predictions.ravel())
        
        # Simular trades
        trades, equity_curve = self._simulate_trades(
            signals, prices, timestamps
        )
        
        # Calcular métricas
        result = self._calculate_metrics(trades, equity_curve)
        
        # Imprimir resultados
        if verbose > 0:
            self.print_results(result)
        
        return result
    
    def _simulate_trades(
        self,
        signals: np.ndarray,
        prices: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> tuple[List[Trade], pd.DataFrame]:
        """
        Simula execução de trades.
        
        Returns:
            (lista de trades, equity curve)
        """
        trades: List[Trade] = []
        capital = self.config.initial_capital
        position = 0  # 0: neutral, 1: long, -1: short
        entry_price = 0.0
        entry_idx = 0
        
        equity_history = []
        
        for i in range(len(signals)):
            current_price = prices[i]
            current_signal = signals[i]
            
            # Registrar equity
            current_equity = capital
            if position != 0:
                pnl = position * (current_price - entry_price) * (capital / entry_price)
                current_equity = capital + pnl
            
            equity_history.append({
                'index': i,
                'timestamp': timestamps[i] if timestamps is not None else i,
                'price': current_price,
                'signal': current_signal,
                'position': position,
                'equity': current_equity
            })
            
            # Lógica de trading
            if position == 0 and current_signal != 0:
                # Abrir posição
                position = current_signal
                entry_price = current_price
                entry_idx = i
            
            elif position != 0 and (current_signal == -position or current_signal == 0):
                # Fechar posição
                exit_price = current_price
                pnl = position * (exit_price - entry_price)
                pnl_pct = (pnl / entry_price) * 100
                
                # Aplicar custos
                cost = self.config.transaction_cost * 2  # entrada + saída
                pnl_net = pnl - cost
                
                # Atualizar capital
                position_size = capital
                capital = capital + (pnl_net * position_size / entry_price)
                
                # Registrar trade
                trade = Trade(
                    entry_price=entry_price,
                    exit_price=exit_price,
                    entry_time=timestamps[entry_idx] if timestamps is not None else entry_idx,
                    exit_time=timestamps[i] if timestamps is not None else i,
                    direction=TradeDirection.LONG if position == 1 else TradeDirection.SHORT,
                    pnl=pnl_net,
                    pnl_percent=pnl_pct
                )
                trades.append(trade)
                
                # Reset
                position = 0
                entry_price = 0.0
        
        # Fechar posição final se necessário
        if position != 0:
            exit_price = prices[-1]
            pnl = position * (exit_price - entry_price)
            pnl_pct = (pnl / entry_price) * 100
            cost = self.config.transaction_cost
            pnl_net = pnl - cost
            
            capital = capital + (pnl_net * capital / entry_price)
            
            trade = Trade(
                entry_price=entry_price,
                exit_price=exit_price,
                entry_time=timestamps[entry_idx] if timestamps is not None else entry_idx,
                exit_time=timestamps[-1] if timestamps is not None else len(prices)-1,
                direction=TradeDirection.LONG if position == 1 else TradeDirection.SHORT,
                pnl=pnl_net,
                pnl_percent=pnl_pct
            )
            trades.append(trade)
        
        equity_curve = pd.DataFrame(equity_history)
        
        return trades, equity_curve
    
    def _calculate_metrics(
        self,
        trades: List[Trade],
        equity_curve: pd.DataFrame
    ) -> BacktestResult:
        """Calcula métricas de performance."""
        if not trades:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                profit_factor=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                trades=[],
                equity_curve=equity_curve
            )
        
        # Trades
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl < 0]
        
        winning_trades = len(wins)
        losing_trades = len(losses)
        total_trades = len(trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # PnL
        avg_win = np.mean([t.pnl for t in wins]) if wins else 0.0
        avg_loss = np.mean([t.pnl for t in losses]) if losses else 0.0
        total_pnl = sum(t.pnl for t in trades)
        total_return = (equity_curve['equity'].iloc[-1] / self.config.initial_capital - 1) * 100
        
        # Profit Factor
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = abs(sum(t.pnl for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        # Sharpe Ratio
        returns = equity_curve['equity'].pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
        
        # Max Drawdown
        cummax = equity_curve['equity'].cummax()
        drawdown = (equity_curve['equity'] - cummax) / cummax
        max_drawdown = abs(drawdown.min()) * 100
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            trades=trades,
            equity_curve=equity_curve
        )
    
    def print_results(self, result: BacktestResult) -> None:
        """Imprime resultados formatados."""
        print("📊 RESULTADOS DO BACKTEST:")
        print("-" * 80)
        print(f"   Total de Trades:      {result.total_trades}")
        print(f"   Trades Vencedores:    {result.winning_trades}")
        print(f"   Trades Perdedores:    {result.losing_trades}")
        print(f"   Win Rate:             {result.win_rate*100:.2f}%")
        print()
        print(f"💰 PERFORMANCE FINANCEIRA:")
        print("-" * 80)
        print(f"   Retorno Total:        {result.total_return:.2f}%")
        print(f"   Sharpe Ratio:         {result.sharpe_ratio:.2f}")
        print(f"   Max Drawdown:         {result.max_drawdown:.2f}%")
        print(f"   Profit Factor:        {result.profit_factor:.2f}")
        print(f"   Ganho Médio:          ${result.avg_win:.2f}")
        print(f"   Perda Média:          ${result.avg_loss:.2f}")
        print()
        
        # Análise
        if result.win_rate > 0.55:
            print("✅ Win Rate EXCELENTE (>55%)")
        elif result.win_rate > 0.45:
            print("⚠️  Win Rate OK (45-55%)")
        else:
            print("❌ Win Rate BAIXO (<45%)")
        
        if result.sharpe_ratio > 1.5:
            print("✅ Sharpe Ratio EXCELENTE (>1.5)")
        elif result.sharpe_ratio > 0.8:
            print("⚠️  Sharpe Ratio OK (0.8-1.5)")
        else:
            print("❌ Sharpe Ratio BAIXO (<0.8)")
        
        print("=" * 80 + "\n")
    
    def save_results(
        self,
        result: BacktestResult,
        output_dir: Path,
        prefix: str = "backtest"
    ) -> None:
        """
        Salva resultados do backtest.
        
        Args:
            result: Resultado do backtest
            output_dir: Diretório de saída
            prefix: Prefixo para arquivos
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar métricas
        metrics_path = output_dir / f"{prefix}_metrics_{timestamp}.json"
        metrics_dict = {
            'total_trades': result.total_trades,
            'winning_trades': result.winning_trades,
            'losing_trades': result.losing_trades,
            'win_rate': result.win_rate,
            'total_return': result.total_return,
            'sharpe_ratio': result.sharpe_ratio,
            'max_drawdown': result.max_drawdown,
            'profit_factor': result.profit_factor,
            'avg_win': result.avg_win,
            'avg_loss': result.avg_loss
        }
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        print(f"✅ Métricas salvas em: {metrics_path}")
        
        # Salvar equity curve
        equity_path = output_dir / f"{prefix}_equity_{timestamp}.csv"
        result.equity_curve.to_csv(equity_path, index=False)
        
        print(f"✅ Equity curve salva em: {equity_path}")
        
        # Salvar trades
        trades_path = output_dir / f"{prefix}_trades_{timestamp}.csv"
        trades_df = pd.DataFrame([
            {
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'entry_time': t.entry_time,
                'exit_time': t.exit_time,
                'direction': t.direction.value,
                'pnl': t.pnl,
                'pnl_percent': t.pnl_percent
            }
            for t in result.trades
        ])
        trades_df.to_csv(trades_path, index=False)
        
        print(f"✅ Trades salvos em: {trades_path}")


# Export
__all__ = [
    'BacktestService',
    'BacktestResult',
    'TradingStrategy'
]
