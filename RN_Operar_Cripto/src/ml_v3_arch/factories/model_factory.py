"""
Factory Pattern para criação de modelos.
Princípios aplicados:
- Factory Method: Centraliza criação de objetos complexos
- OCP (Open/Closed): Extensível para novos modelos sem modificar código existente
- DIP: Retorna abstrações (BaseModel), não implementações concretas
"""
from typing import Optional
from tensorflow import keras
from tensorflow.keras import layers

from ..domain import ModelConfig
from ..interfaces import BaseModel


class ModelFactory:
    """
    Factory para criar diferentes tipos de modelos ML.
    
    Suporta:
    - LSTM para regressão
    - GRU para regressão
    - LSTM direcional (classificação)
    - Modelos customizados
    """
    
    @staticmethod
    def create_model(config: ModelConfig) -> keras.Model:
        """
        Cria modelo baseado na configuração.
        
        Args:
            config: Configuração do modelo
            
        Returns:
            Modelo Keras compilado
            
        Raises:
            ValueError: Se model_type não for reconhecido
        """
        model_type = config.model_type.lower()
        
        if model_type == 'lstm':
            return ModelFactory._create_lstm_regression(config)
        elif model_type == 'gru':
            return ModelFactory._create_gru_regression(config)
        elif model_type == 'directional':
            return ModelFactory._create_directional_lstm(config)
        elif model_type == 'improved_directional':
            return ModelFactory._create_improved_directional(config)
        else:
            raise ValueError(
                f"Unknown model_type: {config.model_type}. "
                f"Supported: 'lstm', 'gru', 'directional', 'improved_directional'"
            )
    
    @staticmethod
    def _create_lstm_regression(config: ModelConfig) -> keras.Model:
        """
        Cria modelo LSTM para regressão de preço.
        
        Arquitetura:
        - N camadas LSTM com dropout
        - Dense(1) para saída contínua
        """
        model = keras.Sequential(name="LSTM_Regression")
        
        # Primeira camada LSTM
        model.add(layers.LSTM(
            config.lstm_units,
            return_sequences=config.lstm_layers > 1,
            name="lstm_1"
        ))
        model.add(layers.Dropout(config.dropout, name="dropout_1"))
        
        # Camadas intermediárias
        for i in range(2, config.lstm_layers + 1):
            return_seq = i < config.lstm_layers
            model.add(layers.LSTM(
                config.lstm_units // (2 ** (i - 1)),
                return_sequences=return_seq,
                name=f"lstm_{i}"
            ))
            model.add(layers.Dropout(config.dropout, name=f"dropout_{i}"))
        
        # Saída
        model.add(layers.Dense(1, name="output"))
        
        # Compilar
        model.compile(
            optimizer=keras.optimizers.Adam(config.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    @staticmethod
    def _create_gru_regression(config: ModelConfig) -> keras.Model:
        """
        Cria modelo GRU para regressão de preço.
        
        GRU é mais leve que LSTM e pode convergir mais rápido.
        """
        model = keras.Sequential(name="GRU_Regression")
        
        # Primeira camada GRU
        model.add(layers.GRU(
            config.lstm_units,
            return_sequences=config.lstm_layers > 1,
            name="gru_1"
        ))
        model.add(layers.Dropout(config.dropout, name="dropout_1"))
        
        # Camadas intermediárias
        for i in range(2, config.lstm_layers + 1):
            return_seq = i < config.lstm_layers
            model.add(layers.GRU(
                config.lstm_units // (2 ** (i - 1)),
                return_sequences=return_seq,
                name=f"gru_{i}"
            ))
            model.add(layers.Dropout(config.dropout, name=f"dropout_{i}"))
        
        # Saída
        model.add(layers.Dense(1, name="output"))
        
        # Compilar
        model.compile(
            optimizer=keras.optimizers.Adam(config.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    @staticmethod
    def _create_directional_lstm(config: ModelConfig) -> keras.Model:
        """
        Cria modelo LSTM para classificação direcional.
        
        Arquitetura:
        - LSTMs com dropout recorrente
        - Dense(3) com softmax (BAIXA/LATERAL/ALTA)
        """
        model = keras.Sequential(name="Directional_LSTM")
        
        # LSTMs empilhadas
        for i in range(1, config.lstm_layers + 1):
            return_seq = i < config.lstm_layers
            units = config.lstm_units // (2 ** max(0, i - 1))
            
            model.add(layers.LSTM(
                units,
                return_sequences=return_seq,
                dropout=config.dropout,
                recurrent_dropout=config.dropout,
                name=f"lstm_{i}"
            ))
        
        # Dense intermediária
        model.add(layers.Dense(32, activation='relu', name="dense_hidden"))
        model.add(layers.Dropout(config.dropout, name="dropout_final"))
        
        # Saída: 3 classes
        model.add(layers.Dense(3, activation='softmax', name="output"))
        
        # Compilar
        model.compile(
            optimizer=keras.optimizers.Adam(config.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    @staticmethod
    def _create_improved_directional(config: ModelConfig) -> keras.Model:
        """
        Cria modelo direcional aprimorado.
        
        Melhorias:
        - BatchNormalization entre camadas
        - Mais camadas densas
        - Focal Loss (opcional)
        """
        model = keras.Sequential(name="Improved_Directional_LSTM")
        
        # Conv1D inicial (opcional para capturar padrões locais)
        model.add(layers.Conv1D(
            filters=32,
            kernel_size=3,
            padding='same',
            activation='relu',
            name="conv1d"
        ))
        
        # LSTMs com BatchNorm
        for i in range(1, config.lstm_layers + 1):
            return_seq = i < config.lstm_layers
            units = config.lstm_units // (2 ** max(0, i - 1))
            
            model.add(layers.LSTM(
                units,
                return_sequences=return_seq,
                dropout=config.dropout,
                recurrent_dropout=config.dropout / 2,
                name=f"lstm_{i}"
            ))
            
            if return_seq:
                model.add(layers.BatchNormalization(name=f"batchnorm_{i}"))
        
        # Dense layers
        model.add(layers.Dense(64, activation='relu', name="dense_1"))
        model.add(layers.Dropout(config.dropout, name="dropout_1"))
        
        model.add(layers.Dense(32, activation='relu', name="dense_2"))
        model.add(layers.Dropout(config.dropout / 2, name="dropout_2"))
        
        # Saída
        model.add(layers.Dense(3, activation='softmax', name="output"))
        
        # Compilar (pode usar Focal Loss se disponível)
        model.compile(
            optimizer=keras.optimizers.Adam(config.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    @staticmethod
    def get_callbacks(
        config: ModelConfig,
        monitor: str = 'val_loss'
    ) -> list:
        """
        Cria callbacks padrão para treinamento.
        
        Args:
            config: Configuração do modelo
            monitor: Métrica a monitorar
            
        Returns:
            Lista de callbacks
        """
        mode = 'min' if 'loss' in monitor else 'max'
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor=monitor,
                patience=config.patience,
                restore_best_weights=True,
                verbose=1,
                mode=mode
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor=monitor,
                factor=0.5,
                patience=config.patience // 2,
                min_lr=1e-6,
                verbose=1,
                mode=mode
            )
        ]
        
        return callbacks


# Exemplo de uso
if __name__ == "__main__":
    from ..domain import ModelConfig
    
    # Criar configuração
    config = ModelConfig(
        model_type='lstm',
        lookback=60,
        lstm_units=64,
        lstm_layers=2,
        dropout=0.3,
        learning_rate=1e-3
    )
    
    # Criar modelo via factory
    model = ModelFactory.create_model(config)
    
    print(f"✅ Modelo criado: {model.name}")
    print(f"   Parâmetros: {model.count_params():,}")
    
    # Callbacks
    callbacks = ModelFactory.get_callbacks(config)
    print(f"   Callbacks: {len(callbacks)}")
