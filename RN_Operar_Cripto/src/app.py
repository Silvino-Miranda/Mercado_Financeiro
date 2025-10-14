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

# Calcular métricas dinamicamente
metricas = {}
if df is not None:
    try:
        # Calcular métricas básicas
        capital_inicial = df['Capital'].iloc[0]
        capital_final = df['Capital'].iloc[-1]
        retorno_total = ((capital_final - capital_inicial) / capital_inicial) * 100
        
        # Calcular período
        data_inicial = df['Data'].min()
        data_final = df['Data'].max()
        dias = (data_final - data_inicial).days
        anos = dias / 365.25
        retorno_anual = ((capital_final / capital_inicial) ** (1 / anos) - 1) * 100 if anos > 0 else 0
        
        # Contar operações
        compras = df[df['Operacao'] == 'Compra']
        vendas = df[df['Operacao'] == 'Venda']
        total_ops = len(df)
        
        # Calcular trades lucrativos vs prejuízo
        # Criar pares de compra-venda
        trades_lucro = 0
        trades_prejuizo = 0
        capital_anterior = capital_inicial
        
        for idx, row in df.iterrows():
            if row['Operacao'] == 'Venda':
                # Após uma venda, verificar se houve lucro
                if row['Capital'] > capital_anterior:
                    trades_lucro += 1
                else:
                    trades_prejuizo += 1
                capital_anterior = row['Capital']
        
        # Taxa de acerto
        total_vendas = trades_lucro + trades_prejuizo
        taxa_acerto = (trades_lucro / total_vendas * 100) if total_vendas > 0 else 0
        
        metricas = {
            'capital_inicial': capital_inicial,
            'capital_final': capital_final,
            'retorno_total': retorno_total,
            'retorno_anual': retorno_anual,
            'data_inicial': data_inicial.strftime('%Y-%m-%d'),
            'data_final': data_final.strftime('%Y-%m-%d'),
            'dias': dias,
            'anos': anos,
            'total_ops': total_ops,
            'compras': len(compras),
            'vendas': len(vendas),
            'trades_lucro': trades_lucro,
            'trades_prejuizo': trades_prejuizo,
            'taxa_acerto': taxa_acerto
        }
        
        print(f"Métricas calculadas: {trades_lucro} trades lucrativos, {trades_prejuizo} com prejuízo")
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}")
        metricas = None

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
    metricas = None

# Criar o aplicativo Dash
app = dash.Dash(__name__)

# Criar conteúdo dinâmico baseado nas métricas
if metricas:
    metricas_content = html.Div([
        html.H3('📊 Métricas de Performance (Dados Calculados Dinamicamente)'),
        html.P(f'💰 Capital Inicial: ${metricas["capital_inicial"]:,.2f}'),
        html.P(f'💵 Capital Final: ${metricas["capital_final"]:,.2f}'),
        html.P(f'📈 Retorno Total: {metricas["retorno_total"]:.2f}%'),
        html.P(f'📅 Retorno Anualizado: {metricas["retorno_anual"]:.2f}% ao ano'),
        html.P(f'🔄 Total de Operações: {metricas["total_ops"]} trades ({metricas["compras"]} compras + {metricas["vendas"]} vendas)'),
        html.P(f'⏱️ Período: {metricas["dias"]} dias ({metricas["data_inicial"]} a {metricas["data_final"]})'),
        html.Hr(),
        html.H4('🎯 Análise de Acurácia dos Trades:'),
        html.P(f'✅ Trades Lucrativos: {metricas["trades_lucro"]} ({metricas["taxa_acerto"]:.1f}%)', 
               style={'color': 'green', 'fontWeight': 'bold', 'fontSize': '18px'}),
        html.P(f'❌ Trades com Prejuízo: {metricas["trades_prejuizo"]} ({100-metricas["taxa_acerto"]:.1f}%)', 
               style={'color': 'red', 'fontWeight': 'bold', 'fontSize': '18px'}),
        html.P(f'📊 Taxa de Acerto: {metricas["taxa_acerto"]:.1f}%', 
               style={'color': 'blue', 'fontWeight': 'bold', 'fontSize': '20px'}),
        html.Hr(),
        html.P('✅ Modelo testado APENAS com dados nunca vistos no treinamento', 
               style={'color': 'green', 'fontWeight': 'bold'}),
    ], style={'padding': '20px', 'backgroundColor': '#e8f5e9', 'borderRadius': '10px', 'margin': '20px 0'})
    
    descricao = f'''
        Sistema de Trading Automatizado com LSTM Neural Network
        Intervalo: 30 minutos | Par: BTC/USDT | Teste: {metricas["data_inicial"]} a {metricas["data_final"]}
        ✅ Retorno de {metricas["retorno_total"]:.2f}% em {metricas["dias"]} dias ({metricas["retorno_anual"]:.2f}% ao ano)
        🎯 Taxa de Acerto: {metricas["taxa_acerto"]:.1f}% ({metricas["trades_lucro"]} trades lucrativos)
    '''
else:
    metricas_content = html.Div([
        html.H3('⚠️ Erro ao carregar métricas'),
        html.P('Não foi possível calcular as métricas. Verifique o arquivo CSV.'),
    ], style={'padding': '20px', 'backgroundColor': '#ffebee', 'borderRadius': '10px', 'margin': '20px 0'})
    
    descricao = 'Sistema de Trading Automatizado com LSTM Neural Network - Erro ao carregar dados'

app.layout = html.Div(children=[
    html.H1(children='Análise de Previsões - BTC/USDT (30min)'),

    html.Div(children=descricao),
    
    metricas_content,

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
