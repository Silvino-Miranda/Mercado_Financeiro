import pandas as pd
import numpy as np

print('='*70)
print('PREPARANDO NOVA BASE DE DADOS COM INDICADORES TÉCNICOS')
print('='*70)

# Carregar dados
print('\n1. Carregando BTCUSDT_30m_full.csv...')
df = pd.read_csv('data/BTCUSDT_30m_full.csv')
print(f'   ✅ {len(df):,} registros carregados')
print(f'   📅 Período: {df["Date"].min()} a {df["Date"].max()}')

# Converter Date para datetime
df['Date'] = pd.to_datetime(df['Date'])

print('\n2. Calculando indicadores técnicos...')

# SMA (Simple Moving Average) - 20 períodos
df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
print('   ✅ SMA_20 calculado')

# EMA (Exponential Moving Average) - 20 períodos
df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
print('   ✅ EMA_20 calculado')

print('\n3. Removendo NaN dos indicadores...')
initial_rows = len(df)
df = df.dropna(subset=['SMA_20', 'EMA_20'])
removed = initial_rows - len(df)
print(f'   ✅ {removed} linhas removidas com NaN')
print(f'   ✅ {len(df):,} linhas restantes')

print('\n4. Validando dados finais...')
print(f'   Colunas: {df.columns.tolist()}')
print(f'   Total de NaN: {df.isnull().sum().sum()}')
print(f'   Preço Close - Min: ${df["Close"].min():,.2f} | Max: ${df["Close"].max():,.2f}')

print('\n5. Salvando nova base preparada...')
output_file = 'data/BTCUSDT_30m_prepared.csv'
df.to_csv(output_file, index=False)
print(f'   ✅ Arquivo salvo: {output_file}')

print('\n6. Amostra dos dados preparados:')
print(df[['Date', 'Close', 'SMA_20', 'EMA_20']].head(10).to_string())

print('\n' + '='*70)
print('✅ PREPARAÇÃO CONCLUÍDA COM SUCESSO!')
print('='*70)
print(f'Arquivo pronto para treinamento: {output_file}')
print(f'Total de registros: {len(df):,}')
print(f'Período: {df["Date"].min()} a {df["Date"].max()}')
duration_days = (df['Date'].max() - df['Date'].min()).days
print(f'Duração: {duration_days} dias ({duration_days/365.25:.2f} anos)')
