import pandas as pd

# Carregar a nova base de dados
df = pd.read_csv('data/BTCUSDT_30m_full.csv')

print('='*70)
print('ANÁLISE DA NOVA BASE DE DADOS: BTCUSDT_30m_full.csv')
print('='*70)

print(f'\n📊 INFORMAÇÕES GERAIS:')
print(f'Total de registros: {len(df):,}')
print(f'Período: {df["Date"].min()} a {df["Date"].max()}')

# Calcular duração
df['Date'] = pd.to_datetime(df['Date'])
duration_days = (df['Date'].max() - df['Date'].min()).days
duration_years = duration_days / 365.25
print(f'Duração: {duration_days} dias ({duration_years:.2f} anos)')

print(f'\n📋 COLUNAS DISPONÍVEIS ({len(df.columns)}):\n{df.columns.tolist()}')

print(f'\n💰 ESTATÍSTICAS DO PREÇO (Close):')
print(f'Mínimo: ${df["Close"].min():,.2f}')
print(f'Máximo: ${df["Close"].max():,.2f}')
print(f'Média: ${df["Close"].mean():,.2f}')
print(f'Mediana: ${df["Close"].median():,.2f}')

print(f'\n⚠️ VALORES FALTANTES POR COLUNA:')
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100
for col in df.columns:
    if missing[col] > 0:
        print(f'  {col}: {missing[col]} ({missing_percent[col]:.2f}%)')
    else:
        print(f'  {col}: 0 (OK)')

print(f'\n📈 PRIMEIRAS 5 LINHAS:')
print(df.head().to_string())

print(f'\n📉 ÚLTIMAS 5 LINHAS:')
print(df.tail().to_string())

print(f'\n✅ Análise concluída!')
