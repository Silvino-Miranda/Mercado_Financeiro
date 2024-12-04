import pandas as pd

# Função para Executar o Backtest:
def executar_backtest(
    df: pd.DataFrame, RISCO_RETORNO, TAMANHO_POSICAO, RISK_PERCENTAGE
) -> pd.DataFrame:
    posicao = 0
    saldo = 100
    lista_saldos = [saldo]  # Inicializa com o saldo inicial

    for i in range(1, len(df)):
        if df["Sinal"].iloc[i] == 1 and posicao == 0:
            # Entrada na posição de compra
            entrada = df["Close"].iloc[i]
            stop_loss = entrada * (1 - RISK_PERCENTAGE)
            take_profit = entrada * (1 + RISCO_RETORNO * RISK_PERCENTAGE)
            posicao = 1
            print(f"Compra em {entrada} na data {df['Date'].iloc[i]}")
        elif posicao == 1:
            if df["Low"].iloc[i] <= stop_loss:
                # Stop Loss acionado
                perda = (entrada - stop_loss) * TAMANHO_POSICAO
                saldo -= perda
                posicao = 0
                print(f"Stop Loss em {stop_loss} na data {df['Date'].iloc[i]}")
            elif df["High"].iloc[i] >= take_profit:
                # Take Profit acionado
                ganho = (take_profit - entrada) * TAMANHO_POSICAO
                saldo += ganho
                posicao = 0
                print(f"Take Profit em {take_profit} na data {df['Date'].iloc[i]}")
            elif df["Sinal"].iloc[i] == -1:
                # Sinal de venda aparece, fechamos a posição
                saida = df["Close"].iloc[i]
                resultado = (saida - entrada) * TAMANHO_POSICAO
                saldo += resultado
                posicao = 0
                print(
                    f"Fechando posição em {saida} na data {df['Date'].iloc[i]} devido ao sinal de venda"
                )
        lista_saldos.append(saldo)

    df["Saldo"] = lista_saldos
    return df
