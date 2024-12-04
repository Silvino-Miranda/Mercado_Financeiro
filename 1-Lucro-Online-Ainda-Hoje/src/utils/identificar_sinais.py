# Função para Identificar Sinais de Compra e Venda:
def identificar_sinais(df):
    df["Sinal"] = 0
    df.loc[
        (df["Close"] > df["MME"]) & (df["Close"].shift(1) <= df["MME"].shift(1)),
        "Sinal",
    ] = 1  # Sinal de Compra
    df.loc[
        (df["Close"] < df["MME"]) & (df["Close"].shift(1) >= df["MME"].shift(1)),
        "Sinal",
    ] = -1  # Sinal de Venda
    return df