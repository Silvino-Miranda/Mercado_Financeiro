import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml.data.data_loader import DataLoader
from src.ml.utils.data_preprocessing import DataPreprocessor
from src.ml.models.lstm_model import LSTMModel
from src.ml.backtesting.backtester import Backtester
import pandas as pd


def main():
    # Definições de parâmetros
    symbol = "BTCUSDT"
    interval = "30m"

    # Carregar os dados do arquivo local com TODOS os indicadores técnicos
    data_loader = DataLoader(
        symbol=symbol, 
        interval=interval,
        use_local_file=True,
        local_filename="BTCUSDT_30m_full.csv"
    )
    df = data_loader.load_data()

    # Definir features (MESMAS do treinamento)
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
    
    print(f"\nUsando {len(feature_columns)} features: {feature_columns}")

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

    print(f"\nTotal de sequências disponíveis: {len(X)}")
    
    # IMPORTANTE: Usar apenas dados de TESTE (últimos 15%) para backtesting válido
    # Isso evita data leakage - o modelo não pode ser testado com dados que ele viu no treinamento
    train_size = 0.7
    val_size = 0.15
    total_samples = len(X)
    train_end = int(total_samples * train_size)
    val_end = train_end + int(total_samples * val_size)
    
    # Separar apenas o conjunto de TESTE (dados não vistos)
    X_test = X[val_end:]
    Y_test = Y[val_end:]
    dates_test = dates[val_end:]
    
    print(f"Usando apenas dados de TESTE para backtesting: {len(X_test)} sequências")
    print(f"Período de teste: {dates_test[0]} a {dates_test[-1]}")
    print(f"⚠️ IMPORTANTE: Estes dados NÃO foram usados no treinamento!")
    
    # Usar X_test, Y_test, dates_test daqui em diante
    X = X_test
    Y = Y_test
    dates = dates_test
    
    print(f"\nTotal de sequências para previsão: {len(X)}")
    
    # Carregar o modelo salvo da pasta checkpoints
    model_path = "src/ml/checkpoints/lstm_model.keras"
    print(f"Carregando modelo treinado de: {model_path}")
    lstm_model = LSTMModel(
        input_shape=(X.shape[1], X.shape[2]),
        output_size=3,  # Close, High, Low
        model_path=model_path
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
    # Calcular o índice inicial no DataFrame original
    # val_end já foi calculado como 29,800 (85% do total)
    # Precisamos pular sequence_length (60) + val_end
    start_idx = 60 + val_end
    data_bt = df.iloc[start_idx:start_idx+len(Y)].copy()
    data_bt.reset_index(drop=True, inplace=True)
    
    print(f"Dados extraídos do índice {start_idx} a {start_idx+len(Y)} do dataset original")
    
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
    
    # Salvar o histórico do backtest na pasta outputs
    import os
    os.makedirs("src/ml/outputs", exist_ok=True)
    output_path = f"src/ml/outputs/capital_history-{symbol}.csv"
    backtester.save_capital_history(output_path)
    print(f"\n✅ Histórico de capital salvo em: {output_path}")
    
    # Note: backtester.plot() is disabled due to backtrader plotting issues
    # Use the Dash app (src/app.py) to visualize results instead


if __name__ == "__main__":
    main()
