import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Definir os ativos
assets = ["BTC-USD", "ETH-USD", "DX-Y.NYB", "^BVSP"]

# Nomes amigáveis para os ativos
asset_names = {
    "BTC-USD": "Bitcoin (BTC)",
    "ETH-USD": "Ethereum (ETH)",
    "DX-Y.NYB": "US Dollar Index (USD)",
    "^BVSP": "Bovespa (IBOV)"
}

# Baixar os dados históricos dos ativos
start_date = "2013-01-01"
end_date = "2024-07-21"

data = yf.download(assets, start=start_date, end=end_date)['Adj Close']

# Preencher valores ausentes
data.fillna(method='ffill', inplace=True)

# Calcular retornos diários
returns = data.pct_change().dropna()

# Simular o backtest
initial_investment = 10000
allocation = 1 / len(data.columns)
portfolio = (returns * allocation + 1).cumprod() * initial_investment

# Calcular métricas de desempenho
cumulative_returns = portfolio.iloc[-1] / initial_investment - 1
annualized_volatility = returns.std() * np.sqrt(252)
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

# Mostrar os resultados
results = pd.DataFrame({
    "Cumulative Return": cumulative_returns,
    "Annualized Volatility": annualized_volatility,
    "Sharpe Ratio": sharpe_ratio
})

print("Backtest Results")
print(results)

# Plotar a evolução do portfólio
plt.figure(figsize=(14, 7))
for column in portfolio.columns:
    plt.plot(portfolio.index, portfolio[column], label=asset_names[column])
plt.title('Evolução do Portfólio')
plt.xlabel('Data')
plt.ylabel('Valor do Portfólio')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
