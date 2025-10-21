"""
Walk-forward validation para classificação direcional.
Treina em janelas deslizantes para evitar data leakage temporal.
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple
import json

from src.ml_v2.preprocess_classification import DirectionalPreprocessor
from src.ml_v2.models.directional_model import (
    build_directional_lstm,
    get_directional_callbacks,
    calculate_class_weights,
    evaluate_directional_model,
    print_directional_results
)


def walkforward_classification(
    df: pd.DataFrame,
    feature_cols: List[str],
    n_folds: int = 5,
    train_size_months: int = 12,
    test_size_months: int = 3,
    **model_params
) -> Dict:
    """
    Walk-forward validation para classificação direcional.
    
    Args:
        df: DataFrame com dados temporais
        feature_cols: Colunas de features
        n_folds: Número de folds temporais
        train_size_months: Tamanho da janela de treino (meses)
        test_size_months: Tamanho da janela de teste (meses)
        **model_params: Parâmetros do modelo
        
    Returns:
        Dict com resultados de todos os folds
    """
    
    print("\n" + "="*80)
    print("WALK-FORWARD VALIDATION - CLASSIFICAÇÃO DIRECIONAL")
    print("="*80 + "\n")
    
    # Parâmetros do preprocessor
    lookback = model_params.get('lookback', 60)
    horizon = model_params.get('horizon', 6)
    threshold = model_params.get('threshold', 0.3)
    
    # Parâmetros do modelo
    epochs = model_params.get('epochs', 20)
    batch_size = model_params.get('batch_size', 64)
    units = model_params.get('units', 64)
    dropout = model_params.get('dropout', 0.4)
    lr = model_params.get('lr', 1e-3)
    
    print(f"📊 Configurações:")
    print(f"   Folds: {n_folds}")
    print(f"   Janela treino: {train_size_months} meses")
    print(f"   Janela teste: {test_size_months} meses")
    print(f"   Threshold: ±{threshold}%")
    print(f"   Horizon: {horizon} períodos ({horizon * 0.5:.1f}h)")
    
    # Converter Date para datetime se necessário
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
    
    results = {
        'folds': [],
        'avg_metrics': {},
        'config': model_params
    }
    
    # Calcular janelas temporais
    total_samples = len(df)
    samples_per_month = total_samples // 36  # Aproximadamente 36 meses de dados
    
    train_size = train_size_months * samples_per_month
    test_size = test_size_months * samples_per_month
    step_size = test_size  # Avanço por fold
    
    print(f"\n📊 Tamanhos calculados:")
    print(f"   Samples por mês: ~{samples_per_month:,}")
    print(f"   Treino: {train_size:,} samples")
    print(f"   Teste: {test_size:,} samples")
    
    for fold in range(n_folds):
        print(f"\n" + "="*60)
        print(f"FOLD {fold + 1}/{n_folds}")
        print("="*60)
        
        # Calcular índices
        test_start = train_size + fold * step_size
        test_end = test_start + test_size
        train_start = test_start - train_size
        
        if test_end > total_samples:
            print(f"⚠️  Fold {fold + 1} excede dados disponíveis. Parando.")
            break
        
        # Extrair dados
        df_train = df.iloc[train_start:test_start].copy()
        df_test = df.iloc[test_start:test_end].copy()
        
        print(f"📅 Período treino: {df_train['Date'].iloc[0].strftime('%Y-%m-%d')} "
              f"até {df_train['Date'].iloc[-1].strftime('%Y-%m-%d')}")
        print(f"📅 Período teste: {df_test['Date'].iloc[0].strftime('%Y-%m-%d')} "
              f"até {df_test['Date'].iloc[-1].strftime('%Y-%m-%d')}")
        
        try:
            # Preprocessamento
            preprocessor = DirectionalPreprocessor(
                feature_cols=feature_cols,
                price_col="Close",
                lookback=lookback,
                horizon=horizon,
                threshold_pct=threshold
            )
            
            X_train, y_train = preprocessor.fit_transform(df_train)
            X_test, y_test = preprocessor.transform(df_test)
            
            if len(X_train) == 0 or len(X_test) == 0:
                print(f"❌ Fold {fold + 1}: Dados insuficientes")
                continue
            
            print(f"🎯 Treino: {X_train.shape}, Teste: {X_test.shape}")
            
            # Class weights
            class_weights = calculate_class_weights(y_train)
            
            # Construir modelo
            input_shape = (X_train.shape[1], X_train.shape[2])
            
            model = build_directional_lstm(
                input_shape=input_shape,
                n_classes=3,
                lstm_units=units,
                dropout=dropout,
                learning_rate=lr
            )
            
            # Callbacks
            callbacks = get_directional_callbacks(
                patience_early=8,
                patience_lr=4,
                monitor='val_accuracy'
            )
            
            # Split interno para validação
            val_split = 0.15
            val_samples = int(len(X_train) * val_split)
            
            X_train_fold = X_train[:-val_samples]
            y_train_fold = y_train[:-val_samples]
            X_val_fold = X_train[-val_samples:]
            y_val_fold = y_train[-val_samples:]
            
            print(f"🔥 Treinando fold {fold + 1}...")
            
            # Treinar
            history = model.fit(
                X_train_fold, y_train_fold,
                validation_data=(X_val_fold, y_val_fold),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                class_weight=class_weights,
                verbose=0
            )
            
            # Avaliar
            fold_results = evaluate_directional_model(model, X_test, y_test)
            fold_results['fold'] = fold + 1
            fold_results['train_samples'] = len(X_train)
            fold_results['test_samples'] = len(X_test)
            fold_results['epochs_trained'] = len(history.history['loss'])
            
            results['folds'].append(fold_results)
            
            print(f"✅ Fold {fold + 1} completo:")
            print(f"   Accuracy: {fold_results['accuracy']:.4f}")
            print(f"   F1-macro: {fold_results['f1_macro']:.4f}")
            print(f"   Épocas: {fold_results['epochs_trained']}")
            
        except Exception as e:
            print(f"❌ Erro no fold {fold + 1}: {e}")
            continue
    
    # Calcular métricas médias
    if results['folds']:
        metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
        
        for metric in metrics:
            values = [fold[metric] for fold in results['folds']]
            results['avg_metrics'][metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }
        
        print(f"\n" + "="*80)
        print("RESULTADOS WALK-FORWARD VALIDATION")
        print("="*80)
        
        print(f"\n📊 MÉTRICAS MÉDIAS ({len(results['folds'])} folds):")
        for metric in metrics:
            stats = results['avg_metrics'][metric]
            print(f"   {metric.capitalize()}: "
                  f"{stats['mean']:.4f} ± {stats['std']:.4f} "
                  f"(min: {stats['min']:.4f}, max: {stats['max']:.4f})")
        
        # Análise
        avg_acc = results['avg_metrics']['accuracy']['mean']
        avg_f1 = results['avg_metrics']['f1_macro']['mean']
        
        print(f"\n💡 ANÁLISE WALK-FORWARD:")
        if avg_acc >= 0.45 and avg_f1 >= 0.35:
            print("   ✅ EXCELENTE: Modelo generaliza bem!")
        elif avg_acc >= 0.40 and avg_f1 >= 0.30:
            print("   ✅ BOM: Performance consistente!")
        elif avg_acc >= 0.35:
            print("   ⚠️  MÉDIO: Melhor que aleatório.")
        else:
            print("   ❌ RUIM: Não consegue generalizar.")
        
        baseline_improvement = (avg_acc - 1/3) / (1/3) * 100
        print(f"   📈 Melhoria vs baseline: {baseline_improvement:+.1f}%")
    
    return results


def save_walkforward_results(results: Dict, output_path: str):
    """Salva resultados do walk-forward."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Resultados salvos: {output_path}")


if __name__ == "__main__":
    # Teste básico
    print("Testando walk-forward validation...")
    
    # Dados sintéticos
    np.random.seed(42)
    n = 10000
    
    dates = pd.date_range('2020-01-01', periods=n, freq='30min')
    
    df = pd.DataFrame({
        'Date': dates,
        'Close': np.cumsum(np.random.randn(n) * 0.01) + 100,
        'Volume': np.random.randn(n),
        'RSI': np.random.randn(n)
    })
    
    # Teste rápido
    results = walkforward_classification(
        df=df,
        feature_cols=['Volume', 'RSI'],
        n_folds=2,
        train_size_months=6,
        test_size_months=2,
        epochs=3,
        lookback=30,
        threshold=0.5
    )
    
    print("✅ Teste concluído!")