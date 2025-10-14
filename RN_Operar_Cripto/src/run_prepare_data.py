# prepare_data.py
# Script para preparar e adicionar indicadores técnicos aos dados

import pandas as pd
import os
import sys
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.data.indicator import IndicatorCalculator
from config import DATA_CONFIG


def prepare_btcusdt_data(force_recalculate=False, auto_confirm=False):
    """
    Prepara o arquivo BTCUSDT_30m.csv:
    1. Faz backup do CSV original
    2. Calcula TODOS os indicadores técnicos
    3. Valida se todos foram calculados corretamente
    4. Salva CSV com indicadores
    
    Args:
        force_recalculate: Se True, recalcula sem perguntar
        auto_confirm: Se True, confirma automaticamente todas as perguntas
    """
    filepath = os.path.join(DATA_CONFIG["data_dir"], DATA_CONFIG["local_filename"])
    
    print("=" * 70)
    print("🚀 PREPARAÇÃO DOS DADOS - BTC/USDT 30min")
    print("=" * 70)
    
    # 1. VERIFICAR SE ARQUIVO EXISTE
    if not os.path.exists(filepath):
        print(f"\n❌ Erro: Arquivo não encontrado!")
        print(f"   Esperado: {filepath}")
        return False
    
    # 2. CARREGAR DADOS
    print(f"\n� Carregando dados de {filepath}...")
    try:
        df = pd.read_csv(filepath, sep=';' if ';' in open(filepath).readline() else ',')
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return False
    
    print(f"✅ Dados carregados: {len(df):,} registros")
    
    if 'Date' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"📅 Período: {df['Date'].iloc[0]} até {df['Date'].iloc[-1]}")
        except:
            pass
    
    # 3. VERIFICAR COLUNAS NECESSÁRIAS
    required_cols = ['Open', 'High', 'Low', 'Close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"\n❌ Colunas obrigatórias faltando: {missing_cols}")
        print(f"   Colunas disponíveis: {df.columns.tolist()}")
        return False
    
    # Volume é opcional, mas importante
    has_volume = 'Volume' in df.columns
    if not has_volume:
        print(f"\n⚠️  Coluna 'Volume' não encontrada")
        print(f"   Alguns indicadores de volume não poderão ser calculados")
        # Criar coluna Volume com zeros
        df['Volume'] = 0
    
    print(f"\n✅ Colunas OHLC presentes" + (" + Volume" if has_volume else " (sem Volume)"))
    print(f"📊 Total de colunas atuais: {len(df.columns)}")
    
    # 4. VERIFICAR SE JÁ TEM INDICADORES
    calculator = IndicatorCalculator(df)
    existing_indicators = [col for col in df.columns if col not in ['Date'] + required_cols]
    
    if len(existing_indicators) > 0 and not force_recalculate:
        print(f"\n⚠️  Arquivo já possui {len(existing_indicators)} indicadores:")
        for ind in existing_indicators[:10]:
            print(f"   - {ind}")
        if len(existing_indicators) > 10:
            print(f"   ... e mais {len(existing_indicators) - 10}")
        
        if not auto_confirm:
            response = input("\n🔄 Recalcular todos os indicadores? (s/N): ").strip().lower()
            if response != 's':
                print("\n✅ Mantendo indicadores existentes.")
                return True
        else:
            print("\n🔄 Modo automático: Recalculando indicadores...")
        
        # Remover indicadores antigos
        df = df[['Date'] + required_cols if 'Date' in df.columns else required_cols]
        print(f"🧹 Indicadores antigos removidos. Recalculando...")
    
    # 5. CRIAR BACKUP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.replace('.csv', f'_backup_{timestamp}.csv')
    
    print(f"\n💾 Criando backup em:")
    print(f"   {backup_path}")
    
    try:
        # Salvar backup do arquivo original (antes de calcular indicadores)
        original_df = pd.read_csv(filepath, sep=';' if ';' in open(filepath).readline() else ',')
        original_df.to_csv(backup_path, index=False)
        print(f"✅ Backup criado com sucesso!")
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível criar backup: {e}")
    
    # 6. CALCULAR INDICADORES
    print("\n" + "=" * 70)
    print("� CALCULANDO INDICADORES TÉCNICOS")
    print("=" * 70)
    
    try:
        df = calculator.calculate_indicators()
    except Exception as e:
        print(f"\n❌ Erro ao calcular indicadores: {e}")
        return False
    
    # 7. VALIDAR INDICADORES
    print("\n" + "=" * 70)
    print("🔍 VALIDAÇÃO DOS INDICADORES")
    print("=" * 70)
    
    validation = calculator.validate_indicators()
    
    if validation['has_errors']:
        print(f"\n⚠️  Alguns indicadores têm problemas!")
        print(f"   Considere investigar antes de continuar.")
        
        if not auto_confirm:
            response = input("\n💾 Salvar mesmo assim? (s/N): ").strip().lower()
            if response != 's':
                print("\n❌ Salvamento cancelado.")
                return False
        else:
            print("\n💾 Modo automático: Salvando mesmo assim...")
    
    # 8. REMOVER NaNs (opcional)
    rows_before = len(df)
    df_clean = df.dropna()
    rows_after = len(df_clean)
    rows_removed = rows_before - rows_after
    
    if rows_removed > 0:
        print(f"\n🧹 NaNs encontrados:")
        print(f"   Total de linhas: {rows_before:,}")
        print(f"   Linhas com NaN: {rows_removed:,} ({rows_removed/rows_before*100:.1f}%)")
        print(f"   Linhas limpas: {rows_after:,}")
        
        if not auto_confirm:
            response = input("\n🧹 Remover linhas com NaN? (S/n): ").strip().lower()
            if response != 'n':
                df = df_clean
                print(f"✅ NaNs removidos!")
        else:
            df = df_clean
            print(f"✅ Modo automático: NaNs removidos!")
    
    # 9. SALVAR CSV COM INDICADORES
    print("\n" + "=" * 70)
    print("💾 SALVANDO ARQUIVO COM INDICADORES")
    print("=" * 70)
    
    print(f"\n📄 Salvando em: {filepath}")
    print(f"📊 Total de linhas: {len(df):,}")
    print(f"📊 Total de colunas: {len(df.columns)}")
    
    try:
        df.to_csv(filepath, index=False)
        print(f"\n✅ Arquivo salvo com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao salvar: {e}")
        return False
    
    # 10. RESUMO FINAL
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL")
    print("=" * 70)
    
    print(f"\n✅ Arquivo preparado: {filepath}")
    print(f"📦 Backup criado: {backup_path}")
    print(f"📊 Registros: {len(df):,}")
    print(f"📊 Indicadores: {validation['total_indicators']}")
    print(f"\n🎯 Indicadores principais:")
    
    important = ['RSI_14', 'MACD', 'BB_High', 'BB_Low', 'ATR_14', 'OBV', 'ADX', 'SMA_20', 'EMA_20']
    for ind in important:
        if ind in df.columns:
            print(f"   ✅ {ind}")
        else:
            print(f"   ❌ {ind} (faltando)")
    
    print(f"\n📋 Colunas no arquivo:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepara dados com indicadores técnicos')
    parser.add_argument('--force', action='store_true', help='Força recálculo sem perguntar')
    parser.add_argument('--auto', action='store_true', help='Modo automático (confirma tudo)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("PREPARAÇÃO DOS DADOS - BTC/USDT 30min")
    print("=" * 60)
    
    success = prepare_btcusdt_data(
        force_recalculate=args.force,
        auto_confirm=args.auto
    )
    
    if success:
        print("\n" + "=" * 60)
        print("✅ DADOS PREPARADOS COM SUCESSO!")
        print("=" * 60)
        print("\nAgora você pode executar:")
        print("  - uv run python src/ml/train_balanced.py  (treinar modelo)")
        print("  - uv run python src/ml/main_predict.py (fazer previsões)")
    else:
        print("\n❌ Falha na preparação dos dados.")
