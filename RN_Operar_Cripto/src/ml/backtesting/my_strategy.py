import backtrader as bt
from datetime import datetime


class MyStrategy(bt.Strategy):
    params = dict(
        stake_percentage=0.95,  # 95% do capital total
        profit_target=0.03,  # 3% de lucro para vender (Take Profit)
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
        # Calcular tamanho da posição
        cash = self.broker.getcash()
        size = (cash * self.params.stake_percentage) / self.dataclose[0]
        
        if size < 0.01 and not self.position:
            return  # Não operar se não há dinheiro suficiente

        # Valores atuais
        pred_current = self.prediction[0]
        actual_current = self.actual[0]
        
        # Calcular variação percentual entre previsão e preço atual
        # Se previsão > preço atual = sinal de ALTA (modelo prevê subida)
        # Se previsão < preço atual = sinal de BAIXA (modelo prevê queda)
        prediction_deviation = (pred_current - actual_current) / actual_current
        
        if not self.position:
            # COMPRA quando modelo prevê ALTA (previsão > preço atual)
            # Threshold mínimo de 0.5% de diferença para evitar ruído
            if prediction_deviation > 0.005:  # Previsão 0.5% maior que preço atual
                self.order = self.buy(size=size)
                # Nota: buy_price será definido no notify_order quando a ordem for executada
        else:
            # Só processa lógica de venda se já temos buy_price definido
            if self.buy_price is None:
                return
                
            self.periods_in_position += 1
            
            # Calcular variação de preço desde a compra (%)
            price_change = (actual_current - self.buy_price) / self.buy_price
            
            # VENDA apenas se:
            # 1. Atingiu o alvo de lucro (3%)
            # 2. Atingiu o stop loss (1.5%)
            # 3. Já está há tempo suficiente na posição E modelo prevê queda
            should_sell = False
            
            if price_change >= self.params.profit_target:
                should_sell = True  # Take profit (3%)
            elif price_change <= -self.params.stop_loss:
                should_sell = True  # Stop loss
            elif (self.periods_in_position >= self.params.hold_periods and 
                  prediction_deviation < -0.005):  # Previsão indica queda > 0.5%
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

            # Se é compra, salvar o preço de entrada
            if order.isbuy():
                self.buy_price = order.executed.price
                self.periods_in_position = 0
                status = "Entrada"
            else:
                # Se é venda, resetar
                self.buy_price = None
                self.periods_in_position = 0
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
