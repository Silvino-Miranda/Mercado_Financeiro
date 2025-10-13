import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Definir o caminho para o arquivo CSV
csv_file_path = 'capital_history-BTCUSDT.csv'  # Arquivo de histórico do Bitcoin

# Carregar o arquivo CSV com tratamento de exceções
try:
    # Verificar se o arquivo contém apenas comentários
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if first_line.startswith('#'):
            print("Aviso: Nenhuma operação registrada no backtest. Arquivo vazio.")
            df = None
        else:
            df = pd.read_csv(csv_file_path, sep=';')
            print("Arquivo CSV carregado com sucesso.")
except Exception as e:
    print(f"Erro ao carregar o arquivo CSV: {e}")
    df = None

# Se o DataFrame foi carregado corretamente, prosseguir
if df is not None:
    # Pré-processamento dos dados
    try:
        # Converter a coluna 'Data' para datetime
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        
        # Converter colunas numéricas de string para float
        cols_numericas = ['Previsao', 'Valor Atual', 'Preco', 'Custo', 'Capital']
        for col in cols_numericas:
            # Remover pontos de milhares e substituir vírgulas por pontos
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = df[col].astype(float)
        print("Dados pré-processados com sucesso.")
    except Exception as e:
        print(f"Erro no pré-processamento dos dados: {e}")
        df = None

# Se o DataFrame foi pré-processado corretamente, criar a figura
if df is not None:
    try:
        fig = px.line(df, x='Data', y=['Valor Atual', 'Previsao'],
                      labels={'value': 'Preço', 'variable': 'Série', 'Data': 'Data'},
                      title='Previsão do Modelo vs. Valor Real')
        print("Figura criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar a figura: {e}")
        fig = None
else:
    # Se houve erro no carregamento ou pré-processamento, criar uma figura vazia
    fig = px.line(title='Nenhuma operação foi realizada durante o backtest')

# Criar o aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Análise de Previsões - BTC/USDT (30min)'),

    html.Div(children='''
        Comparação entre as previsões do modelo LSTM e os valores reais do Bitcoin.
        Intervalo: 30 minutos | Par: BTC/USDT
        
        Nota: A estratégia não realizou operações porque as condições de entrada não foram atingidas.
        As previsões do modelo estão consistentemente acima dos valores reais (~27,700 vs ~26,900).
    '''),

    dcc.Graph(
        id='grafico-previsoes',
        figure=fig
    )
])

if __name__ == '__main__':
    print("Iniciando o servidor Dash...")
    app.run_server(debug=True)
