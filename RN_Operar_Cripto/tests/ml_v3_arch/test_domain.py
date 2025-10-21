"""
Testes para Domain Layer - Entities e Value Objects.

Testa:
- ModelConfig: validações, criação
- BacktestConfig: validações
- Trade: criação, cálculos de PnL
- TradeSignal: validações
- MarketData: validações OHLC
"""
import pytest
from datetime import datetime
from pathlib import Path
import sys

# Adicionar src ao path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from ml_v3_arch.domain.entities import (
    ModelConfig,
    BacktestConfig,
    Trade,
    TradeSignal,
    TradeDirection,
    TradeStatus,
    MarketDirection,
    MarketData
)


# ============================================================================
# TESTES DE ModelConfig
# ============================================================================

class TestModelConfig:
    """Testes para ModelConfig Value Object."""
    
    def test_create_valid_config(self, sample_model_config):
        """Testa criação de config válida."""
        assert sample_model_config.model_type == 'lstm'
        assert sample_model_config.lookback == 60
        assert sample_model_config.lstm_units == 64
        assert sample_model_config.lstm_layers == 2
        assert sample_model_config.dropout == 0.3
        assert sample_model_config.learning_rate == 0.001
        assert sample_model_config.batch_size == 32
        assert sample_model_config.epochs == 10
    
    def test_invalid_lookback(self):
        """Testa validação de lookback inválido."""
        with pytest.raises(ValueError, match="Lookback deve ser > 0"):
            ModelConfig(
                model_type='lstm',
                lookback=0
            )
    
    def test_invalid_dropout_negative(self):
        """Testa validação de dropout negativo."""
        with pytest.raises(ValueError, match="Dropout deve estar entre 0 e 1"):
            ModelConfig(
                model_type='lstm',
                dropout=-0.1
            )
    
    def test_invalid_dropout_above_one(self):
        """Testa validação de dropout >= 1."""
        with pytest.raises(ValueError, match="Dropout deve estar entre 0 e 1"):
            ModelConfig(
                model_type='lstm',
                dropout=1.5
            )
    
    def test_invalid_learning_rate(self):
        """Testa validação de learning_rate inválida."""
        with pytest.raises(ValueError, match="Learning rate deve ser > 0"):
            ModelConfig(
                model_type='lstm',
                learning_rate=0
            )
    
    def test_invalid_batch_size(self):
        """Testa validação de batch_size inválida."""
        with pytest.raises(ValueError, match="Batch size deve ser > 0"):
            ModelConfig(
                model_type='lstm',
                batch_size=-1
            )
    
    def test_config_equality(self):
        """Testa igualdade entre configs."""
        config1 = ModelConfig(model_type='lstm', lookback=60)
        config2 = ModelConfig(model_type='lstm', lookback=60)
        
        assert config1.model_type == config2.model_type
        assert config1.lookback == config2.lookback
    
    def test_different_model_types(self):
        """Testa diferentes tipos de modelos."""
        for model_type in ['lstm', 'gru', 'directional']:
            config = ModelConfig(model_type=model_type)
            assert config.model_type == model_type


# ============================================================================
# TESTES DE BacktestConfig
# ============================================================================

class TestBacktestConfig:
    """Testes para BacktestConfig Value Object."""
    
    def test_create_valid_config(self, sample_backtest_config):
        """Testa criação de config válida."""
        assert sample_backtest_config.initial_capital == 10000.0
        assert sample_backtest_config.fee_bps == 10.0
        assert sample_backtest_config.slippage_bps == 5.0
        assert sample_backtest_config.position_size == 0.95
    
    def test_invalid_initial_capital_negative(self):
        """Testa validação de capital inicial negativo."""
        with pytest.raises(ValueError, match="Capital inicial deve ser > 0"):
            BacktestConfig(initial_capital=-1000.0)
    
    def test_invalid_initial_capital_zero(self):
        """Testa validação de capital inicial zero."""
        with pytest.raises(ValueError, match="Capital inicial deve ser > 0"):
            BacktestConfig(initial_capital=0.0)
    
    def test_invalid_position_size_zero(self):
        """Testa validação de position_size zero."""
        with pytest.raises(ValueError, match="Position size deve estar entre 0 e 1"):
            BacktestConfig(position_size=0.0)
    
    def test_invalid_position_size_above_one(self):
        """Testa validação de position_size > 1."""
        with pytest.raises(ValueError, match="Position size deve estar entre 0 e 1"):
            BacktestConfig(position_size=1.5)
    
    def test_invalid_min_confidence_negative(self):
        """Testa validação de min_confidence negativa."""
        with pytest.raises(ValueError, match="Min confidence deve estar entre 0 e 1"):
            BacktestConfig(min_confidence=-0.1)
    
    def test_invalid_min_confidence_above_one(self):
        """Testa validação de min_confidence > 1."""
        with pytest.raises(ValueError, match="Min confidence deve estar entre 0 e 1"):
            BacktestConfig(min_confidence=1.5)
    
    def test_config_equality(self):
        """Testa igualdade entre configs."""
        config1 = BacktestConfig(initial_capital=10000.0)
        config2 = BacktestConfig(initial_capital=10000.0)
        
        assert config1.initial_capital == config2.initial_capital


