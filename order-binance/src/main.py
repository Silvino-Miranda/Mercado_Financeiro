import ccxt
import json
from Order import Order
from Report import Report
from constants import api_key, api_secret

# Carregue suas credenciais de API da Binance


dataPath = "data/crypto_list.json"

# Inicialize a exchange Binance
binance = ccxt.binance(
    {
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
    }
)
# Carregue a lista de criptos do arquivo JSON
with open(dataPath, 'r') as file:
    data = json.load(file)

# Para cada cripto na lista, execute a compra e gere um relatório
for crypto in data['cryptos']:
    order = Order(binance, crypto['symbol'], crypto['amount_brl'])
    if crypto['amount_brl'] > 0 :
        if order.execute():
            Report.save(order)
