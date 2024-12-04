import pandas as pd
import matplotlib.pyplot as plt
from backtest_ma200 import BacktestMA200

# Lista de ativos para o backtest
tickers = [
    "BTC-USD",
    "SOL-USD",
    "NMR-USD",
    "FET-USD",
    "AVAX-USD",
    "ADA-USD",
    "LINK-USD",
    "SNX-USD",
    "ETH-USD",
    "MATIC-USD",
    "RUNE-USD",
    "PENDLE-USD",
    "UNI-USD",
    "STX-USD",
    "IMX-USD",
    "MKR-USD",
]

# DataFrame para armazenar os resultados
results = []

# Itera sobre cada ativo, executando o backtest e armazenando os resultados
for ticker in tickers:
    try:
        backtest = BacktestMA200(ticker, file_path=f"data/{ticker}.csv")
        backtest.load_data()
        backtest.run_backtest()
        results.append(backtest.get_results())  # Corrigido para 'append'
    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")

# Concatenando os resultados para criar o DataFrame
results_df = pd.DataFrame(results)

# # Exibindo os resultados
print(results_df.sort_values("profit_percent", ascending=False))

# Plotando o gráfico comparativo
plt.figure(figsize=(12, 8))
plt.bar(results_df["ticker"], results_df["profit_percent"], color="skyblue")
plt.xlabel("Ativo")
plt.ylabel("Lucro (%)")
plt.title("Comparação do Desempenho dos Ativos no Backtest MA200")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
