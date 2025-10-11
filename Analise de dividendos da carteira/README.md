# Análise de Dividendos da Carteira

## 📊 Descrição
Sistema para análise de dividendos recebidos em carteira de investimentos brasileiros. Calcula yield sobre preço histórico e atual, oferecendo insights sobre a rentabilidade dos dividendos em diferentes períodos.

## 🎯 Objetivo
Permitir aos investidores analisar a rentabilidade dos dividendos recebidos, comparando o yield histórico (baseado no preço na data do pagamento) com o yield atual, facilitando decisões de investimento.

## 🛠️ Funcionalidades

### Análise de Dividendos
- **Carregamento de Dados**: Importa dados de dividendos de arquivo Excel
- **Busca de Preços Históricos**: Obtém preços das ações na data do pagamento via Yahoo Finance
- **Cálculo de Yield**: Calcula dividend yield histórico e atual
- **Análise Comparativa**: Compara rentabilidade entre diferentes ativos
- **Dados B3**: Suporte completo para ações da Bolsa Brasileira (B3)

### Métricas Calculadas
- Yield sobre preço histórico (data do pagamento)
- Yield sobre preço atual
- Valor total de dividendos por ativo
- Comparação de rentabilidade entre períodos

## 📁 Estrutura do Projeto
```
Analise de dividendos da carteira/
├── src/
│   └── main.py                 # Script principal de análise
├── requirements.txt            # Dependências do projeto
├── Dividendos.xlsx            # Arquivo de dados (exemplo)
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Preparação dos Dados
Crie um arquivo Excel (`Dividendos.xlsx`) com as seguintes colunas:
- **Ativo**: Código da ação (ex: PETR4, VALE3)
- **Data Pagamento**: Data do pagamento do dividendo
- **Valor**: Valor do dividendo recebido
- **Quantidade**: Quantidade de ações

### 3. Execução
```bash
cd src
python main.py
```

### 4. Análise dos Resultados
O sistema irá:
- Buscar preços históricos automaticamente
- Calcular yields por ativo
- Exibir relatório comparativo
- Identificar melhores e piores performances

## 📊 Exemplo de Saída
```
Análise de Dividendos - Relatório
================================
PETR4:
  - Dividendos Totais: R$ 1.250,00
  - Yield Histórico: 8,5%
  - Yield Atual: 12,3%

VALE3:
  - Dividendos Totais: R$ 2.100,00
  - Yield Histórico: 6,2%
  - Yield Atual: 9,8%
```

## 🔧 Principais Dependências
- `pandas`: Manipulação de dados e análise
- `yfinance`: Coleta de dados financeiros da B3
- `openpyxl`: Leitura de arquivos Excel
- `datetime`: Manipulação de datas

## 📈 Funcionalidades Técnicas

### Busca de Preços
- Integração com Yahoo Finance para dados da B3
- Tratamento automático de feriados e fins de semana
- Busca em janela de tempo para máxima precisão
- Fallback para preços próximos quando data exata não disponível

### Tratamento de Dados
- Validação automática de tickers da B3
- Conversão de formatos de data
- Tratamento de erros de conexão
- Limpeza e normalização de dados

## ⚠️ Observações Importantes
- Os dados são obtidos do Yahoo Finance e podem ter delays
- Certifique-se de que os códigos das ações estão corretos
- O sistema adiciona automaticamente ".SA" para ações da B3
- Recomenda-se verificar dados críticos manualmente

## 🎯 Casos de Uso
- **Análise de Carteira**: Avaliar performance de dividendos
- **Tomada de Decisão**: Identificar ações com melhores yields
- **Planejamento Fiscal**: Organizar dados para declaração IR
- **Relatórios**: Gerar relatórios periódicos de dividendos

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de melhoria:
- Interface gráfica para visualização
- Exportação para diferentes formatos
- Análise de tendências temporais
- Integração com outras fontes de dados

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
