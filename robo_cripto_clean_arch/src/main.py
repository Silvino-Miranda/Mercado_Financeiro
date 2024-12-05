# main.py
import time
from binance.client import Client
from frameworks_drivers.binance_client import binance_client
from use_cases.calculate_quantity import calculate_quantity_available
from use_cases.trade_strategy import fetch_data, trade_strategy

symbol = "BTCUSDT"
asset_name = "BTC"
interval = Client.KLINE_INTERVAL_1HOUR
position = False

print("Iniciando Robô de Trade")

while True:
    data = fetch_data(binance_client, symbol, interval)
    quantity = calculate_quantity_available(symbol)
    
    if quantity:
        position = trade_strategy(binance_client, data, symbol, asset_name, quantity, position)
    
    time.sleep(60)