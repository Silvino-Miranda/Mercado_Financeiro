"""
Model Persistence - Save/Load de modelos e artifacts.

Princípios aplicados:
- SRP: Responsável apenas por persistência
- Versioning: Controle de versões
- Format flexibility: Suporta múltiplos formatos
"""
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import pickle

import numpy as np


class ModelPersistenceError(Exception):
    """Erro de persistência de modelo."""
    pass


class ModelPersistence:
    """
    Gerenciamento de persistência que:
    1. Salva/carrega modelos Keras
    2. Salva/carrega preprocessors sklearn
    3. Salva/carrega configurações JSON
    4. Versionamento automático
    5. Metadata tracking
    """
    
    def __init__(self, base_dir: Path):
        """
        Args:
            base_dir: Diretório base para salvar artifacts
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_keras_model(
        self,
        model: Any,  # keras.Model
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        verbose: int = 1
    ) -> Path:
        """
        Salva modelo Keras.
        
        Args:
            model: Modelo Keras
            name: Nome do modelo
            metadata: Metadata adicional
            verbose: Nível de verbosidade
            
        Returns:
            Path onde modelo foi salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = self.base_dir / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = model_dir / f"{name}_{timestamp}.keras"
        
        try:
            model.save(model_path)
            
            if verbose > 0:
                print(f"✅ Modelo Keras salvo: {model_path}")
            
            # Salvar metadata
            if metadata:
                metadata_path = model_path.with_suffix('.json')
                metadata['saved_at'] = timestamp
                metadata['model_path'] = str(model_path)
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                if verbose > 0:
                    print(f"✅ Metadata salva: {metadata_path}")
            
            return model_path
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao salvar modelo Keras: {e}")
    
    def load_keras_model(
        self,
        model_path: Path,
        verbose: int = 1
    ) -> Any:
        """
        Carrega modelo Keras.
        
        Args:
            model_path: Caminho do modelo
            verbose: Nível de verbosidade
            
        Returns:
            Modelo Keras carregado
        """
        try:
            # Import aqui para não forçar dependência
            from tensorflow import keras
            
            model = keras.models.load_model(model_path)
            
            if verbose > 0:
                print(f"✅ Modelo Keras carregado: {model_path}")
            
            # Carregar metadata se existir
            metadata_path = model_path.with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if verbose > 0:
                    print(f"✅ Metadata carregada: {metadata_path}")
                
                return model, metadata
            
            return model, {}
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao carregar modelo Keras: {e}")
    
    def save_preprocessor(
        self,
        preprocessor: Any,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        verbose: int = 1
    ) -> Path:
        """
        Salva preprocessor sklearn.
        
        Args:
            preprocessor: Preprocessor (ex: StandardScaler)
            name: Nome do preprocessor
            metadata: Metadata adicional
            verbose: Nível de verbosidade
            
        Returns:
            Path onde preprocessor foi salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prep_dir = self.base_dir / "preprocessors"
        prep_dir.mkdir(parents=True, exist_ok=True)
        
        prep_path = prep_dir / f"{name}_{timestamp}.pkl"
        
        try:
            with open(prep_path, 'wb') as f:
                pickle.dump(preprocessor, f)
            
            if verbose > 0:
                print(f"✅ Preprocessor salvo: {prep_path}")
            
            # Salvar metadata
            if metadata:
                metadata_path = prep_path.with_suffix('.json')
                metadata['saved_at'] = timestamp
                metadata['preprocessor_path'] = str(prep_path)
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                if verbose > 0:
                    print(f"✅ Metadata salva: {metadata_path}")
            
            return prep_path
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao salvar preprocessor: {e}")
    
    def load_preprocessor(
        self,
        prep_path: Path,
        verbose: int = 1
    ) -> Any:
        """
        Carrega preprocessor sklearn.
        
        Args:
            prep_path: Caminho do preprocessor
            verbose: Nível de verbosidade
            
        Returns:
            Preprocessor carregado
        """
        try:
            with open(prep_path, 'rb') as f:
                preprocessor = pickle.load(f)
            
            if verbose > 0:
                print(f"✅ Preprocessor carregado: {prep_path}")
            
            # Carregar metadata se existir
            metadata_path = prep_path.with_suffix('.json')
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if verbose > 0:
                    print(f"✅ Metadata carregada: {metadata_path}")
                
                return preprocessor, metadata
            
            return preprocessor, {}
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao carregar preprocessor: {e}")
    
    def save_config(
        self,
        config: Dict[str, Any],
        name: str,
        verbose: int = 1
    ) -> Path:
        """
        Salva configuração JSON.
        
        Args:
            config: Dicionário de configuração
            name: Nome da configuração
            verbose: Nível de verbosidade
            
        Returns:
            Path onde config foi salva
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_dir = self.base_dir / "configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / f"{name}_{timestamp}.json"
        
        try:
            # Adicionar timestamp
            config['saved_at'] = timestamp
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            if verbose > 0:
                print(f"✅ Config salva: {config_path}")
            
            return config_path
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao salvar config: {e}")
    
    def load_config(
        self,
        config_path: Path,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        Carrega configuração JSON.
        
        Args:
            config_path: Caminho da configuração
            verbose: Nível de verbosidade
            
        Returns:
            Dict de configuração
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if verbose > 0:
                print(f"✅ Config carregada: {config_path}")
            
            return config
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao carregar config: {e}")
    
    def save_history(
        self,
        history: Dict[str, list],
        name: str,
        verbose: int = 1
    ) -> Path:
        """
        Salva histórico de treinamento.
        
        Args:
            history: Dict com histórico (ex: history.history do Keras)
            name: Nome do histórico
            verbose: Nível de verbosidade
            
        Returns:
            Path onde histórico foi salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_dir = self.base_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        
        history_path = history_dir / f"{name}_{timestamp}.json"
        
        try:
            # Converter numpy arrays para listas
            history_clean = {}
            for key, value in history.items():
                if isinstance(value, np.ndarray):
                    history_clean[key] = value.tolist()
                elif isinstance(value, list):
                    history_clean[key] = [
                        float(v) if isinstance(v, (np.floating, np.integer)) else v
                        for v in value
                    ]
                else:
                    history_clean[key] = value
            
            history_clean['saved_at'] = timestamp
            
            with open(history_path, 'w') as f:
                json.dump(history_clean, f, indent=2)
            
            if verbose > 0:
                print(f"✅ Histórico salvo: {history_path}")
            
            return history_path
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao salvar histórico: {e}")
    
    def load_history(
        self,
        history_path: Path,
        verbose: int = 1
    ) -> Dict[str, list]:
        """
        Carrega histórico de treinamento.
        
        Args:
            history_path: Caminho do histórico
            verbose: Nível de verbosidade
            
        Returns:
            Dict com histórico
        """
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            if verbose > 0:
                print(f"✅ Histórico carregado: {history_path}")
            
            return history
        
        except Exception as e:
            raise ModelPersistenceError(f"Erro ao carregar histórico: {e}")
    
    def list_models(self, pattern: str = "*.keras") -> list[Path]:
        """Lista modelos salvos."""
        model_dir = self.base_dir / "models"
        if not model_dir.exists():
            return []
        
        return sorted(model_dir.glob(pattern), reverse=True)
    
    def list_preprocessors(self, pattern: str = "*.pkl") -> list[Path]:
        """Lista preprocessors salvos."""
        prep_dir = self.base_dir / "preprocessors"
        if not prep_dir.exists():
            return []
        
        return sorted(prep_dir.glob(pattern), reverse=True)
    
    def get_latest_model(self, name_prefix: str = "") -> Optional[Path]:
        """Retorna modelo mais recente."""
        models = self.list_models(f"{name_prefix}*.keras")
        return models[0] if models else None
    
    def get_latest_preprocessor(self, name_prefix: str = "") -> Optional[Path]:
        """Retorna preprocessor mais recente."""
        preps = self.list_preprocessors(f"{name_prefix}*.pkl")
        return preps[0] if preps else None


# Export
__all__ = [
    'ModelPersistence',
    'ModelPersistenceError'
]
