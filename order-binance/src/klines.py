import ccxt
import pandas as pd
from datetime import datetime
from constants import api_key, api_secret

# Inicialize a exchange Binance
binance = ccxt.binance(
    {
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
    }
)

# Definindo o par de negociação e o intervalo
symbol = 'BTC/USDT'
timeframe = '1m'

# Obtendo dados de velas (limitado a 500 velas por chamada)
ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=binance.parse8601('2024-01-01T00:00:00Z'))

# Convertendo para DataFrame
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')


# salvar em um arquivo CSV
df.to_csv('data/ohlcv2.csv', index=False, sep=';')

print(df.head())
