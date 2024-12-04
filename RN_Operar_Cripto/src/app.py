import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Definir o caminho para o arquivo CSV
csv_file_path = 'capital_history-petr4.sa.csv'  # Substitua pelo caminho correto

# Carregar o arquivo CSV com tratamento de exceções
try:
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
    fig = px.line(title='Erro ao carregar ou processar os dados')

# Criar o aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Análise de Previsões'),

    html.Div(children='''
        Comparação entre as previsões do modelo e os valores reais.
    '''),

    dcc.Graph(
        id='grafico-previsoes',
        figure=fig
    )
])

if __name__ == '__main__':
    print("Iniciando o servidor Dash...")
    app.run_server(debug=True)
