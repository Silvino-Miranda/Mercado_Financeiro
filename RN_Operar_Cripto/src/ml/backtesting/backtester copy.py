import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import locale


class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.positions = []
        self.capital_history = []

    def run(self, Y_true, Y_pred, scaler, dates, close_prices):
        print("Iniciando o backtest...")

        # Reverter a normalização para os valores reais e armazenar como atributos
        self.Y_true_scaled = scaler.inverse_transform(Y_true.reshape(-1, 1)).flatten()
        self.Y_pred_scaled = scaler.inverse_transform(Y_pred.reshape(-1, 1)).flatten()
        self.dates = pd.to_datetime(dates)

        capital = self.initial_capital
        position = 0  # Quantidade de BTC em posse
        self.capital_history = [capital]

        for i in range(len(self.Y_pred_scaled) - 1):
            date = self.dates[i]
            pred_next = self.Y_pred_scaled[i + 1]
            true_value = self.Y_true_scaled[i]
            close_price = close_prices[i]

            operation = None

            if pred_next > self.Y_pred_scaled[i] and position == 0:
                # Comprar BTC
                price = true_value
                position = capital / price
                capital = 0
                operation = "Compra"
                self.positions.append(
                    [
                        date,
                        pred_next,
                        close_price,
                        operation,
                        capital + position * true_value,
                    ]
                )
            elif pred_next < self.Y_pred_scaled[i] and position > 0:
                # Vender BTC
                price = true_value
                capital = position * price
                position = 0
                operation = "Venda"
                self.positions.append(
                    [date, pred_next, close_price, operation, capital]
                )
            # Calcular o capital total atual
            total_capital = capital + position * true_value
            self.capital_history.append(total_capital)

        print("Backtest concluído.")
        return self.capital_history

    def plot_capital_evolution(self):
        plt.figure(figsize=(16, 8))
        plt.plot(self.capital_history, label="Capital")
        plt.title("Evolução do Capital")
        plt.xlabel("Período")
        plt.ylabel("Capital em USD")
        plt.legend()
        plt.show()

    def save_capital_history(self, filepath):
        # Configurar o locale para português do Brasil
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

        # Criar um DataFrame com os dados de capital e operações
        df = pd.DataFrame(
            self.positions,
            columns=["Data", "Previsao do Modelo", "Close", "Operacao", "Capital"],
        )

        # Formatar os valores numéricos no formato brasileiro
        df["Previsao do Modelo"] = df["Previsao do Modelo"].apply(
            lambda x: locale.format_string('%.2f', x, grouping=True)
        )
        df["Close"] = df["Close"].apply(
            lambda x: locale.format_string('%.2f', x, grouping=True)
        )
        df["Capital"] = df["Capital"].apply(
            lambda x: locale.format_string('%.2f', x, grouping=True)
        )

        # Salvar o arquivo CSV com os valores formatados
        df.to_csv(filepath, index=False, sep=";")
        print(f"Histórico de capital e operações salvo em {filepath}.")

    def plot_predictions_vs_actuals(self):
        plt.figure(figsize=(16, 8))
        plt.plot(self.dates, self.Y_true_scaled, label='Valor Real (Close)', color='blue')
        plt.plot(self.dates, self.Y_pred_scaled, label='Previsão do Modelo', color='red')
        plt.xlabel('Data')
        plt.ylabel('Preço')
        plt.title('Previsão do Modelo vs. Valor Real')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
