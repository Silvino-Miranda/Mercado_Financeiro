"""
Preprocessador para classificação direcional.
Cria labels ALTA/BAIXA/LATERAL baseados no movimento futuro do preço.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List


class DirectionalPreprocessor:
    """Preprocessa dados para classificação direcional."""
    
    def __init__(
        self,
        feature_cols: List[str],
        price_col: str = "Close",
        lookback: int = 60,
        horizon: int = 12,  # 6 horas (12 × 30min)
        threshold_pct: float = 0.5  # 0.5% threshold
    ):
        """
        Args:
            feature_cols: Colunas de features
            price_col: Coluna de preço
            lookback: Janela temporal (sequências)
            horizon: Períodos à frente para calcular movimento
            threshold_pct: Threshold em % para ALTA/BAIXA vs LATERAL
        """
        self.feature_cols = feature_cols
        self.price_col = price_col
        self.lookback = lookback
        self.horizon = horizon
        self.threshold_pct = threshold_pct
        
        # Scalers
        self.feature_scaler = StandardScaler()
        
        # Labels: 0=BAIXA, 1=LATERAL, 2=ALTA
        self.label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
    
    def _create_directional_labels(self, prices: np.ndarray) -> np.ndarray:
        """
        Cria labels direcionais baseados no movimento futuro.
        
        Args:
            prices: Array de preços
            
        Returns:
            Array de labels (0=BAIXA, 1=LATERAL, 2=ALTA)
        """
        n = len(prices)
        labels = np.full(n, -1, dtype=int)  # -1 = inválido
        
        for i in range(n - self.horizon):
            current_price = prices[i]
            future_price = prices[i + self.horizon]
            
            # Calcular movimento percentual
            pct_change = (future_price - current_price) / current_price * 100
            
            # Classificar
            if pct_change > self.threshold_pct:
                labels[i] = 2  # ALTA
            elif pct_change < -self.threshold_pct:
                labels[i] = 0  # BAIXA
            else:
                labels[i] = 1  # LATERAL
        
        return labels
    
    def fit(self, df: pd.DataFrame) -> 'DirectionalPreprocessor':
        """
        Fit nos dados de treino.
        
        Args:
            df: DataFrame de treino
            
        Returns:
            Self para chaining
        """
        # Features
        features = df[self.feature_cols].values
        self.feature_scaler.fit(features)
        
        print(f"✅ Preprocessor fitted:")
        print(f"   Features: {len(self.feature_cols)}")
        print(f"   Lookback: {self.lookback}")
        print(f"   Horizon: {self.horizon} períodos ({self.horizon * 0.5:.1f}h)")
        print(f"   Threshold: ±{self.threshold_pct}%")
        
        return self
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transforma dados em sequências X, y.
        
        Args:
            df: DataFrame
            
        Returns:
            Tuple (X, y) onde:
            - X: (n_samples, lookback, n_features)
            - y: (n_samples,) labels direcionais
        """
        # Features escaladas
        features = df[self.feature_cols].values
        features_scaled = self.feature_scaler.transform(features)
        
        # Labels direcionais
        prices = df[self.price_col].values
        labels = self._create_directional_labels(prices)
        
        # Criar sequências
        X, y = [], []
        
        for i in range(self.lookback, len(features_scaled)):
            # Features: janela do passado
            X.append(features_scaled[i-self.lookback:i])
            
            # Label: movimento futuro
            y.append(labels[i])
        
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=int)
        
        # Filtrar labels válidos (não -1)
        valid_mask = y != -1
        X = X[valid_mask]
        y = y[valid_mask]
        
        print(f"📊 Sequências criadas: {X.shape}")
        print(f"📊 Distribuição de labels:")
        
        for label, name in self.label_names.items():
            count = np.sum(y == label)
            pct = count / len(y) * 100 if len(y) > 0 else 0
            print(f"   {name}: {count:,} ({pct:.1f}%)")
        
        return X, y
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Fit + transform em uma chamada."""
        return self.fit(df).transform(df)


def create_directional_labels(
    prices: pd.Series,
    horizon: int = 12,
    threshold_pct: float = 0.5
) -> pd.Series:
    """
    Função utilitária para criar labels direcionais.
    
    Args:
        prices: Série de preços
        horizon: Períodos à frente
        threshold_pct: Threshold em %
        
    Returns:
        Série com labels (0=BAIXA, 1=LATERAL, 2=ALTA)
    """
    n = len(prices)
    labels = pd.Series(-1, index=prices.index, dtype=int)
    
    for i in range(n - horizon):
        if i + horizon >= n:
            break
            
        current = prices.iloc[i]
        future = prices.iloc[i + horizon]
        
        pct_change = (future - current) / current * 100
        
        if pct_change > threshold_pct:
            labels.iloc[i] = 2  # ALTA
        elif pct_change < -threshold_pct:
            labels.iloc[i] = 0  # BAIXA
        else:
            labels.iloc[i] = 1  # LATERAL
    
    return labels


if __name__ == "__main__":
    # Teste básico
    import pandas as pd
    
    # Dados sintéticos
    np.random.seed(42)
    n = 1000
    
    df = pd.DataFrame({
        'Close': np.cumsum(np.random.randn(n) * 0.01) + 100,
        'Volume': np.random.randn(n),
        'RSI': np.random.randn(n)
    })
    
    # Teste
    preprocessor = DirectionalPreprocessor(['Volume', 'RSI'], 'Close')
    X, y = preprocessor.fit_transform(df)
    
    print(f"\n✅ Teste concluído:")
    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")
    print(f"   Labels únicos: {np.unique(y)}")