# Sistema de Backtest Dollar-Cost Averaging (DCA)

## 💰 Descrição
Sistema de backtest para estratégia Dollar-Cost Averaging (DCA) em criptomoedas. Simula investimentos periódicos e regulares, calculando a performance desta estratégia passiva de longo prazo em diferentes ativos digitais.

## 🎯 Objetivo
Avaliar a eficácia da estratégia DCA em criptomoedas, demonstrando como investimentos regulares e disciplinados podem gerar retornos consistentes ao longo do tempo, independentemente da volatilidade do mercado.

## 🛠️ Funcionalidades

### Estratégia DCA
- **Investimento Regular**: Valor fixo em intervalos regulares
- **Média de Preços**: Redução do impacto da volatilidade
- **Disciplina Automatizada**: Eliminação de timing do mercado
- **Acumulação Progressiva**: Construção gradual de posição

### Análise de Performance
- **Múltiplos Ativos**: Suporte para diferentes criptomoedas
- **Métricas de Retorno**: Cálculo de lucro percentual
- **Comparação Temporal**: Análise de diferentes períodos
- **Visualização Gráfica**: Gráficos comparativos de performance

### Simulação Realística
- **Dados Históricos**: Preços reais do mercado
- **Flexibilidade Temporal**: Períodos customizáveis
- **Múltiplas Frequências**: Diário, semanal, mensal
- **Tratamento de Dados**: Limpeza e preparação automática

## 📁 Estrutura do Projeto
```
Dollar-Cost_Averaging_DCA/
├── src/
│   ├── main.py                 # Script principal
│   ├── backtest_dca.py         # Classe de backtest DCA
│   ├── DataHandler.py          # Manipulação de dados
│   ├── main.ipynb             # Notebook Jupyter
│   └── data/                   # Dados processados
├── data/
│   └── BTC-USD_2010-01-01_to_2024-12-01_1d.csv
├── load.ipynb                  # Notebook de carregamento
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Preparação dos Dados
Os dados já estão incluídos, mas você pode adicionar novos ativos:
```python
# Formato esperado do CSV
# Date,Open,High,Low,Close,Volume
```

### 3. Configuração do Backtest
No arquivo `main.py`, configure os ativos:
```python
tickers = ["BTC-USD"]  # Adicione mais ativos se desejar
```

### 4. Execução
```bash
cd src
python main.py
```

### 5. Análise dos Resultados
- Tabela comparativa de performance
- Gráfico de barras com lucros percentuais
- Métricas detalhadas por ativo

## 📊 Exemplo de Saída
```
Resultados do Backtest DCA
=========================
ticker       profit_percent    total_invested    final_value
BTC-USD           1,247.5%        $10,000        $134,750
```

## 🔧 Principais Dependências
- `pandas`: Manipulação de dados financeiros
- `matplotlib`: Visualização de resultados
- `numpy`: Cálculos numéricos (implícito)

## 📈 Classe BacktestDCA

### Inicialização
```python
class BacktestDCA:
    def __init__(self, ticker, file_path=None):
        self.ticker = ticker
        self.file_path = file_path
        self.data = None
        self.results = {}
```

### Métodos Principais
- **load_data()**: Carregamento de dados históricos
- **run_backtest()**: Execução da simulação DCA
- **get_results()**: Obtenção de métricas finais

### Configurações Padrão
```python
# Parâmetros típicos de DCA
investment_amount = 100      # Valor por compra
frequency = "monthly"        # Frequência de compra
start_date = "2020-01-01"   # Data inicial
end_date = "2024-01-01"     # Data final
```

## ⚙️ Estratégia DCA Implementada

### Funcionamento
1. **Investimento Regular**: Mesmo valor todo período
2. **Compra Automática**: Independente do preço
3. **Acumulação**: Aumento gradual da posição
4. **Média Ponderada**: Preço médio de compra

### Vantagens da Estratégia
- **Redução de Risco**: Menor impacto da volatilidade
- **Disciplina**: Elimina emoções do investimento
- **Simplicidade**: Fácil implementação e manutenção
- **Acessibilidade**: Não requer timing de mercado

### Métricas Calculadas
- **Investimento Total**: Soma de todos os aportes
- **Valor Final**: Valor da carteira no final
- **Lucro Absoluto**: Diferença entre valor final e investido
- **Lucro Percentual**: Retorno sobre o investimento

## 📊 Análise de Resultados

### Interpretação dos Dados
- **Profit > 0%**: Estratégia rentável
- **Comparação entre Ativos**: Identificação dos melhores
- **Período de Análise**: Impacto do timing na performance
- **Volatilidade**: Benefício da estratégia DCA

### Visualização
```python
plt.figure(figsize=(12, 8))
plt.bar(results_df["ticker"], results_df["profit_percent"])
plt.xlabel("Ativo")
plt.ylabel("Lucro (%)")
plt.title("Comparação DCA por Ativo")
```

## 🔄 Fluxo de Execução
1. **Carregamento**: Importação de dados históricos
2. **Configuração**: Definição de parâmetros DCA
3. **Simulação**: Execução compra a compra
4. **Cálculo**: Métricas de performance
5. **Visualização**: Gráficos e tabelas
6. **Comparação**: Ranking de ativos

## 📈 Cenários de Teste

### Período Bull Market
- Mercado em alta: DCA pode ter performance inferior ao lump sum
- Benefício: Redução de risco de timing

### Período Bear Market
- Mercado em baixa: DCA oferece proteção
- Vantagem: Compras a preços menores

### Mercado Volátil
- Alta volatilidade: Máximo benefício do DCA
- Resultado: Preço médio mais favorável

## ⚠️ Considerações Importantes
- **Performance Passada**: Não garante resultados futuros
- **Custos de Transação**: Não incluídos na simulação
- **Disciplina**: Sucesso depende de consistência
- **Horizon Temporal**: Estratégia de longo prazo

## 🎯 Casos de Uso
- **Investidor Iniciante**: Estratégia simples e efetiva
- **Aposentadoria**: Construção de patrimônio de longo prazo
- **Redução de Risco**: Minimização de impacto da volatilidade
- **Automação**: Investimento sistemático e disciplinado

## 🔮 Melhorias Futuras
- [ ] Integração com APIs de exchanges
- [ ] Cálculo de custos de transação
- [ ] Diferentes frequências de investimento
- [ ] Análise de correlação entre ativos
- [ ] Interface web interativa

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novos algoritmos de DCA
- Métricas de risco adicionais
- Visualizações avançadas
- Otimização de parâmetros

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.