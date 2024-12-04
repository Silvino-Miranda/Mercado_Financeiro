
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Definir os ativos
assets = [
    "VGIA11.SA",
    "AGRX11.SA",
    "BTCI11.SA",
    "BTLG11.SA",
    "GARE11.SA",
    "GLOG11.SA",
    "VISC11.SA",
    "CYCR11.SA",
    "VSLH11.SA",
    "^BVSP",
]

# Nomes amigáveis para os ativos
asset_names = {
    "VGIA11.SA": "VGIA11",
    "AGRX11.SA": "AGRX11",
    "BTCI11.SA": "BTCI11",
    "BTLG11.SA": "BTLG11",
    "GARE11.SA": "GARE11",
    "GLOG11.SA": "GLOG11",
    "VISC11.SA": "VISC11",
    "CYCR11.SA": "CYCR11",
    "VSLH11.SA": "VSLH11",
    "^BVSP": "Bovespa (IBOV)",
}

# Baixar os dados históricos dos ativos
start_date = "2013-01-01"
end_date = "2024-09-30"

# Baixar os dados e capturar falhas
data = yf.download(assets, start=start_date, end=end_date)["Adj Close"]

# Remover ativos que falharam no download
data = data.dropna(axis=1, how='all')

# Preencher valores ausentes com ffill
data.ffill(inplace=True)

# Verificar se o dataframe está vazio
if data.empty:
    raise ValueError("Nenhum dado disponível para os ativos selecionados.")

# Calcular retornos diários
returns = data.pct_change().dropna()

# Definir investimento inicial
initial_investment = 100000

# Pesos do portfólio (iguais para todos os ativos restantes)
weights = np.ones(len(data.columns)) / len(data.columns)

# Calcular o portfólio ao longo do tempo
portfolio = (returns * weights).sum(axis=1).cumsum() * initial_investment

# Verificar se o portfólio contém dados
if portfolio.empty:
    raise IndexError("O portfólio não contém dados suficientes para cálculo.")

# Calcular métricas de desempenho
cumulative_returns = portfolio.iloc[-1] / initial_investment - 1

# Exibir o resultado final
print(f"Retorno acumulado: {cumulative_returns * 100:.2f}%")

# Plotar o portfólio
portfolio.plot(title="Cumulative Portfolio Returns")
plt.show()
