# src/data/indicator.py

import ta
import pandas as pd


class IndicatorCalculator:
    def __init__(self, df):
        self.df = df

    def calculate_indicators(self):
        # Certifique-se de que 'Close' é uma série 1D
        self.df["Close"] = self.df["Close"].squeeze()

        # RSI
        self.df["RSI_14"] = ""
        # ta.momentum.RSIIndicator(close=self.df["Close"], window=14).rsi()

        # MACD
        # macd = ta.trend.MACD(close=self.df["Close"])
        self.df["MACD"] = "" # macd.macd()
        self.df["MACD_Signal"] = "" # macd.macd_signal()

        # Bollinger Bands
        # bollinger = ta.volatility.BollingerBands(close=self.df["Close"], window=20)
        self.df["BB_High"] = "" # bollinger.bollinger_hband()
        self.df["BB_Low"] = ""  # bollinger.bollinger_lband()

        # Médias Móveis
        self.df["SMA_20"] = self.df["Close"].rolling(window=20).mean()
        self.df["EMA_20"] = self.df["Close"].ewm(span=20, adjust=False).mean()

        # Estocástico Oscilador
        stoch = ta.momentum.StochasticOscillator(
            high=self.df["High"],
            low=self.df["Low"],
            close=self.df["Close"],
            window=14,
        )
        self.df["Stoch"] = ""  # stoch.stoch()

        # On-Balance Volume (OBV)
        self.df["OBV"] = ""
        # ta.volume.OnBalanceVolumeIndicator(close=self.df["Close"], volume=self.df["Volume"]).on_balance_volume()

        # Remover possíveis NaNs gerados pelo cálculo dos indicadores
        self.df = self.df.dropna()

        return self.df