# ============================================================================
# TESTES DE Trade
# ============================================================================

class TestTrade:
    """Testes para Trade Entity."""
    
    def test_create_long_trade(self):
        """Testa criação de trade LONG."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.LONG,
            quantity=0.1
        )
        
        assert trade.direction == TradeDirection.LONG
        assert trade.entry_price == 50000.0
        assert trade.status == TradeStatus.ENTRY
        assert not trade.is_closed
    
    def test_create_short_trade(self):
        """Testa criação de trade SHORT."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.SHORT,
            quantity=0.1
        )
        
        assert trade.direction == TradeDirection.SHORT
    
    def test_close_long_trade_profitable(self):
        """Testa fechamento de trade LONG lucrativo."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.LONG,
            quantity=0.1
        )
        
        trade.close(
            exit_date=datetime(2025, 1, 2),
            exit_price=51000.0
        )
        
        assert trade.is_closed
        assert trade.status == TradeStatus.EXIT
        assert trade.gross_return > 0
    
    def test_close_long_trade_loss(self):
        """Testa fechamento de trade LONG com prejuízo."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.LONG,
            quantity=0.1
        )
        
        trade.close(
            exit_date=datetime(2025, 1, 2),
            exit_price=49000.0
        )
        
        assert trade.is_closed
        assert trade.gross_return < 0
    
    def test_close_short_trade_profitable(self):
        """Testa fechamento de trade SHORT lucrativo."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.SHORT,
            quantity=0.1
        )
        
        trade.close(
            exit_date=datetime(2025, 1, 2),
            exit_price=49000.0
        )
        
        assert trade.is_closed
        assert trade.gross_return > 0
    
    def test_profit_loss_calculation(self):
        """Testa cálculo de P&L."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.LONG,
            quantity=0.1
        )
        
        trade.close(
            exit_date=datetime(2025, 1, 2),
            exit_price=51000.0
        )
        
        assert trade.profit_loss is not None
        assert trade.profit_loss > 0
    
    def test_trade_with_fees(self):
        """Testa trade com fees."""
        trade = Trade(
            entry_date=datetime(2025, 1, 1),
            entry_price=50000.0,
            direction=TradeDirection.LONG,
            quantity=0.1,
            fee=10.0
        )
        
        trade.close(
            exit_date=datetime(2025, 1, 2),
            exit_price=51000.0,
            fee=10.0
        )
        
        assert trade.fee == 20.0
        assert trade.net_return < trade.gross_return


# ============================================================================
# TESTES DE TradeSignal
# ============================================================================

