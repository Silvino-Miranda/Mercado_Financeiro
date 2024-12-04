import pandas as pd
import yfinance as yf
from datetime import timedelta

# Carregar os dados do arquivo .xlsx
file_path = 'Dividendos.xlsx'  # Substitua pelo caminho correto do arquivo
df = pd.read_excel(file_path)

# Função para buscar o preço mais próximo da data usando Yahoo Finance
def get_closest_price(ticker, date, days_before=5):
    try:
        stock = yf.Ticker(ticker + ".SA")  # Adicionando ".SA" para os tickers da B3
        # Buscar um intervalo de datas ao redor da data fornecida (5 dias antes e 5 dias depois)
        start_date = pd.to_datetime(date) - timedelta(days=days_before)
        end_date = pd.to_datetime(date) + timedelta(days=days_before)
        historical_data = stock.history(start=start_date, end=end_date)
        if not historical_data.empty:
            # Acessar o último preço disponível usando iloc
            return historical_data['Close'].iloc[-1]
        else:
            print(f"Sem dados históricos para {ticker} entre {start_date} e {end_date}")
            return None
    except Exception as e:
        print(f"Erro ao buscar o preço para {ticker} em torno da data {date}: {e}")
        return None


# Adicionar uma coluna para os preços atuais com base na Data Pagamento
df['Preço Atual'] = df.apply(lambda row: get_closest_price(row['Ativo'], row['Data Pagamento']), axis=1)

# Remover linhas sem preço atual (caso não seja possível obter o preço)
df = df.dropna(subset=['Preço Atual'])

# Calcular o Yield on Cost (YoC)
df['YoC'] = df['Valor do Dividendo'] / df['Preço Atual'] * 100

# Ordenar pelo YoC do maior para o menor
df_sorted = df.sort_values(by='YoC', ascending=False)

# Calcular a média de YoC por ativo
df_avg_yoc = df.groupby('Ativo')['YoC'].mean()

# Ordenar a média de YoC do maior para o menor
df_avg_yoc = df_avg_yoc.sort_values(ascending=False)

# Exibir o DataFrame final ordenado e a média de YoC por ativo
print("DataFrame Ordenado por YoC:")
print(df_sorted)

print("\nMédia de YoC por Ativo:")
print(df_avg_yoc)

# Opcional: salvar os resultados em um novo arquivo Excel
# df_sorted.to_excel('ativos_ordenados_por_yoc.xlsx', index=False)
# df_avg_yoc.to_excel('media_yoc_por_ativo.xlsx')
