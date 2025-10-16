"""
Modelo LSTM para regressão de Close(t+1).
Simples, sem complexidade desnecessária.
"""
from tensorflow import keras
from typing import Tuple


def build_lstm(input_shape: Tuple[int, int], learning_rate: float = 1e-3) -> keras.Model:
    """
    Constrói LSTM de 2 camadas para prever Close(t+1).
    
    Args:
        input_shape: (lookback, n_features)
        learning_rate: Taxa de aprendizado inicial
        
    Returns:
        Modelo Keras compilado
        
    Arquitetura:
        - LSTM(64) + Dropout(0.2) + return_sequences
        - LSTM(32) + Dropout(0.2)
        - Dense(1) - saída: Close(t+1) normalizado
    """
    inputs = keras.Input(shape=input_shape, name="input_sequence")
    
    # Primeira camada LSTM
    x = keras.layers.LSTM(64, return_sequences=True, name="lstm_1")(inputs)
    x = keras.layers.Dropout(0.2, name="dropout_1")(x)
    
    # Segunda camada LSTM
    x = keras.layers.LSTM(32, return_sequences=False, name="lstm_2")(x)
    x = keras.layers.Dropout(0.2, name="dropout_2")(x)
    
    # Saída: 1 valor (Close futuro)
    outputs = keras.layers.Dense(1, name="output_close")(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs, name="LSTM_Close_Predictor")
    
    # Compilar com MSE (regressão)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss="mse",
        metrics=["mae"]
    )
    
    return model


def get_callbacks(patience_early: int = 10, patience_lr: int = 5) -> list:
    """
    Callbacks padrão para treino robusto.
    
    Args:
        patience_early: Épocas sem melhora para parar
        patience_lr: Épocas sem melhora para reduzir LR
        
    Returns:
        Lista de callbacks
    """
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=patience_early,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            patience=patience_lr,
            factor=0.5,
            min_lr=1e-6,
            verbose=1
        ),
    ]
    
    return callbacks
