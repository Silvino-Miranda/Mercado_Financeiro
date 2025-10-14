from data.data_loader import DataLoader
from utils.data_preprocessing import DataPreprocessor
from models.lstm_model import LSTMModel
from backtesting.backtester import Backtester
import pandas as pd


def main():
    # Definições de parâmetros
    symbol = "BTCUSDT"
    interval = "30m"

    # Carregar os dados do arquivo local BTCUSDT_30m.csv
    data_loader = DataLoader(
        symbol=symbol, 
        interval=interval,
        use_local_file=True,
        local_filename="BTCUSDT_30m.csv"
    )
    df = data_loader.load_data()

    # Definir as mesmas features e targets usados no treinamento
    feature_columns = [
        "Open",
        "High",
        "Low",
        "SMA_20",
        "EMA_20",
    ]
    target_columns = ["Close", "High", "Low"]

    # Inicializar o preprocessador com as mesmas configurações do treinamento
    preprocessor = DataPreprocessor(
        feature_columns=feature_columns,
        target_columns=target_columns,
        sequence_length=60,
    )

    # Pré-processar os dados
    X, Y, dates = preprocessor.fit_transform(df)

    # Verificar se o número de amostras está consistente entre X, Y e dates
    if len(X) != len(Y) or len(X) != len(dates):
        print(
            f"Inconsistência encontrada: X tem {len(X)} amostras, Y tem {len(Y)} amostras, e dates tem {len(dates)}."
        )
        return

    print(f"\nTotal de sequências para previsão: {len(X)}")
    
    # Carregar o modelo salvo
    print("Carregando modelo treinado...")
    lstm_model = LSTMModel(
        input_shape=(X.shape[1], X.shape[2]),
        output_size=3,  # Close, High, Low
        model_path="lstm_model.keras"
    )

    # Fazer previsões usando o modelo carregado
    print("Gerando previsões...")
    Y_pred = lstm_model.predict(X)
    
    # Inverter a normalização para os valores reais
    print("Desnormalizando valores...")
    Y_actual_scaled = preprocessor.scaler.inverse_transform(Y)
    Y_pred_scaled = preprocessor.scaler.inverse_transform(Y_pred)
    
    # Pegar apenas a coluna Close (primeira coluna dos targets)
    Y_actual_close = Y_actual_scaled[:, 0]
    Y_pred_close = Y_pred_scaled[:, 0]

    # Criar o DataFrame para o Backtrader
    print("Preparando dados para backtesting...")
    data_bt = df.iloc[60:60+len(Y)].copy()  # Pular as primeiras 60 linhas (sequence_length)
    data_bt.reset_index(drop=True, inplace=True)
    
    # Selecionar apenas as colunas necessárias (remove colunas com NaN)
    columns_needed = ['Date', 'Open', 'High', 'Low', 'Close', 'SMA_20', 'EMA_20']
    data_bt = data_bt[columns_needed].copy()
    
    # Renomear e preparar colunas para o backtester
    data_bt.rename(columns={
        'Date': 'datetime',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close'
    }, inplace=True)
    
    # Adicionar coluna de volume (padrão = 1.0)
    data_bt['volume'] = 1.0

    # Adicionar as previsões ao DataFrame (Close previsto)
    data_bt["prediction"] = Y_pred_close
    data_bt["actual"] = Y_actual_close
    
    print(f"\nDataFrame preparado: {len(data_bt)} linhas")
    print("\nAmostra dos dados com previsões:")
    print(data_bt[["close", "actual", "prediction"]].head(10))

    # Verificar se há valores NaN e remover se necessário
    initial_rows = len(data_bt)
    data_bt.dropna(inplace=True)
    if len(data_bt) < initial_rows:
        print(f"Aviso: {initial_rows - len(data_bt)} linhas removidas por conter NaN")

    # Imprimir as primeiras linhas do DataFrame
    data_bt.head(10)

    # Backtesting com capital ajustado para o preço do BTC
    initial_capital = 100000  # $100k para comprar pelo menos 1 BTC
    print(f"\nIniciando backtesting com capital inicial de ${initial_capital:,.2f}")
    
    backtester = Backtester(initial_capital=initial_capital)
    backtester.add_data(data_bt)
    backtester.run()
    
    # Salvar o histórico do backtest
    backtester.save_capital_history(f"capital_history-{symbol}.csv")
    print(f"\nHistórico de capital salvo em: capital_history-{symbol}.csv")
    
    # Note: backtester.plot() is disabled due to backtrader plotting issues
    # Use the Dash app (src/app.py) to visualize results instead


if __name__ == "__main__":
    main()
