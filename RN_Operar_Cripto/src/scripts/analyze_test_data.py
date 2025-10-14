import pandas as pd

df = pd.read_csv('data/BTCUSDT_30m.csv')

print('='*70)
print('ANÁLISE DO PROBLEMA DE DATA LEAKAGE')
print('='*70)

print('\nPERÍODO DE TREINO (70%):')
print(f'De: {df.iloc[0]["Date"]} a {df.iloc[24548]["Date"]}')
print(f'Preço Min: ${df.iloc[:24548]["Close"].min():,.2f}')
print(f'Preço Max: ${df.iloc[:24548]["Close"].max():,.2f}')
print(f'Preço Médio: ${df.iloc[:24548]["Close"].mean():,.2f}')

print('\nPERÍODO DE TESTE (15%):')
print(f'De: {df.iloc[29818]["Date"]} a {df.iloc[-1]["Date"]}')
print(f'Preço Min: ${df.iloc[29818:]["Close"].min():,.2f}')
print(f'Preço Max: ${df.iloc[29818:]["Close"].max():,.2f}')
print(f'Preço Médio: ${df.iloc[29818:]["Close"].mean():,.2f}')

print('\n' + '='*70)
print('CONCLUSÃO:')
print('='*70)
print('O modelo foi treinado com BTC em ~$27k-$44k')
print('Mas está sendo testado com BTC em ~$90k-$108k')
print('Isso é uma MUDANÇA DRÁSTICA de preço (4x maior!)')
print('\nPor isso:')
print('1. As previsões anteriores (38.48% ao ano) eram INVÁLIDAS')
print('2. O modelo estava vendo dados que já conhecia (data leakage)')
print('3. Agora com dados reais de teste: 0 operações, 0% retorno')
