import matplotlib.pyplot as plt

from utils.obter_dados import obter_dados
from utils.calcular_mme import calcular_mme
from utils.identificar_sinais import identificar_sinais
from utils.executar_backtest import executar_backtest


# Função Principal para Executar o Backtest em um Par de Moedas:
def backtest_par(
    par: str,
    MME_PERIOD: int,
    RISCO_RETORNO: int,
    TAMANHO_POSICAO: int,
    RISK_PERCENTAGE: float,
):
    print(f"Executando backtest para {par}")
    df = obter_dados(par)
    if df is None or df.empty:
        print(f"Backtest abortado: sem dados para {par}.")
        return
    df = calcular_mme(df, MME_PERIOD)
    df = identificar_sinais(df)
    df = executar_backtest(df, RISCO_RETORNO, TAMANHO_POSICAO, RISK_PERCENTAGE)
    df.to_csv(f"_backtest/{par}.csv", index=False, sep=";")
    plot_saldo(df, par)

# Plotando o saldo ao longo do tempo
def plot_saldo(df, par):
    plt.figure(figsize=(12, 6))
    plt.plot(df["Date"], df["Saldo"], label="Saldo")
    plt.title(f"Saldo ao longo do tempo para {par}")
    plt.xlabel("Data")
    plt.ylabel("Saldo")
    plt.legend()
    plt.grid()
    plt.show()
