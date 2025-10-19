"""
DataPreprocessorAdapter - Adapter para preprocessamento v2 → v3.

Permite que código v2 use DataLoader e preprocessamento v3.
Mantém interface compatível com ml_v2.preprocess.DataPreprocessor.

Padrão Adapter: Converte interface v3 para interface v2.
"""
from typing import List, Tuple
import pandas as pd
import numpy as np

from ..infrastructure.data_loader import DataLoader, DataLoadConfig
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessorAdapter:
    """
    Adapter que expõe interface v2 usando implementação v3.
    
    Interface v2 (mantida):
        - __init__(feature_cols, target_col, lookback)
        - fit(df_train)
        - transform(df)
        - fit_transform(df)
    
    Implementação v3 (usada internamente):
        - DataLoader para validação
        - Scalers separados para X e y
        - Validações robustas
    
    Exemplo:
        >>> # Código v2 continua funcionando:
        >>> preprocessor = DataPreprocessorAdapter(
        ...     feature_cols=['Open', 'High', 'Low', 'Volume'],
        ...     target_col='Close',
        ...     lookback=60
        ... )
        >>> preprocessor.fit(df_train)
        >>> X_train, y_train = preprocessor.transform(df_train)
    """
    
    def __init__(
        self,
        feature_cols: List[str],
        target_col: str = "Close",
        lookback: int = 60
    ):
        """
        Args:
            feature_cols: Lista de colunas de features
            target_col: Coluna alvo (Close)
            lookback: Janela temporal para LSTM
        """
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.lookback = lookback
        
        # Scalers (igual v2)
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
        self._fitted = False
        
        # DataLoader v3 (validação robusta)
        self.data_loader = DataLoader(
            config=DataLoadConfig(
                required_columns=feature_cols + [target_col],
                optional_columns=['Date', 'timestamp'],
                date_column='Date',
                parse_dates=True,
                drop_duplicates=True,
                handle_missing='drop',
                validate_ohlc=False  # Validação customizada depois
            )
        )
    
    def fit(self, df_train: pd.DataFrame) -> "DataPreprocessorAdapter":
        """
        Fit dos scalers APENAS no conjunto de treino.
        
        Args:
            df_train: DataFrame de treino
            
        Returns:
            self (para chaining)
        """
        # Validar que tem as colunas necessárias
        self._validate_dataframe(df_train, context="fit")
        
        # Extrair features e target
        X = df_train[self.feature_cols].values
        y = df_train[self.target_col].values.reshape(-1, 1)
        
        # Fit dos scalers
        self.scaler_X.fit(X)
        self.scaler_y.fit(y)
        
        self._fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transforma dados em sequências LSTM normalizadas.
        
        Args:
            df: DataFrame a transformar
            
        Returns:
            Tupla (X, y) com sequências LSTM
            - X: (n_samples, lookback, n_features)
            - y: (n_samples,)
            
        Raises:
            RuntimeError: Se fit() não foi chamado antes
        """
        if not self._fitted:
            raise RuntimeError(
                "DataPreprocessorAdapter não foi fitted. "
                "Chame .fit(df_train) antes de .transform()"
            )
        
        # Validar DataFrame
        self._validate_dataframe(df, context="transform")
        
        # Extrair e normalizar
        X = df[self.feature_cols].values
        y = df[self.target_col].values.reshape(-1, 1)
        
        X_scaled = self.scaler_X.transform(X)
        y_scaled = self.scaler_y.transform(y).ravel()
        
        # Criar sequências LSTM
        X_seq, y_seq = self._create_sequences(X_scaled, y_scaled)
        
        return X_seq, y_seq
    
    def fit_transform(self, df_train: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit e transform em uma chamada.
        
        Args:
            df_train: DataFrame de treino
            
        Returns:
            Tupla (X, y) com sequências LSTM
        """
        self.fit(df_train)
        return self.transform(df_train)
    
    def inverse_target(self, y_scaled: np.ndarray) -> np.ndarray:
        """
        Inverte normalização do target.
        
        Args:
            y_scaled: Target normalizado
            
        Returns:
            Target em escala original
        """
        if not self._fitted:
            raise RuntimeError("Preprocessor não foi fitted")
        
        y_reshaped = y_scaled.reshape(-1, 1)
        y_original = self.scaler_y.inverse_transform(y_reshaped)
        return y_original.ravel()
    
    def _create_sequences(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cria sequências LSTM com lookback window.
        
        Args:
            X: Features normalizadas (n_samples, n_features)
            y: Target normalizado (n_samples,)
            
        Returns:
            Tupla (X_seq, y_seq):
            - X_seq: (n_samples - lookback, lookback, n_features)
            - y_seq: (n_samples - lookback,)
        """
        X_seq, y_seq = [], []
        
        for i in range(self.lookback, len(X)):
            X_seq.append(X[i - self.lookback:i])
            y_seq.append(y[i])
        
        return np.array(X_seq), np.array(y_seq)
    
    def _validate_dataframe(self, df: pd.DataFrame, context: str):
        """
        Valida que DataFrame tem todas as colunas necessárias.
        
        Args:
            df: DataFrame a validar
            context: Contexto da chamada ("fit" ou "transform")
            
        Raises:
            ValueError: Se colunas faltando ou DataFrame vazio
        """
        if df.empty:
            raise ValueError(f"DataFrame vazio em {context}()")
        
        # Verificar colunas de features
        missing_features = set(self.feature_cols) - set(df.columns)
        if missing_features:
            raise ValueError(
                f"Colunas de features faltando em {context}(): "
                f"{missing_features}"
            )
        
        # Verificar target
        if self.target_col not in df.columns:
            raise ValueError(
                f"Coluna target '{self.target_col}' não encontrada em {context}()"
            )
        
        # Verificar tamanho mínimo
        min_samples = self.lookback + 1  # Apenas lookback + 1 para criar ao menos 1 sequência
        if len(df) < min_samples:
            raise ValueError(
                f"DataFrame muito pequeno em {context}(): "
                f"{len(df)} samples, mínimo {min_samples}"
            )
    
    def get_config(self) -> dict:
        """
        Retorna configuração do preprocessor (compatibilidade v3).
        
        Returns:
            Dict com configuração
        """
        return {
            'feature_cols': self.feature_cols,
            'target_col': self.target_col,
            'lookback': self.lookback,
            'fitted': self._fitted,
            'n_features': len(self.feature_cols)
        }
    
    def __repr__(self) -> str:
        """Representação string."""
        fitted_str = "fitted" if self._fitted else "not fitted"
        return (
            f"DataPreprocessorAdapter("
            f"n_features={len(self.feature_cols)}, "
            f"lookback={self.lookback}, "
            f"{fitted_str})"
        )
