import talib as ta

# Função para calcular indicadores técnicos
def calculate_technical_analysis(data):
    indicators = {}

    # Exemplo de cálculo de alguns indicadores
    indicators["SMA_50"] = ta.SMA(data["Close"], timeperiod=50).tolist()
    indicators["SMA_200"] = ta.SMA(data["Close"], timeperiod=200).tolist()
    indicators["RSI"] = ta.RSI(data["Close"], timeperiod=14).tolist()
    macd, macd_signal, _ = ta.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    indicators["MACD"] = macd.tolist()
    indicators["MACD_Signal"] = macd_signal.tolist()

    return indicators
