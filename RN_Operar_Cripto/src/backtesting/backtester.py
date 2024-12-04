import matplotlib.pyplot as plt
import backtrader as bt
import pandas as pd
import locale

from my_strategy import MyStrategy


class CustomPandasData(bt.feeds.PandasData):
    # Adicione as novas linhas para 'prediction' e 'actual'
    lines = (
        "prediction",
        "actual",
    )
    # Mapeie as colunas do DataFrame para as linhas do Backtrader
    params = (
        ("prediction", -1),
        ("actual", -1),
    )


class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.cerebro = bt.Cerebro()  # Inicializa o Backtrader
        self.cerebro.broker.set_cash(initial_capital)  # Define capital inicial
        self.strategies = []
        self.trade_history = []
        self.dates = None
        self.Y_true_scaled = None
        self.Y_pred_scaled = None

    def add_data(self, dataframe):
        # Certifique-se de que o DataFrame contém as colunas necessárias
        required_columns = [
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "prediction",
            "actual",
        ]
        for col in required_columns:
            if col not in dataframe.columns:
                raise ValueError(f"A coluna '{col}' está faltando no DataFrame.")

        # Converter a coluna 'datetime' para o índice
        dataframe = dataframe.set_index("datetime")

        # Armazenar os dados para o gráfico
        self.dates = dataframe.index
        self.Y_true_scaled = dataframe["actual"]
        self.Y_pred_scaled = dataframe["prediction"]

        # Adicionar os dados ao Backtrader
        data = CustomPandasData(dataname=dataframe)
        self.cerebro.adddata(data)

    def run(self):
        # Executa o backtest
        self.cerebro.addstrategy(MyStrategy)
        strategies = self.cerebro.run()
        self.strategy = strategies[0]  # Captura a instância da estratégia
        print("Capital final: %.2f" % self.cerebro.broker.getvalue())
        # Obter o histórico de trades da estratégia
        self.trade_history = self.strategy.trade_history

    def plot(self):
        # Gera gráfico com o desempenho
        self.cerebro.plot()

    def save_capital_history(self, filepath):
        # Criar um DataFrame com o histórico de trades
        df = pd.DataFrame(self.trade_history)
        # Formatar as colunas numéricas
        df["Previsao"] = df["Previsao"].apply(
            lambda x: locale.format_string("%.2f", x, grouping=True)
        )
        df["Valor Atual"] = df["Valor Atual"].apply(
            lambda x: locale.format_string("%.2f", x, grouping=True)
        )
        df["Preco"] = df["Preco"].apply(
            lambda x: locale.format_string("%.2f", x, grouping=True)
        )
        df["Custo"] = df["Custo"].apply(
            lambda x: locale.format_string("%.2f", x, grouping=True)
        )
        df["Quantidade"] = df["Quantidade"].round(4)
        df["Capital"] = df["Capital"].apply(
            lambda x: locale.format_string("%.2f", x, grouping=True)
        )
        # Salvar em CSV
        df.to_csv(filepath, index=False, sep=";")
        print(f"Histórico de capital e operações salvo em {filepath}.")

    def plot_predictions_vs_actuals(self):
        plt.figure(figsize=(16, 8))
        plt.plot(
            self.dates, self.Y_true_scaled, label="Valor Real (Close)", color="blue"
        )
        plt.plot(
            self.dates, self.Y_pred_scaled, label="Previsão do Modelo", color="red"
        )
        plt.xlabel("Data")
        plt.ylabel("Preço")
        plt.title("Previsão do Modelo vs. Valor Real")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
