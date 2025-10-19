"""
ModelBuilderAdapter - Adapter para construção de modelos v2 → v3.

Permite que código v2 use ModelFactory v3.
Mantém interface compatível com ml_v2.models.

Padrão Adapter: Converte interface v3 para interface v2.
"""
from typing import List
from tensorflow import keras

from ..factories.model_factory import ModelFactory
from ..domain.entities import ModelConfig


class ModelBuilderAdapter:
    """
    Adapter que expõe interface v2 usando ModelFactory v3.
    
    Interface v2 (mantida):
        - build_lstm(input_shape, learning_rate)
        - build_directional_lstm(input_shape, n_classes, lstm_units, dropout, lr)
        - get_callbacks(patience_early, patience_lr, monitor)
    
    Implementação v3 (usada internamente):
        - ModelFactory com configs tipadas
        - Validações robustas
        - Callbacks configuráveis
    
    Exemplo:
        >>> # Código v2 continua funcionando:
        >>> builder = ModelBuilderAdapter()
        >>> model = builder.build_lstm(
        ...     input_shape=(60, 10),
        ...     learning_rate=1e-3
        ... )
    """
    
    def __init__(self):
        """Inicializa adapter com ModelFactory v3."""
        self.factory = ModelFactory()
    
    @staticmethod
    def build_lstm(
        input_shape: tuple,
        learning_rate: float = 1e-3,
        lstm_units: int = 64,
        dropout: float = 0.2
    ) -> keras.Model:
        """
        Constrói modelo LSTM de regressão (compatível v2).
        
        Args:
            input_shape: Shape (timesteps, features)
            learning_rate: Taxa de aprendizado
            lstm_units: Unidades da primeira LSTM
            dropout: Taxa de dropout
            
        Returns:
            Modelo Keras compilado
        """
        config = ModelConfig(
            model_type='lstm',
            input_shape=input_shape,
            lstm_units=lstm_units,
            lstm_layers=2,
            dropout=dropout,
            learning_rate=learning_rate,
            n_classes=None  # Regressão
        )
        
        factory = ModelFactory()
        return factory.create_model(config)
    
    @staticmethod
    def build_directional_lstm(
        input_shape: tuple,
        n_classes: int = 3,
        lstm_units: int = 64,
        dropout: float = 0.3,
        learning_rate: float = 1e-3
    ) -> keras.Model:
        """
        Constrói modelo LSTM de classificação direcional (compatível v2).
        
        Args:
            input_shape: Shape (timesteps, features)
            n_classes: Número de classes (3: BAIXA, LATERAL, ALTA)
            lstm_units: Unidades da primeira LSTM
            dropout: Taxa de dropout
            learning_rate: Taxa de aprendizado
            
        Returns:
            Modelo Keras compilado
        """
        config = ModelConfig(
            model_type='directional',
            input_shape=input_shape,
            lstm_units=lstm_units,
            lstm_layers=2,
            dropout=dropout,
            learning_rate=learning_rate,
            n_classes=n_classes
        )
        
        factory = ModelFactory()
        return factory.create_model(config)
    
    @staticmethod
    def build_improved_directional_lstm(
        input_shape: tuple,
        lstm_units: int = 128,
        lstm_layers: int = 3,
        dropout: float = 0.4,
        learning_rate: float = 1e-3,
        use_focal_loss: bool = True
    ) -> keras.Model:
        """
        Constrói modelo LSTM melhorado com Focal Loss (compatível v2).
        
        Args:
            input_shape: Shape (timesteps, features)
            lstm_units: Unidades da primeira LSTM
            lstm_layers: Número de camadas LSTM
            dropout: Taxa de dropout
            learning_rate: Taxa de aprendizado
            use_focal_loss: Usar Focal Loss (recomendado para classes desbalanceadas)
            
        Returns:
            Modelo Keras compilado
        """
        config = ModelConfig(
            model_type='improved_directional',
            input_shape=input_shape,
            lstm_units=lstm_units,
            lstm_layers=lstm_layers,
            dropout=dropout,
            learning_rate=learning_rate,
            n_classes=3,
            use_batch_norm=True,
            use_focal_loss=use_focal_loss
        )
        
        factory = ModelFactory()
        return factory.create_model(config)
    
    @staticmethod
    def get_callbacks(
        patience_early: int = 10,
        patience_lr: int = 5,
        monitor: str = 'val_loss',
        min_delta: float = 1e-4,
        factor: float = 0.5,
        min_lr: float = 1e-7,
        restore_best_weights: bool = True
    ) -> List[keras.callbacks.Callback]:
        """
        Retorna callbacks padrão (compatível v2).
        
        Args:
            patience_early: Paciência para EarlyStopping
            patience_lr: Paciência para ReduceLROnPlateau
            monitor: Métrica a monitorar
            min_delta: Mudança mínima para considerar melhoria
            factor: Fator de redução do LR
            min_lr: Learning rate mínimo
            restore_best_weights: Restaurar melhores pesos
            
        Returns:
            Lista de callbacks
        """
        factory = ModelFactory()
        return factory.create_callbacks(
            patience_early=patience_early,
            patience_lr=patience_lr,
            monitor=monitor,
            min_delta=min_delta,
            factor=factor,
            min_lr=min_lr,
            restore_best_weights=restore_best_weights
        )
    
    @staticmethod
    def get_directional_callbacks(
        patience_early: int = 15,
        patience_lr: int = 7,
        monitor: str = 'val_accuracy'
    ) -> List[keras.callbacks.Callback]:
        """
        Retorna callbacks para classificação (compatível v2).
        
        Args:
            patience_early: Paciência para EarlyStopping
            patience_lr: Paciência para ReduceLROnPlateau
            monitor: Métrica a monitorar (val_accuracy ou val_loss)
            
        Returns:
            Lista de callbacks
        """
        factory = ModelFactory()
        return factory.create_callbacks(
            patience_early=patience_early,
            patience_lr=patience_lr,
            monitor=monitor,
            min_delta=1e-4,
            factor=0.5,
            min_lr=1e-6,
            restore_best_weights=True
        )
    
    @staticmethod
    def calculate_class_weights(y_train: list) -> dict:
        """
        Calcula class weights para desbalanceamento (compatível v2).
        
        Args:
            y_train: Labels de treino (numpy array ou lista)
            
        Returns:
            Dict com pesos por classe {0: weight, 1: weight, 2: weight}
        """
        from sklearn.utils.class_weight import compute_class_weight
        import numpy as np
        
        y_array = np.array(y_train)
        classes = np.unique(y_array)
        
        weights = compute_class_weight(
            class_weight='balanced',
            classes=classes,
            y=y_array
        )
        
        return {int(cls): float(w) for cls, w in zip(classes, weights)}
    
    def __repr__(self) -> str:
        """Representação string."""
        return "ModelBuilderAdapter(factory=ModelFactory)"
