# Função para Calcular a MME:
def calcular_mme(df, periodo):
    df["MME"] = df["Close"].ewm(span=periodo, adjust=False).mean()
    df.reset_index(drop=True, inplace=True)
    return df
