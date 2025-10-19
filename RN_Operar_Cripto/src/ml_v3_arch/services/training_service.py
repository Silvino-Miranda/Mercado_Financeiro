"""
Training Service - Orquestra todo o processo de treinamento.

Princípios aplicados:
- SRP: Responsável apenas por coordenar o treino
- DIP: Depende de abstrações (BaseModel, BasePreprocessor)
- OCP: Extensível para novos workflows de treino
"""
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import time
import json

# Lazy imports para evitar RecursionError do NumPy
if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

from ..domain import ModelConfig
from ..interfaces import BaseModel, BasePreprocessor


class TrainingService:
    """
    Serviço de treinamento que orquestra:
    1. Preprocessamento de dados
    2. Criação do modelo
    3. Treinamento com callbacks
    4. Salvamento de artefatos
    5. Logging de métricas
    
    Dependency Injection completa: recebe todas as dependências no construtor.
    """
    
    def __init__(
        self,
        model: BaseModel,
        preprocessor: BasePreprocessor,
        config: ModelConfig,
        artifacts_dir: str = "artifacts"
    ):
        """
        Args:
            model: Modelo a ser treinado (via Factory)
            preprocessor: Preprocessador de dados
            config: Configuração do modelo
            artifacts_dir: Diretório para salvar artefatos
        """
        self.model = model
        self.preprocessor = preprocessor
        self.config = config
        self.artifacts_dir = Path(artifacts_dir)
        
        # Criar estrutura de diretórios
        self._create_artifacts_structure()
    
    def _create_artifacts_structure(self) -> None:
        """Cria estrutura de diretórios para artefatos."""
        dirs = [
            self.artifacts_dir / "checkpoints",
            self.artifacts_dir / "logs",
            self.artifacts_dir / "metrics",
            self.artifacts_dir / "preprocessors"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def train(
        self,
        df_train: "pd.DataFrame",
        df_val: Optional["pd.DataFrame"] = None,
        save_artifacts: bool = True,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        Treina o modelo com dados fornecidos.
        
        Args:
            df_train: DataFrame de treino
            df_val: DataFrame de validação (opcional)
            save_artifacts: Se deve salvar modelo e histórico
            verbose: Nível de verbosidade
            
        Returns:
            Dict com histórico de treino e metadados
        """
        if verbose > 0:
            print("\n" + "="*80)
            print("🚀 TRAINING SERVICE - Iniciando Treino")
            print("="*80)
            print(f"📊 Dataset: {len(df_train):,} amostras de treino")
            if df_val is not None:
                print(f"📊 Validação: {len(df_val):,} amostras")
            print(f"🤖 Modelo: {self.config.model_type}")
            print(f"⚙️  Configuração: {self.config}")
            print()
        
        # 1. Preprocessamento
        if verbose > 0:
            print("🔧 Passo 1: Preprocessamento dos dados...")
        
        start_time = time.time()
        
        # Fit no treino (ZERO VAZAMENTO!)
        X_train, y_train = self.preprocessor.fit_transform(df_train)
        
        if df_val is not None:
            X_val, y_val = self.preprocessor.transform(df_val)
            validation_data = (X_val, y_val)
        else:
            validation_data = None
        
        preprocess_time = time.time() - start_time
        
        if verbose > 0:
            print(f"   ✅ X_train: {X_train.shape}")
            if df_val is not None:
                print(f"   ✅ X_val: {X_val.shape}")
            print(f"   ⏱️  Tempo: {preprocess_time:.2f}s")
            print()
        
        # 2. Treinamento
        if verbose > 0:
            print("🔥 Passo 2: Treinamento do modelo...")
            print(f"   Épocas: {self.config.epochs}")
            print(f"   Batch size: {self.config.batch_size}")
            print(f"   Learning rate: {self.config.learning_rate}")
            print()
        
        train_start = time.time()
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            verbose=verbose
        )
        
        train_time = time.time() - train_start
        
        if verbose > 0:
            print(f"\n   ✅ Treinamento concluído em {train_time:.2f}s")
            print()
        
        # 3. Salvar artefatos
        if save_artifacts:
            if verbose > 0:
                print("💾 Passo 3: Salvando artefatos...")
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Salvar modelo
            model_path = self.artifacts_dir / "checkpoints" / f"model_{timestamp}.keras"
            self.model.save(str(model_path))
            
            # Salvar preprocessor
            import pickle
            prep_path = self.artifacts_dir / "preprocessors" / f"preprocessor_{timestamp}.pkl"
            with open(prep_path, 'wb') as f:
                pickle.dump(self.preprocessor, f)
            
            # Salvar histórico
            history_path = self.artifacts_dir / "logs" / f"history_{timestamp}.json"
            self._save_history(history, history_path)
            
            if verbose > 0:
                print(f"   ✅ Modelo: {model_path}")
                print(f"   ✅ Preprocessor: {prep_path}")
                print(f"   ✅ Histórico: {history_path}")
                print()
        
        # 4. Resumo final
        total_time = preprocess_time + train_time
        
        result = {
            'history': history.history if hasattr(history, 'history') else history,
            'config': {
                'model_type': self.config.model_type,
                'lookback': self.config.lookback,
                'lstm_units': self.config.lstm_units,
                'dropout': self.config.dropout,
                'learning_rate': self.config.learning_rate,
                'epochs': self.config.epochs,
                'batch_size': self.config.batch_size
            },
            'metadata': {
                'train_samples': len(df_train),
                'val_samples': len(df_val) if df_val is not None else 0,
                'preprocess_time': preprocess_time,
                'train_time': train_time,
                'total_time': total_time,
                'timestamp': timestamp if save_artifacts else None
            }
        }
        
        if verbose > 0:
            print("="*80)
            print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO")
            print("="*80)
            print(f"⏱️  Tempo total: {total_time:.2f}s")
            print(f"📊 Amostras treinadas: {len(df_train):,}")
            if df_val is not None:
                final_val_loss = result['history'].get('val_loss', [None])[-1]
                final_val_acc = result['history'].get('val_accuracy', result['history'].get('val_acc', [None]))[-1]
                if final_val_loss is not None:
                    print(f"📈 Val Loss: {final_val_loss:.4f}")
                if final_val_acc is not None:
                    print(f"📈 Val Accuracy: {final_val_acc:.4f}")
            print("="*80 + "\n")
        
        return result
    
    def _save_history(self, history: Any, path: Path) -> None:
        """Salva histórico de treino em JSON."""
        # Lazy import para evitar RecursionError
        import numpy as np
        
        if hasattr(history, 'history'):
            history_dict = history.history
        else:
            history_dict = history
        
        # Converter numpy arrays para listas
        serializable = {}
        for key, values in history_dict.items():
            if isinstance(values, np.ndarray):
                serializable[key] = values.tolist()
            elif isinstance(values, list):
                serializable[key] = [float(v) if isinstance(v, (np.floating, np.integer)) else v for v in values]
            else:
                serializable[key] = values
        
        with open(path, 'w') as f:
            json.dump(serializable, f, indent=2)
    
    def train_with_split(
        self,
        df: "pd.DataFrame",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Treina o modelo com split temporal automático.
        
        Args:
            df: DataFrame completo
            train_ratio: Porcentagem para treino
            val_ratio: Porcentagem para validação
            **kwargs: Argumentos adicionais para train()
            
        Returns:
            Resultado do treinamento
        """
        n = len(df)
        i_train = int(n * train_ratio)
        i_val = int(n * (train_ratio + val_ratio))
        
        df_train = df.iloc[:i_train]
        df_val = df.iloc[i_train:i_val]
        
        return self.train(df_train, df_val, **kwargs)


if __name__ == "__main__":
    """Exemplo de uso do TrainingService."""
    
    print("📚 Exemplo de uso do TrainingService")
    print("="*80)
    print()
    print("```python")
    print("from ml_v3_arch.domain import ModelConfig")
    print("from ml_v3_arch.factories import ModelFactory")
    print("from ml_v3_arch.services import TrainingService")
    print("from ml_v3_arch.infrastructure import DataLoader, PreprocessorFactory")
    print()
    print("# 1. Configurar")
    print("config = ModelConfig(")
    print("    model_type='directional',")
    print("    lookback=60,")
    print("    lstm_units=128")
    print(")")
    print()
    print("# 2. Criar dependências (DI)")
    print("model = ModelFactory.create_model(config)")
    print("preprocessor = PreprocessorFactory.create_preprocessor(config)")
    print()
    print("# 3. Criar serviço (DI)")
    print("service = TrainingService(")
    print("    model=model,")
    print("    preprocessor=preprocessor,")
    print("    config=config")
    print(")")
    print()
    print("# 4. Treinar")
    print("loader = DataLoader()")
    print("df = loader.load_csv('data/BTCUSDT_30m_full.csv')")
    print("result = service.train_with_split(df)")
    print("```")
    print()
    print("✅ TrainingService pronto para uso!")
