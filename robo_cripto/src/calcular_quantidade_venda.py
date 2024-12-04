import os
import ccxt

def calcular_quantidade_disponivel(symbol):
    api_key = os.getenv("KEY_BINANCE")
    secret_key = os.getenv("SECRET_BINANCE")

    binance_client = ccxt.binance(
        {
            "apiKey": api_key,
            "secret": secret_key,
            "enableRateLimit": True,
        }
    )

    # Obtém o saldo disponível em USDT
    balance = binance_client.fetch_balance()
    brl_balance = balance["USDT"]["free"]
    # Verifica se há saldo suficiente
    if brl_balance <= 0.0:
        print(f"Saldo insuficiente. Saldo disponível: {brl_balance} USDT")
        return False

    # Obtém o preço atual de mercado
    ticker = binance_client.fetch_ticker(symbol)
    price = ticker["last"]

    # Calcula a quantidade de cripto a ser comprada usando 95% do saldo disponível
    amount_crypto = (brl_balance) / price

    # Ajusta a quantidade para a precisão permitida
    amount_crypto = binance_client.amount_to_precision(symbol, amount_crypto)
    amount_crypto = float(amount_crypto)

    print(f"Quantidade de {symbol} a ser comprada: {amount_crypto}")
    return amount_crypto