"""
Testes para Adapters - Compatibilidade v2 → v3.

Valida que:
1. Interface v2 é mantida (métodos, assinaturas)
2. Implementação v3 funciona corretamente
3. Comportamento idêntico ao v2 original
"""
import pytest
import numpy as np
import pandas as pd

from src.ml_v3_arch.adapters import (
    DataPreprocessorAdapter,
    ModelBuilderAdapter,
    BacktestAdapter
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_df():
    """DataFrame de exemplo para testes."""
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='30min')
    return pd.DataFrame({
        'Date': dates,
        'Open': np.random.randn(200).cumsum() + 100,
        'High': np.random.randn(200).cumsum() + 101,
        'Low': np.random.randn(200).cumsum() + 99,
        'Close': np.random.randn(200).cumsum() + 100,
        'Volume': np.random.randint(1000, 10000, 200)
    })


@pytest.fixture
def feature_cols():
    """Colunas de features padrão."""
    return ['Open', 'High', 'Low', 'Volume']


# ============================================================================
# TESTES: DataPreprocessorAdapter
# ============================================================================

class TestDataPreprocessorAdapter:
    """Testes para DataPreprocessorAdapter."""
    
    def test_initialization(self, feature_cols):
        """Testa inicialização mantém interface v2."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        assert preprocessor.feature_cols == feature_cols
        assert preprocessor.target_col == 'Close'
        assert preprocessor.lookback == 60
        assert not preprocessor._fitted
    
    def test_fit_updates_fitted_flag(self, sample_df, feature_cols):
        """Testa que fit() marca como fitted."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        preprocessor.fit(sample_df)
        
        assert preprocessor._fitted
    
    def test_transform_requires_fit(self, sample_df, feature_cols):
        """Testa que transform() sem fit() levanta erro."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        with pytest.raises(RuntimeError, match="não foi fitted"):
            preprocessor.transform(sample_df)
    
    def test_fit_transform_works(self, sample_df, feature_cols):
        """Testa fit_transform() em uma chamada."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        X, y = preprocessor.fit_transform(sample_df)
        
        assert preprocessor._fitted
        assert X.shape[0] == len(sample_df) - 60  # lookback
        assert X.shape[1] == 60  # timesteps
        assert X.shape[2] == len(feature_cols)  # features
        assert y.shape[0] == X.shape[0]
    
    def test_transform_returns_correct_shapes(self, sample_df, feature_cols):
        """Testa que transform() retorna shapes corretos."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        preprocessor.fit(sample_df.iloc[:150])
        X, y = preprocessor.transform(sample_df.iloc[150:])
        
        expected_samples = len(sample_df.iloc[150:]) - 60
        assert X.shape == (expected_samples, 60, len(feature_cols))
        assert y.shape == (expected_samples,)
    
    def test_inverse_target_works(self, sample_df, feature_cols):
        """Testa inverse_target() inverte normalização."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        preprocessor.fit(sample_df)
        X, y_scaled = preprocessor.transform(sample_df)
        
        y_original = preprocessor.inverse_target(y_scaled)
        
        # Verificar que está na escala original (aproximado)
        expected_y = sample_df['Close'].values[60:]
        np.testing.assert_allclose(y_original, expected_y, rtol=1e-5)
    
    def test_validates_missing_columns(self, feature_cols):
        """Testa validação de colunas faltando."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        df_invalid = pd.DataFrame({
            'Open': [1, 2, 3],
            'Close': [1, 2, 3]
            # Faltam High, Low, Volume
        })
        
        with pytest.raises(ValueError, match="Colunas de features faltando"):
            preprocessor.fit(df_invalid)
    
    def test_validates_dataframe_too_small(self, feature_cols):
        """Testa validação de DataFrame muito pequeno."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        # Apenas 50 samples (< lookback + 10)
        df_small = pd.DataFrame({
            'Open': range(50),
            'High': range(50),
            'Low': range(50),
            'Close': range(50),
            'Volume': range(50)
        })
        
        with pytest.raises(ValueError, match="DataFrame muito pequeno"):
            preprocessor.fit(df_small)
    
    def test_get_config_returns_dict(self, sample_df, feature_cols):
        """Testa get_config() retorna configuração."""
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        preprocessor.fit(sample_df)
        config = preprocessor.get_config()
        
        assert config['feature_cols'] == feature_cols
        assert config['target_col'] == 'Close'
        assert config['lookback'] == 60
        assert config['fitted'] is True
        assert config['n_features'] == len(feature_cols)


