# Sistema Automatizado de Ordens Binance

## 🤖 Descrição
Sistema automatizado para execução de ordens de compra na exchange Binance. Permite investimentos programados em múltiplas criptomoedas com relatórios detalhados de execução e controle de valores em reais (BRL).

## 🎯 Objetivo
Automatizar o processo de investimento em criptomoedas na Binance, permitindo diversificação automática da carteira através de compras programadas com relatórios de acompanhamento.

## 🛠️ Funcionalidades

### Execução Automatizada
- **Ordens de Mercado**: Compras instantâneas ao preço atual
- **Múltiplas Criptomoedas**: Suporte a diversos pares de trading
- **Controle de Valor**: Investimento em BRL com conversão automática
- **Validação de Saldo**: Verificação prévia de fundos disponíveis

### Relatórios Detalhados
- **Registro de Execução**: Log completo de todas as operações
- **Análise de Preços**: Histórico de preços de execução
- **Status de Ordens**: Confirmação de execução
- **Relatórios JSON**: Estrutura organizada para análise

### Gestão de Carteira
- **Diversificação Automática**: Distribuição entre ativos
- **Controle de Riscos**: Limites por operação
- **Histórico Completo**: Rastreamento de todas as compras
- **Análise de Performance**: Métricas de acompanhamento

## 📁 Estrutura do Projeto
```
order-binance/
├── src/
│   ├── main.py                 # Script principal
│   ├── Order.py                # Classe de ordem
│   ├── Report.py               # Geração de relatórios
│   ├── klines.py               # Dados de candlestick
│   └── constants.py            # Configurações e chaves API
├── data/
│   └── crypto_list.json        # Lista de criptomoedas
├── requirements.txt            # Dependências
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Pré-requisitos
- Conta na Binance com API habilitada
- Saldo em USDT ou BRL na carteira spot
- Python 3.8+

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração da API
No arquivo `constants.py`, configure suas credenciais:
```python
api_key = "sua_api_key_aqui"
api_secret = "sua_api_secret_aqui"
```

### 4. Configuração dos Ativos
Edite o arquivo `data/crypto_list.json`:
```json
{
    "cryptos": [
        {
            "symbol": "BTCUSDT",
            "amount_brl": 100.0
        },
        {
            "symbol": "ETHUSDT", 
            "amount_brl": 50.0
        }
    ]
}
```

### 5. Execução
```bash
cd src
python main.py
```

## 📊 Exemplo de Configuração

### Arquivo crypto_list.json
```json
{
    "cryptos": [
        {
            "symbol": "BTCUSDT",
            "amount_brl": 200.0,
            "active": true
        },
        {
            "symbol": "ETHUSDT",
            "amount_brl": 150.0,
            "active": true
        },
        {
            "symbol": "ADAUSDT",
            "amount_brl": 100.0,
            "active": false
        }
    ]
}
```

## 🔧 Principais Dependências
- `ccxt`: Biblioteca para integração com exchanges
- `json`: Manipulação de dados de configuração
- Módulos customizados para ordem e relatórios

## 📈 Classe Order

### Inicialização
```python
class Order:
    def __init__(self, binance, symbol, amount_brl):
        self.binance = binance      # Cliente da exchange
        self.symbol = symbol        # Par de trading
        self.amount_brl = amount_brl # Valor em reais
        self.status = None          # Status da ordem
```

### Métodos Principais
- **execute()**: Execução da ordem de compra
- **validate_balance()**: Validação de saldo disponível
- **calculate_quantity()**: Cálculo da quantidade a comprar
- **get_current_price()**: Obtenção do preço atual

### Fluxo de Execução
1. **Validação**: Verificação de saldo e parâmetros
2. **Cálculo**: Quantidade baseada no valor em BRL
3. **Execução**: Ordem de mercado na Binance
4. **Confirmação**: Validação do status da ordem
5. **Relatório**: Geração de log da operação

## 📊 Classe Report

### Geração de Relatórios
```python
class Report:
    @staticmethod
    def save(order):
        # Salva relatório da ordem executada
        report_data = {
            "timestamp": datetime.now(),
            "symbol": order.symbol,
            "amount_brl": order.amount_brl,
            "quantity": order.quantity,
            "price": order.execution_price,
            "status": order.status
        }
```

### Informações Incluídas
- **Timestamp**: Data e hora da execução
- **Symbol**: Par de trading
- **Amount BRL**: Valor investido em reais
- **Quantity**: Quantidade de cripto comprada
- **Price**: Preço de execução
- **Fees**: Taxas cobradas
- **Status**: Sucesso/Erro da operação

## ⚙️ Configurações Avançadas

### Parâmetros de Ordem
```python
# Tipo de ordem
order_type = "market"

# Validações
min_notional = 10.0  # Valor mínimo em USDT
max_amount = 1000.0  # Valor máximo por ordem

# Timeouts
connection_timeout = 30
order_timeout = 60
```

### Tratamento de Erros
- **Saldo Insuficiente**: Verificação prévia
- **Conexão**: Retry automático
- **API Limits**: Controle de rate limiting
- **Ordens Parciais**: Tratamento de execução parcial

## 🔐 Segurança

### Boas Práticas
- **API Keys**: Mantenha em ambiente seguro
- **Permissões**: Apenas trading (sem withdraw)
- **IP Whitelist**: Configure na Binance
- **Logs**: Monitore todas as execuções

### Variáveis de Ambiente
```bash
export BINANCE_API_KEY="sua_api_key"
export BINANCE_API_SECRET="sua_api_secret"
```

## 📊 Monitoramento

### Logs de Execução
```
[2024-10-11 10:30:15] INFO: Iniciando compra de BTCUSDT
[2024-10-11 10:30:16] INFO: Saldo USDT: $1,500.00
[2024-10-11 10:30:17] INFO: Preço atual BTC: $67,500.00
[2024-10-11 10:30:18] SUCCESS: Ordem executada - 0.00148 BTC
[2024-10-11 10:30:19] INFO: Relatório salvo
```

### Métricas de Acompanhamento
- **Taxa de Sucesso**: Ordens executadas vs. tentativas
- **Slippage**: Diferença entre preço esperado e executado
- **Tempo de Execução**: Latência das operações
- **Custos**: Total de taxas pagas

## 🎯 Casos de Uso

### DCA Automatizado
- Investimento regular em criptomoedas
- Redução do impacto da volatilidade
- Disciplina de investimento

### Diversificação de Carteira
- Distribuição automática entre ativos
- Rebalanceamento periódico
- Gestão de riscos

### Trading Sistemático
- Execução de estratégias predefinidas
- Eliminação de emoções
- Backtesting de estratégias

## ⚠️ Avisos Importantes
- **Teste em Sandbox**: Use o ambiente de teste primeiro
- **Valores Pequenos**: Comece com valores baixos
- **Monitoramento**: Acompanhe as execuções
- **Backup de Chaves**: Mantenha suas API keys seguras
- **Não é Aconselhamento**: Sistema para fins educacionais

## 🔮 Melhorias Futuras
- [ ] Interface web para configuração
- [ ] Estratégias de DCA avançadas
- [ ] Integração com outras exchanges
- [ ] Notificações via email/Telegram
- [ ] Análise de performance em tempo real
- [ ] Stop loss e take profit

## 🤝 Contribuições
Contribuições são bem-vindas! Áreas de interesse:
- Melhorias na interface
- Novas estratégias de trading
- Integrações com outras exchanges
- Ferramentas de análise
- Melhorias de segurança

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.