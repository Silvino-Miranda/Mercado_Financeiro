# frameworks_drivers/binance_client.py
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

binance_client = Client(api_key, secret_key)