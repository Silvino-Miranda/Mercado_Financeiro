import yfinance as yf
import streamlit as st

# Função para buscar dados de uma criptomoeda
def download_data(ticker):
    try:
        data = yf.download(ticker, period="5y", interval="1d")
        # Resetar o índice para que a data seja uma coluna
        data = data.reset_index()

        # renomear as colunas
        data.columns = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]

        # Deixar as colunas que serão utilizadas
        data = data[["Date", "Open", "High", "Low", "Close", "Volume"]]

        if data.empty:
            st.warning(f"Dados não disponíveis para o ativo {ticker}.")
            return None
        return data
    except Exception as e:
        st.error(f"Ocorreu um erro ao baixar os dados do ativo {ticker}: {e}")
        return None

# Função para calcular indicadores
def calculate_indicators(data):
    data["MA_200"] = data["Close"].rolling(window=200).mean()
    
    # Média Móvel de 50 dias
    data["MA_50"] = data["Close"].rolling(window=50).mean()
    
    # Média Móvel Exponencial de 20 dias
    data["EMA_20"] = data["Close"].ewm(span=20, adjust=False).mean()
    
    # Índice de Força Relativa (RSI)
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    data["BB_Middle"] = data["Close"].rolling(window=20).mean()
    data["BB_Upper"] = data["BB_Middle"] + 2 * data["Close"].rolling(window=20).std()
    data["BB_Lower"] = data["BB_Middle"] - 2 * data["Close"].rolling(window=20).std()
    
    # Média Móvel Convergente e Divergente (MACD)
    data["MACD"] = data["Close"].ewm(span=12, adjust=False).mean() - data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    
    # Estocástico
    low_14 = data["Low"].rolling(window=14).min()
    high_14 = data["High"].rolling(window=14).max()
    data["%K"] = (data["Close"] - low_14) * 100 / (high_14 - low_14)
    data["%D"] = data["%K"].rolling(window=3).mean()
    
    # Média Móvel de 100 dias
    data["MA_100"] = data["Close"].rolling(window=100).mean()
    
    # Volume Médio de 20 dias
    data["Volume_MA_20"] = data["Volume"].rolling(window=20).mean()
    
    data.dropna(subset=["Close"], inplace=True)
    return data

# Função para buscar dados de uma criptomoeda e calcular indicadores
def fetch_data(ticker):
    data = download_data(ticker)
    if data is not None:
        data = calculate_indicators(data)
    return data
