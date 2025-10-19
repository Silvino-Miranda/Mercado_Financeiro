"""
Testes para TrainingService.

Cobertura:
- Treinamento com e sem validação
- Preprocessamento sem data leakage
- Salvamento de artefatos
- Callbacks aplicados
- Error handling
"""
import numpy as np
import pandas as pd
import json
from unittest.mock import Mock, call, patch, mock_open

from src.ml_v3_arch.services.training_service import TrainingService
from src.ml_v3_arch.domain import ModelConfig


class TestTrainingServiceInitialization:
    """Testes de inicialização do TrainingService."""
    
    def test_create_training_service(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve criar TrainingService com todas as dependências."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        assert service.model == mock_keras_model
        assert service.preprocessor == mock_preprocessor
        assert service.config == sample_model_config
        assert service.artifacts_dir == tmp_path
    
    def test_creates_artifacts_directory_structure(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve criar estrutura de diretórios para artefatos."""
        TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        # Verificar que diretórios foram criados
        assert (tmp_path / "checkpoints").exists()
        assert (tmp_path / "logs").exists()
        assert (tmp_path / "metrics").exists()
        assert (tmp_path / "preprocessors").exists()


class TestTrainingServiceTrain:
    """Testes do método train."""
    
    def test_train_without_validation(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve treinar modelo sem dados de validação."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        # Criar DataFrame de treino
        df_train = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'target': np.random.rand(100)
        })
        
        # Configurar mocks
        X_train = np.random.rand(100, 60, 2)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5, 0.4], 'val_loss': [0.6, 0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        result = service.train(df_train, save_artifacts=False, verbose=0)
        
        # Verificar que fit_transform foi chamado no treino
        mock_preprocessor.fit_transform.assert_called_once_with(df_train)
        
        # Verificar que model.fit foi chamado
        mock_keras_model.fit.assert_called_once()
        call_args = mock_keras_model.fit.call_args
        
        assert np.array_equal(call_args[0][0], X_train)
        assert np.array_equal(call_args[0][1], y_train)
        assert call_args[1]['validation_data'] is None
        assert call_args[1]['epochs'] == sample_model_config.epochs
        assert call_args[1]['batch_size'] == sample_model_config.batch_size
        
        # Verificar resultado
        assert 'history' in result
        assert 'config' in result
        assert 'metadata' in result
        assert result['metadata']['train_samples'] == 100
        assert result['metadata']['val_samples'] == 0
    
    def test_train_with_validation(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve treinar modelo com dados de validação."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        # Criar DataFrames
        df_train = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'target': np.random.rand(100)
        })
        
        df_val = pd.DataFrame({
            'feature1': np.random.rand(20),
            'feature2': np.random.rand(20),
            'target': np.random.rand(20)
        })
        
        # Configurar mocks
        X_train = np.random.rand(100, 60, 2)
        y_train = np.random.rand(100)
        X_val = np.random.rand(20, 60, 2)
        y_val = np.random.rand(20)
        
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        mock_preprocessor.transform.return_value = (X_val, y_val)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5, 0.4], 'val_loss': [0.6, 0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        result = service.train(df_train, df_val=df_val, save_artifacts=False, verbose=0)
        
        # Verificar preprocessamento sem data leakage
        mock_preprocessor.fit_transform.assert_called_once_with(df_train)
        mock_preprocessor.transform.assert_called_once_with(df_val)
        
        # Verificar que validation_data foi passada
        call_args = mock_keras_model.fit.call_args
        validation_data = call_args[1]['validation_data']
        
        assert validation_data is not None
        assert len(validation_data) == 2
        assert np.array_equal(validation_data[0], X_val)
        assert np.array_equal(validation_data[1], y_val)
        
        # Verificar metadata
        assert result['metadata']['train_samples'] == 100
        assert result['metadata']['val_samples'] == 20
    
    def test_no_data_leakage_in_preprocessing(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve garantir que preprocessor.fit é chamado apenas no treino."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        df_val = pd.DataFrame({'feature': np.random.rand(20), 'target': np.random.rand(20)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        X_val = np.random.rand(20, 60, 1)
        y_val = np.random.rand(20)
        
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        mock_preprocessor.transform.return_value = (X_val, y_val)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        service.train(df_train, df_val=df_val, save_artifacts=False, verbose=0)
        
        # CRÍTICO: fit_transform apenas no treino, transform no val
        assert mock_preprocessor.fit_transform.call_count == 1
        assert mock_preprocessor.transform.call_count == 1
        
        # Verificar ordem das chamadas
        calls = [
            call.fit_transform(df_train),
            call.transform(df_val)
        ]
        mock_preprocessor.assert_has_calls(calls, any_order=False)
    
    def test_save_artifacts_when_requested(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path, mocker):
        """Deve salvar modelo, preprocessor e histórico quando save_artifacts=True."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5, 0.4], 'accuracy': [0.8, 0.9]}
        mock_keras_model.fit.return_value = mock_history
        
        # Mock pickle.dump para evitar erro de serialização
        mock_pickle_dump = mocker.patch('pickle.dump')
        
        # Treinar com save_artifacts=True
        service.train(df_train, save_artifacts=True, verbose=0)
        
        # Verificar que model.save foi chamado
        mock_keras_model.save.assert_called_once()
        saved_model_path = mock_keras_model.save.call_args[0][0]
        assert 'model_' in saved_model_path
        assert saved_model_path.endswith('.keras')
        
        # Verificar que pickle.dump foi chamado (preprocessor)
        assert mock_pickle_dump.call_count == 1
        
        # Verificar que histórico foi salvo
        history_files = list((tmp_path / "logs").glob("history_*.json"))
        assert len(history_files) == 1
        
        # Verificar conteúdo do histórico
        with open(history_files[0], 'r') as f:
            saved_history = json.load(f)
        
        assert 'loss' in saved_history
        assert 'accuracy' in saved_history
        assert saved_history['loss'] == [0.5, 0.4]
    
    def test_no_save_artifacts_when_not_requested(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Não deve salvar artefatos quando save_artifacts=False."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar com save_artifacts=False
        service.train(df_train, save_artifacts=False, verbose=0)
        
        # Verificar que model.save NÃO foi chamado
        mock_keras_model.save.assert_not_called()
        
        # Verificar que nenhum arquivo foi criado
        prep_files = list((tmp_path / "preprocessors").glob("preprocessor_*.pkl"))
        history_files = list((tmp_path / "logs").glob("history_*.json"))
        
        assert len(prep_files) == 0
        assert len(history_files) == 0
    
    def test_result_contains_all_metadata(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Resultado deve conter todas as informações relevantes."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        result = service.train(df_train, save_artifacts=False, verbose=0)
        
        # Verificar estrutura do resultado
        assert 'history' in result
        assert 'config' in result
        assert 'metadata' in result
        
        # Verificar config
        assert result['config']['model_type'] == sample_model_config.model_type
        assert result['config']['lookback'] == sample_model_config.lookback
        assert result['config']['lstm_units'] == sample_model_config.lstm_units
        assert result['config']['dropout'] == sample_model_config.dropout
        assert result['config']['learning_rate'] == sample_model_config.learning_rate
        
        # Verificar metadata
        assert 'train_samples' in result['metadata']
        assert 'val_samples' in result['metadata']
        assert 'preprocess_time' in result['metadata']
        assert 'train_time' in result['metadata']
        assert 'total_time' in result['metadata']
        
        # Verificar valores
        assert result['metadata']['train_samples'] == 100
        assert result['metadata']['preprocess_time'] >= 0
        assert result['metadata']['train_time'] >= 0
    
    def test_respects_config_parameters(self, mock_keras_model, mock_preprocessor, tmp_path):
        """Deve usar parâmetros do ModelConfig no treinamento."""
        config = ModelConfig(
            model_type='lstm',
            lookback=60,
            lstm_units=128,
            lstm_layers=3,
            dropout=0.4,
            learning_rate=0.0001,
            batch_size=64,
            epochs=50,
            patience=10
        )
        
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        service.train(df_train, save_artifacts=False, verbose=0)
        
        # Verificar que model.fit foi chamado com parâmetros corretos
        call_args = mock_keras_model.fit.call_args
        
        assert call_args[1]['epochs'] == 50
        assert call_args[1]['batch_size'] == 64


class TestTrainingServiceVerbosity:
    """Testes de verbosidade (logging)."""
    
    def test_verbose_0_no_output(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path, capsys):
        """verbose=0 não deve imprimir nada."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar com verbose=0
        service.train(df_train, save_artifacts=False, verbose=0)
        
        # Capturar output
        captured = capsys.readouterr()
        
        # Não deve ter nenhuma mensagem do TrainingService
        assert "TRAINING SERVICE" not in captured.out
        assert "Passo 1" not in captured.out
        assert "Passo 2" not in captured.out
    
    def test_verbose_1_prints_progress(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path, capsys):
        """verbose=1 deve imprimir progresso."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar com verbose=1
        service.train(df_train, save_artifacts=False, verbose=1)
        
        # Capturar output
        captured = capsys.readouterr()
        
        # Deve ter mensagens
        assert "TRAINING SERVICE" in captured.out
        assert "Preprocessamento" in captured.out
        assert "Treinamento" in captured.out
        assert "CONCLUÍDO" in captured.out


class TestTrainingServiceEdgeCases:
    """Testes de casos extremos."""
    
    def test_train_with_small_dataset(self, mock_keras_model, mock_preprocessor, sample_model_config, tmp_path):
        """Deve funcionar com dataset pequeno."""
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=sample_model_config,
            artifacts_dir=str(tmp_path)
        )
        
        # Dataset com apenas 10 amostras
        df_train = pd.DataFrame({'feature': np.random.rand(10), 'target': np.random.rand(10)})
        
        X_train = np.random.rand(10, 60, 1)
        y_train = np.random.rand(10)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        result = service.train(df_train, save_artifacts=False, verbose=0)
        
        assert result['metadata']['train_samples'] == 10
    
    def test_train_with_single_epoch(self, mock_keras_model, mock_preprocessor, tmp_path):
        """Deve funcionar com apenas 1 época."""
        config = ModelConfig(
            model_type='lstm',
            lookback=60,
            lstm_units=64,
            lstm_layers=2,
            dropout=0.3,
            learning_rate=0.001,
            batch_size=32,
            epochs=1,  # Apenas 1 época
            patience=5
        )
        
        service = TrainingService(
            model=mock_keras_model,
            preprocessor=mock_preprocessor,
            config=config,
            artifacts_dir=str(tmp_path)
        )
        
        df_train = pd.DataFrame({'feature': np.random.rand(100), 'target': np.random.rand(100)})
        
        X_train = np.random.rand(100, 60, 1)
        y_train = np.random.rand(100)
        mock_preprocessor.fit_transform.return_value = (X_train, y_train)
        
        mock_history = Mock()
        mock_history.history = {'loss': [0.5]}
        mock_keras_model.fit.return_value = mock_history
        
        # Treinar
        result = service.train(df_train, save_artifacts=False, verbose=0)
        
        # Verificar que foi chamado com 1 época
        call_args = mock_keras_model.fit.call_args
        assert call_args[1]['epochs'] == 1
