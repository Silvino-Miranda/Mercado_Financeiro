import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Definir os ativos
assets = [
    "BCRI11.SA",
    "ALZR11.SA",
    "TVRI11.SA",
    "VGIP11.SA",
    "HGLG11.SA",
    "GTWR11.SA",
    "GGRC11.SA",
    "KNCR11.SA",
    "RBVA11.SA",
    "BTLG11.SA",
    "RNGO11.SA",
    "CVBI11.SA",
    "XPCI11.SA",
    "BTCI11.SA",
    "^BVSP",
]

# Baixar os dados históricos dos ativos
start_date = "2024-01-01"
# start_date = "2013-01-01"
end_date = "2024-09-30"

# Baixar os dados e capturar falhas
data = yf.download(assets, start=start_date, end=end_date)["Adj Close"]

# Remover ativos que falharam no download
data = data.dropna(axis=1, how="all")

# Preencher valores ausentes com ffill
data.ffill(inplace=True)

# Verificar se o dataframe está vazio
if data.empty:
    raise ValueError("Nenhum dado disponível para os ativos selecionados.")

# Calcular retornos diários
returns = data.pct_change().dropna()

# Definir investimento inicial
initial_investment = 10000

# Pesos do portfólio (iguais para todos os ativos restantes)
weights = np.ones(len(data.columns)) / len(data.columns)

# Calcular os retornos do portfólio
portfolio_returns = (returns * weights).sum(axis=1)

# Calcular o portfólio ao longo do tempo
portfolio = (1 + portfolio_returns).cumprod() * initial_investment

# Verificar se o portfólio contém dados
if portfolio.empty:
    raise IndexError("O portfólio não contém dados suficientes para cálculo.")

# Calcular o retorno acumulado por ativo
cumulative_returns = (1 + returns).prod() - 1

# Volatilidade anualizada por ativo
annualized_volatility = returns.std() * np.sqrt(252)

# Índice de Sharpe por ativo
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)

# Criar o DataFrame de resultados por ativo
results = pd.DataFrame(
    {
        "Cumulative Return": cumulative_returns,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
    }
)

# Calcular as métricas do portfólio
portfolio_cumulative_return = portfolio.iloc[-1] / initial_investment - 1
portfolio_annualized_volatility = portfolio_returns.std() * np.sqrt(252)
portfolio_sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

# Adicionar as métricas do portfólio aos resultados
results.loc['Portfolio'] = [portfolio_cumulative_return, portfolio_annualized_volatility, portfolio_sharpe_ratio]

# Exibir os resultados
print("Backtest Results")
print(results)

# Plotar a evolução do portfólio
plt.figure(figsize=(14, 7))
plt.plot(portfolio.index, portfolio, label="Portfolio")
plt.title("Evolução do Portfólio")
plt.xlabel("Data")
plt.ylabel("Valor do Portfólio")
plt.legend(loc="upper left")
plt.grid(True)
plt.show()
