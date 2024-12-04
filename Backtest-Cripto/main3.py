import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

from assets import asset_names, bovespa

# Definir os ativos
cryptos = list(asset_names.keys())[:-1]
assets = cryptos + [bovespa]

# Baixar os dados históricos dos ativos
start_date = "2013-01-01"
end_date = "2024-07-21"
data = yf.download(assets, start=start_date, end=end_date)["Adj Close"]

# Preencher valores ausentes
data.fillna(method="ffill", inplace=True)
data.fillna(method="bfill", inplace=True)

# Calcular retornos diários
returns = data.pct_change().dropna()

# Calcular métricas
risk_free_rate = 0.03 / 252  # Assumindo uma taxa livre de risco anual de 3%

metrics = {}
for asset in returns.columns:
    asset_returns = returns[asset]
    mean_return = asset_returns.mean()
    volatility = asset_returns.std()
    sharpe_ratio = (mean_return - risk_free_rate) / volatility
    sortino_ratio = (mean_return - risk_free_rate) / asset_returns[asset_returns < 0].std()
    cumulative_return = (data[asset].iloc[-1] / data[asset].iloc[0]) - 1
    max_drawdown = ((data[asset] / data[asset].cummax()) - 1).min()

    metrics[asset] = {
        "Mean Return": mean_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Cumulative Return": cumulative_return,
        "Max Drawdown": max_drawdown
    }

metrics_df = pd.DataFrame(metrics).T

# Selecionar os 10 melhores ativos com base no Sharpe Ratio
top_10_assets = metrics_df.sort_values(by="Sharpe Ratio", ascending=False)

# Mostrar os resultados
print("Top 10 Assets by Sharpe Ratio")
print(top_10_assets)

# Plotar a evolução do portfólio
plt.figure(figsize=(14, 7))
for asset in top_10_assets.index:
    plt.plot(data.index, data[asset] / data[asset].iloc[0], label=asset_names[asset])
plt.title('Evolução dos Melhores Ativos')
plt.xlabel('Data')
plt.ylabel('Valor Normalizado')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
