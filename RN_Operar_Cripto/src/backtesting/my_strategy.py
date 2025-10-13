import backtrader as bt
from datetime import datetime


class MyStrategy(bt.Strategy):
    params = dict(
        stake_percentage=0.95,  # 95% do capital total
        profit_target=0.02,  # 2% de lucro para vender
        stop_loss=0.015,  # 1.5% de perda para stop loss
        hold_periods=48  # Manter por pelo menos 48 períodos (24 horas em velas de 30min)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.prediction = self.datas[0].prediction
        self.actual = self.datas[0].actual
        self.order = None
        self.trade_history = []
        self.buy_price = None
        self.periods_in_position = 0

    def next(self):
        # Debug: imprimir apenas nos primeiros 5 períodos
        if len(self) <= 5:
            print(f"Período {len(self)}: Cash=${self.broker.getcash():.2f}, "
                  f"Value=${self.broker.getvalue():.2f}, "
                  f"Close={self.dataclose[0]:.2f}, "
                  f"Position={self.position.size if self.position else 0}")
        
        # Calcular tamanho da posição
        cash = self.broker.getcash()
        size = int((cash * self.params.stake_percentage) / self.dataclose[0])
        
        if len(self) <= 5:
            print(f"  -> Size calculado: {size}")
        
        if size < 1 and not self.position:
            if len(self) <= 5:
                print(f"  -> Pulando: size < 1")
            return  # Não operar se não há dinheiro suficiente

        # Valores atuais
        pred_current = self.prediction[0]
        actual_current = self.actual[0]
        
        if not self.position:
            # COMPRA SEMPRE que não tem posição e tem dinheiro
            # (estratégia buy and hold com saídas táticas)
            if len(self) <= 5:
                print(f"  -> COMPRANDO {size} unidades a ${self.dataclose[0]:.2f}")
            self.buy_price = actual_current
            self.periods_in_position = 0
            self.order = self.buy(size=size)
        else:
            self.periods_in_position += 1
            
            # Calcular variação de preço desde a compra
            price_change = (actual_current - self.buy_price) / self.buy_price
            
            # VENDA apenas se:
            # 1. Atingiu o alvo de lucro
            # 2. Atingiu o stop loss
            # 3. Já está há tempo suficiente na posição E previsão indica queda
            should_sell = False
            
            if price_change >= self.params.profit_target:
                should_sell = True  # Take profit
            elif price_change <= -self.params.stop_loss:
                should_sell = True  # Stop loss
            elif (self.periods_in_position >= self.params.hold_periods and 
                  pred_current < actual_current):
                should_sell = True  # Holding time + bearish signal
            
            if should_sell:
                self.order = self.sell(size=self.position.size)
                self.buy_price = None
                self.periods_in_position = 0

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
