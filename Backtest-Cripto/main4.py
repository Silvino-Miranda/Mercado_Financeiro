import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

from assets import asset_names, bovespa

# Definir os ativos selecionados
selected_assets = [
    "BTC-USD",
    "SOL-USD",
    "MATIC-USD",
    "LINK-USD",
    "OCEAN-USD",
    "ADA-USD",
    "SNX-USD",
    "MAN-USD",
    "ETH-USD",
    "FET-USD",
]

# Baixar os dados históricos dos ativos
start_date = "2013-01-01"
end_date = "2024-07-21"
data = yf.download(selected_assets, start=start_date, end=end_date)["Adj Close"]

# Preencher valores ausentes
data.fillna(method="ffill", inplace=True)
data.fillna(method="bfill", inplace=True)

# Obter o preço de fechamento mais recente para cada ativo
latest_prices = data.iloc[-1]

# Calcular a alocação de R$ 1000 igualmente entre os 10 ativos
total_investment = 1000
allocation_per_asset = total_investment / len(selected_assets)

# Calcular a quantidade de cada ativo que pode ser comprada
quantities = allocation_per_asset / latest_prices

# Criar um DataFrame para exibir as alocações
allocations = pd.DataFrame(
    {
        "Asset": selected_assets,
        "Latest Price (BRL)": latest_prices,
        "Allocation (BRL)": allocation_per_asset,
        "Quantity": quantities,
    }
)

# Mostrar os resultados
print("Alocações de R$ 1000 entre os 10 ativos selecionados")
print(allocations)

# Plotar a alocação
plt.figure(figsize=(14, 7))
allocations.set_index("Asset")["Quantity"].plot(kind="bar")
plt.title("Quantidade de cada ativo comprada com R$ 1000")
plt.xlabel("Ativo")
plt.ylabel("Quantidade")
plt.grid(True)
plt.show()
