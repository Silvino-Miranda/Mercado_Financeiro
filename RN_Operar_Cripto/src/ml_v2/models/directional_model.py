"""
Modelo LSTM para classificação direcional.
Prediz ALTA/BAIXA/LATERAL ao invés de preço exato.
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from typing import Tuple, List


def build_directional_lstm(
    input_shape: Tuple[int, int],
    n_classes: int = 3,
    lstm_units: int = 64,
    dropout: float = 0.3,
    learning_rate: float = 1e-3,
    class_weights: dict = None
) -> keras.Model:
    """
    Constrói modelo LSTM para classificação direcional.
    
    Args:
        input_shape: (timesteps, features)
        n_classes: Número de classes (3 = BAIXA/LATERAL/ALTA)
        lstm_units: Unidades LSTM
        dropout: Taxa de dropout
        learning_rate: Taxa de aprendizado
        class_weights: Pesos das classes para balanceamento
        
    Returns:
        Modelo compilado
    """
    model = keras.Sequential([
        # Entrada
        layers.Input(shape=input_shape),
        
        # LSTM com dropout
        layers.LSTM(
            lstm_units,
            return_sequences=True,
            dropout=dropout,
            recurrent_dropout=dropout
        ),
        
        # Segunda LSTM
        layers.LSTM(
            lstm_units // 2,
            dropout=dropout,
            recurrent_dropout=dropout
        ),
        
        # Dense layers
        layers.Dense(32, activation='relu'),
        layers.Dropout(dropout),
        
        # Output (classificação)
        layers.Dense(n_classes, activation='softmax')
    ])
    
    # Compilar
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def get_directional_callbacks(
    patience_early: int = 15,
    patience_lr: int = 7,
    monitor: str = 'val_accuracy'
) -> List[keras.callbacks.Callback]:
    """
    Callbacks para classificação direcional.
    
    Args:
        patience_early: Paciência para early stopping
        patience_lr: Paciência para redução de LR
        monitor: Métrica a monitorar
        
    Returns:
        Lista de callbacks
    """
    callbacks = [
        # Early stopping
        keras.callbacks.EarlyStopping(
            monitor=monitor,
            patience=patience_early,
            restore_best_weights=True,
            verbose=1,
            mode='max'  # Maximizar accuracy
        ),
        
        # Redução de learning rate
        keras.callbacks.ReduceLROnPlateau(
            monitor=monitor,
            factor=0.5,
            patience=patience_lr,
            min_lr=1e-6,
            verbose=1,
            mode='max'
        )
    ]
    
    return callbacks


def calculate_class_weights(y: np.ndarray) -> dict:
    """
    Calcula pesos das classes para balanceamento.
    
    Args:
        y: Labels
        
    Returns:
        Dict com pesos {0: weight_baixa, 1: weight_lateral, 2: weight_alta}
    """
    from sklearn.utils.class_weight import compute_class_weight
    
    classes = np.unique(y)
    weights = compute_class_weight('balanced', classes=classes, y=y)
    
    class_weights = {int(cls): float(weight) for cls, weight in zip(classes, weights)}
    
    print(f"📊 Class weights calculados:")
    label_names = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
    for cls, weight in class_weights.items():
        name = label_names.get(cls, f"Class_{cls}")
        print(f"   {name}: {weight:.3f}")
    
    return class_weights


def predict_directional(
    model: keras.Model,
    X: np.ndarray,
    return_proba: bool = False
) -> np.ndarray:
    """
    Faz predições direcionais.
    
    Args:
        model: Modelo treinado
        X: Features de entrada
        return_proba: Se True, retorna probabilidades
        
    Returns:
        Array com predições (classes ou probabilidades)
    """
    y_proba = model.predict(X, verbose=0)
    
    if return_proba:
        return y_proba
    else:
        return np.argmax(y_proba, axis=1)


def evaluate_directional_model(
    model: keras.Model,
    X_test: np.ndarray,
    y_test: np.ndarray
) -> dict:
    """
    Avalia modelo direcional.
    
    Args:
        model: Modelo treinado
        X_test: Features de teste
        y_test: Labels de teste
        
    Returns:
        Dict com métricas
    """
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    from sklearn.metrics import precision_recall_fscore_support
    
    # Predições
    y_pred = predict_directional(model, X_test)
    y_proba = predict_directional(model, X_test, return_proba=True)
    
    # Métricas básicas
    accuracy = accuracy_score(y_test, y_pred)
    
    # Métricas por classe
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, average=None, zero_division=0
    )
    
    # Métricas agregadas
    precision_macro = precision_recall_fscore_support(
        y_test, y_pred, average='macro', zero_division=0
    )[0]
    
    recall_macro = precision_recall_fscore_support(
        y_test, y_pred, average='macro', zero_division=0
    )[1]
    
    f1_macro = precision_recall_fscore_support(
        y_test, y_pred, average='macro', zero_division=0
    )[2]
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # Classification report
    report = classification_report(
        y_test, y_pred,
        target_names=['BAIXA', 'LATERAL', 'ALTA'],
        output_dict=True,
        zero_division=0
    )
    
    return {
        'accuracy': float(accuracy),
        'precision_macro': float(precision_macro),
        'recall_macro': float(recall_macro),
        'f1_macro': float(f1_macro),
        'precision_per_class': precision.tolist(),
        'recall_per_class': recall.tolist(),
        'f1_per_class': f1.tolist(),
        'support_per_class': support.tolist(),
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }


def print_directional_results(results: dict):
    """
    Imprime resultados da classificação direcional.
    
    Args:
        results: Dict com métricas
    """
    print("\n" + "="*80)
    print("RESULTADOS DA CLASSIFICAÇÃO DIRECIONAL")
    print("="*80)
    
    print(f"\n📊 MÉTRICAS GERAIS:")
    print(f"   Accuracy: {results['accuracy']:.4f}")
    print(f"   Precision (Macro): {results['precision_macro']:.4f}")
    print(f"   Recall (Macro): {results['recall_macro']:.4f}")
    print(f"   F1-Score (Macro): {results['f1_macro']:.4f}")
    
    print(f"\n📊 MÉTRICAS POR CLASSE:")
    labels = ['BAIXA', 'LATERAL', 'ALTA']
    
    print("Classe      Precision  Recall     F1-Score   Support")
    print("-" * 55)
    
    for i, label in enumerate(labels):
        precision = results['precision_per_class'][i]
        recall = results['recall_per_class'][i]
        f1 = results['f1_per_class'][i]
        support = results['support_per_class'][i]
        
        print(f"{label:<12}{precision:>9.4f}{recall:>9.4f}{f1:>11.4f}{support:>9}")
    
    print(f"\n📊 CONFUSION MATRIX:")
    cm = np.array(results['confusion_matrix'])
    
    print("         Pred:")
    print("Actual   BAIXA  LATERAL  ALTA")
    print("-" * 32)
    
    for i, label in enumerate(labels):
        row_str = f"{label:<8}"
        for j in range(len(labels)):
            row_str += f"{cm[i,j]:>7}"
        print(row_str)
    
    # Análise qualitativa
    print(f"\n💡 ANÁLISE:")
    
    accuracy = results['accuracy']
    f1_macro = results['f1_macro']
    
    if accuracy >= 0.65 and f1_macro >= 0.60:
        print("   ✅ EXCELENTE: Modelo com boa performance!")
    elif accuracy >= 0.55 and f1_macro >= 0.50:
        print("   ✅ BOM: Modelo funcional, pode melhorar.")
    elif accuracy >= 0.40:
        print("   ⚠️  MÉDIO: Melhor que aleatório, precisa ajustes.")
    else:
        print("   ❌ RUIM: Performance similar ao aleatório.")
    
    # Baseline aleatório
    baseline_acc = 1/3  # 33.33% para 3 classes
    improvement = (accuracy - baseline_acc) / baseline_acc * 100
    
    print(f"   📈 Melhoria vs baseline aleatório: {improvement:+.1f}%")


if __name__ == "__main__":
    # Teste básico
    print("Testando modelo direcional...")
    
    # Dados sintéticos
    np.random.seed(42)
    X = np.random.randn(1000, 60, 10)
    y = np.random.randint(0, 3, 1000)
    
    # Modelo
    model = build_directional_lstm(input_shape=(60, 10))
    print(f"Modelo criado: {model.count_params():,} parâmetros")
    
    # Class weights
    weights = calculate_class_weights(y)
    
    print("✅ Teste concluído!")