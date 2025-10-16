"""
Backtest engine com custos reais.
Fee, slippage, latência e threshold de confiança.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any


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
    Backtest de estratégia baseada em predições de regressão.
    
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
        
    Lógica:
        - Calcula retorno esperado: (pred - close_t) / close_t
        - Se |ret_exp| > (custo_total + threshold): abre posição
        - Executa no candle t+latency
        - Fecha no t+latency+1
    """
    close = df['Close'].values
    dates = df['Date'].values if 'Date' in df.columns else np.arange(len(df))
    
    # Custos totais (entrada + saída)
    cost_bps = fee_bps + slippage_bps
    cost_frac = cost_bps / 10000.0
    threshold_frac = threshold_bps / 10000.0
    
    # Alinhamento: preds correspondem a Close(t+1)
    # Queremos comparar pred[t] com close[t] para decidir entrada
    min_len = min(len(preds_usd), len(close))
    preds_usd = preds_usd[:min_len]
    close = close[:min_len]
    dates = dates[:min_len]
    
    # Resultados
    equity = [initial_capital]
    positions = []
    returns = []
    
    for t in range(len(preds_usd) - latency - 1):
        # Retorno esperado baseado na predição
        exp_return = (preds_usd[t] - close[t]) / close[t]
        
        # Sinal: long se exp_return > threshold+cost, short se < -(threshold+cost)
        if exp_return > (threshold_frac + 2 * cost_frac):
            signal = 1  # Long
        elif exp_return < -(threshold_frac + 2 * cost_frac):
            signal = -1  # Short
        else:
            signal = 0  # Sem posição
        
        # Execução com latência
        if signal != 0:
            px_entry = close[t + latency]
            px_exit = close[t + latency + 1]
            
            # Retorno bruto
            gross_return = (px_exit - px_entry) / px_entry * signal
            
            # Retorno líquido (descontar custos de entrada e saída)
            net_return = gross_return - 2 * cost_frac
            
            returns.append(net_return)
            positions.append({
                'entry_idx': t + latency,
                'exit_idx': t + latency + 1,
                'signal': signal,
                'gross_return': gross_return,
                'net_return': net_return
            })
        else:
            returns.append(0.0)
        
        # Atualizar equity
        equity.append(equity[-1] * (1.0 + returns[-1]))
    
    # Criar equity curve
    equity_dates = dates[:len(equity)]
    equity_curve = pd.DataFrame({
        'Date': equity_dates,
        'Equity': equity,
        'Return': [0.0] + returns
    })
    
    # Calcular métricas
    metrics = calculate_metrics(equity_curve, initial_capital, positions)
    
    return equity_curve, metrics


def calculate_metrics(
    equity_curve: pd.DataFrame,
    initial_capital: float,
    positions: list
) -> Dict[str, Any]:
    """
    Calcula métricas de performance do backtest.
    
    Args:
        equity_curve: DataFrame com equity
        initial_capital: Capital inicial
        positions: Lista de posições executadas
        
    Returns:
        Dict com métricas
    """
    equity = equity_curve['Equity'].values
    returns = equity_curve['Return'].values[1:]  # Pular primeiro (zero)
    
    # Total return
    total_return = (equity[-1] - initial_capital) / initial_capital
    
    # CAGR (assumindo dados diários, ajustar se necessário)
    n_periods = len(equity)
    years = n_periods / (365 * 48)  # 30min candles: 48 por dia
    cagr = (equity[-1] / initial_capital) ** (1 / years) - 1 if years > 0 else 0.0
    
    # Max Drawdown
    cummax = np.maximum.accumulate(equity)
    drawdown = (equity - cummax) / cummax
    max_dd = float(np.min(drawdown))
    
    # Sharpe Ratio (anualized)
    if len(returns) > 0 and np.std(returns) > 0:
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(365 * 48)
    else:
        sharpe = 0.0
    
    # Sortino Ratio
    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0 and np.std(downside_returns) > 0:
        sortino = np.mean(returns) / np.std(downside_returns) * np.sqrt(365 * 48)
    else:
        sortino = 0.0
    
    # Win rate
    winning_trades = [p for p in positions if p['net_return'] > 0]
    losing_trades = [p for p in positions if p['net_return'] <= 0]
    win_rate = len(winning_trades) / len(positions) if positions else 0.0
    
    # Profit factor
    gross_profit = sum(p['net_return'] for p in winning_trades)
    gross_loss = abs(sum(p['net_return'] for p in losing_trades))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
    
    # Exposure
    exposure = len(positions) / len(equity) if len(equity) > 0 else 0.0
    
    return {
        'total_return': float(total_return),
        'cagr': float(cagr),
        'max_drawdown': float(max_dd),
        'sharpe_ratio': float(sharpe),
        'sortino_ratio': float(sortino),
        'win_rate': float(win_rate),
        'profit_factor': float(profit_factor),
        'exposure': float(exposure),
        'total_trades': len(positions),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'final_equity': float(equity[-1]),
        'initial_capital': float(initial_capital)
    }


def print_backtest_report(metrics: Dict[str, Any]):
    """
    Imprime relatório do backtest.
    
    Args:
        metrics: Métricas calculadas
    """
    print("\n" + "="*80)
    print("BACKTEST REPORT")
    print("="*80)
    print(f"Initial Capital:    ${metrics['initial_capital']:,.2f}")
    print(f"Final Equity:       ${metrics['final_equity']:,.2f}")
    print(f"Total Return:       {metrics['total_return']*100:.2f}%")
    print(f"CAGR:               {metrics['cagr']*100:.2f}%")
    print(f"Max Drawdown:       {metrics['max_drawdown']*100:.2f}%")
    print("-"*80)
    print(f"Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio:      {metrics['sortino_ratio']:.2f}")
    print(f"Profit Factor:      {metrics['profit_factor']:.2f}")
    print("-"*80)
    print(f"Total Trades:       {metrics['total_trades']}")
    print(f"Winning Trades:     {metrics['winning_trades']}")
    print(f"Losing Trades:      {metrics['losing_trades']}")
    print(f"Win Rate:           {metrics['win_rate']*100:.2f}%")
    print(f"Exposure:           {metrics['exposure']*100:.2f}%")
    print("="*80 + "\n")
