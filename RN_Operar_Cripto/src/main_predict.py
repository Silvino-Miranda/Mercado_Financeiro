from data.data_loader import DataLoader
from utils.data_preprocessing import DataPreprocessor
from models.lstm_model import LSTMModel
from backtesting.backtester import Backtester
import pandas as pd


def main():
    # Definições de parâmetros
    symbol = "BTC-USD"
    start_date = "2010-01-01"
    interval = "1d"

    # Carregar os dados de hora em hora ou diário
    data_loader = DataLoader(symbol=symbol, start_date=start_date, interval=interval)
    data = data_loader.load_data()

    # Verificar se há valores não numéricos ou inconsistentes
    # print("Verificando a presença de valores não numéricos...")
    # print(data.dtypes)  # Verificar os tipos de dados das colunas

    # Remover caracteres indesejados e converter as colunas de preços para numérico
    # Substituir quaisquer pontos, vírgulas ou caracteres especiais que possam estar nos dados
    for col in ["Open", "High", "Low", "Close"]:
        data[col] = data[col].replace({",": ""}, regex=True)

    # Converter colunas de preços para float
    cols_to_convert = ["Open", "High", "Low", "Close", "Volume"]
    for col in cols_to_convert:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )  # Forçar conversão para numérico, erros para NaN

    # Verificar novamente se os dados estão válidos após a limpeza
    # print("Dados após a limpeza:")
    # print(data.head(10))

    # Preprocessar os dados
    preprocessor = DataPreprocessor()
    X, Y, dates, scaler = preprocessor.preprocess(data)

    # Verificar se o número de amostras está consistente entre X, Y e dates
    if len(X) != len(Y) or len(X) != len(dates):
        print(
            f"Inconsistência encontrada: X tem {len(X)} amostras, Y tem {len(Y)} amostras, e dates tem {len(dates)}."
        )
        return

    # Usar todo o conjunto de dados para previsão
    X_predict = X
    Y_actual = Y
    dates_all = dates

    # Carregar o modelo salvo
    lstm_model = LSTMModel(
        input_shape=(X_predict.shape[1], 1), model_path="lstm_model.keras"
    )

    # Fazer previsões usando o modelo carregado em todos os dados
    Y_pred = lstm_model.predict(X_predict)
    lstm_model.plot_predictions(Y_actual, Y_pred, scaler)

    # Inverter a normalização para os valores reais
    Y_actual_scaled = scaler.inverse_transform(Y_actual.reshape(-1, 1)).flatten()
    Y_pred_scaled = scaler.inverse_transform(Y_pred.reshape(-1, 1)).flatten()

    # Criar o DataFrame para o Backtrader
    data_bt = data.loc[dates_all].copy()
    data_bt.index = pd.to_datetime(
        dates_all
    )  # Garantir que o índice seja DateTimeIndex

    # Adicionar as previsões ao DataFrame
    data_bt["prediction"] = Y_pred_scaled
    data_bt["actual"] = Y_actual_scaled

    # Verificar se há valores NaN e remover se necessário
    data_bt.dropna(inplace=True)

    # Imprimir as primeiras linhas do DataFrame
    data_bt.head(10)

    # Backtesting
    backtester = Backtester(initial_capital=10000)
    backtester.add_data(data_bt)
    backtester.run()
    backtester.plot()

    # Salvar o histórico do backtest
    backtester.save_capital_history(f"capital_history-{symbol}.csv")


if __name__ == "__main__":
    main()
