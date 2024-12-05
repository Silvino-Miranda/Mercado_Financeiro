# frameworks_drivers/order.py
import ccxt

class Order:
    def __init__(self, exchange, symbol, amount_brl):
        self.exchange = exchange
        self.symbol = symbol
        self.amount_brl = amount_brl
        self.order_id = None
        self.price = None
        self.amount_crypto = None
        self.cost = None
        self.average = None

    def execute(self):
        try:
            balance = self.exchange.fetch_balance()
            brl_balance = balance["BRL"]["free"]

            if self.amount_brl > brl_balance:
                print(f"Saldo insuficiente. Saldo disponível: {brl_balance} BRL")
                return False

            ticker = self.exchange.fetch_ticker(self.symbol)
            self.price = ticker["last"]

            self.amount_crypto = self.amount_brl / self.price

            order = self.exchange.create_market_buy_order(self.symbol, self.amount_crypto)

            self.order_id = order["id"]
            self.cost = order["cost"]
            self.average = order["average"]

            print(f"Ordem de compra executada: {order.get('symbol')}")
            return True

        except ccxt.BaseError as e:
            print(f"Erro ao tentar comprar {self.symbol}: {str(e)}")
            return False