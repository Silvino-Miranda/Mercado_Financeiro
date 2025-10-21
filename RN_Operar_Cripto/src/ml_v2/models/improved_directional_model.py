"""
Implementação de Focal Loss e melhorias na função de loss.
Focal Loss ajuda com classes desbalanceadas focando em exemplos difíceis.
"""
import tensorflow as tf
from tensorflow import keras
import numpy as np


class FocalLoss(keras.losses.Loss):
    """
    Focal Loss para classificação com classes desbalanceadas.
    
    Focal Loss = -α(1-p)^γ * log(p)
    
    Args:
        alpha: Peso para balanceamento de classes [classe_0, classe_1, classe_2]
        gamma: Fator de foco (padrão: 2.0)
    """
    
    def __init__(self, alpha=None, gamma=2.0, name='focal_loss'):
        super().__init__(name=name)
        self.gamma = gamma
        self.alpha = alpha
        
        if alpha is not None:
            self.alpha = tf.constant(alpha, dtype=tf.float32)
    
    def call(self, y_true, y_pred):
        # Convert labels to one-hot if needed
        if len(y_true.shape) == 1:
            y_true = tf.one_hot(tf.cast(y_true, tf.int32), depth=tf.shape(y_pred)[1])
        
        # Clip predictions to prevent log(0)
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
        
        # Calculate cross entropy
        ce = -y_true * tf.math.log(y_pred)
        
        # Calculate focal weight (1-p)^gamma
        p_t = tf.reduce_sum(y_true * y_pred, axis=1, keepdims=True)
        focal_weight = tf.pow(1.0 - p_t, self.gamma)
        
        # Apply alpha weighting if provided
        if self.alpha is not None:
            alpha_t = tf.reduce_sum(y_true * self.alpha, axis=1, keepdims=True)
            focal_loss = alpha_t * focal_weight * tf.reduce_sum(ce, axis=1, keepdims=True)
        else:
            focal_loss = focal_weight * tf.reduce_sum(ce, axis=1, keepdims=True)
        
        return tf.reduce_mean(focal_loss)


def get_aggressive_class_weights(y_train: np.ndarray, strategy: str = "extreme") -> dict:
    """
    Calcula class weights agressivos para forçar aprendizado de classes minoritárias.
    
    Args:
        y_train: Labels de treino
        strategy: "moderate", "aggressive", ou "extreme"
        
    Returns:
        Dict com class weights
    """
    from collections import Counter
    
    # Contar distribuição
    class_counts = Counter(y_train)
    total_samples = len(y_train)
    
    # Calcular frequências
    class_freqs = {cls: count / total_samples for cls, count in class_counts.items()}
    
    print(f"📊 Distribuição original:")
    label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
    for cls, freq in class_freqs.items():
        name = label_names.get(cls, f"Class_{cls}")
        print(f"   {name}: {class_counts[cls]:,} ({freq:.1%})")
    
    if strategy == "moderate":
        # Inverso da frequência com limitação
        base_weights = {cls: min(1 / freq, 3.0) for cls, freq in class_freqs.items()}
        
    elif strategy == "aggressive":
        # Inverso da frequência com boost para minoritárias
        base_weights = {cls: 1 / freq for cls, freq in class_freqs.items()}
        # Boost extra para BAIXA e ALTA se são minoritárias
        if class_freqs.get(0, 0) < 0.4:  # BAIXA < 40%
            base_weights[0] *= 1.5
        if class_freqs.get(2, 0) < 0.4:  # ALTA < 40%
            base_weights[2] *= 1.5
            
    elif strategy == "extreme":
        # Weights extremos para forçar aprendizado
        base_weights = {}
        for cls, freq in class_freqs.items():
            if cls == 1:  # LATERAL (majoritária)
                base_weights[cls] = 0.3  # Peso muito baixo
            else:  # BAIXA e ALTA
                base_weights[cls] = min(8.0, 1 / freq)  # Peso alto, limitado a 8x
    
    # Normalizar para que a soma seja aproximadamente o número de classes
    n_classes = len(base_weights)
    weight_sum = sum(base_weights.values())
    normalized_weights = {cls: weight * n_classes / weight_sum 
                         for cls, weight in base_weights.items()}
    
    print(f"\n📈 Class weights ({strategy}):")
    for cls, weight in normalized_weights.items():
        name = label_names.get(cls, f"Class_{cls}")
        print(f"   {name}: {weight:.3f}")
    
    return normalized_weights