# ============================================================================
# TESTES: ModelBuilderAdapter
# ============================================================================

class TestModelBuilderAdapter:
    """Testes para ModelBuilderAdapter."""
    
    def test_build_lstm_returns_model(self):
        """Testa build_lstm() retorna modelo Keras."""
        model = ModelBuilderAdapter.build_lstm(
            input_shape=(60, 10),
            learning_rate=1e-3
        )
        
        assert model is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'predict')
        assert model.count_params() > 0
    
    def test_build_directional_lstm_returns_model(self):
        """Testa build_directional_lstm() retorna modelo classificação."""
        model = ModelBuilderAdapter.build_directional_lstm(
            input_shape=(60, 10),
            n_classes=3,
            lstm_units=64,
            dropout=0.3,
            learning_rate=1e-3
        )
        
        assert model is not None
        assert model.output_shape[-1] == 3  # 3 classes
    
    def test_build_improved_directional_lstm_returns_model(self):
        """Testa build_improved_directional_lstm() com Focal Loss."""
        model = ModelBuilderAdapter.build_improved_directional_lstm(
            input_shape=(60, 10),
            lstm_units=128,
            lstm_layers=3,
            dropout=0.4,
            use_focal_loss=True
        )
        
        assert model is not None
        assert model.output_shape[-1] == 3  # 3 classes
    
    def test_get_callbacks_returns_list(self):
        """Testa get_callbacks() retorna lista de callbacks."""
        callbacks = ModelBuilderAdapter.get_callbacks(
            patience_early=10,
            patience_lr=5
        )
        
        assert isinstance(callbacks, list)
        assert len(callbacks) >= 2  # EarlyStopping + ReduceLR
    
    def test_get_directional_callbacks_returns_list(self):
        """Testa get_directional_callbacks() para classificação."""
        callbacks = ModelBuilderAdapter.get_directional_callbacks(
            patience_early=15,
            patience_lr=7,
            monitor='val_accuracy'
        )
        
        assert isinstance(callbacks, list)
        assert len(callbacks) >= 2
    
    def test_calculate_class_weights_balanced(self):
        """Testa calculate_class_weights() retorna pesos balanceados."""
        # Dados desbalanceados: 70% classe 0, 20% classe 1, 10% classe 2
        y_train = [0] * 70 + [1] * 20 + [2] * 10
        
        weights = ModelBuilderAdapter.calculate_class_weights(y_train)
        
        assert len(weights) == 3
        assert 0 in weights
        assert 1 in weights
        assert 2 in weights
        
        # Classe minoritária deve ter peso maior
        assert weights[2] > weights[0]  # classe 2 (10%) > classe 0 (70%)


# ============================================================================
# TESTES: BacktestAdapter
# ============================================================================

