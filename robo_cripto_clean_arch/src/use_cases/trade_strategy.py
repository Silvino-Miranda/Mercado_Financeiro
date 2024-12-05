# use_cases/trade_strategy.py
import pandas as pd
from binance.enums import *

def fetch_data(client, symbol, interval):
    candles = client.get_klines(symbol=symbol, interval=interval, limit=500)
    prices = pd.DataFrame(candles)
    prices.columns = [
        "tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume",
        "tempo_fechamento", "moedas_negociadas", "numero_trades", "volume_ativo_base_compra",
        "volume_ativo_cotacao", "_"
    ]
    prices = prices[["fechamento", "tempo_fechamento"]]
    prices["fechamento"] = prices["fechamento"].astype(float)
    prices["tempo_fechamento"] = pd.to_datetime(prices["tempo_fechamento"], unit="ms").dt.tz_localize("UTC")
    prices["tempo_fechamento"] = prices["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")
    return prices

def trade_strategy(client, data, symbol, asset_name, quantity, position):
    if len(data) < 40:
        print("Dados insuficientes para calcular as médias móveis.")
        return position

    data["media_rapida"] = data["fechamento"].rolling(window=7).mean()
    data["media_devagar"] = data["fechamento"].rolling(window=40).mean()

    last_fast_avg = data["media_rapida"].iloc[-1]
    last_slow_avg = data["media_devagar"].iloc[-1]

    print(f"Última Média Rápida: {last_fast_avg} | Última Média Devagar: {last_slow_avg}")

    account = client.get_account()
    balances = account["balances"]
    current_quantity = next(
        (float(bal["free"]) for bal in balances if bal["asset"] == asset_name), 0.0
    )

    if last_fast_avg > last_slow_avg and not position:
        client.create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity)
        print("COMPROU O ATIVO")
        position = True
    elif last_fast_avg < last_slow_avg and position:
        sell_quantity = round(current_quantity, 6)
        client.create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=sell_quantity)
        print("VENDEU O ATIVO")
        position = False

    return position