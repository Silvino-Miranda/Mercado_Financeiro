import pandas as pd
import os
import time
import ccxt
from binance.client import Client
from binance.enums import *

api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

cliente_binance2 = ccxt.binance(
    {
        "apiKey": api_key,
        "secret": secret_key,
        "enableRateLimit": True,
    }
)

# cliente_binance = Client(api_key, secret_key)

# symbol_info = cliente_binance.get_symbol_info('BTCUSDT')
# lot_size_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
# min_qty = float(lot_size_filter['minQty'])
# max_qty = float(lot_size_filter['maxQty'])
# step_size = float(lot_size_filter['stepSize'])

# print(lot_size_filter, min_qty, max_qty, step_size)


def pegando_dados(codigo, intervalo):

    candles = cliente_binance2.get_market_from_symbols(symbol=codigo, interval=intervalo, limit=1000)
    precos = pd.DataFrame(candles)
    precos.columns = [
        "tempo_abertura",
        "abertura",
        "maxima",
        "minima",
        "fechamento",
        "volume",
        "tempo_fechamento",
        "moedas_negociadas",
        "numero_trades",
        "volume_ativo_base_compra",
        "volume_ativo_cotação",
        "-",
    ]
    precos = precos[["fechamento", "tempo_fechamento"]]
    precos["tempo_fechamento"] = pd.to_datetime(
        precos["tempo_fechamento"], unit="ms"
    ).dt.tz_localize("UTC")
    precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert(
        "America/Sao_Paulo"
    )

    return precos


def calcular_quantidade_disponivel(cliente_binance2, amount_brl, symbol):
    # Obtém o saldo disponível em BRL
    balance = cliente_binance2.fetch_balance()
    brl_balance = balance["BRL"]["free"]
    # Verifica se há saldo suficiente
    if 10.0 > brl_balance:
        print(f"Saldo insuficiente. Saldo disponível: {brl_balance} BRL")
        return False

    # Obtém o preço atual de mercado
    ticker = cliente_binance2.fetch_ticker(symbol)
    price = ticker["last"]

    # Calcula a quantidade de cripto a ser comprada
    amount_crypto = amount_brl / price
    return amount_crypto


def estrategia_trade(dados, codigo_ativo, ativo_operado, quantidade, posicao):

    dados["media_rapida"] = dados["fechamento"].rolling(window=7).mean()
    dados["media_devagar"] = dados["fechamento"].rolling(window=40).mean()

    ultima_media_rapida = dados["media_rapida"].iloc[-1]
    ultima_media_devagar = dados["media_devagar"].iloc[-1]

    print(
        f"Última Média Rápida: {ultima_media_rapida} | Última Média Devagar: {ultima_media_devagar}"
    )

    conta = cliente_binance2.get_account()

    for ativo in conta["balances"]:
        if ativo["asset"] == ativo_operado:
            quantidade_atual = float(ativo["free"])

    if ultima_media_rapida > ultima_media_devagar:
        if posicao == False:
            order = cliente_binance2.create_order(
                symbol=codigo_ativo,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantidade,
            )

            print("COMPROU O ATIVO")
            posicao = True

    elif ultima_media_rapida < ultima_media_devagar:
        if posicao == True:
            order = cliente_binance2.create_order(
                symbol=codigo_ativo,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=int(quantidade_atual * 1000) / 1000,
            )

            print("VENDER O ATIVO")
            posicao = False

    return posicao


posicao_atual = False

while True:
    codigo_operado = "SOLBRL"
    ativo_operado = "SOL"
    periodo_candle = Client.KLINE_INTERVAL_1MINUTE

    quantidade = calcular_quantidade_disponivel(cliente_binance2, 10.0, ativo_operado)

    dados_atualizados = pegando_dados(codigo=codigo_operado, intervalo=periodo_candle)

    posicao_atual = estrategia_trade(
        dados_atualizados,
        codigo_ativo=codigo_operado,
        ativo_operado=ativo_operado,
        quantidade=quantidade,
        posicao=posicao_atual,
    )
    time.sleep(10)
