"""
Preprocessamento sem vazamento de dados.
Scaler fit() apenas no treino, transform() em val/test.
"""
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


@dataclass
class SplitIndices:
    """Índices de split temporal."""
    train_end: int
    val_end: int
    # test: from val_end -> end


class DataPreprocessor:
    """
    Preprocessador que garante zero vazamento de dados.
    
    - fit() apenas no treino
    - transform() em val/test
    - Cria sequências LSTM com lookback
    - Normaliza features e target separadamente
    """
    
    def __init__(self, feature_cols: List[str], target_col: str = "Close", lookback: int = 60):
        """
        Args:
            feature_cols: Lista de colunas de features
            target_col: Coluna alvo (Close)
            lookback: Janela temporal para LSTM
        """
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.lookback = lookback
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
        self._fitted = False

    def fit(self, df_train: pd.DataFrame):
        """
        Fit dos scalers APENAS no conjunto de treino.
        
        Args:
            df_train: DataFrame de treino
        """
        X = df_train[self.feature_cols].values
        y = df_train[[self.target_col]].values
        
        self.scaler_X.fit(X)
        self.scaler_y.fit(y)
        self._fitted = True
        
        return self

    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Transform usando scalers já ajustados.
        
        Args:
            df: DataFrame a transformar
            
        Returns:
            X_seq: (n_samples, lookback, n_features)
            y_seq: (n_samples,) - Close(t+1) normalizado
            
        Raises:
            RuntimeError: Se tentar transform antes de fit
        """
        if not self._fitted:
            raise RuntimeError(
                "Scaler not fitted. Call fit() on train split first. "
                "ZERO VAZAMENTO: fit() só no treino!"
            )
        
        X = self.scaler_X.transform(df[self.feature_cols].values)
        y = self.scaler_y.transform(df[[self.target_col]].values)
        
        return self._to_sequences(X, y)

    def inverse_target(self, y_scaled: np.ndarray) -> np.ndarray:
        """
        Desnormaliza o target para USD.
        
        Args:
            y_scaled: Array normalizado
            
        Returns:
            Array em USD (desnormalizado)
        """
        return self.scaler_y.inverse_transform(y_scaled.reshape(-1, 1)).ravel()

    def _to_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converte dados para sequências LSTM.
        
        Args:
            X: Features normalizadas (n_samples, n_features)
            y: Target normalizado (n_samples, 1)
            
        Returns:
            X_seq: (n_samples - lookback, lookback, n_features)
            y_seq: (n_samples - lookback,) - alvo é Close(t+1)
        """
        L = self.lookback
        X_seq, y_seq = [], []
        
        for i in range(L, len(X)):
            X_seq.append(X[i-L:i])      # [t-L, ..., t-1]
            y_seq.append(y[i])            # Close(t) - target é o futuro
            
        return np.array(X_seq), np.array(y_seq).squeeze()

    def get_lookback_dates(self, df: pd.DataFrame) -> pd.DatetimeIndex:
        """
        Retorna as datas alinhadas às sequências (após lookback).
        
        Args:
            df: DataFrame com coluna 'Date'
            
        Returns:
            DatetimeIndex alinhado aos dados transformados
        """
        return df['Date'].iloc[self.lookback:].values
