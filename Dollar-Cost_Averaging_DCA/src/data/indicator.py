# src/data/indicator.py

# import ta
import pandas as pd


class IndicatorCalculator:
    def __init__(self, df):
        self.df = df

    def calculate_indicators(self):
        # RSI
        # self.df["RSI_14"] = ""
        # ta.momentum.RSIIndicator(Close=self.df["Close"], window=14).rsi()

        # MACD
        # macd = ta.trend.MACD(Close=self.df["Close"])
        # self.df["MACD"] = ""  # macd.macd()
        # self.df["MACD_Signal"] = ""  # macd.macd_signal()

        # Bollinger Bands
        # bollinger = ta.volatility.BollingerBands(Close=self.df["Close"], window=20)
        # self.df["BB_High"] = ""  # bollinger.bollinger_hband()
        # self.df["BB_Low"] = ""  # bollinger.bollinger_lband()

        # Médias Móveis
        # self.df["EMA_20"] = self.df["Close"].ewm(span=20, adjust=False).mean()
        # self.df["SMA_20"] = self.df["Close"].rolling(window=20).mean()
        self.df["SMA_200"] = self.df["Close"].rolling(window=200).mean()

        # Estocástico Oscilador
        # stoch = ta.momentum.StochasticOscillator(
        #     high=self.df["High"],
        #     low=self.df["Low"],
        #     Close=self.df["Close"],
        #     window=14,
        # )
        # self.df["Stoch"] = ""  # stoch.stoch()

        # On-Balance Volume (OBV)
        # self.df["OBV"] = ""
        # ta.volume.OnBalanceVolumeIndicator(Close=self.df["Close"], volume=self.df["Volume"]).on_balance_volume()

        # Cria a coluna de sinais de compra/venda com base no cruzamento da média móvel
        signals = []

        for i in range(len(self.df)):
            if self.df["Close"].iloc[i] < self.df["SMA_200"].iloc[i]:
                signals.append("Compra")

            elif self.df["Close"].iloc[i] >= (self.df["SMA_200"].iloc[i] * 2):
                signals.append("Venda")

            else:
                signals.append("Espera")

        self.df["Sinal"] = signals

        # Remover possíveis NaNs gerados pelo cálculo dos indicadores
        self.df = self.df.dropna()

        return self.df
