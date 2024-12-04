import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.fetch_data import fetch_data
from utils.generate_signal import generate_signal
from components.tabela import Tabela  # Import the new Tabela component
from components.grafico import Grafico  # Import the new Grafico component

# ------------------------------------------------

# Lista de criptomoedas
from assets_cryptos import stock, stock_names

# Lista de FIIs
# from assets_fiis import stock, stock_names

# ------------------------------------------------

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard", layout="wide")

# Título do Dashboard
st.title("Dashboard de Sinais")

# Seção para selecionar criptomoedas
st.sidebar.header("Configurações")
selected_cryptos = st.sidebar.multiselect(
    "Selecione os ativos", options=stock, default=stock
)

# Filtro por sinal
signal_filter = st.sidebar.multiselect(
    "Filtrar por sinal",
    options=["Compra", "Venda", "Espera"],
    default=["Compra", "Venda", "Espera"],
)

# Dicionário para armazenar dados e sinais
crypto_data = {}
signals = {}

# Barra de progresso
progress_bar = st.progress(0)
progress_step = 1 / len(selected_cryptos)

# Loop para processar cada criptomoeda selecionada
for idx, ticker in enumerate(selected_cryptos):
    data = fetch_data(ticker)
    signal = generate_signal(data)
    if signal in signal_filter:
        crypto_data[ticker] = data
        signals[ticker] = signal
    progress_bar.progress((idx + 1) * progress_step)

# Limpa a barra de progresso
progress_bar.empty()


# Criando uma coluna de rank baseada nos indicadores
# crypto_data["Ranking"] = (
#     crypto_data["RSI"].rank(
#         ascending=True
#     )  # Supondo que menor RSI é mais atraente para compra
#     + crypto_data["MACD"].rank(ascending=False)  # MACD mais positivo é melhor
#     + crypto_data["%K"].rank(ascending=False)  # %K maior é preferível
#     + crypto_data["%D"].rank(ascending=False)  # %D maior também é melhor
# )
# print(crypto_data)

# Create tabs
tab1, tab2 = st.tabs(["Indicadores", "Análise Gráfica"])

with tab1:
    st.subheader("Indicadores dos ativos Selecionados")
    Tabela(crypto_data, signals, stock_names)

with tab2:
    st.subheader("Análise Gráfica")
    for ticker, data in crypto_data.items():
        Grafico(ticker, data, stock_names)

# Atualização automática a cada 24 horas
st.sidebar.markdown("---")
if st.sidebar.button("Atualizar Dados"):
    st.experimental_rerun()
else:
    st.sidebar.write("Os dados são atualizados a cada 24 horas.")

# Rodapé
st.markdown("---")
st.write(
    "Dashboard desenvolvido para monitorar sinais de compra, venda e espera em criptomoedas com base na Média Móvel de 200 dias."
)
