# frameworks_drivers/binance_client.py
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

binance_client_ccxt = ccxt.binance(
    {
        "apiKey": api_key,
        "secret": secret_key,
        "enableRateLimit": True,
    }
)
