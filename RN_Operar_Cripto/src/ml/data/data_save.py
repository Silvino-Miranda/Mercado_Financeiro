import os
import pandas as pd


class DataSave:
    def __init__(self, data):
        self.data = data

    def save_data(self, filepath, data_dir="data"):
        # Verificar se a pasta de destino existe
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Remover o nível superior do MultiIndex se ele existir
        if isinstance(self.data.columns, pd.MultiIndex):
            # Mantém apenas o nível inferior das colunas, por exemplo, 'Close', 'High', etc.
            self.data.columns = self.data.columns.get_level_values(-1)

        # Certificar que o índice está correto e remover colunas duplicadas
        if not self.data.index.name == "Date":
            self.data.reset_index(drop=True, inplace=True)

        # Remover colunas duplicadas se existirem
        self.data = self.data.loc[:, ~self.data.columns.duplicated()]

        # Salvar o arquivo em formato Parquet
        # self.data.to_parquet(filepath + ".parquet", index=False)
        # print(f"Dados salvos em {filepath}.parquet")

        # Salvar o arquivo em formato CSV
        self.data.to_csv(filepath + ".csv", index=False, sep=";")
        print(f"Dados salvos em {filepath}.csv")
