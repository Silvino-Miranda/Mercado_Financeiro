# src/utils/data_preprocessing.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List, Tuple


class DataPreprocessor:
    """
    Classe para pré-processamento de dados para modelos LSTM.

    Parameters:
    - feature_columns: Lista de nomes das colunas de features a serem usadas.
    - target_columns: Lista de nomes das colunas alvo a serem previstas.
    - sequence_length: Comprimento das sequências de entrada.
    - scaler: Instância de um scaler do scikit-learn.
    """

    def __init__(
        self,
        feature_columns: List[str] = ["Open", "High", "Low"],
        target_columns: List[str] = ["Close", "High", "Low"],
        sequence_length: int = 60,
        scaler: MinMaxScaler = None,
    ):
        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.sequence_length = sequence_length
        self.scaler = scaler if scaler else MinMaxScaler(feature_range=(0, 1))

    def fit_transform(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Ajusta o scaler nos dados e transforma os dados de treinamento.

        Parameters:
        - data: DataFrame contendo os dados brutos.

        Returns:
        - X: Arrays de sequências de entrada.
        - Y: Arrays de valores alvo.
        - dates: Datas correspondentes às sequências.
        """
        return self._preprocess(data, fit_scaler=True)

    def transform(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Transforma novos dados usando o scaler ajustado.

        Parameters:
        - data: DataFrame contendo os dados brutos.

        Returns:
        - X: Arrays de sequências de entrada.
        - Y: Arrays de valores alvo.
        - dates: Datas correspondentes às sequências.
        """
        return self._preprocess(data, fit_scaler=False)

    def _preprocess(
        self, data: pd.DataFrame, fit_scaler: bool
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        print("Iniciando o preprocessamento dos dados...")

        # Verificar se as colunas necessárias existem no DataFrame
        all_columns = self.feature_columns + self.target_columns
        missing_columns = [col for col in all_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(
                f"As seguintes colunas estão ausentes no DataFrame: {missing_columns}"
            )

        print(data.head())
        # Remover valores ausentes nas colunas de interesse
        data = data.dropna(subset=all_columns)

        # Extrair as features e os targets
        feature_data = data[self.feature_columns].values
        target_data = data[self.target_columns].values

        # Ajustar ou aplicar o scaler
        if fit_scaler:
            scaled_features = self.scaler.fit_transform(feature_data)
            scaled_targets = self.scaler.fit_transform(target_data)
        else:
            scaled_features = self.scaler.transform(feature_data)
            scaled_targets = self.scaler.transform(target_data)

        dates = data["Date"].values  # Supondo que 'Date' seja uma coluna no DataFrame

        num_samples = len(scaled_features) - self.sequence_length
        X = np.array(
            [scaled_features[i : i + self.sequence_length] for i in range(num_samples)]
        )
        Y = np.array(
            [scaled_targets[i + self.sequence_length - 1] for i in range(num_samples)]
        )

        dates = dates[self.sequence_length - 1 :]  # Ajuste do tamanho de dates

        print("Preprocessamento concluído.")
        return X, Y, dates

    def split_data(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        dates: np.ndarray,
        train_size=0.7,
        val_size=0.15,
    ):
        """
        Divide os dados em conjuntos de treinamento, validação e teste.

        Parameters:
        - X: Arrays de sequências de entrada.
        - Y: Arrays de valores alvo.
        - dates: Datas correspondentes às sequências.
        - train_size: Proporção dos dados para treinamento.
        - val_size: Proporção dos dados para validação.

        Returns:
        - Tuplas de dados para treinamento, validação e teste.
        """
        total_samples = len(X)
        train_end = int(total_samples * train_size)
        val_end = train_end + int(total_samples * val_size)

        X_train, Y_train = X[:train_end], Y[:train_end]
        X_val, Y_val = X[train_end:val_end], Y[train_end:val_end]
        X_test, Y_test = X[val_end:], Y[val_end:]
        dates_train = dates[:train_end]
        dates_val = dates[train_end:val_end]
        dates_test = dates[val_end:]

        return (
            (X_train, Y_train, dates_train),
            (X_val, Y_val, dates_val),
            (X_test, Y_test, dates_test),
        )
