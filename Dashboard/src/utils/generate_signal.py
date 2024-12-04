import pandas as pd


# Função para gerar o sinal de compra/venda/espera
def generate_signal(
    data, rsi_buy=30, rsi_sell=70, k_buy=20, k_sell=80, ma_multiplier_sell=1.2
):
    required_columns = ["Close", "MA_200", "RSI", "MACD", "MACD_Signal", "%K", "%D"]
    if (
        data is not None
        and not data.empty
        and all(col in data.columns for col in required_columns)
    ):
        last_close = data["Close"].iloc[-1]
        last_ma200 = data["MA_200"].iloc[-1]
        # last_rsi = data["RSI"].iloc[-1]
        # last_macd = data["MACD"].iloc[-1]
        # last_macd_signal = data["MACD_Signal"].iloc[-1]
        # last_k = data["%K"].iloc[-1]
        # last_d = data["%D"].iloc[-1]

        if (
            pd.isna(last_close)
            or pd.isna(last_ma200)
            # or pd.isna(last_rsi)
            # or pd.isna(last_macd)
            # or pd.isna(last_macd_signal)
            # or pd.isna(last_k)
            # or pd.isna(last_d)
        ):
            return "Espera"

        # Condições de compra
        # Se o preço de fechamento estiver abaixo da média móvel de 200 períodos (MA_200),
        # o RSI estiver abaixo de 30 (indicando que o ativo está sobrevendido),
        # o MACD estiver acima da linha de sinal do MACD (indicando uma tendência de alta),
        # e os indicadores estocásticos %K e %D estiverem ambos abaixo de 20 (indicando que o ativo está sobrevendido),
        # então é gerado um sinal de "Compra".
        if (
            last_close < last_ma200
            # and last_rsi < rsi_buy
            # and last_macd > last_macd_signal
            # and last_k < k_buy
            # and last_d < k_buy
        ):
            return "Compra"

        # Condições de venda
        # Se o preço de fechamento estiver igual ou acima do dobro da média móvel de 200 períodos (MA_200),
        # o RSI estiver acima de 70 (indicando que o ativo está sobrecomprado),
        # o MACD estiver abaixo da linha de sinal do MACD (indicando uma tendência de baixa),
        # e os indicadores estocásticos %K e %D estiverem ambos acima de 80 (indicando que o ativo está sobrecomprado),
        # então é gerado um sinal de "Venda".
        elif (
            last_close >= (last_ma200 * ma_multiplier_sell)
            # and last_rsi > rsi_sell
            # and last_macd < last_macd_signal
            # and last_k > k_sell
            # and last_d > k_sell
        ):
            return "Venda"

        # Se nenhuma das condições acima for atendida, é gerado um sinal de "Espera".
        else:
            return "Espera"
    else:
        return "Dados indisponíveis"
