# prepare_data.py
# Script para preparar e adicionar indicadores técnicos aos dados

import pandas as pd
import os
from src.data.indicator import IndicatorCalculator
from config import DATA_CONFIG


def prepare_btcusdt_data():
    """
    Prepara o arquivo BTCUSDT_30m.csv adicionando indicadores técnicos se necessário
    """
    filepath = os.path.join(DATA_CONFIG["data_dir"], DATA_CONFIG["local_filename"])
    
    if not os.path.exists(filepath):
        print(f"❌ Erro: Arquivo {filepath} não encontrado!")
        return False
    
    # Carregar dados
    print(f"📊 Carregando dados de {filepath}...")
    df = pd.read_csv(filepath)
    print(f"✅ Dados carregados: {len(df)} registros")
    print(f"📅 Período: {df['Date'].iloc[0]} até {df['Date'].iloc[-1]}")
    print(f"\nColunas existentes: {df.columns.tolist()}")
    
    # Verificar se os indicadores já existem
    indicators = ['SMA_20', 'EMA_20', 'RSI_14', 'MACD', 'BB_High', 'BB_Low', 'Stoch', 'OBV']
    missing_indicators = [ind for ind in indicators if ind not in df.columns]
    
    if missing_indicators:
        print(f"\n⚠️  Indicadores faltantes: {missing_indicators}")
        print("🔧 Calculando indicadores técnicos...")
        
        # Calcular indicadores
        calculator = IndicatorCalculator(df)
        df = calculator.calculate_indicators()
        
        # Salvar arquivo atualizado
        backup_path = filepath.replace('.csv', '_backup.csv')
        print(f"\n💾 Criando backup em: {backup_path}")
        df.to_csv(backup_path, index=False)
        
        print(f"💾 Salvando dados com indicadores em: {filepath}")
        df.to_csv(filepath, index=False)
        print("✅ Indicadores adicionados e arquivo atualizado!")
    else:
        print("\n✅ Todos os indicadores técnicos já estão presentes!")
    
    # Exibir estatísticas
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS DOS DADOS")
    print("=" * 60)
    print(f"Total de registros: {len(df)}")
    print("Valores nulos por coluna:")
    print(df.isnull().sum())
    print("\nPrimeiros registros:")
    print(df.head())
    print("\nÚltimos registros:")
    print(df.tail())
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("PREPARAÇÃO DOS DADOS - BTC/USDT 30min")
    print("=" * 60)
    success = prepare_btcusdt_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ DADOS PREPARADOS COM SUCESSO!")
        print("=" * 60)
        print("\nAgora você pode executar:")
        print("  - python src/main_train.py  (para treinar o modelo)")
        print("  - python src/main_predict.py (para fazer previsões)")
    else:
        print("\n❌ Falha na preparação dos dados.")
