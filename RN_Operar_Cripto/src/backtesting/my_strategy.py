import backtrader as bt
from datetime import datetime


class MyStrategy(bt.Strategy):
    params = dict(stake_percentage=0.1)  # 10% do capital total

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.prediction = self.datas[0].prediction
        self.actual = self.datas[0].actual
        self.order = None
        self.trade_history = []

    def next(self):
        if len(self) < 2:
            return  # Aguarda ter dados suficientes

        size = (self.broker.getvalue() * self.params.stake_percentage) / self.dataclose[
            0
        ]
        size = int(size)  # Converte para inteiro

        pred_prev = self.prediction[-1]  # Previsão do dia anterior
        actual_prev = self.actual[-1]  # Valor real do dia anterior

        if not self.position:
            if pred_prev > actual_prev:
                self.order = self.buy(size=size)
        else:
            if pred_prev < actual_prev:
                self.order = self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            operation = "Compra" if order.isbuy() else "Venda"
            pred_value = self.prediction[0]
            actual_value = self.actual[0]

            # Determinar se é entrada ou saída
            status = "Entrada"
            if self.position.size != 0:
                status = "Saida"

            trade_data = {
                "Data": self.data.datetime.date(0).strftime("%Y-%m-%d"),
                "Operacao": operation,
                "Status": status,
                "Previsao": pred_value,
                "Valor Atual": actual_value,
                "Preco": order.executed.price,
                "Quantidade": order.executed.size,
                "Custo": order.executed.comm,
                "Capital": self.broker.getvalue(),
            }
            self.trade_history.append(trade_data)