def build_improved_directional_lstm(
    input_shape: tuple,
    n_classes: int = 3,
    lstm_units: int = 128,
    lstm_layers: int = 3,
    dropout: float = 0.4,
    recurrent_dropout: float = 0.3,
    learning_rate: float = 1e-3,
    use_focal_loss: bool = True,
    focal_alpha: list = None,
    focal_gamma: float = 2.0
):
    """
    Constrói modelo LSTM aprimorado para classificação direcional.
    
    Args:
        input_shape: (timesteps, features)
        n_classes: Número de classes
        lstm_units: Unidades na primeira LSTM
        lstm_layers: Número de camadas LSTM
        dropout: Taxa de dropout
        recurrent_dropout: Dropout recorrente
        learning_rate: Taxa de aprendizado
        use_focal_loss: Usar Focal Loss
        focal_alpha: Pesos alpha para Focal Loss
        focal_gamma: Parâmetro gamma do Focal Loss
        
    Returns:
        Modelo compilado
    """
    model = keras.Sequential([
        keras.layers.Input(shape=input_shape)
    ])
    
    # Camadas LSTM empilhadas
    for i in range(lstm_layers):
        units = lstm_units // (2 ** i)  # Decrescente: 128 -> 64 -> 32
        units = max(units, 16)  # Mínimo 16 units
        
        return_sequences = (i < lstm_layers - 1)  # Última camada não retorna sequências
        
        model.add(keras.layers.LSTM(
            units,
            return_sequences=return_sequences,
            dropout=dropout,
            recurrent_dropout=recurrent_dropout
        ))
        
        # Batch normalization entre LSTMs
        if return_sequences:
            model.add(keras.layers.BatchNormalization())
    
    # Camadas densas com regularização
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dropout(dropout))
    
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dropout(dropout / 2))
    
    # Output layer
    model.add(keras.layers.Dense(n_classes, activation='softmax'))
    
    # Configurar loss function
    if use_focal_loss:
        if focal_alpha is None:
            # Alpha padrão: penalizar LATERAL, favorecer BAIXA/ALTA
            focal_alpha = [2.0, 0.5, 2.0]  # [BAIXA, LATERAL, ALTA]
        
        loss = FocalLoss(alpha=focal_alpha, gamma=focal_gamma)
        print(f"🎯 Usando Focal Loss: alpha={focal_alpha}, gamma={focal_gamma}")
    else:
        loss = 'sparse_categorical_crossentropy'
        print("🎯 Usando Sparse Categorical Crossentropy")
    
    # Compilar
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss=loss,
        metrics=['accuracy', 'sparse_categorical_crossentropy']
    )
    
    print(f"\n🤖 Modelo aprimorado criado:")
    print(f"   LSTM layers: {lstm_layers}")
    print(f"   LSTM units: {lstm_units} -> {units}")
    print(f"   Dropout: {dropout}")
    print(f"   Recurrent dropout: {recurrent_dropout}")
    print(f"   Parâmetros: {model.count_params():,}")
    
    return model


def get_improved_callbacks(
    patience_early: int = 20,
    patience_lr: int = 8,
    monitor: str = 'val_accuracy',
    min_lr: float = 1e-7
):
    """
    Callbacks melhorados para treinamento.
    
    Args:
        patience_early: Paciência para early stopping
        patience_lr: Paciência para redução de LR
        monitor: Métrica a monitorar
        min_lr: Learning rate mínimo
        
    Returns:
        Lista de callbacks
    """
    callbacks = [
        # Early stopping mais paciente
        keras.callbacks.EarlyStopping(
            monitor=monitor,
            patience=patience_early,
            restore_best_weights=True,
            verbose=1,
            mode='max'
        ),
        
        # Learning rate reduction mais gradual
        keras.callbacks.ReduceLROnPlateau(
            monitor=monitor,
            factor=0.7,  # Redução menos agressiva
            patience=patience_lr,
            min_lr=min_lr,
            verbose=1,
            mode='max'
        ),
        
        # Learning rate scheduler warmup
        keras.callbacks.LearningRateScheduler(
            lambda epoch: 1e-3 * min(1.0, epoch / 5.0)  # Warmup primeiras 5 épocas
        )
    ]
    
    return callbacks


if __name__ == "__main__":
    # Teste da arquitetura aprimorada
    print("🧪 Testando arquitetura aprimorada...")
    
    # Dados sintéticos
    np.random.seed(42)
    X = np.random.randn(1000, 60, 18)
    y = np.random.randint(0, 3, 1000)
    
    # Class weights agressivos
    weights = get_aggressive_class_weights(y, strategy="aggressive")
    
    # Modelo aprimorado
    model = build_improved_directional_lstm(
        input_shape=(60, 18),
        lstm_units=128,
        lstm_layers=3,
        use_focal_loss=True
    )
    
    # Callbacks
    callbacks = get_improved_callbacks()
    
    print(f"\n✅ Teste concluído!")
    print(f"   Modelo: {model.count_params():,} parâmetros")
    print(f"   Callbacks: {len(callbacks)} configurados")
    print(f"   Class weights: {len(weights)} classes")