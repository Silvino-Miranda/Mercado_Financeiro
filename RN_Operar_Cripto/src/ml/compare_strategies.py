"""
Compare Strategies
Executa backtesting com todas as estratégias ativas e compara os resultados
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml.data.data_loader import DataLoader
from src.ml.utils.data_preprocessing import DataPreprocessor
from src.ml.models.lstm_model import LSTMModel
from src.ml.backtesting.backtester import Backtester
from src.ml.backtesting.strategy_config import StrategyConfig
from src.ml.backtesting.my_strategy import MyStrategy
import pandas as pd
from datetime import datetime


def run_strategy(strategy, df_test, model):
    """
    Executa backtesting para uma estratégia específica
    
    Args:
        strategy: Objeto Strategy com configuração
        df_test: DataFrame com dados de teste
        model: Modelo LSTM treinado
        
    Returns:
        Tuple (final_capital, trades_count, results_dict)
    """
    print(f"\n{'='*70}")
    print(f"▶️  Executando: {strategy.name}")
    print(f"{'='*70}")
    print(f"TP: {strategy.parameters.profit_target*100:.2f}% | "
          f"SL: {strategy.parameters.stop_loss*100:.2f}% | "
          f"Threshold: {strategy.parameters.prediction_threshold*100:.2f}%")
    
    # Preparar DataFrame para backtester
    df_bt = df_test.copy()
    df_bt.rename(columns={'Date': 'datetime'}, inplace=True)
    df_bt['open'] = df_bt['close']  # Usar close como open para simplificar
    df_bt['high'] = df_bt['close']
    df_bt['low'] = df_bt['close']
    df_bt['volume'] = 0.0  # Volume não disponível
    
    # Criar estratégia configurada
    strategy_class = MyStrategy.from_strategy_config(strategy)
    
    # Executar backtesting
    initial_capital = 100000.0
    backtester = Backtester(initial_capital=initial_capital)
    backtester.add_data(df_bt)
    backtester.add_strategy(strategy_class)
    final_capital = backtester.run()
    
    # Salvar histórico com nome da estratégia
    output_file = Path("src/ml/outputs") / f"capital_history-{strategy.name.replace(' ', '_')}.csv"
    backtester.save_capital_history(str(output_file))
    
    # Coletar estatísticas
    history = backtester.get_trade_history()
    
    if history:
        trades_df = pd.DataFrame(history)
        compras = len(trades_df[trades_df['Operacao'] == 'Compra'])
        vendas = len(trades_df[trades_df['Operacao'] == 'Venda'])
        total_trades = len(trades_df)
        
        # Calcular retorno
        initial_capital = 100000.0
        return_pct = ((final_capital - initial_capital) / initial_capital) * 100
        
        # Calcular dias e retorno anualizado
        if not trades_df.empty:
            first_date = pd.to_datetime(trades_df['Data'].iloc[0])
            last_date = pd.to_datetime(trades_df['Data'].iloc[-1])
            days = (last_date - first_date).days
            years = days / 365.25
            annual_return = ((final_capital / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        else:
            days = 0
            annual_return = 0
    else:
        compras = vendas = total_trades = days = 0
        return_pct = 0
        annual_return = 0
    
    results = {
        'strategy_id': strategy.id,
        'strategy_name': strategy.name,
        'initial_capital': 100000.0,
        'final_capital': final_capital,
        'return_pct': return_pct,
        'annual_return': annual_return,
        'total_trades': total_trades,
        'compras': compras,
        'vendas': vendas,
        'days': days,
        'profit_target': strategy.parameters.profit_target,
        'stop_loss': strategy.parameters.stop_loss,
        'stake_percentage': strategy.parameters.stake_percentage,
        'prediction_threshold': strategy.parameters.prediction_threshold,
        'hold_periods': strategy.parameters.hold_periods
    }
    
    print(f"\n✅ Resultado:")
    print(f"   Capital Final: ${final_capital:,.2f}")
    print(f"   Retorno: {return_pct:.2f}%")
    print(f"   Retorno Anualizado: {annual_return:.2f}%")
    print(f"   Total de Trades: {total_trades}")
    print(f"   Período: {days} dias")
    
    return final_capital, total_trades, results


def main():
    print("\n🚀 COMPARADOR DE ESTRATÉGIAS - LSTM Trading Bot")
    print("="*70)
    
    # 1. Carregar configuração de estratégias
    print("\n📋 Carregando estratégias...")
    config = StrategyConfig()
    strategies = config.get_active_strategies()
    
    print(f"✅ {len(strategies)} estratégias ativas encontradas:")
    for s in strategies:
        print(f"   • {s.name} (TP: {s.parameters.profit_target*100:.1f}%)")
    
    # 2. Carregar dados de teste
    print("\n📊 Carregando dados de teste...")
    symbol = "BTCUSDT"
    interval = "30m"
    
    data_loader = DataLoader(
        symbol=symbol,
        interval=interval,
        use_local_file=True,
        local_filename="BTCUSDT_30m_full.csv"
    )
    df = data_loader.load_data()
    
    # Definir features (MESMAS do treinamento)
    feature_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "SMA_20",
        "EMA_20",
    ]
    
    target_columns = ["Open", "High", "Low"]
    
    print("Iniciando o preprocessamento dos dados...")
    preprocessor = DataPreprocessor(
        feature_columns=feature_columns,
        target_columns=target_columns,
        sequence_length=60
    )
    
    X, Y, dates = preprocessor.fit_transform(df)
    
    # Usar apenas dados de TESTE (últimos 15%)
    # Split: 70% treino, 15% validação, 15% teste
    val_end = int(len(X) * (0.70 + 0.15))
    X_test = X[val_end:]
    Y_test = Y[val_end:]
    dates_test = dates[val_end:]
    
    print(f"✅ Dados de teste: {len(X_test)} sequências")
    print(f"   Período: {dates_test[0]} a {dates_test[-1]}")
    
    # 3. Carregar modelo treinado
    print("\n🤖 Carregando modelo LSTM...")
    model_path = "src/ml/checkpoints/lstm_model.keras"
    model = LSTMModel(
        input_shape=(X_test.shape[1], X_test.shape[2]),
        output_size=3,  # Close, High, Low
        model_path=model_path
    )
    print("✅ Modelo carregado")
    
    # 4. Gerar previsões
    print("\n🔮 Gerando previsões...")
    predictions = model.predict(X_test)
    
    # Desnormalizar
    predictions_denorm = preprocessor.scaler.inverse_transform(predictions)
    actual_denorm = preprocessor.scaler.inverse_transform(Y_test)
    
    # Preparar DataFrame para backtesting
    start_idx = val_end + 60
    end_idx = len(df)
    df_extracted = df.iloc[start_idx:end_idx].copy()
    df_extracted = df_extracted.reset_index(drop=True)
    
    df_extracted['actual'] = actual_denorm[:, 0]  # Close price
    df_extracted['prediction'] = predictions_denorm[:, 0]  # Close price prediction
    
    df_test = df_extracted[['Date', 'Close', 'actual', 'prediction']].copy()
    df_test.rename(columns={'Close': 'close'}, inplace=True)
    
    print(f"✅ DataFrame preparado: {len(df_test)} linhas")
    
    # 5. Executar backtesting para cada estratégia
    print("\n" + "="*70)
    print("🔄 EXECUTANDO BACKTESTING PARA TODAS AS ESTRATÉGIAS")
    print("="*70)
    
    all_results = []
    
    for strategy in strategies:
        try:
            final_capital, total_trades, results = run_strategy(strategy, df_test, model)
            all_results.append(results)
        except Exception as e:
            print(f"\n❌ Erro ao executar estratégia {strategy.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 6. Comparar resultados
    print("\n" + "="*70)
    print("📊 COMPARAÇÃO DE RESULTADOS")
    print("="*70)
    
    if not all_results:
        print("❌ Nenhum resultado para comparar")
        return
    
    results_df = pd.DataFrame(all_results)
    results_df = results_df.sort_values('final_capital', ascending=False)
    
    # Salvar comparação
    output_file = "src/ml/outputs/strategies_comparison.csv"
    results_df.to_csv(output_file, index=False, sep=';', decimal=',')
    print(f"\n✅ Comparação salva em: {output_file}")
    
    # Exibir ranking
    print("\n🏆 RANKING DE ESTRATÉGIAS (Por Capital Final)")
    print("="*70)
    
    for idx, row in results_df.iterrows():
        rank = idx + 1 if idx == results_df.index[0] else len(results_df) - idx + 1
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}º"
        
        print(f"\n{medal} {row['strategy_name']}")
        print(f"   Capital Final: ${row['final_capital']:,.2f}")
        print(f"   Retorno: {row['return_pct']:.2f}% ({row['annual_return']:.2f}% ao ano)")
        print(f"   Trades: {row['total_trades']} em {row['days']} dias")
        print(f"   Parâmetros: TP={row['profit_target']*100:.1f}% | "
              f"SL={row['stop_loss']*100:.1f}% | "
              f"Threshold={row['prediction_threshold']*100:.2f}%")
    
    # Melhor estratégia
    best = results_df.iloc[0]
    print("\n" + "="*70)
    print(f"🎯 MELHOR ESTRATÉGIA: {best['strategy_name']}")
    print("="*70)
    print(f"Capital Final: ${best['final_capital']:,.2f}")
    print(f"Retorno Total: {best['return_pct']:.2f}%")
    print(f"Retorno Anualizado: {best['annual_return']:.2f}%")
    print(f"Total de Trades: {best['total_trades']}")
    
    print("\n✅ Comparação concluída!")


if __name__ == "__main__":
    main()
