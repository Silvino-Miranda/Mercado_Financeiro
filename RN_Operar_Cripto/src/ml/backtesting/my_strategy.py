import backtrader as bt
from datetime import datetime
from typing import Optional
from .strategy_config import Strategy, StrategyParameters


class MyStrategy(bt.Strategy):
    """
    Estratégia de Trading LSTM com parâmetros configuráveis
    
    Agora os parâmetros são carregados de strategy_config.py / strategies.json
    permitindo testar múltiplas estratégias sem alterar o código.
    """
    
    params = dict(
        # Parâmetros padrão (podem ser sobrescritos pelo strategy_config)
        stake_percentage=0.95,  # 95% do capital total
        profit_target=0.02,  # 2% de lucro para vender (Take Profit)
        stop_loss=0.015,  # 1.5% de perda para stop loss
        prediction_threshold=0.005,  # 0.5% threshold para sinais
        hold_periods=48,  # Manter por pelo menos 48 períodos (24 horas em velas de 30min)
        strategy_name="Padrão"  # Nome da estratégia (para identificação)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.prediction = self.datas[0].prediction
        self.actual = self.datas[0].actual
        self.order = None
        self.trade_history = []
        self.buy_price = None
        self.periods_in_position = 0
        
    @classmethod
    def from_strategy_config(cls, strategy: Strategy):
        """
        Cria uma instância da MyStrategy a partir de um objeto Strategy
        
        Args:
            strategy: Objeto Strategy do strategy_config
            
        Returns:
            Classe MyStrategy configurada com os parâmetros da estratégia
        """
        # Cria uma nova classe com os parâmetros da estratégia
        params = dict(
            stake_percentage=strategy.parameters.stake_percentage,
            profit_target=strategy.parameters.profit_target,
            stop_loss=strategy.parameters.stop_loss,
            prediction_threshold=strategy.parameters.prediction_threshold,
            hold_periods=strategy.parameters.hold_periods,
            strategy_name=strategy.name
        )
        
        # Retorna a classe (não a instância) para o Backtrader usar
        return type(f'MyStrategy_{strategy.id}', (cls,), {'params': params})

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
            # Threshold configurável para evitar ruído
            if prediction_deviation > self.params.prediction_threshold:
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
                  prediction_deviation < -self.params.prediction_threshold):
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
