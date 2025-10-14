# Robô de Trading Criptomoedas

## 🤖 Descrição
Sistema de trading automatizado para criptomoedas utilizando a API da Binance. Implementa estratégias de trading baseadas em análise técnica com execução automática de ordens de compra e venda.

## 🎯 Objetivo
Criar um robô de trading que opere de forma autônoma no mercado de criptomoedas, executando estratégias predefinidas com gestão de risco integrada e monitoramento contínuo.

## 🛠️ Funcionalidades

### Trading Automatizado
- **Execução de Ordens**: Compra e venda automática via Binance
- **Análise Técnica**: Indicadores para tomada de decisão
- **Gestão de Posições**: Controle de entrada e saída
- **Monitoramento 24/7**: Operação contínua

### Integração com APIs
- **Binance API**: Conexão oficial via python-binance
- **CCXT**: Suporte alternativo multi-exchange
- **Dados em Tempo Real**: Preços e volume atualizados
- **Execução de Ordens**: Market e limit orders

### Sistema de Repositório
- **Persistência de Dados**: Armazenamento de operações
- **Histórico de Trades**: Registro completo
- **Configurações**: Parâmetros salvos
- **Logs de Sistema**: Monitoramento de atividades

## 📁 Estrutura do Projeto
```
robo_cripto/
├── src/
│   ├── robo_cripto.py              # Robô principal
│   ├── robo_cripto_old.py          # Versão anterior
│   ├── Order.py                    # Classe de ordem
│   ├── calcular_quantidade_venda.py # Cálculo de quantidades
│   ├── models/                     # Modelos de dados
│   ├── repository/                 # Camada de persistência
│   └── utils/                      # Utilitários
├── data/                           # Dados persistidos
├── requirements.txt                # Dependências
└── README.md                      # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração das Variáveis de Ambiente
```bash
# Configure as variáveis de ambiente
export KEY_BINANCE="sua_api_key"
export SECRET_BINANCE="sua_api_secret"
```

### 3. Configuração da API Binance
- Crie uma conta na Binance
- Gere suas chaves API
- Configure permissões apenas para trading
- Adicione seu IP à whitelist

### 4. Execução do Robô
```bash
cd src
python robo_cripto.py
```

## 🔧 Principais Dependências
- `python-binance`: API oficial da Binance
- `ccxt`: Biblioteca multi-exchange
- `pandas`: Manipulação de dados
- `numpy`: Cálculos numéricos
- `time`: Controle de tempo e loops

## 📊 Funcionalidades Principais

### Coleta de Dados
```python
def pegando_dados(codigo, intervalo):
    # Coleta dados históricos via Binance
    # Retorna DataFrame com OHLCV
```

### Análise Técnica
- **Médias Móveis**: SMA e EMA
- **RSI**: Força relativa
- **MACD**: Convergência/divergência
- **Bollinger Bands**: Bandas de volatilidade
- **Volume**: Análise de volume

### Execução de Ordens
```python
# Ordem de compra
order = cliente_binance2.create_market_buy_order(
    symbol='BTCUSDT',
    amount=quantity
)

# Ordem de venda
order = cliente_binance2.create_market_sell_order(
    symbol='BTCUSDT',
    amount=quantity
)
```

## ⚙️ Configurações do Sistema

### Parâmetros de Trading
- **Symbol**: Par de negociação (ex: BTCUSDT)
- **Intervalo**: Timeframe dos dados
- **Quantidade**: Volume por operação
- **Stop Loss**: Limitação de perdas
- **Take Profit**: Realização de lucros

### Filtros de Negociação
```python
# Exemplo de configuração
symbol_info = cliente_binance.get_symbol_info('BTCUSDT')
lot_size_filter = next(f for f in symbol_info['filters'] 
                      if f['filterType'] == 'LOT_SIZE')
min_qty = float(lot_size_filter['minQty'])
```

## 🔒 Gestão de Riscos

### Validações Implementadas
- **Saldo Disponível**: Verificação antes de operar
- **Quantidade Mínima**: Respeitando limites da exchange
- **Posição Máxima**: Evitando overexposure
- **Timeouts**: Proteção contra falhas de rede

### Stop Loss e Take Profit
- **Stop Loss Dinâmico**: Ajuste conforme volatilidade
- **Take Profit Escalonado**: Realizações parciais
- **Trailing Stop**: Proteção de lucros
- **Emergency Stop**: Parada de emergência

## 📈 Estratégias Implementadas

### Estratégia de Médias Móveis
- Cruzamento de médias para sinais
- Confirmação com volume
- Filtros de tendência

### Estratégia de Reversão à Média
- RSI para identificar extremos
- Bollinger Bands para confirmação
- Entrada em reversões

### Arbitragem
- Identificação de oportunidades
- Execução simultânea
- Gestão de spreads

## 🔄 Fluxo de Execução

### Loop Principal
```python
while True:
    # 1. Coletar dados de mercado
    dados = pegando_dados(symbol, interval)
    
    # 2. Calcular indicadores
    indicadores = calcular_indicadores(dados)
    
    # 3. Analisar sinais
    sinal = analisar_sinais(indicadores)
    
    # 4. Executar ordem se necessário
    if sinal:
        executar_ordem(sinal)
    
    # 5. Aguardar próximo ciclo
    time.sleep(60)
```

## 📊 Monitoramento e Logs

### Sistema de Logs
- **Execução de Ordens**: Registro detalhado
- **Análise Técnica**: Valores de indicadores
- **Erros e Exceções**: Tratamento de falhas
- **Performance**: Métricas de resultado

### Métricas de Acompanhamento
- **P&L**: Lucros e perdas
- **Win Rate**: Taxa de acerto
- **Drawdown**: Perda máxima
- **Sharpe Ratio**: Relação risco-retorno

## 🛡️ Segurança

### Boas Práticas
- **API Keys**: Armazenamento seguro
- **Permissões Limitadas**: Apenas trading
- **IP Whitelist**: Restrição de acesso
- **Rate Limiting**: Controle de requisições

### Tratamento de Erros
- **Reconexão Automática**: Em caso de falha
- **Validação de Dados**: Verificação de integridade
- **Backup de Ordens**: Registro local
- **Notificações**: Alertas de problemas

## ⚠️ Avisos Importantes
- **Teste em Sandbox**: Use ambiente de teste primeiro
- **Capital de Risco**: Nunca arrisque mais do que pode perder
- **Monitoramento**: Acompanhe o robô constantemente
- **Volatilidade**: Criptomoedas são ativos voláteis

## 🎯 Casos de Uso
- **Day Trading**: Operações intraday automatizadas
- **Swing Trading**: Posições de médio prazo
- **Market Making**: Provisão de liquidez
- **Arbitragem**: Exploração de diferenças de preço

## 🔮 Melhorias Futuras
- [ ] Interface web para monitoramento
- [ ] Múltiplas estratégias simultâneas
- [ ] Machine learning para otimização
- [ ] Integração com Telegram/Discord
- [ ] Backtesting avançado
- [ ] Análise de sentimento

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novas estratégias de trading
- Melhorias na gestão de risco
- Otimização de performance
- Interfaces de usuário
- Documentação adicional

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.