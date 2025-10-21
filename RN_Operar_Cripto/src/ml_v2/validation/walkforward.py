"""
Walk-forward validation: validação temporal robusta.
Cada fold tem seu próprio fit de scaler e modelo.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from ..preprocess import DataPreprocessor
from ..models.lstm_model import build_lstm
from ..metrics import mae_mape_rmse_usd, hit_rate_directional


def create_walk_forward_splits(
    n_samples: int, 
    n_folds: int = 3,
    test_size: float = 0.15
) -> List[Tuple[int, int, int]]:
    """
    Cria splits para walk-forward validation.
    
    Args:
        n_samples: Total de amostras
        n_folds: Número de folds
        test_size: Fração para teste em cada fold
        
    Returns:
        Lista de (train_end, val_end, test_end)
    """
    test_samples = int(n_samples * test_size)
    fold_size = (n_samples - test_samples) // n_folds
    
    splits = []
    for i in range(n_folds):
        test_end = n_samples - i * fold_size
        test_start = test_end - test_samples
        train_end = test_start - int(test_samples * 0.5)  # Validação = 50% do teste
        
        if train_end > fold_size:  # Garantir treino mínimo
            splits.append((train_end, test_start, test_end))
    
    return list(reversed(splits))  # Ordem cronológica


def run_walkforward(
    df: pd.DataFrame,
    feature_cols: List[str],
    lookback: int = 60,
    n_folds: int = 3,
    epochs: int = 50,
    batch_size: int = 32,
    verbose: int = 0
) -> Dict[str, Any]:
    """
    Executa walk-forward validation.
    
    Args:
        df: DataFrame completo
        feature_cols: Colunas de features
        lookback: Janela temporal
        n_folds: Número de folds
        epochs: Épocas de treino
        batch_size: Batch size
        verbose: Verbosidade do treino
        
    Returns:
        Dict com métricas por fold e agregadas
    """
    from tensorflow import keras
    
    splits = create_walk_forward_splits(len(df), n_folds)
    fold_results = []
    
    print(f"\n{'='*80}")
    print(f"WALK-FORWARD VALIDATION: {n_folds} folds")
    print(f"{'='*80}\n")
    
    for fold_idx, (train_end, val_end, test_end) in enumerate(splits, 1):
        print(f"Fold {fold_idx}/{n_folds}: train={train_end}, val={val_end}, test={test_end}")
        
        # Split dos dados
        df_train = df.iloc[:train_end]
        df_val = df.iloc[train_end:val_end]
        df_test = df.iloc[val_end:test_end]
        
        # Preprocessamento (fit APENAS no treino deste fold)
        preprocessor = DataPreprocessor(feature_cols, target_col="Close", lookback=lookback)
        preprocessor.fit(df_train)
        
        X_train, y_train = preprocessor.transform(df_train)
        X_val, y_val = preprocessor.transform(df_val)
        X_test, y_test = preprocessor.transform(df_test)
        
        # Modelo novo para cada fold
        model = build_lstm(input_shape=X_train.shape[1:])
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=10,
                restore_best_weights=True,
                verbose=0
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                patience=5,
                factor=0.5,
                min_lr=1e-6,
                verbose=0
            ),
        ]
        
        # Treino
        model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            shuffle=False,  # TEMPORAL!
            callbacks=callbacks,
            verbose=verbose
        )
        
        # Predição no teste
        y_pred_scaled = model.predict(X_test, verbose=0).ravel()
        y_pred_usd = preprocessor.inverse_target(y_pred_scaled)
        y_true_usd = preprocessor.inverse_target(y_test)
        
        # Close(t) para hit rate
        y_prev_usd = df_test['Close'].values[lookback-1:-1]
        min_len = min(len(y_true_usd), len(y_prev_usd))
        y_true_usd = y_true_usd[:min_len]
        y_pred_usd = y_pred_usd[:min_len]
        y_prev_usd = y_prev_usd[:min_len]
        
        # Métricas
        metrics = mae_mape_rmse_usd(y_true_usd, y_pred_usd)
        hr = hit_rate_directional(y_true_usd, y_pred_usd, y_prev_usd)
        
        fold_result = {
            "fold": fold_idx,
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            **metrics,
            "hit_rate": hr
        }
        
        fold_results.append(fold_result)
        
        print(f"  MAE: {metrics['mae_usd']:.2f} USD | Hit Rate: {hr:.4f}")
    
    # Agregação
    mae_values = [r['mae_usd'] for r in fold_results]
    rmse_values = [r['rmse_usd'] for r in fold_results]
    mape_values = [r['mape_pct'] for r in fold_results]
    hr_values = [r['hit_rate'] for r in fold_results]
    
    summary = {
        "folds": fold_results,
        "summary": {
            "mae_usd_mean": float(np.mean(mae_values)),
            "mae_usd_std": float(np.std(mae_values)),
            "rmse_usd_mean": float(np.mean(rmse_values)),
            "rmse_usd_std": float(np.std(rmse_values)),
            "mape_pct_mean": float(np.mean(mape_values)),
            "mape_pct_std": float(np.std(mape_values)),
            "hit_rate_mean": float(np.mean(hr_values)),
            "hit_rate_std": float(np.std(hr_values)),
        }
    }
    
    print(f"\n{'='*80}")
    print("RESUMO WALK-FORWARD")
    print(f"{'='*80}")
    print(f"MAE (USD):   {summary['summary']['mae_usd_mean']:.2f} ± {summary['summary']['mae_usd_std']:.2f}")
    print(f"RMSE (USD):  {summary['summary']['rmse_usd_mean']:.2f} ± {summary['summary']['rmse_usd_std']:.2f}")
    print(f"MAPE (%):    {summary['summary']['mape_pct_mean']:.4f} ± {summary['summary']['mape_pct_std']:.4f}")
    print(f"Hit Rate:    {summary['summary']['hit_rate_mean']:.4f} ± {summary['summary']['hit_rate_std']:.4f}")
    print(f"{'='*80}\n")
    
    return summary