class TestTradeSignal:
    """Testes para TradeSignal Entity."""
    
    def test_create_long_signal(self):
        """Testa criação de sinal de LONG."""
        signal = TradeSignal(
            timestamp=datetime(2025, 1, 1),
            direction=TradeDirection.LONG,
            confidence=0.85,
            price=50000.0
        )
        
        assert signal.direction == TradeDirection.LONG
        assert signal.confidence == 0.85
        assert signal.price == 50000.0
    
    def test_create_short_signal(self):
        """Testa criação de sinal de SHORT."""
        signal = TradeSignal(
            timestamp=datetime(2025, 1, 1),
            direction=TradeDirection.SHORT,
            confidence=0.75,
            price=51000.0
        )
        
        assert signal.direction == TradeDirection.SHORT
    
    def test_create_neutral_signal(self):
        """Testa criação de sinal de NEUTRAL."""
        signal = TradeSignal(
            timestamp=datetime(2025, 1, 1),
            direction=TradeDirection.NEUTRAL,
            confidence=0.95,
            price=50500.0
        )
        
        assert signal.direction == TradeDirection.NEUTRAL
    
    def test_invalid_confidence_negative(self):
        """Testa validação de confidence negativa."""
        with pytest.raises(ValueError, match="Confidence deve estar entre 0 e 1"):
            TradeSignal(
                timestamp=datetime(2025, 1, 1),
                direction=TradeDirection.LONG,
                confidence=-0.5,
                price=50000.0
            )
    
    def test_invalid_confidence_above_one(self):
        """Testa validação de confidence > 1."""
        with pytest.raises(ValueError, match="Confidence deve estar entre 0 e 1"):
            TradeSignal(
                timestamp=datetime(2025, 1, 1),
                direction=TradeDirection.LONG,
                confidence=1.5,
                price=50000.0
            )
    
    def test_invalid_price_negative(self):
        """Testa validação de price negativo."""
        with pytest.raises(ValueError, match="Price deve ser positivo"):
            TradeSignal(
                timestamp=datetime(2025, 1, 1),
                direction=TradeDirection.LONG,
                confidence=0.85,
                price=-50000.0
            )
    
    def test_signal_with_predicted_price(self):
        """Testa sinal com preço predito."""
        signal = TradeSignal(
            timestamp=datetime(2025, 1, 1),
            direction=TradeDirection.LONG,
            confidence=0.85,
            price=50000.0,
            predicted_price=51000.0
        )
        
        assert signal.predicted_price == 51000.0


# ============================================================================
# TESTES DE MarketData
# ============================================================================

class TestMarketData:
    """Testes para MarketData Value Object."""
    
    def test_create_valid_market_data(self):
        """Testa criação de market data válido."""
        data = MarketData(
            timestamp=datetime(2025, 1, 1),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=1000.0
        )
        
        assert data.open == 50000.0
        assert data.high == 51000.0
        assert data.low == 49000.0
        assert data.close == 50500.0
    
    def test_invalid_high_below_open(self):
        """Testa validação de high < open."""
        with pytest.raises(ValueError, match="High deve ser >= max"):
            MarketData(
                timestamp=datetime(2025, 1, 1),
                open=51000.0,
                high=50000.0,
                low=49000.0,
                close=50500.0,
                volume=1000.0
            )
    
    def test_invalid_low_above_close(self):
        """Testa validação de low > close."""
        with pytest.raises(ValueError, match="Low deve ser <= min"):
            MarketData(
                timestamp=datetime(2025, 1, 1),
                open=50000.0,
                high=51000.0,
                low=51000.0,
                close=50500.0,
                volume=1000.0
            )
    
    def test_invalid_negative_prices(self):
        """Testa validação de preços negativos."""
        with pytest.raises(ValueError):
            MarketData(
                timestamp=datetime(2025, 1, 1),
                open=-50000.0,
                high=51000.0,
                low=49000.0,
                close=50500.0,
                volume=1000.0
            )


# ============================================================================
# TESTES DE ENUMS
# ============================================================================

class TestEnums:
    """Testes para Enums."""
    
    def test_trade_direction_values(self):
        """Testa valores de TradeDirection."""
        assert TradeDirection.LONG.value == 1
        assert TradeDirection.SHORT.value == -1
        assert TradeDirection.NEUTRAL.value == 0
    
    def test_trade_status_values(self):
        """Testa valores de TradeStatus."""
        assert TradeStatus.ENTRY.value == "Entrada"
        assert TradeStatus.EXIT.value == "Saida"
    
    def test_market_direction_values(self):
        """Testa valores de MarketDirection."""
        assert MarketDirection.BAIXA.value == 0
        assert MarketDirection.LATERAL.value == 1
        assert MarketDirection.ALTA.value == 2
    
    def test_enum_equality(self):
        """Testa igualdade de enums."""
        assert TradeDirection.LONG == TradeDirection.LONG
        assert MarketDirection.ALTA == MarketDirection.ALTA
        assert TradeDirection.LONG != TradeDirection.SHORT
