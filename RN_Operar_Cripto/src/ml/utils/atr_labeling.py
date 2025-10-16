"""
Rotulagem baseada em ATR% para classificação ALTA/LATERAL/BAIXA.

Uso:
    from src.ml.utils.atr_labeling import create_labels_with_atr
    
    df['target'] = create_labels_with_atr(df, horizon=12, k=0.75)
"""

import pandas as pd
import numpy as np


def create_labels_with_atr(df, horizon=12, k=0.75, atr_col='ATR_14'):
    """
    Cria labels ALTA/LATERAL/BAIXA baseado em retorno futuro normalizado por ATR%.
    
    Args:
        df: DataFrame com colunas 'Close' e ATR
        horizon: Número de períodos para frente (ex: 12 = 6h em candles de 30min)
        k: Multiplicador de ATR% (padrão: 0.75)
        atr_col: Nome da coluna ATR (padrão: 'ATR_14')
    
    Returns:
        Series com valores:
        - 2: ALTA (retorno futuro > k × ATR%)
        - 1: LATERAL (retorno futuro entre -k × ATR% e +k × ATR%)
        - 0: BAIXA (retorno futuro < -k × ATR%)
    
    Exemplo:
        Com k=0.75:
        - Se ATR% = 2%, thresholds são ±1.5%
        - Retorno futuro > +1.5% → ALTA
        - Retorno futuro < -1.5% → BAIXA
        - Entre -1.5% e +1.5% → LATERAL
    """
    
    # Validar colunas necessárias
    if 'Close' not in df.columns:
        raise ValueError("DataFrame precisa ter coluna 'Close'")
    
    if atr_col not in df.columns:
        raise ValueError(f"DataFrame precisa ter coluna '{atr_col}'")
    
    # Calcular ATR% se não existir
    if 'ATR_Pct' not in df.columns:
        df['ATR_Pct'] = (df[atr_col] / df['Close']) * 100
    
    # Calcular retorno futuro percentual
    future_return = (df['Close'].shift(-horizon) - df['Close']) / df['Close'] * 100
    
    # Calcular threshold dinâmico (k × ATR%)
    threshold = k * df['ATR_Pct']
    
    # Criar labels
    labels = pd.Series(1, index=df.index)  # Default: LATERAL
    labels[future_return > threshold] = 2   # ALTA
    labels[future_return < -threshold] = 0  # BAIXA
    
    # Estatísticas
    total = labels.notna().sum()
    if total > 0:
        baixa_count = (labels == 0).sum()
        lateral_count = (labels == 1).sum()
        alta_count = (labels == 2).sum()
        
        print(f"\n📊 Distribuição dos labels (k={k}, horizon={horizon}):")
        print(f"   0 (BAIXA):   {baixa_count:6,} ({baixa_count/total*100:5.1f}%)")
        print(f"   1 (LATERAL): {lateral_count:6,} ({lateral_count/total*100:5.1f}%)")
        print(f"   2 (ALTA):    {alta_count:6,} ({alta_count/total*100:5.1f}%)")
        print(f"\n   Threshold médio: ±{threshold.mean():.2f}%")
        print(f"   Threshold min/max: ±{threshold.min():.2f}% / ±{threshold.max():.2f}%")
    
    return labels


def find_optimal_k(df, horizon=12, atr_col='ATR_14', target_balance=0.3):
    """
    Encontra valor de k que equilibra as classes.
    
    Args:
        df: DataFrame
        horizon: Horizonte de previsão
        atr_col: Coluna ATR
        target_balance: Percentual mínimo desejado para ALTA e BAIXA (padrão: 30%)
    
    Returns:
        float: Valor de k otimizado
    """
    print(f"\n🔍 Buscando k ótimo (target: {target_balance*100}% mín. para ALTA/BAIXA)...")
    
    best_k = 0.75
    best_score = 0
    
    for k in np.arange(0.3, 1.5, 0.05):
        labels = create_labels_with_atr(df, horizon=horizon, k=k, atr_col=atr_col)
        
        total = labels.notna().sum()
        if total == 0:
            continue
        
        baixa_pct = (labels == 0).sum() / total
        alta_pct = (labels == 2).sum() / total
        
        # Score: quanto mais próximo do target, melhor
        # Penaliza se qualquer classe ficar abaixo do target
        min_pct = min(baixa_pct, alta_pct)
        score = min_pct if min_pct >= target_balance else min_pct - 0.5
        
        if score > best_score:
            best_score = score
            best_k = k
    
    print(f"\n✅ k ótimo: {best_k:.2f}")
    print(f"   Score: {best_score:.3f}")
    
    # Mostrar distribuição com k ótimo
    labels_final = create_labels_with_atr(df, horizon=horizon, k=best_k, atr_col=atr_col)
    
    return best_k


if __name__ == "__main__":
    # Exemplo de uso
    print("="*70)
    print("🧪 TESTE: Rotulagem com ATR%")
    print("="*70)
    
    # Criar dados fake
    n = 1000
    np.random.seed(42)
    
    close = 100 * (1 + np.random.randn(n).cumsum() * 0.01)
    atr = np.random.uniform(1, 3, n)
    
    df_test = pd.DataFrame({
        'Close': close,
        'ATR_14': atr
    })
    
    # Testar diferentes k
    for k in [0.5, 0.75, 1.0]:
        labels = create_labels_with_atr(df_test, horizon=12, k=k)
    
    # Buscar k ótimo
    best_k = find_optimal_k(df_test, horizon=12, target_balance=0.25)
    
    print("\n✅ Teste concluído!")
