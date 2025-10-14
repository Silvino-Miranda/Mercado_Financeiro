# Robô de Trading - Clean Architecture

## 🏗️ Descrição
Sistema de trading automatizado desenvolvido seguindo os princípios da Clean Architecture. Implementa um robô para operações em criptomoedas com separação clara de responsabilidades, facilitando manutenção e testes.

## 🎯 Objetivo
Criar um sistema de trading robusto e escalável, aplicando conceitos de arquitetura limpa para garantir código organizados, testável e de fácil manutenção.

## 🛠️ Funcionalidades

### Arquitetura Limpa
- **Entities**: Modelos de domínio (Position)
- **Use Cases**: Regras de negócio (Trade Strategy, Calculate Quantity)
- **Interface Adapters**: Repositórios e adaptadores
- **Frameworks & Drivers**: Integração com exchanges (Binance)

### Trading Automatizado
- **Análise Técnica**: Indicadores em tempo real
- **Execução de Ordens**: Compra e venda automática
- **Gestão de Posições**: Controle de portfólio
- **Monitoramento Contínuo**: Loop de execução 24/7

### Integração com Binance
- **API Real**: Conexão com Binance via python-binance
- **CCXT Support**: Alternativa com CCXT
- **Dados em Tempo Real**: Klines e book de ofertas
- **Execução de Ordens**: Market e limit orders

## 📁 Estrutura do Projeto (Clean Architecture)
```
robo_cripto_clean_arch/
├── src/
│   ├── main.py                             # Ponto de entrada
│   ├── entities/                           # Camada de Entidades
│   │   ├── __init__.py
│   │   └── position.py                     # Entidade Position
│   ├── use_cases/                          # Camada de Casos de Uso
│   │   ├── __init__.py
│   │   ├── trade_strategy.py               # Estratégia de trading
│   │   └── calculate_quantity.py           # Cálculo de quantidade
│   ├── interface_adapters/                 # Camada de Adaptadores
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── position_repository.py      # Repositório de posições
│   └── frameworks_drivers/                 # Camada Externa
│       ├── __init__.py
│       ├── binance_client.py               # Cliente Binance
│       ├── binance_client_ccxt.py          # Cliente CCXT
│       └── order.py                        # Execução de ordens
├── data/                                   # Dados persistidos
├── requirements.txt                        # Dependências
└── README.md                              # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Configuração da API Binance
Configure suas credenciais da Binance (recomenda-se usar variáveis de ambiente):
```python
# Em binance_client.py
API_KEY = "sua_api_key"
API_SECRET = "sua_api_secret"
```

### 3. Execução do Robô
```bash
cd src
python main.py
```

### 4. Monitoramento
O robô executará continuamente:
- Análise de dados a cada minuto
- Execução de estratégias automaticamente
- Logs de atividades no console

## 🏗️ Camadas da Arquitetura

### 1. Entities (Entidades)
```python
# entities/position.py
class Position:
    def __init__(self, symbol, quantity, side):
        self.symbol = symbol
        self.quantity = quantity
        self.side = side  # 'BUY' or 'SELL'
        self.timestamp = datetime.now()
```

### 2. Use Cases (Casos de Uso)
```python
# use_cases/trade_strategy.py
def trade_strategy(client, data, symbol, asset_name, quantity, position):
    # Implementa lógica de trading
    # Retorna nova posição baseada na análise
```

### 3. Interface Adapters (Adaptadores)
```python
# interface_adapters/repositories/position_repository.py
class PositionRepository:
    def save(self, position):
        # Persiste posição
    
    def get_current_position(self, symbol):
        # Recupera posição atual
