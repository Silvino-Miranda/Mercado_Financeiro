import pandas as pd
import matplotlib.pyplot as plt
from backtest_dca import BacktestDCA

# Lista de ativos para o backtest
tickers = ["BTC-USD"]

# DataFrame para armazenar os resultados
results = []

# Itera sobre cada ativo, executando o backtest e armazenando os resultados
for ticker in tickers:
    try:
        backtest = BacktestDCA(ticker, file_path=f"data/{ticker}.csv")
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
