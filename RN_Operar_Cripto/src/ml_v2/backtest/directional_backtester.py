"""
Backtester para classificação direcional.
Gera CSV de histórico compatível com o dashboard da v1.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from datetime import datetime


class DirectionalBacktester:
    """
    Backtester para estratégias de classificação direcional.
    Gera histórico de operações compatível com o dashboard.
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
        min_confidence: float = 0.6,
        position_size: float = 0.95
    ):
        """
        Args:
            initial_capital: Capital inicial em USD
            fee_bps: Taxa de transação em basis points
            slippage_bps: Slippage em basis points
            min_confidence: Confiança mínima para entrar em posição
            position_size: Fração do capital a usar por operação
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.min_confidence = min_confidence
        self.position_size = position_size
        
        # Estado da posição
        self.position = 0.0  # 0 = sem posição, > 0 = long, < 0 = short
        self.entry_price = 0.0
        self.entry_date = None
        
        # Histórico de operações (formato compatível com dashboard)
        self.history = []
        
        print(f"💰 Backtester inicializado:")
        print(f"   Capital inicial: ${self.initial_capital:,.2f}")
        print(f"   Taxa: {self.fee_bps} bps")
        print(f"   Slippage: {self.slippage_bps} bps")
        print(f"   Confiança mínima: {self.min_confidence:.1%}")
        print(f"   Tamanho posição: {self.position_size:.1%}")
    
    def _calculate_fees(self, amount: float) -> float:
        """Calcula taxas de transação."""
        return amount * (self.fee_bps / 10000)
    
    def _apply_slippage(self, price: float, direction: str) -> float:
        """Aplica slippage ao preço."""
        slippage_factor = self.slippage_bps / 10000
        
        if direction == "buy":
            return price * (1 + slippage_factor)
        else:  # sell
            return price * (1 - slippage_factor)
    
    def _get_prediction_confidence(self, probabilities: np.ndarray) -> Tuple[str, float]:
        """
        Extrai predição e confiança das probabilidades.
        
        Args:
            probabilities: Array [prob_baixa, prob_lateral, prob_alta]
            
        Returns:
            Tuple (direção, confiança)
        """
        prediction = np.argmax(probabilities)
        confidence = probabilities[prediction]
        
        # Mapear para direções
        directions = {0: "BAIXA", 1: "LATERAL", 2: "ALTA"}
        
        return directions[prediction], confidence
    
    def _should_enter_position(self, direction: str, confidence: float) -> bool:
        """Decide se deve entrar em posição."""
        # Só entrar se confiança >= mínima e não for LATERAL
        return confidence >= self.min_confidence and direction != "LATERAL"
    
    def _should_exit_position(self, direction: str, confidence: float) -> bool:
        """Decide se deve sair da posição atual."""
        # Sair se:
        # 1. Direção mudou (long->BAIXA ou short->ALTA)
        # 2. Confiança baixa
        # 3. Direção virou LATERAL
        
        if self.position == 0:
            return False
        
        if direction == "LATERAL":
            return True
        
        if confidence < self.min_confidence:
            return True
        
        # Verificar mudança de direção
        if self.position > 0 and direction == "BAIXA":  # Long + previsão BAIXA
            return True
        
        if self.position < 0 and direction == "ALTA":  # Short + previsão ALTA
            return True
        
        return False
    
    def _execute_trade(
        self,
        date: str,
        price: float,
        prediction: float,
        direction: str,
        operation: str,
        status: str
    ):
        """
        Executa uma operação e registra no histórico.
        
        Args:
            date: Data da operação
            price: Preço atual
            prediction: Preço previsto
            direction: Direção prevista
            operation: "Compra" ou "Venda"
            status: "Entrada" ou "Saida"
        """
        # Aplicar slippage
        execution_price = self._apply_slippage(
            price, 
            "buy" if operation == "Compra" else "sell"
        )
        
        if status == "Entrada":
            # Calcular quantidade baseada no capital disponível
            capital_to_use = self.current_capital * self.position_size
            
            if operation == "Compra":
                # Long position
                quantity = capital_to_use / execution_price
                fees = self._calculate_fees(capital_to_use)
                self.position = quantity
                self.current_capital -= fees
            else:
                # Short position (vendemos primeiro)
                quantity = capital_to_use / execution_price
                fees = self._calculate_fees(capital_to_use)
                self.position = -quantity
                self.current_capital += capital_to_use - fees
            
            self.entry_price = execution_price
            self.entry_date = date
            
        else:  # Saída
            if operation == "Venda" and self.position > 0:
                # Fechar long
                proceeds = abs(self.position) * execution_price
                fees = self._calculate_fees(proceeds)
                self.current_capital += proceeds - fees
                quantity = -abs(self.position)
                
            elif operation == "Compra" and self.position < 0:
                # Fechar short
                cost = abs(self.position) * execution_price
                fees = self._calculate_fees(cost)
                # Para short, já tínhamos recebido o dinheiro na entrada
                # Agora gastamos para recomprar
                self.current_capital -= cost + fees
                quantity = abs(self.position)
            
            self.position = 0.0
            self.entry_price = 0.0
            self.entry_date = None
        
        # Registrar operação no histórico (formato compatível com dashboard)
        self.history.append({
            'Data': date,
            'Operacao': operation,
            'Status': status,
            'Previsao': f"{prediction:.2f}",
            'Valor Atual': f"{price:.2f}",
            'Preco': f"{execution_price:.2f}",
            'Quantidade': f"{quantity:.4f}",
            'Custo': "0.00",  # Compatibilidade com formato original
            'Capital': f"{self.current_capital:.2f}"
        })
    
    def run_backtest(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        probabilities: np.ndarray
    ) -> pd.DataFrame:
        """
        Executa o backtest.
        
        Args:
            df: DataFrame com colunas ['Date', 'Close', ...]
            predictions: Array de predições (0=BAIXA, 1=LATERAL, 2=ALTA)
            probabilities: Array de probabilidades [n_samples, 3]
            
        Returns:
            DataFrame com histórico de operações
        """
        print(f"\n🔥 Iniciando backtest:")
        print(f"   Período: {df['Date'].iloc[0]} a {df['Date'].iloc[-1]}")
        print(f"   Samples: {len(df):,}")
        
        for i in range(len(df)):
            date = df['Date'].iloc[i].strftime('%Y-%m-%d')
            price = df['Close'].iloc[i]
            
            # Obter predição e confiança
            direction, confidence = self._get_prediction_confidence(probabilities[i])
            predicted_price = price * (1.01 if direction == "ALTA" else 0.99 if direction == "BAIXA" else 1.0)
            
            # Decidir ação
            if self.position == 0:
                # Sem posição - verificar entrada
                if self._should_enter_position(direction, confidence):
                    if direction == "ALTA":
                        self._execute_trade(
                            date, price, predicted_price, direction,
                            "Compra", "Entrada"
                        )
                    elif direction == "BAIXA":
                        self._execute_trade(
                            date, price, predicted_price, direction,
                            "Venda", "Entrada"
                        )
            else:
                # Com posição - verificar saída
                if self._should_exit_position(direction, confidence):
                    if self.position > 0:
                        # Fechar long
                        self._execute_trade(
                            date, price, predicted_price, direction,
                            "Venda", "Saida"
                        )
                    else:
                        # Fechar short
                        self._execute_trade(
                            date, price, predicted_price, direction,
                            "Compra", "Saida"
                        )
        
        # Fechar posição aberta no final
        if self.position != 0:
            final_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')
            final_price = df['Close'].iloc[-1]
            
            if self.position > 0:
                self._execute_trade(
                    final_date, final_price, final_price, "LATERAL",
                    "Venda", "Saida"
                )
            else:
                self._execute_trade(
                    final_date, final_price, final_price, "LATERAL",
                    "Compra", "Saida"
                )
        
        # Criar DataFrame do histórico
        history_df = pd.DataFrame(self.history)
        
        # Calcular métricas finais
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        num_trades = len(history_df) // 2  # Entrada + Saída = 1 trade
        
        print(f"\n📊 Resultado do Backtest:")
        print(f"   Capital inicial: ${self.initial_capital:,.2f}")
        print(f"   Capital final: ${self.current_capital:,.2f}")
        print(f"   Retorno total: {total_return:.2%}")
        print(f"   Número de trades: {num_trades}")
        print(f"   Operações registradas: {len(history_df)}")
        
        return history_df
    
    def save_history(self, df: pd.DataFrame, filename: str):
        """Salva histórico em CSV compatível com dashboard."""
        # Garantir que o diretório existe
        from pathlib import Path
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar com separador ; (compatível com dashboard)
        df.to_csv(filename, sep=';', index=False)
        print(f"✅ Histórico salvo: {filename}")


if __name__ == "__main__":
    # Teste básico
    import pandas as pd
    import numpy as np
    
    # Dados sintéticos
    np.random.seed(42)
    n = 100
    
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=n, freq='D'),
        'Close': np.cumsum(np.random.randn(n) * 100) + 50000
    })
    
    # Predições sintéticas
    predictions = np.random.randint(0, 3, n)
    probabilities = np.random.dirichlet(np.ones(3), n)
    
    # Teste
    backtester = DirectionalBacktester(initial_capital=100000)
    history = backtester.run_backtest(df, predictions, probabilities)
    
    print("\n✅ Teste do backtester concluído!")
    print(f"Histórico gerado: {len(history)} operações")
    print(history.head())