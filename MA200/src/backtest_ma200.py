from data.data_loader import DataLoader


class BacktestMA200:
    def __init__(
        self,
        ticker,
        start="2010-01-01",
        end="2023-10-01",
        initial_balance=1000.0,
        file_path="data/data.csv",
    ):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.btc_held = 0.0
        self.position = False
        self.data = None
        self.final_balance = 0.0
        self.file_path = file_path
        self.data_handler = DataLoader(symbol=ticker, start_date=start, interval="1d")

    def load_data(self):
        self.data = self.data_handler.load_data()

    def run_backtest(self):
        if self.data is None:
            raise ValueError(
                "Os dados não foram carregados. Execute o método load_data() primeiro."
            )

        # Implementação do backtest usando o MA200
        for _, row in self.data.iterrows():
            close_price = row["Close"]  # Atualizado para "Close"
            ma200 = row["SMA_200"]  # Atualizado para "SMA_200"
            double_ma200 = ma200 * 2

            # Regra de compra: o preço está abaixo da MA200
            if not self.position and close_price < ma200:
                self.btc_held = self.balance / close_price
                self.balance = 0.0
                self.position = True

            # Regra de venda: o preço atinge ou ultrapassa o dobro da MA200
            elif self.position and close_price >= double_ma200:
                self.balance = self.btc_held * close_price
                self.btc_held = 0.0
                self.position = False

        # Saldo final: se ainda tiver posição aberta, vende no último preço
        if self.position:
            final_close = self.data["Close"].iloc[-1]
            self.balance = self.btc_held * final_close

        self.final_balance = self.balance

    def get_results(self):
        return {
            "ticker": self.ticker,
            "initial_balance": self.initial_balance,
            "final_balance": self.final_balance,
            "profit_percent": (
                (self.final_balance - self.initial_balance) / self.initial_balance
            )
            * 100,
        }
