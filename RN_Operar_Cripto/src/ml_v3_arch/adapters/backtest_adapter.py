"""
BacktestAdapter - Adapter para backtesting v2 → v3.

Permite que código v2 use BacktestService v3.
Mantém interface compatível com ml_v2.backtest.

Padrão Adapter: Converte interface v3 para interface v2.
"""
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np

from ..services.backtest_service import BacktestService
from ..domain.entities import BacktestConfig, Trade


class BacktestAdapter:
    """
    Adapter que expõe interface v2 usando BacktestService v3.
    
    Interface v2 (mantida):
        - backtest_regression(df, preds_usd, fee_bps, slippage_bps, ...)
        - backtest_classifier(df, predictions, probabilities, ...)
        - print_backtest_report(metrics)
    
    Implementação v3 (usada internamente):
        - BacktestService com validações
        - Entidades Trade tipadas
        - Métricas financeiras robustas
    
    Exemplo:
        >>> # Código v2 continua funcionando:
        >>> adapter = BacktestAdapter()
        >>> equity_curve, metrics = adapter.backtest_regression(
        ...     df=df_test,
        ...     preds_usd=predictions,
        ...     fee_bps=10.0,
        ...     slippage_bps=5.0
        ... )
    """
    
    def __init__(self):
        """Inicializa adapter."""
        self.service = None  # Criado dinamicamente por backtest
    
    @staticmethod
    def backtest_regression(
        df: pd.DataFrame,
        preds_usd: np.ndarray,
        fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
        latency: int = 1,
        threshold_bps: float = 20.0,
        initial_capital: float = 10000.0
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Backtest de estratégia de regressão (compatível v2).
        
        Args:
            df: DataFrame com coluna 'Close' e 'Date'
            preds_usd: Predições do modelo (Close futuro)
            fee_bps: Taxa de exchange (basis points)
            slippage_bps: Slippage (basis points)
            latency: Candles de delay para execução
            threshold_bps: Threshold mínimo de retorno esperado
            initial_capital: Capital inicial
            
        Returns:
            equity_curve: DataFrame com equity ao longo do tempo
            metrics: Dict com métricas de performance
        """
        # Criar config v3
        config = BacktestConfig(
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            position_size=0.95,  # 95% do capital
            min_confidence=0.0,  # Não usado em regressão
            threshold_bps=threshold_bps
        )
        
        # Preparar dados para v3
        close = df['Close'].values
        dates = df['Date'].values if 'Date' in df.columns else np.arange(len(df))
        
        # Alinhar
        min_len = min(len(preds_usd), len(close))
        preds_usd = preds_usd[:min_len]
        close = close[:min_len]
        
        # Gerar sinais baseados nas predições
        signals = BacktestAdapter._generate_regression_signals(
            preds_usd, close, threshold_bps, fee_bps, slippage_bps
        )
        
        # Criar DataFrame para backtest v3
        df_bt = pd.DataFrame({
            'Date': dates[:len(signals)],
            'Close': close[:len(signals)],
            'Signal': signals
        })
        
        # Executar backtest usando v3
        service = BacktestService(config)
        trades, history = service.run_backtest(df_bt)
        
        # Converter para formato v2
        equity_curve = BacktestAdapter._format_equity_curve_v2(history, dates)
        metrics = BacktestAdapter._calculate_metrics_v2(trades, history, initial_capital)
        
        return equity_curve, metrics
    
    @staticmethod
    def backtest_classifier(
        df: pd.DataFrame,
        predictions: np.ndarray,
        probabilities: np.ndarray,
        fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
        min_confidence: float = 0.6,
        initial_capital: float = 100000.0,
        position_size: float = 0.95
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Backtest de estratégia de classificação (compatível v2).
        
        Args:
            df: DataFrame com coluna 'Close' e 'Date'
            predictions: Classes preditas (0=BAIXA, 1=LATERAL, 2=ALTA)
            probabilities: Probabilidades por classe (n_samples, n_classes)
            fee_bps: Taxa de exchange (basis points)
            slippage_bps: Slippage (basis points)
            min_confidence: Confiança mínima para entrar (0-1)
            initial_capital: Capital inicial
            position_size: Fração do capital a usar (0-1)
            
        Returns:
            equity_curve: DataFrame com equity ao longo do tempo
            metrics: Dict com métricas de performance
        """
        # Criar config v3
        config = BacktestConfig(
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            position_size=position_size,
            min_confidence=min_confidence,
            threshold_bps=20.0  # Default
        )
        
        # Gerar sinais baseados nas predições
        signals = BacktestAdapter._generate_classification_signals(
            predictions, probabilities, min_confidence
        )
        
        # Criar DataFrame para backtest v3
        close = df['Close'].values
        dates = df['Date'].values if 'Date' in df.columns else np.arange(len(df))
        
        min_len = min(len(signals), len(close))
        
        df_bt = pd.DataFrame({
            'Date': dates[:min_len],
            'Close': close[:min_len],
            'Signal': signals[:min_len]
        })
        
        # Executar backtest usando v3
        service = BacktestService(config)
        trades, history = service.run_backtest(df_bt)
        
        # Converter para formato v2
        equity_curve = BacktestAdapter._format_equity_curve_v2(history, dates[:min_len])
        metrics = BacktestAdapter._calculate_metrics_v2(trades, history, initial_capital)
        
        return equity_curve, metrics
    
    @staticmethod
    def _generate_regression_signals(
        preds_usd: np.ndarray,
        close: np.ndarray,
        threshold_bps: float,
        fee_bps: float,
        slippage_bps: float
    ) -> np.ndarray:
        """
        Gera sinais de trading para regressão.
        
        Returns:
            Array de sinais: 1 (long), -1 (short), 0 (neutral)
        """
        cost_bps = fee_bps + slippage_bps
        cost_frac = cost_bps / 10000.0
        threshold_frac = threshold_bps / 10000.0
        
        signals = np.zeros(len(preds_usd), dtype=int)
        
        for t in range(len(preds_usd)):
            exp_return = (preds_usd[t] - close[t]) / close[t]
            
            if exp_return > (threshold_frac + 2 * cost_frac):
                signals[t] = 1  # Long
            elif exp_return < -(threshold_frac + 2 * cost_frac):
                signals[t] = -1  # Short
            else:
                signals[t] = 0  # Neutral
        
        return signals
    
    @staticmethod
    def _generate_classification_signals(
        predictions: np.ndarray,
        probabilities: np.ndarray,
        min_confidence: float
    ) -> np.ndarray:
        """
        Gera sinais de trading para classificação.
        
        Lógica:
        - Classe 0 (BAIXA) + confiança > min → Short (-1)
        - Classe 2 (ALTA) + confiança > min → Long (1)
        - Classe 1 (LATERAL) ou baixa confiança → Neutral (0)
        
        Returns:
            Array de sinais: 1 (long), -1 (short), 0 (neutral)
        """
        signals = np.zeros(len(predictions), dtype=int)
        
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            confidence = probs[pred]
            
            if confidence >= min_confidence:
                if pred == 2:  # ALTA
                    signals[i] = 1
                elif pred == 0:  # BAIXA
                    signals[i] = -1
                else:  # LATERAL
                    signals[i] = 0
            else:
                signals[i] = 0  # Confiança baixa
        
        return signals
    
    @staticmethod
    def _format_equity_curve_v2(
        history: List[Dict[str, Any]],
        dates: np.ndarray
    ) -> pd.DataFrame:
        """
        Formata equity curve para formato v2.
        
        Returns:
            DataFrame com colunas: Date, Equity
        """
        if not history:
            return pd.DataFrame({'Date': dates, 'Equity': [10000.0] * len(dates)})
        
        equity_values = [h['capital'] for h in history]
        equity_dates = dates[:len(equity_values)]
        
        return pd.DataFrame({
            'Date': equity_dates,
            'Equity': equity_values
        })
    
    @staticmethod
    def _calculate_metrics_v2(
        trades: List[Trade],
        history: List[Dict[str, Any]],
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Calcula métricas no formato v2.
        
        Returns:
            Dict com métricas: total_return, sharpe, max_drawdown, win_rate, etc.
        """
        if not trades or not history:
            return {
                'total_trades': 0,
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'final_capital': initial_capital
            }
        
        # Retorno total
        final_capital = history[-1]['capital']
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Trades vencedores/perdedores
        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl < 0]
        
        win_rate = len(wins) / len(trades) if trades else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = abs(np.mean(losses)) if losses else 0.0
        
        # Profit factor
        total_wins = sum(wins) if wins else 0.0
        total_losses = abs(sum(losses)) if losses else 0.0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0
        
        # Sharpe Ratio (aproximado com returns diários)
        returns = []
        for i in range(1, len(history)):
            ret = (history[i]['capital'] - history[i-1]['capital']) / history[i-1]['capital']
            returns.append(ret)
        
        if returns:
            mean_ret = np.mean(returns)
            std_ret = np.std(returns)
            sharpe_ratio = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max Drawdown
        capitals = [h['capital'] for h in history]
        peak = capitals[0]
        max_dd = 0.0
        
        for cap in capitals:
            if cap > peak:
                peak = cap
            dd = (peak - cap) / peak
            if dd > max_dd:
                max_dd = dd
        
        return {
            'total_trades': len(trades),
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_capital': final_capital
        }
    
    @staticmethod
    def print_backtest_report(metrics: Dict[str, Any]):
        """
        Imprime relatório de backtest (compatível v2).
        
        Args:
            metrics: Dict com métricas
        """
        print("\n" + "="*80)
        print("📊 BACKTEST REPORT")
        print("="*80)
        print(f"\n💰 Retorno Total: {metrics['total_return']:.2%}")
        print(f"📈 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"📉 Max Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"\n🎯 Total de Trades: {metrics['total_trades']}")
        print(f"✅ Win Rate: {metrics['win_rate']:.2%}")
        print(f"💵 Ganho Médio: ${metrics['avg_win']:.2f}")
        print(f"💸 Perda Média: ${metrics['avg_loss']:.2f}")
        print(f"⚖️  Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"\n💼 Capital Final: ${metrics['final_capital']:,.2f}")
        print("="*80 + "\n")
    
    def __repr__(self) -> str:
        """Representação string."""
        return "BacktestAdapter(service=BacktestService)"
