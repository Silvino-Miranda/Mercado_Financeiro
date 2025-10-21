"""
Métricas em USD e baselines para comparação.
Sem enganação: tudo desnormalizado, direção real.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error


def mae_mape_rmse_usd(y_true_usd: np.ndarray, y_pred_usd: np.ndarray) -> Dict[str, float]:
    """
    Métricas de erro em USD (desnormalizadas).
    
    Args:
        y_true_usd: Valores reais em USD
        y_pred_usd: Predições em USD
        
    Returns:
        Dict com mae_usd, rmse_usd, mape_pct
    """
    mae = mean_absolute_error(y_true_usd, y_pred_usd)
    rmse = np.sqrt(mean_squared_error(y_true_usd, y_pred_usd))
    
    # MAPE: cuidado com divisão por zero
    mape = float(
        np.mean(np.abs((y_true_usd - y_pred_usd) / np.clip(y_true_usd, 1e-6, None))) * 100.0
    )
    
    return {
        "mae_usd": float(mae),
        "rmse_usd": float(rmse),
        "mape_pct": mape
    }


def hit_rate_directional(
    y_true_usd: np.ndarray, 
    y_pred_usd: np.ndarray, 
    y_prev_usd: np.ndarray
) -> float:
    """
    Hit rate: % de acerto na direção do movimento.
    
    Args:
        y_true_usd: Close real (t+1)
        y_pred_usd: Close predito (t+1)
        y_prev_usd: Close anterior (t)
        
    Returns:
        Hit rate [0, 1]
    """
    true_dir = np.sign(y_true_usd - y_prev_usd)
    pred_dir = np.sign(y_pred_usd - y_prev_usd)
    
    return float(np.mean(true_dir == pred_dir))


def baseline_naive1(y_prev_usd: np.ndarray) -> np.ndarray:
    """
    Baseline Naive1: predição = último valor conhecido.
    "Amanhã será igual a hoje."
    
    Args:
        y_prev_usd: Close(t)
        
    Returns:
        Predições: y_prev[:-1] alinhado com y_true[1:]
    """
    return y_prev_usd


def baseline_sma20(df: pd.DataFrame, lookback: int) -> np.ndarray:
    """
    Baseline SMA20: média móvel simples de 20 períodos.
    
    Args:
        df: DataFrame com coluna 'Close'
        lookback: Lookback usado no preprocessamento
        
    Returns:
        SMA20 alinhado com as predições
    """
    close = df['Close'].values
    
    # Calcular SMA20
    sma = pd.Series(close).rolling(window=20, min_periods=1).mean().values
    
    # Alinhar com as sequências (após lookback)
    return sma[lookback:]


def evaluate_model(
    y_true_usd: np.ndarray,
    y_pred_usd: np.ndarray,
    y_prev_usd: np.ndarray,
    model_name: str = "LSTM"
) -> Dict[str, Any]:
    """
    Avalia modelo com métricas completas.
    
    Args:
        y_true_usd: Valores reais
        y_pred_usd: Predições do modelo
        y_prev_usd: Valores anteriores (para hit rate)
        model_name: Nome do modelo
        
    Returns:
        Dict com todas as métricas
    """
    metrics = mae_mape_rmse_usd(y_true_usd, y_pred_usd)
    hr = hit_rate_directional(y_true_usd, y_pred_usd, y_prev_usd)
    
    return {
        "model": model_name,
        **metrics,
        "hit_rate": hr
    }


def compare_with_baselines(
    df: pd.DataFrame,
    y_true_usd: np.ndarray,
    y_pred_lstm: np.ndarray,
    lookback: int
) -> Dict[str, Dict[str, Any]]:
    """
    Compara LSTM com baselines Naive1 e SMA20.
    
    Args:
        df: DataFrame original (para calcular baselines)
        y_true_usd: Valores reais
        y_pred_lstm: Predições do LSTM
        lookback: Lookback usado
        
    Returns:
        Dict com resultados de todos os modelos
    """
    # Pegar Close(t) - valor anterior ao alvo
    y_prev_usd = df['Close'].values[lookback-1:-1]
    
    # Garantir alinhamento
    min_len = min(len(y_true_usd), len(y_pred_lstm), len(y_prev_usd))
    y_true_usd = y_true_usd[:min_len]
    y_pred_lstm = y_pred_lstm[:min_len]
    y_prev_usd = y_prev_usd[:min_len]
    
    # LSTM
    results = {
        "LSTM": evaluate_model(y_true_usd, y_pred_lstm, y_prev_usd, "LSTM")
    }
    
    # Baseline Naive1
    y_pred_naive = baseline_naive1(y_prev_usd)
    results["Naive1"] = evaluate_model(y_true_usd, y_pred_naive, y_prev_usd, "Naive1")
    
    # Baseline SMA20
    y_pred_sma = baseline_sma20(df, lookback)[:min_len]
    results["SMA20"] = evaluate_model(y_true_usd, y_pred_sma, y_prev_usd, "SMA20")
    
    return results


def print_comparison(results: Dict[str, Dict[str, Any]]):
    """
    Imprime comparação formatada.
    
    Args:
        results: Resultados do compare_with_baselines
    """
    print("\n" + "="*80)
    print("COMPARAÇÃO: LSTM vs BASELINES")
    print("="*80)
    print(f"{'Modelo':<10} {'MAE (USD)':<12} {'RMSE (USD)':<12} {'MAPE (%)':<10} {'Hit Rate':<10}")
    print("-"*80)
    
    for model_name, metrics in results.items():
        print(
            f"{model_name:<10} "
            f"{metrics['mae_usd']:<12.2f} "
            f"{metrics['rmse_usd']:<12.2f} "
            f"{metrics['mape_pct']:<10.4f} "
            f"{metrics['hit_rate']:<10.4f}"
        )
    
    print("="*80)
    
    # Verifica se LSTM é melhor
    lstm_mae = results["LSTM"]["mae_usd"]
    naive_mae = results["Naive1"]["mae_usd"]
    sma_mae = results["SMA20"]["mae_usd"]
    
    if lstm_mae >= naive_mae and lstm_mae >= sma_mae:
        print("⚠️  ALERTA: LSTM NÃO SUPEROU OS BASELINES!")
        print("💡 Considere mudar para CLASSIFICAÇÃO DIRECIONAL.\n")
    else:
        print("✅ LSTM superou pelo menos um baseline.\n")
