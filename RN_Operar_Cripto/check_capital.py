import pandas as pd

df = pd.read_csv('capital_history-BTCUSDT.csv', sep=';')

print('='*70)
print('ANÁLISE DO CAPITAL_HISTORY-BTCUSDT.csv')
print('='*70)

print(f'\nTotal de operações: {len(df)}')

print(f'\nPrimeiras 5 linhas:')
print(df.head())

print(f'\nÚltimas 5 linhas:')
print(df.tail())

# Capital já está em formato numérico
print(f'\nCapital Inicial: ${df["Capital"].iloc[0]:,.2f}')
print(f'Capital Final: ${df["Capital"].iloc[-1]:,.2f}')

inicial = 100000
final = df['Capital'].iloc[-1]
retorno = ((final - inicial) / inicial) * 100

print(f'Retorno Total: {retorno:.2f}%')

df['Data'] = pd.to_datetime(df['Data'])
dias = (df['Data'].max() - df['Data'].min()).days
anos = dias / 365.25
retorno_anual = ((final / inicial) ** (1 / anos) - 1) * 100

print(f'\nPrimeira data: {df["Data"].iloc[0].date()}')
print(f'Última data: {df["Data"].iloc[-1].date()}')
print(f'Dias: {dias} ({anos:.2f} anos)')
print(f'Retorno Anualizado: {retorno_anual:.2f}% ao ano')

compras = df[df['Operacao'] == 'Compra']
vendas = df[df['Operacao'] == 'Venda']
print(f'\nCompras: {len(compras)}')
print(f'Vendas: {len(vendas)}')
