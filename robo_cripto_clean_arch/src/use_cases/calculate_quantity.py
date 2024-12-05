# use_cases/calculate_quantity.py
import os
from dotenv import load_dotenv
from frameworks_drivers.binance_client_ccxt import binance_client_ccxt

load_dotenv()

def calculate_quantity_available(symbol):
    balance = binance_client_ccxt.fetch_balance()
    usdt_balance = float(balance["USDT"]["free"])

    if usdt_balance <= 0.0:
        print(f"Saldo insuficiente. Saldo disponível: {usdt_balance} USDT")
        return False

    ticker = binance_client_ccxt.fetch_ticker(symbol)
    price = ticker["last"]

    amount_crypto = usdt_balance / price
    amount_crypto = binance_client_ccxt.amount_to_precision(symbol, amount_crypto)
    amount_crypto = float(amount_crypto)

    print(f"Quantidade de {symbol} a ser comprada: {amount_crypto}")
    return amount_crypto