# src/ml/main_train.py

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml.data.data_loader import DataLoader
from src.ml.utils.data_preprocessing import DataPreprocessor
from src.ml.models.lstm_model import LSTMModel
import pandas as pd


def main():
    # Definições de parâmetros
    symbol = "BTCUSDT"
    interval = "30m"  # Intervalo de 30 minutos

    # Carregar os dados do arquivo local com TODOS os indicadores técnicos
    data_loader = DataLoader(
        symbol=symbol, 
        interval=interval,
        use_local_file=True,
        local_filename="BTCUSDT_30m_full.csv"
    )
    df = data_loader.load_data()
    
    print(f"\n{'='*70}")
    print("BASE DE DADOS COMPLETA - 8 ANOS DE HISTÓRICO")
    print(f"{'='*70}")
    print(f"Total de registros: {len(df):,}")
    print(f"Período: {df['Date'].min()} a {df['Date'].max()}")
    print(f"Colunas disponíveis: {df.columns.tolist()}")
    print(f"{'='*70}\n")

    # ========================================
    # TODAS AS 18 FEATURES TÉCNICAS DISPONÍVEIS
    # ========================================
    feature_columns = [
        # 1. Dados OHLC (4 features)
        "Open",
        "High",
        "Low",
        "Close",
        
        # 2. Bollinger Bands (3 features)
        "BB_High",
        "BB_Mid",
        "BB_Low",
        
        # 3. Keltner Channel (2 features)
        "Keltner_High",
        "Keltner_Low",
        
        # 4. Donchian Channel (2 features)
        "Donchian_High",
        "Donchian_Low",
        
        # 5. Médias Móveis Exponenciais (3 features)
        "EMA_9",
        "EMA_20",
        "EMA_50",
        
        # 6. Médias Móveis Simples (2 features)
        "SMA_20",
        "SMA_50",
        
        # 7. Indicadores de Momentum/Tendência (2 features)
        "Aroon_Spread",
        "MACD_Hist",
    ]
    
    target_columns = ["Close", "High", "Low"]
    
    print(f"\n{'='*70}")
    print("CONFIGURAÇÃO DAS FEATURES")
    print(f"{'='*70}")
    print(f"Total de features: {len(feature_columns)}")
    print(f"\n📊 Grupos de Indicadores:")
    print(f"   • OHLC:                4 features")
    print(f"   • Bollinger Bands:     3 features")
    print(f"   • Keltner Channel:     2 features")
    print(f"   • Donchian Channel:    2 features")
    print(f"   • Médias Exponenciais: 3 features")
    print(f"   • Médias Simples:      2 features")
    print(f"   • Momentum/Tendência:  2 features")
    print(f"\n🎯 Targets para predição: {target_columns}")
    print(f"{'='*70}\n")

    # Inicializar o preprocessador de dados
    preprocessor = DataPreprocessor(
        feature_columns=feature_columns,
        target_columns=target_columns,
        sequence_length=60,
    )

    # Pré-processar os dados (ajusta o scaler nos dados de treinamento)
    X, Y, dates = preprocessor.fit_transform(df)

    # Verificar a consistência dos tamanhos
    assert len(X) == len(Y) == len(dates), (
        f"Inconsistência nos tamanhos dos arrays: "
        f"len(X)={len(X)}, len(Y)={len(Y)}, len(dates)={len(dates)}"
    )

    # Dividir os dados em conjuntos de treinamento, validação e teste
    (
        (X_train, Y_train, dates_train),
        (X_val, Y_val, dates_val),
        (X_test, Y_test, dates_test),
    ) = preprocessor.split_data(X, Y, dates)

    # Exibir as formas dos conjuntos de dados
    print("Formas dos conjuntos de dados:")
    print(f"X_train: {X_train.shape}, Y_train: {Y_train.shape}")
    print(f"X_val: {X_val.shape}, Y_val: {Y_val.shape}")
    print(f"X_test: {X_test.shape}, Y_test: {Y_test.shape}")

    # Inicializar o modelo LSTM
    input_shape = (
        X_train.shape[1],
        X_train.shape[2],
    )  # (sequence_length, num_features)
    output_size = Y_train.shape[1]  # Número de valores a serem previstos (3)

    lstm_model = LSTMModel(input_shape=input_shape, output_size=output_size)

    # Treinar o modelo com os dados de treinamento e validação
    print("\n" + "="*70)
    print("INICIANDO TREINAMENTO COM CONFIGURAÇÃO OTIMIZADA")
    print("="*70)
    print(f"Epochs: 50 (aumento de 10 para 50)")
    print(f"Batch size: 32 (redução de 64 para 32 para melhor convergência)")
    print(f"Early stopping: Ativado (paciência de 10 epochs)")
    print(f"Learning rate: Padrão (0.001 com Adam optimizer)")
    print("="*70 + "\n")
    
    history = lstm_model.train(
        X_train,
        Y_train,
        X_val=X_val,
        Y_val=Y_val,
        epochs=50,  # Aumentado de 10 para 50 epochs
        batch_size=32,  # Reduzido de 64 para 32 para melhor convergência
    )

    # Salvar o histórico de treinamento para uso futuro
    print("\n" + "="*70)
    print("HISTÓRICO DE TREINAMENTO")
    print("="*70)
    print(history.history)
    print("="*70 + "\n")

    # Salvar o modelo treinado na pasta checkpoints
    import os
    os.makedirs("src/ml/checkpoints", exist_ok=True)
    model_path = "src/ml/checkpoints/lstm_model.keras"
    lstm_model.model.save(model_path)
    
    print("\n" + "="*70)
    print("✅ MODELO SALVO COM SUCESSO")
    print("="*70)
    print(f"📁 Local: {model_path}")
    print(f"📊 Checkpoints: src/ml/checkpoints/model_weights_epoch_*.h5")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
