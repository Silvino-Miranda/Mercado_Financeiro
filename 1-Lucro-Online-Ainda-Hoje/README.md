# Sistema de Backtest para Trading de Forex

## 📈 Descrição
Sistema automatizado de backtest para estratégias de trading em pares de moedas do mercado Forex. Utiliza médias móveis exponenciais (MME) e gestão de risco baseada em relação risco/retorno para identificar oportunidades de trading.

## 🎯 Objetivo
Validar estratégias de trading através de testes históricos, permitindo avaliar a performance de diferentes configurações de parâmetros antes de aplicar em operações reais.

## 🛠️ Funcionalidades

### Estratégia de Trading
- **Indicador Principal**: Média Móvel Exponencial (MME) de 21 períodos
- **Gestão de Risco**: Relação risco/retorno de 1:2
- **Gestão de Capital**: 10% de risco por operação
### Análise e Visualização
- Cálculo de sinais de compra e venda
- Simulação de operações com stop loss e take profit
- Gráficos de evolução do saldo
- Relatórios de performance por par de moedas

## 📁 Estrutura do Projeto
```
1-Lucro-Online-Ainda-Hoje/
├── src/
│   ├── main.py                 # Script principal
│   └── utils/
│       ├── backtest.py         # Função principal de backtest
│       ├── obter_dados.py      # Coleta de dados históricos
│       ├── calcular_mme.py     # Cálculo da MME
│       ├── identificar_sinais.py # Identificação de sinais
│       └── executar_backtest.py # Execução do backtest
├── _backtest/                  # Resultados dos testes
│   └── EURUSD=X.csv           # Dados históricos
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração dos Parâmetros
No arquivo `main.py`, ajuste os parâmetros conforme necessário:
```python
MME_PERIOD = 21          # Período da MME
RISCO_RETORNO = 2        # Relação risco/retorno
TAMANHO_POSICAO = 1      # Tamanho da posição
RISK_PERCENTAGE = 0.1    # Percentual de risco
```

### 3. Execução
```bash
cd src
python main.py
```

### 4. Análise dos Resultados
- Os resultados são salvos em arquivos CSV na pasta `_backtest/`
- Gráficos de performance são exibidos automaticamente
- Métricas de saldo final e evolução temporal

## 📊 Saídas do Sistema
- **Arquivos CSV**: Histórico completo de operações e saldos
- **Gráficos**: Evolução do saldo ao longo do tempo
- **Console**: Resumo de performance por par de moedas

## 🔧 Principais Dependências
- `yfinance`: Coleta de dados financeiros
- `pandas`: Manipulação de dados
- `matplotlib`: Visualização de gráficos
- `numpy`: Cálculos numéricos

## 📈 Indicadores Utilizados
- **MME (Média Móvel Exponencial)**: Identificação de tendências
- **Stop Loss**: Limitação de perdas
- **Take Profit**: Realização de lucros
- **Gestão de Capital**: Controle de risco por operação

## ⚠️ Aviso Legal
Este sistema é destinado apenas para fins educacionais e de pesquisa. Não constitui aconselhamento financeiro. Trading de Forex envolve riscos significativos e pode resultar em perdas substanciais.

## 🤝 Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novos indicadores
- Melhorar a documentação

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
   - **Atualização Constante:** Mantenha-se informado sobre as condições macroeconômicas que afetam os pares de moedas que você negocia.
   - **Aprimoramento de Habilidades:** Invista em cursos e materiais que aprofundem seu conhecimento em análise técnica e fundamental.

9. **Teste da Estratégia:**
   - **Backtesting:** Avalie a estratégia em dados históricos para verificar sua eficácia antes de aplicá-la em tempo real.
   - **Conta Demo:** Pratique em uma conta demo para ganhar confiança sem arriscar capital real.

---

Ao incorporar essas melhorias, sua estratégia de day trade será mais sólida, aumentando suas chances de sucesso no mercado. Lembre-se de que consistência e disciplina são fundamentais para o trading eficaz.