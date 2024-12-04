import yfinance as yf

# Função para obter dados históricos
def get_historical_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    return data
