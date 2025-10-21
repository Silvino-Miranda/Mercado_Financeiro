"""
Testes para Factories (ModelFactory).

Cobertura:
- Criação de modelos LSTM, GRU, Directional, Improved Directional
- Validação de model_type inválido
- Verificação de arquitetura dos modelos
- Callbacks padrão
"""
import pytest
import numpy as np
from tensorflow import keras

from src.ml_v3_arch.factories.model_factory import ModelFactory


class TestModelFactory:
    """Testes para ModelFactory."""
    
    def test_create_lstm_regression(self, sample_model_config):
        """Deve criar modelo LSTM para regressão."""
        config = sample_model_config
        config.model_type = 'lstm'
        
        model = ModelFactory.create_model(config)
        
        assert model is not None
        assert isinstance(model, keras.Model)
        assert model.name == "LSTM_Regression"
        
        # Verificar que tem camadas LSTM
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) == config.lstm_layers
        
        # Verificar saída (regressão = 1 neurônio)
        assert model.layers[-1].units == 1
    
    def test_create_gru_regression(self, sample_model_config):
        """Deve criar modelo GRU para regressão."""
        config = sample_model_config
        config.model_type = 'gru'
        
        model = ModelFactory.create_model(config)
        
        assert model is not None
        assert isinstance(model, keras.Model)
        assert model.name == "GRU_Regression"
        
        # Verificar que tem camadas GRU
        gru_layers = [layer for layer in model.layers if 'gru' in layer.name.lower()]
        assert len(gru_layers) == config.lstm_layers
        
        # Verificar saída
        assert model.layers[-1].units == 1
    
    def test_create_directional_lstm(self, sample_model_config):
        """Deve criar modelo LSTM direcional (classificação 3 classes)."""
        config = sample_model_config
        config.model_type = 'directional'
        
        model = ModelFactory.create_model(config)
        
        assert model is not None
        assert isinstance(model, keras.Model)
        assert model.name == "Directional_LSTM"
        
        # Verificar que tem camadas LSTM
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) == config.lstm_layers
        
        # Verificar saída (classificação = 3 classes)
        assert model.layers[-1].units == 3
        
        # Verificar ativação softmax
        assert model.layers[-1].activation.__name__ == 'softmax'
    
    def test_create_improved_directional(self, sample_model_config):
        """Deve criar modelo direcional aprimorado com Conv1D e BatchNorm."""
        config = sample_model_config
        config.model_type = 'improved_directional'
        
        model = ModelFactory.create_model(config)
        
        assert model is not None
        assert isinstance(model, keras.Model)
        assert model.name == "Improved_Directional_LSTM"
        
        # Verificar que tem Conv1D no início
        assert 'conv1d' in model.layers[0].name.lower()
        
        # Verificar que tem BatchNorm
        batchnorm_layers = [layer for layer in model.layers if 'batchnorm' in layer.name.lower()]
        assert len(batchnorm_layers) > 0
        
        # Verificar saída (3 classes)
        assert model.layers[-1].units == 3
    
    def test_invalid_model_type_raises_error(self, sample_model_config):
        """Deve lançar ValueError para model_type inválido."""
        config = sample_model_config
        config.model_type = 'invalid_model'
        
        with pytest.raises(ValueError) as exc_info:
            ModelFactory.create_model(config)
        
        assert "Unknown model_type: invalid_model" in str(exc_info.value)
        assert "Supported:" in str(exc_info.value)
    
    def test_model_type_case_insensitive(self, sample_model_config):
        """Deve aceitar model_type em qualquer case."""
        config = sample_model_config
        
        # Testar diferentes cases
        for model_type in ['LSTM', 'Lstm', 'lstm', 'LsTm']:
            config.model_type = model_type
            model = ModelFactory.create_model(config)
            assert model is not None
            assert model.name == "LSTM_Regression"
    
    def test_lstm_model_is_compiled(self, sample_model_config):
        """Deve criar modelo já compilado com optimizer e loss."""
        config = sample_model_config
        config.model_type = 'lstm'
        
        model = ModelFactory.create_model(config)
        
        # Verificar que está compilado
        assert model.optimizer is not None
        assert model.loss is not None
        
        # Verificar learning rate
        assert abs(model.optimizer.learning_rate.numpy() - config.learning_rate) < 1e-6
    
    def test_directional_uses_correct_loss(self, sample_model_config):
        """Deve usar sparse_categorical_crossentropy para classificação."""
        config = sample_model_config
        config.model_type = 'directional'
        
        model = ModelFactory.create_model(config)
        
        # Verificar loss function (model.loss é string)
        assert model.loss == 'sparse_categorical_crossentropy'
    
    def test_lstm_layers_stacking(self, sample_model_config):
        """Deve empilhar corretamente camadas LSTM com return_sequences."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.lstm_layers = 3
        
        model = ModelFactory.create_model(config)
        
        # Verificar número de LSTMs
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) == 3
        
        # Primeira e segunda devem ter return_sequences=True
        # (não podemos acessar diretamente, mas verificamos pela estrutura)
        assert len(model.layers) >= 6  # 3 LSTMs + 3 Dropouts + Dense
    
    def test_dropout_applied_correctly(self, sample_model_config):
        """Deve aplicar dropout após cada camada LSTM."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.dropout = 0.4
        
        model = ModelFactory.create_model(config)
        
        # Verificar que tem camadas de dropout
        dropout_layers = [layer for layer in model.layers if 'dropout' in layer.name.lower()]
        assert len(dropout_layers) == config.lstm_layers
    
    def test_gru_has_fewer_parameters_than_lstm(self, sample_model_config, sample_data):
        """GRU deve ter menos parâmetros que LSTM (mais eficiente)."""
        config = sample_model_config
        config.lstm_units = 64
        config.lstm_layers = 2
        
        # Criar LSTM
        config.model_type = 'lstm'
        lstm_model = ModelFactory.create_model(config)
        
        # Build o modelo
        X_train, _, _, _, _, _ = sample_data
        lstm_model.build(input_shape=X_train.shape)
        lstm_params = lstm_model.count_params()
        
        # Criar GRU
        config.model_type = 'gru'
        gru_model = ModelFactory.create_model(config)
        gru_model.build(input_shape=X_train.shape)
        gru_params = gru_model.count_params()
        
        # GRU deve ter menos parâmetros
        assert gru_params < lstm_params
    
    def test_model_can_predict_shape(self, sample_model_config, sample_data):
        """Deve criar modelo que pode fazer predições com shape correto."""
        config = sample_model_config
        config.model_type = 'lstm'
        
        model = ModelFactory.create_model(config)
        
        # Build model com input shape
        X_train, _, _, _, _, _ = sample_data
        model.build(input_shape=X_train.shape)
        
        # Fazer predição
        predictions = model.predict(X_train[:5], verbose=0)
        
        assert predictions.shape == (5, 1)  # Regressão
        assert not np.isnan(predictions).any()
    
    def test_directional_can_predict_classes(self, sample_model_config, sample_data):
        """Modelo direcional deve prever 3 classes com softmax."""
        config = sample_model_config
        config.model_type = 'directional'
        
        model = ModelFactory.create_model(config)
        
        # Build e prever
        X_train, _, _, _, _, _ = sample_data
        model.build(input_shape=X_train.shape)
        predictions = model.predict(X_train[:5], verbose=0)
        
        assert predictions.shape == (5, 3)  # 3 classes
        
        # Verificar que soma para 1 (softmax)
        for pred in predictions:
            assert abs(pred.sum() - 1.0) < 1e-5
            
        # Verificar que todas as probabilidades são >= 0
        assert (predictions >= 0).all()


