# import numpy as np
# import pandas as pd
# import yfinance as yf
# import os


# class DataHandler:
#     def __init__(self, ticker, start, end, file_path):
#         self.ticker = ticker
#         self.start = start
#         self.end = end
#         self.file_path = file_path

#     def load_data(self):
#         # Carregar dados do arquivo ou fazer download se o arquivo não existir
#         if os.path.exists(self.file_path):
#             self.data = pd.read_csv(self.file_path)
#         else:
#             self.data = yf.download(self.ticker, start=self.start, end=self.end)[
#                 ["Close"]
#             ]
            
#             self.data = self.data[['Close']]
#             self.data.columns = ['close']  # Renomeando a coluna para minúsculas
#             self.data = self.data.reset_index()  # Reseta o índice para facilitar o acesso

#             self.data.to_csv(self.file_path, index=False, sep=";")

#         # Calcula a média móvel de 200 dias
#         self.calculate_ma200()
#         # self.data["sinal"] = self.calculate_signals()

#     def calculate_ma200(self):
#         # Calcula a média móvel e aplica o sinal de compra/venda linha a linha
#         self.data["ma200"] = self.data["close"].rolling(window=200).mean()
#         self.data.dropna(inplace=True)

#     def calculate_signals(self):
#         # Cria a coluna de sinais de compra/venda com base no cruzamento da média móvel
#         signals = []
#         position = None  # None = não posicionado, True = comprado, False = vendido

#         for i in range(len(self.data)):
#             if (
#                 self.data["close"].iloc[i] < self.data["ma200"].iloc[i]
#                 and position != True
#             ):
#                 signals.append("Compra")
#                 position = True
#             elif (
#                 self.data["close"].iloc[i] > self.data["ma200"].iloc[i]
#                 and position != False
#             ):
#                 signals.append("Venda")
#                 position = False
#             else:
#                 signals.append("Espera")

#         return signals
