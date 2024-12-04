# src/data/data_loader.py

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

from src.data.indicator import IndicatorCalculator
from src.data.data_save import DataSave


class DataLoader:
    def __init__(
        self,
        symbol="BTC-USD",
        start_date="2015-01-01",
        end_date=None,
        interval="1h",
        data_dir="data",
    ):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date if end_date else datetime.now().strftime("%Y-%m-%d")
        self.interval = interval
        self.data_dir = data_dir

        # Criar o nome do arquivo com base no símbolo e intervalo de tempo
        self.filename = f"{self.symbol}_{self.start_date}_to_{self.end_date}_{self.interval}".replace(
            "/", "-"
        )
        self.filepath = os.path.join(self.data_dir, self.filename)

    def download_data(self):
        # Verificar se end_date não está no futuro
        today = datetime.now().strftime("%Y-%m-%d")
        if self.end_date > today:
            print("A data de término está no futuro. Ajustando para a data atual.")
            self.end_date = today

        # Verificar se o intervalo é '1h' e ajustar o intervalo de datas
        if self.interval == "1h":
            max_days = 729  # 730 dias no total
            end_datetime = datetime.strptime(self.end_date, "%Y-%m-%d")
            start_datetime = end_datetime - timedelta(days=max_days)
            self.start_date = start_datetime.strftime("%Y-%m-%d")

        print(
            f"Baixando dados para {self.symbol} de {self.start_date} até {self.end_date} com intervalo de {self.interval}..."
        )
        df = yf.download(
            self.symbol,
            start=self.start_date,
            end=self.end_date,
            interval=self.interval,
        )

        # df = pd.DataFrame(df)

        df.head()

        if df.empty:
            raise ValueError(
                "Não foi possível baixar os dados. Verifique o intervalo de datas e tente novamente."
            )

        # Remover a coluna 'Adj Close' se existir
        if "Adj Close" in df.columns:
            df = df.drop(columns=["Adj Close"])

        # # Resetar o índice para garantir que 'Date' seja uma coluna
        df.reset_index(inplace=True)

        # Renomear a coluna 'Datetime' para 'Date' se necessário
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "Date"}, inplace=True)

        # Verificar se a coluna 'Date' existe
        if "Date" not in df.columns:
            raise ValueError(
                "A coluna 'Date' não foi encontrada no DataFrame após o reset do índice."
            )

        # remover a primeira linha
        # df = df.iloc[1:]
        # Exibir os primeiros registros dos dados
        # print(df.head())

        # Salvar os dados após calcular os indicadores
        data_save = DataSave(df)
        data_save.save_data(self.filepath)  # Passa o filepath como argumento
        print(f"Download concluído e dados salvos em {self.filepath}.")

        # Adicionar indicadores técnicos
        # df = self.add_indicators(df)

        return df

    def add_indicators(self, df):
        calculator = IndicatorCalculator(df)
        return calculator.calculate_indicators()

    def load_data(self):
        # Verificar se o arquivo existe, se sim, carregar os dados do arquivo Parquet
        if os.path.exists(self.filepath):
            df = pd.read_csv(self.filepath)
            print(f"Dados carregados do arquivo {self.filepath}.")
        else:
            print("Arquivo de dados não encontrado. Baixando dados...")
            df = self.download_data()
        return df
