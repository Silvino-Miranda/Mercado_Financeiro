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
            # Obtém o saldo disponível em BRL
            balance = self.exchange.fetch_balance()
            brl_balance = balance["BRL"]["free"]

            # Verifica se há saldo suficiente
            if self.amount_brl > brl_balance:
                print(f"Saldo insuficiente. Saldo disponível: {brl_balance} BRL")
                return False

            # Obtém o preço atual de mercado
            ticker = self.exchange.fetch_ticker(self.symbol)
            self.price = ticker["last"]

            # Calcula a quantidade de cripto a ser comprada
            self.amount_crypto = self.amount_brl / self.price

            # Coloca uma ordem de mercado de compra
            order = self.exchange.create_market_buy_order(
                self.symbol, self.amount_crypto
            )

            # Preenche os detalhes da ordem
            self.order_id = order["id"]
            self.cost = order["cost"]
            self.average = order["average"]

            print(f"Ordem de compra executada: {order.get('symbol')}")
            return True

        except ccxt.BaseError as e:
            print(f"Erro ao tentar comprar {self.symbol}: {str(e)}")
            return False
