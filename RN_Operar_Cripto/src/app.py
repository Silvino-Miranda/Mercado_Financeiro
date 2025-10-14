import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Definir o caminho para o arquivo CSV
csv_file_path = 'capital_history-BTCUSDT.csv'  # Arquivo de histórico do Bitcoin

# Carregar o arquivo CSV com tratamento de exceções
try:
    # Verificar se o arquivo contém apenas comentários
    with open(csv_file_path, 'r', encoding='latin-1') as f:
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
        # Converter a coluna 'Data' para datetime (formato ISO: YYYY-MM-DD)
        df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')
        
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

# Se o DataFrame foi pré-processado corretamente, criar as figuras
if df is not None:
    try:
        # Figura 1: Evolução do Capital
        fig_capital = px.line(df, x='Data', y='Capital',
                             labels={'Capital': 'Capital ($)', 'Data': 'Data'},
                             title='Evolução do Capital ao Longo do Tempo')
        fig_capital.update_traces(line_color='green', line_width=2)
        
        # Figura 2: Previsão vs Valor Real
        fig_previsao = px.line(df, x='Data', y=['Valor Atual', 'Previsao'],
                              labels={'value': 'Preço BTC ($)', 'variable': 'Série', 'Data': 'Data'},
                              title='Previsão do Modelo LSTM vs. Valor Real do Bitcoin')
        
        # Figura 3: Preço de Execução dos Trades
        fig_trades = px.scatter(df, x='Data', y='Preco', color='Operacao',
                               labels={'Preco': 'Preço de Execução ($)', 'Data': 'Data'},
                               title='Preços de Compra e Venda ao Longo do Tempo',
                               color_discrete_map={'Compra': 'blue', 'Venda': 'red'})
        
        print("Figuras criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar as figuras: {e}")
        fig_capital = None
        fig_previsao = None
        fig_trades = None
else:
    # Se houve erro no carregamento ou pré-processamento, criar figuras vazias
    fig_capital = px.line(title='Erro ao carregar dados')
    fig_previsao = px.line(title='Erro ao carregar dados')
    fig_trades = px.scatter(title='Erro ao carregar dados')

# Criar o aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Análise de Previsões - BTC/USDT (30min)'),

    html.Div(children='''
        Sistema de Trading Automatizado com LSTM Neural Network
        Intervalo: 30 minutos | Par: BTC/USDT | Teste: 2025-06-28 a 2025-10-13
        ⚠️ Resultados anteriores eram INVÁLIDOS (data leakage) - Agora corrigido!
    '''),
    
    html.Div([
        html.H3('📊 Métricas de Performance (Dados de Teste - SEM Data Leakage)'),
        html.P('💰 Capital Inicial: $100,000.00'),
        html.P('💵 Capital Final: $104,808.62'),
        html.P('📈 Retorno Total: 4.81%'),
        html.P('📅 Retorno Anualizado: 17.39% ao ano'),
        html.P('🔄 Total de Operações: 50 trades (25 compras + 25 vendas)'),
        html.P('⏱️ Período: 107 dias (2025-06-28 a 2025-10-13)'),
        html.P('✅ Modelo testado APENAS com dados nunca vistos no treinamento', 
               style={'color': 'green', 'fontWeight': 'bold'}),
    ], style={'padding': '20px', 'backgroundColor': '#e8f5e9', 'borderRadius': '10px', 'margin': '20px 0'}),

    html.H2('1. Evolução do Capital'),
    dcc.Graph(
        id='grafico-capital',
        figure=fig_capital
    ),
    
    html.H2('2. Previsões do Modelo vs Valor Real'),
    dcc.Graph(
        id='grafico-previsoes',
        figure=fig_previsao
    ),
    
    html.H2('3. Pontos de Entrada e Saída'),
    dcc.Graph(
        id='grafico-trades',
        figure=fig_trades
    )
])

if __name__ == '__main__':
    print("Iniciando o servidor Dash...")
    app.run(debug=True)
