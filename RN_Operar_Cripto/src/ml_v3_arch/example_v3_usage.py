"""
Script de exemplo: Execução completa da v3 (Clean Architecture)

Demonstra o workflow completo:
1. Carregar dados (DataLoader)
2. Configurar modelo (ModelConfig)
3. Treinar (TrainingService)
4. Salvar artefatos (ModelPersistence)

Uso:
    python src/ml_v3_arch/example_v3_usage.py
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_v3_arch.domain.entities import ModelConfig
from ml_v3_arch.factories.model_factory import ModelFactory
from ml_v3_arch.infrastructure.data_loader import DataLoader, DataLoadConfig
from ml_v3_arch.infrastructure.model_persistence import ModelPersistence
from ml_v3_arch.services.training_service import TrainingService


def main():
    """Executa pipeline completo v3."""
    print("\n" + "="*80)
    print("🚀 EXEMPLO DE EXECUÇÃO - v3 (Clean Architecture)")
    print("="*80 + "\n")
    
    # ========================================
    # 1. CONFIGURAR DATALOADER
    # ========================================
    print("📂 ETAPA 1: Configurar DataLoader\n")
    
    data_config = DataLoadConfig(
        required_columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        optional_columns=['Date'],
        date_column='Date',
        parse_dates=True,
        drop_duplicates=True,
        handle_missing='drop',
        validate_ohlc=True
    )
    
    data_loader = DataLoader(data_config)
    print("   ✅ DataLoader configurado")
    print(f"   - Validações: OHLC, duplicatas, missing values")
    print(f"   - Colunas obrigatórias: {data_config.required_columns}")
    
    # ========================================
    # 2. CARREGAR DADOS
    # ========================================
    print("\n📊 ETAPA 2: Carregar dados\n")
    
    csv_path = Path('data/BTCUSDT_30m_full.csv')
    
    if not csv_path.exists():
        print(f"   ❌ Arquivo não encontrado: {csv_path}")
        print(f"   💡 Certifique-se de que o CSV existe neste caminho.")
        return
    
    df = data_loader.load(csv_path, verbose=1)
    
    print(f"\n   ✅ Dados carregados: {len(df):,} samples")
    print(f"   - Colunas: {list(df.columns)}")
    print(f"   - Período: {df['Date'].min()} a {df['Date'].max()}")
    
    # ========================================
    # 3. CONFIGURAR MODELO
    # ========================================
    print("\n🤖 ETAPA 3: Configurar modelo LSTM\n")
    
    model_config = ModelConfig(
        model_type='lstm',          # Regressão para prever preço
        lookback=60,                # 30 horas (30min × 60)
        lstm_units=64,              # Neurônios LSTM (pequeno para teste rápido)
        lstm_layers=2,              # 2 camadas LSTM
        dropout=0.3,                # Dropout moderado
        learning_rate=1e-3,         # LR padrão
        batch_size=64,              # Batch size
        epochs=10,                  # Apenas 10 épocas para teste
        patience=5                  # Early stopping
    )
    
    print(f"   ✅ Configuração criada:")
    print(f"   - Tipo: {model_config.model_type}")
    print(f"   - Lookback: {model_config.lookback} períodos (30h)")
    print(f"   - LSTM units: {model_config.lstm_units}")
    print(f"   - Camadas: {model_config.lstm_layers}")
    print(f"   - Dropout: {model_config.dropout}")
    print(f"   - Épocas: {model_config.epochs} (teste rápido)")
    
    # ========================================
    # 4. CRIAR FACTORY E SERVICE
    # ========================================
    print("\n🏭 ETAPA 4: Criar Factory e TrainingService\n")
    
    # Features: todas exceto Date e Close (target)
    feature_cols = [c for c in df.columns if c not in ['Date', 'Close']]
    
    print(f"   Features selecionadas: {len(feature_cols)}")
    print(f"   - {feature_cols}")
    
    model_factory = ModelFactory()
    print("   ✅ ModelFactory criado")
    
    training_service = TrainingService(
        model_config=model_config,
        model_factory=model_factory,
        feature_cols=feature_cols,
        target_col='Close'
    )
    print("   ✅ TrainingService criado (DI injetado)")
    
    # ========================================
    # 5. TREINAR MODELO
    # ========================================
    print("\n🔥 ETAPA 5: Treinar modelo\n")
    print("   Iniciando treinamento...\n")
    
    model, history, metadata = training_service.train(
        df=df,
        validation_split=0.15,      # 15% para validação
        save_artifacts=False,       # Não salvar durante exemplo
        verbose=1                   # Mostrar progresso
    )
    
    print(f"\n   ✅ Treinamento concluído!")
    print(f"   - Épocas executadas: {len(history['loss'])}")
    print(f"   - Loss final (treino): {history['loss'][-1]:.6f}")
    print(f"   - Loss final (val): {history['val_loss'][-1]:.6f}")
    print(f"   - MAE final (val): {history['val_mae'][-1]:.6f}")
    print(f"   - Tempo de treino: {metadata['training_duration_seconds']:.2f}s")
    
    # ========================================
    # 6. SALVAR MODELO (OPCIONAL)
    # ========================================
    print("\n💾 ETAPA 6: Salvar modelo (OPCIONAL)\n")
    
    response = input("   Deseja salvar o modelo? (s/n): ").strip().lower()
    
    if response == 's':
        persistence = ModelPersistence(base_dir='artifacts/v3/checkpoints')
        
        model_path = persistence.save_model(
            model=model,
            model_name='lstm_v3_example',
            metadata=metadata
        )
        
        print(f"\n   ✅ Modelo salvo: {model_path}")
        print(f"   ✅ Metadata salvo: {model_path.replace('.keras', '_metadata.json')}")
    else:
        print("   ℹ️  Modelo não foi salvo")
    
    # ========================================
    # RESUMO FINAL
    # ========================================
    print("\n" + "="*80)
    print("✅ EXECUÇÃO v3 CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print("\n📋 Resumo:")
    print(f"   - Dados: {len(df):,} samples")
    print(f"   - Features: {len(feature_cols)}")
    print(f"   - Modelo: LSTM ({model_config.lstm_units} units, {model_config.lstm_layers} layers)")
    print(f"   - Épocas: {len(history['loss'])}")
    print(f"   - MAE final: {history['val_mae'][-1]:.6f}")
    print(f"   - Tempo: {metadata['training_duration_seconds']:.2f}s")
    
    print("\n🎯 Próximos passos:")
    print("   1. Treinar mais épocas: alterar model_config.epochs")
    print("   2. Testar classificador: model_config.model_type='directional'")
    print("   3. Usar CLI completo: python -m src.ml_v3_arch.cli train --csv data/...")
    print("   4. Consultar guia: _doc/V3_EXECUTION_GUIDE.md")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
