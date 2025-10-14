# src/main_train.py

from data.data_loader import DataLoader
from utils.data_preprocessing import DataPreprocessor
from models.lstm_model import LSTMModel
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

    # Definir features disponíveis (apenas as que não dependem de Volume)
    # Nota: RSI_14, MACD, BB, Stoch, OBV têm NaN porque dependem de Volume que não está disponível
    feature_columns = [
        "Open",
        "High",
        "Low",
        "Close",  # Adicionando Close como feature também
        "SMA_20",
        "EMA_20",
    ]
    target_columns = ["Close", "High", "Low"]
    
    print(f"Features usadas ({len(feature_columns)}): {feature_columns}")
    print(f"Targets ({len(target_columns)}): {target_columns}")
    print("Nota: Indicadores que dependem de Volume (RSI, MACD, BB, Stoch, OBV) não estão disponíveis\n")

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
    print("Histórico de treinamento:")
    print(history.history)

    # (Opcional) Plotar o histórico de treinamento (perda ao longo das épocas)
    # Você precisará implementar o método 'plot_training_history' na classe LSTMModel
    # lstm_model.plot_training_history(history)

    # Salvar o modelo treinado para uso futuro
    lstm_model.model.save("lstm_model.keras")
    print("Modelo treinado e salvo como 'lstm_model.keras'.")


if __name__ == "__main__":
    main()
