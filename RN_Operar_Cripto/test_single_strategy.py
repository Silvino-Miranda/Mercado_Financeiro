"""
Test Single Strategy
Testa apenas UMA estratégia para validar o sistema
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ml.data.data_loader import DataLoader
from src.ml.utils.data_preprocessing import DataPreprocessor
from src.ml.models.lstm_model import LSTMModel
from src.ml.backtesting.backtester import Backtester
from src.ml.backtesting.strategy_config import StrategyConfig
from src.ml.backtesting.my_strategy import MyStrategy


def main():
    print("\n🚀 TESTE DE UMA ESTRATÉGIA")
    print("="*70)
    
    # 1. Carregar estratégia
    print("\n📋 Carregando estratégia...")
    config = StrategyConfig()
    strategy = config.get_strategy_by_name("Moderada TP 2%")
    print(f"✅ Estratégia selecionada: {strategy.name}")
    print(f"   TP: {strategy.parameters.profit_target*100:.1f}% | SL: {strategy.parameters.stop_loss*100:.1f}%")
    
    # 2. Carregar dados
    print("\n📊 Carregando dados...")
    data_loader = DataLoader(
        symbol="BTCUSDT",
        interval="30m",
        use_local_file=True,
        local_filename="BTCUSDT_30m_full.csv"
    )
    df = data_loader.load_data()
    
    # 3. Preprocessar
    print("\n⚙️ Preprocessando dados...")
    feature_columns = ["Open", "High", "Low", "Close", "SMA_20", "EMA_20"]
    target_columns = ["Open", "High", "Low"]
    
    preprocessor = DataPreprocessor(
        feature_columns=feature_columns,
        target_columns=target_columns,
        sequence_length=60
    )
    
    X, Y, dates = preprocessor.fit_transform(df)
    
    # Usar apenas dados de TESTE (últimos 15%)
    val_end = int(len(X) * 0.85)
    X_test = X[val_end:]
    Y_test = Y[val_end:]
    dates_test = dates[val_end:]
    
    print(f"✅ Dados de teste: {len(X_test)} sequências")
    
    # 4. Carregar modelo
    print("\n🤖 Carregando modelo...")
    model = LSTMModel(
        input_shape=(X_test.shape[1], X_test.shape[2]),
        output_size=3,
        model_path="src/ml/checkpoints/lstm_model.keras"
    )
    print("✅ Modelo carregado")
    
    # 5. Gerar previsões
    print("\n🔮 Gerando previsões...")
    predictions = model.predict(X_test)
    
    # Desnormalizar
    predictions_denorm = preprocessor.scaler.inverse_transform(predictions)
    actual_denorm = preprocessor.scaler.inverse_transform(Y_test)
    
    # Preparar DataFrame
    start_idx = val_end + 60
    end_idx = len(df)
    df_extracted = df.iloc[start_idx:end_idx].copy()
    df_extracted = df_extracted.reset_index(drop=True)
    
    df_extracted['actual'] = actual_denorm[:, 0]
    df_extracted['prediction'] = predictions_denorm[:, 0]
    
    df_test = df_extracted[['Date', 'Close', 'actual', 'prediction']].copy()
    df_test.rename(columns={'Close': 'close'}, inplace=True)
    
    print(f"✅ DataFrame preparado: {len(df_test)} linhas")
    
    # 6. Executar backtesting
    print("\n" + "="*70)
    print(f"▶️  EXECUTANDO BACKTESTING: {strategy.name}")
    print("="*70)
    
    # Criar estratégia configurada
    strategy_class = MyStrategy.from_strategy_config(strategy)
    
    # Executar backtesting
    backtester = Backtester(
        df=df_test,
        model=model,
        strategy=strategy_class,
        initial_cash=100000.0
    )
    
    final_capital = backtester.run()
    
    # Salvar histórico
    output_file = f"src/ml/outputs/test_{strategy.name.replace(' ', '_')}.csv"
    backtester.save_history(output_file)
    
    # Resultado
    initial_capital = 100000.0
    return_pct = ((final_capital - initial_capital) / initial_capital) * 100
    
    print("\n" + "="*70)
    print("✅ RESULTADO")
    print("="*70)
    print(f"Capital Inicial: ${initial_capital:,.2f}")
    print(f"Capital Final: ${final_capital:,.2f}")
    print(f"Retorno: {return_pct:.2f}%")
    print(f"\nHistórico salvo em: {output_file}")
    print("\n🎯 Teste concluído com sucesso!")


if __name__ == "__main__":
    main()