class TestBacktestAdapter:
    """Testes para BacktestAdapter."""
    
    def test_backtest_regression_returns_equity_and_metrics(self, sample_df):
        """Testa backtest_regression() retorna equity curve e métricas."""
        close = sample_df['Close'].values
        preds_usd = close + np.random.randn(len(close)) * 2
        
        equity_curve, metrics = BacktestAdapter.backtest_regression(
            df=sample_df,
            preds_usd=preds_usd,
            fee_bps=10.0,
            slippage_bps=5.0,
            initial_capital=10000.0
        )
        
        assert isinstance(equity_curve, pd.DataFrame)
        assert isinstance(metrics, dict)
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert 'win_rate' in metrics
    
    def test_backtest_classifier_returns_equity_and_metrics(self, sample_df):
        """Testa backtest_classifier() com predições de classes."""
        n_samples = len(sample_df) - 60  # lookback
        predictions = np.random.randint(0, 3, n_samples)
        probabilities = np.random.dirichlet(np.ones(3), n_samples)
        
        df_aligned = sample_df.iloc[60:].reset_index(drop=True)
        
        equity_curve, metrics = BacktestAdapter.backtest_classifier(
            df=df_aligned,
            predictions=predictions,
            probabilities=probabilities,
            fee_bps=10.0,
            slippage_bps=5.0,
            min_confidence=0.6,
            initial_capital=100000.0
        )
        
        assert isinstance(equity_curve, pd.DataFrame)
        assert isinstance(metrics, dict)
        assert 'total_trades' in metrics
        assert 'win_rate' in metrics
    
    def test_print_backtest_report_runs(self, capsys):
        """Testa print_backtest_report() imprime corretamente."""
        metrics = {
            'total_trades': 50,
            'total_return': 0.15,
            'sharpe_ratio': 1.5,
            'max_drawdown': 0.10,
            'win_rate': 0.60,
            'avg_win': 100.0,
            'avg_loss': 50.0,
            'profit_factor': 2.0,
            'final_capital': 11500.0
        }
        
        BacktestAdapter.print_backtest_report(metrics)
        
        captured = capsys.readouterr()
        assert '15.00%' in captured.out  # total_return
        assert '1.50' in captured.out    # sharpe_ratio
        assert '50' in captured.out      # total_trades
    
    def test_generate_regression_signals_logic(self):
        """Testa lógica de geração de sinais para regressão."""
        close = np.array([100.0, 101.0, 102.0, 103.0, 104.0])
        preds_usd = np.array([102.0, 100.0, 103.0, 102.0, 105.0])
        
        signals = BacktestAdapter._generate_regression_signals(
            preds_usd=preds_usd,
            close=close,
            threshold_bps=20.0,
            fee_bps=10.0,
            slippage_bps=5.0
        )
        
        assert len(signals) == len(close)
        assert all(s in [-1, 0, 1] for s in signals)
    
    def test_generate_classification_signals_logic(self):
        """Testa lógica de geração de sinais para classificação."""
        predictions = np.array([0, 1, 2, 2, 0])  # BAIXA, LATERAL, ALTA, ALTA, BAIXA
        probabilities = np.array([
            [0.8, 0.1, 0.1],  # Alta confiança em BAIXA
            [0.3, 0.4, 0.3],  # Baixa confiança em LATERAL
            [0.1, 0.1, 0.8],  # Alta confiança em ALTA
            [0.2, 0.2, 0.6],  # Confiança mediana em ALTA
            [0.7, 0.2, 0.1],  # Alta confiança em BAIXA
        ])
        min_confidence = 0.6
        
        signals = BacktestAdapter._generate_classification_signals(
            predictions=predictions,
            probabilities=probabilities,
            min_confidence=min_confidence
        )
        
        assert len(signals) == len(predictions)
        assert signals[0] == -1  # BAIXA com alta confiança → Short
        assert signals[1] == 0   # LATERAL → Neutral
        assert signals[2] == 1   # ALTA com alta confiança → Long
        assert signals[3] == 1   # ALTA com confiança == 0.6 → Long (>= 0.6)
        assert signals[4] == -1  # BAIXA com alta confiança → Short


# ============================================================================
# TESTES: Integração entre Adapters
# ============================================================================

class TestAdaptersIntegration:
    """Testes de integração entre adapters."""
    
    def test_full_pipeline_with_adapters(self, sample_df, feature_cols):
        """Testa pipeline completo: preprocess → model → backtest."""
        # 1. Preprocessamento
        preprocessor = DataPreprocessorAdapter(
            feature_cols=feature_cols,
            target_col='Close',
            lookback=60
        )
        
        X_train, y_train = preprocessor.fit_transform(sample_df.iloc[:150])
        X_test, y_test = preprocessor.transform(sample_df.iloc[150:])
        
        # 2. Modelo
        model = ModelBuilderAdapter.build_lstm(
            input_shape=X_train.shape[1:],
            learning_rate=1e-3
        )
        
        # Treinar brevemente (1 época para teste)
        model.fit(X_train, y_train, epochs=1, batch_size=16, verbose=0)
        
        # 3. Predições
        y_pred_scaled = model.predict(X_test, verbose=0).ravel()
        y_pred_usd = preprocessor.inverse_target(y_pred_scaled)
        
        # 4. Backtest
        df_test = sample_df.iloc[150+60:].reset_index(drop=True)
        
        equity_curve, metrics = BacktestAdapter.backtest_regression(
            df=df_test,
            preds_usd=y_pred_usd,
            fee_bps=10.0,
            slippage_bps=5.0,
            initial_capital=10000.0
        )
        
        # Validações finais
        assert equity_curve is not None
        assert metrics is not None
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
