# src/main_train.py

from data.data_loader import DataLoader
from utils.data_preprocessing import DataPreprocessor
from models.lstm_model import LSTMModel
import pandas as pd


def main():
    # Definições de parâmetros
    symbol = "BTC-USD"
    start_date = "2024-01-01"  # Ajuste a data de início conforme necessário
    interval = "1d"  # Pode ser '1d' para diário ou '1h' para horário

    # Carregar os dados com indicadores técnicos já calculados
    data_loader = DataLoader(symbol=symbol, start_date=start_date, interval=interval)
    df = data_loader.load_data()

    # Definir colunas de features e targets
    feature_columns = [
        "Open",
        "High",
        "Low",
        "SMA_20",
        "EMA_20",
        "RSI_14",
        "MACD",
        "MACD_Signal",
        "BB_High",
        "BB_Low",
        "Stoch",
        "OBV",
    ]
    target_columns = ["Close", "High", "Low"]

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
    history = lstm_model.train(
        X_train,
        Y_train,
        X_val=X_val,
        Y_val=Y_val,
        epochs=10,  # Ajuste o número de épocas conforme necessário
        batch_size=64,  # Ajuste o tamanho do lote conforme necessário
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