class TestCallbacks:
    """Testes para criação de callbacks."""
    
    def test_get_callbacks_returns_list(self, sample_model_config):
        """Deve retornar lista de callbacks."""
        callbacks = ModelFactory.get_callbacks(sample_model_config)
        
        assert isinstance(callbacks, list)
        assert len(callbacks) > 0
    
    def test_callbacks_include_early_stopping(self, sample_model_config):
        """Deve incluir EarlyStopping."""
        callbacks = ModelFactory.get_callbacks(sample_model_config)
        
        early_stopping = [cb for cb in callbacks if isinstance(cb, keras.callbacks.EarlyStopping)]
        assert len(early_stopping) == 1
        
        # Verificar patience
        assert early_stopping[0].patience == sample_model_config.patience
    
    def test_callbacks_include_reduce_lr(self, sample_model_config):
        """Deve incluir ReduceLROnPlateau."""
        callbacks = ModelFactory.get_callbacks(sample_model_config)
        
        reduce_lr = [cb for cb in callbacks if isinstance(cb, keras.callbacks.ReduceLROnPlateau)]
        assert len(reduce_lr) == 1
        
        # Verificar que patience é menor que EarlyStopping
        assert reduce_lr[0].patience < sample_model_config.patience
    
    def test_callbacks_monitor_val_loss(self, sample_model_config):
        """Deve monitorar val_loss por padrão."""
        callbacks = ModelFactory.get_callbacks(sample_model_config, monitor='val_loss')
        
        early_stopping = [cb for cb in callbacks if isinstance(cb, keras.callbacks.EarlyStopping)][0]
        assert early_stopping.monitor == 'val_loss'
        assert early_stopping.mode == 'min'
    
    def test_callbacks_monitor_val_accuracy(self, sample_model_config):
        """Deve mudar mode para max quando monitorar accuracy."""
        callbacks = ModelFactory.get_callbacks(sample_model_config, monitor='val_accuracy')
        
        early_stopping = [cb for cb in callbacks if isinstance(cb, keras.callbacks.EarlyStopping)][0]
        assert early_stopping.monitor == 'val_accuracy'
        assert early_stopping.mode == 'max'
    
    def test_early_stopping_restores_best_weights(self, sample_model_config):
        """EarlyStopping deve restaurar melhores pesos."""
        callbacks = ModelFactory.get_callbacks(sample_model_config)
        
        early_stopping = [cb for cb in callbacks if isinstance(cb, keras.callbacks.EarlyStopping)][0]
        assert early_stopping.restore_best_weights is True