```

### 4. Frameworks & Drivers (Externa)
```python
# frameworks_drivers/binance_client.py
binance_client = Client(api_key, api_secret)
```

## 🔧 Principais Dependências
- `python-binance`: API oficial da Binance
- `ccxt`: Biblioteca multi-exchange (alternativa)
- `pandas`: Manipulação de dados
- `numpy`: Cálculos numéricos

## 📊 Fluxo de Execução

### Loop Principal
```python
while True:
    # 1. Buscar dados de mercado
    data = fetch_data(binance_client, symbol, interval)
    
    # 2. Calcular quantidade disponível
    quantity = calculate_quantity_available(symbol)
    
    # 3. Executar estratégia de trading
    if quantity:
        position = trade_strategy(binance_client, data, symbol, 
                                asset_name, quantity, position)
    
    # 4. Aguardar próximo ciclo
    time.sleep(60)
```

### Estratégia de Trading
1. **Análise Técnica**: Cálculo de indicadores
2. **Tomada de Decisão**: Baseada em sinais
3. **Execução de Ordem**: Se critérios atendidos
4. **Atualização de Posição**: Registro da operação

## ⚙️ Configurações do Sistema

### Parâmetros de Trading
```python
symbol = "BTCUSDT"           # Par de trading
asset_name = "BTC"           # Nome do ativo
interval = Client.KLINE_INTERVAL_1HOUR  # Timeframe
position = False             # Estado inicial
```

### Configurações de Risco
- **Quantidade Mínima**: Baseada no saldo disponível
- **Stop Loss**: Implementado na estratégia
- **Take Profit**: Definido por indicadores
- **Timeout**: 60 segundos entre análises

## 🔒 Gestão de Riscos

### Validações Implementadas
- **Saldo Disponível**: Verificação antes de operar
- **Quantidade Mínima**: Respeitando limites da exchange
- **Posição Existente**: Evitando overtrading
- **Conexão API**: Tratamento de erros de rede

### Logs e Monitoramento
```python
print("Iniciando Robô de Trade")
print(f"Analisando {symbol}...")
print(f"Quantidade disponível: {quantity}")
print(f"Nova posição: {position}")
```

## 🧪 Testes

### Estrutura de Testes
```python
# Exemplo de teste para use case
def test_trade_strategy():
    # Arrange
    mock_data = create_mock_market_data()
    
    # Act
    result = trade_strategy(mock_client, mock_data, "BTCUSDT", 
                          "BTC", 0.001, False)
    
    # Assert
    assert result is not None
```

### Mocks e Stubs
- Mock da API da Binance
- Dados de mercado simulados
- Repositórios em memória

## 🔄 Padrões Utilizados

### Repository Pattern
```python
class PositionRepository:
    def __init__(self):
        self._positions = {}
    
    def save(self, position):
        self._positions[position.symbol] = position
```

### Dependency Injection
```python
def trade_strategy(client, data, symbol, asset_name, quantity, position):
    # Cliente injetado como dependência
    repository = PositionRepository()
    # ...
```

### Strategy Pattern
- Diferentes estratégias de trading
- Fácil adição de novos algoritmos
- Configuração dinâmica

## 📈 Indicadores Implementados
- **Médias Móveis**: SMA, EMA
- **RSI**: Força relativa
- **MACD**: Convergência/divergência
- **Volume**: Análise de volume
- **Support/Resistance**: Níveis chave

## ⚠️ Avisos Importantes
- **Ambiente de Teste**: Use sandbox primeiro
- **Gestão de Capital**: Nunca arrisque mais do que pode perder
- **Monitoramento**: Acompanhe o robô constantemente
- **Backup**: Mantenha backup das configurações

## 🎯 Casos de Uso
- **Trading Automatizado**: Operações 24/7
- **Backtesting**: Validação de estratégias
- **Gestão de Portfolio**: Múltiplos ativos
- **Educação**: Aprendizado de arquitetura limpa

## 🔮 Melhorias Futuras
- [ ] Interface web para configuração
- [ ] Múltiplas estratégias simultâneas
- [ ] Integração com outras exchanges
- [ ] Sistema de notificações
- [ ] Dashboard de monitoramento
- [ ] Testes automatizados completos

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Novas estratégias de trading
- Melhorias na arquitetura
- Testes automatizados
- Documentação adicional
- Integrações com outras exchanges

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.