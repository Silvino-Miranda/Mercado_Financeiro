import pandas as pd
import yfinance as yf


# Função para Obter Dados Históricos:
def obter_dados(ticker):
    try:
        data = yf.download(ticker, period="5y", interval="1d")

        # Verificar e ajustar colunas com MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Resetar o índice para que a data seja uma coluna
        data = data.reset_index()

        # Deixar as colunas que serão utilizadas
        data = data[["Date", "Open", "High", "Low", "Close", "Volume"]]

        if data.empty:
            print(f"Dados não disponíveis para o ativo {ticker}.")
            return None
        return data
    except Exception as e:
        print(f"Ocorreu um erro ao baixar os dados do ativo {ticker}: {e}")
        return None