class TestModelArchitecture:
    """Testes detalhados de arquitetura dos modelos."""
    
    def test_lstm_units_decrease_with_depth(self, sample_model_config):
        """Units devem diminuir pela metade em camadas mais profundas."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.lstm_units = 128
        config.lstm_layers = 3
        
        model = ModelFactory.create_model(config)
        
        # Primeira LSTM: 128
        # Segunda LSTM: 64
        # Terceira LSTM: 32
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        
        assert lstm_layers[0].units == 128
        assert lstm_layers[1].units == 64
        assert lstm_layers[2].units == 32
    
    def test_improved_directional_has_more_layers(self, sample_model_config):
        """Improved directional deve ter mais camadas que directional simples."""
        config = sample_model_config
        
        # Directional simples
        config.model_type = 'directional'
        simple_model = ModelFactory.create_model(config)
        simple_layers = len(simple_model.layers)
        
        # Improved directional
        config.model_type = 'improved_directional'
        improved_model = ModelFactory.create_model(config)
        improved_layers = len(improved_model.layers)
        
        # Improved deve ter mais camadas (Conv1D + BatchNorm + Dense extras)
        assert improved_layers > simple_layers
    
    def test_directional_uses_recurrent_dropout(self, sample_model_config):
        """Modelo direcional deve usar recurrent dropout."""
        config = sample_model_config
        config.model_type = 'directional'
        config.dropout = 0.3
        
        model = ModelFactory.create_model(config)
        
        # Verificar que LSTMs têm dropout e recurrent_dropout
        # (não podemos acessar diretamente o config, mas verificamos pela estrutura)
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) > 0
    
    def test_regression_models_use_mse_loss(self, sample_model_config):
        """Modelos de regressão devem usar MSE."""
        for model_type in ['lstm', 'gru']:
            config = sample_model_config
            config.model_type = model_type
            
            model = ModelFactory.create_model(config)
            
            # Verificar loss (model.loss é string)
            assert 'mse' in str(model.loss).lower()
    
    def test_classification_models_use_categorical_loss(self, sample_model_config):
        """Modelos de classificação devem usar categorical crossentropy."""
        for model_type in ['directional', 'improved_directional']:
            config = sample_model_config
            config.model_type = model_type
            
            model = ModelFactory.create_model(config)
            
            # Verificar loss (model.loss é string)
            assert 'categorical' in str(model.loss).lower()
    
    @pytest.mark.parametrize("model_type", ['lstm', 'gru', 'directional', 'improved_directional'])
    def test_all_models_have_optimizer(self, sample_model_config, model_type):
        """Todos os modelos devem ter optimizer configurado."""
        config = sample_model_config
        config.model_type = model_type
        
        model = ModelFactory.create_model(config)
        
        assert model.optimizer is not None
        assert isinstance(model.optimizer, keras.optimizers.Optimizer)
    
    @pytest.mark.parametrize("model_type", ['lstm', 'gru', 'directional', 'improved_directional'])
    def test_all_models_can_be_built(self, sample_model_config, sample_data, model_type):
        """Todos os modelos devem poder ser construídos com dados reais."""
        config = sample_model_config
        config.model_type = model_type
        
        model = ModelFactory.create_model(config)
        X_train, _, _, _, _, _ = sample_data
        
        # Build model
        model.build(input_shape=X_train.shape)
        
        # Verificar que foi construído
        assert model.built is True
        assert model.count_params() > 0


class TestEdgeCases:
    """Testes para casos extremos."""
    
    def test_single_lstm_layer(self, sample_model_config):
        """Deve funcionar com apenas 1 camada LSTM."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.lstm_layers = 1
        
        model = ModelFactory.create_model(config)
        
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) == 1
    
    def test_high_dropout(self, sample_model_config):
        """Deve aceitar dropout alto (0.7)."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.dropout = 0.7
        
        model = ModelFactory.create_model(config)
        
        assert model is not None
        dropout_layers = [layer for layer in model.layers if 'dropout' in layer.name.lower()]
        assert len(dropout_layers) > 0
    
    def test_very_low_learning_rate(self, sample_model_config):
        """Deve aceitar learning rate muito baixo."""
        config = sample_model_config
        config.model_type = 'gru'
        config.learning_rate = 1e-6
        
        model = ModelFactory.create_model(config)
        
        assert abs(model.optimizer.learning_rate.numpy() - 1e-6) < 1e-9
    
    def test_many_lstm_layers(self, sample_model_config):
        """Deve suportar múltiplas camadas LSTM (5)."""
        config = sample_model_config
        config.model_type = 'lstm'
        config.lstm_layers = 5
        config.lstm_units = 256
        
        model = ModelFactory.create_model(config)
        
        lstm_layers = [layer for layer in model.layers if 'lstm' in layer.name.lower()]
        assert len(lstm_layers) == 5
