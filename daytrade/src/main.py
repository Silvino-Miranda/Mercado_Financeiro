import yfinance as yf
import talib as ta
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from langchain_openai import ChatOpenAI
from langchain.globals import set_debug

import os
from dotenv import load_dotenv

load_dotenv()
set_debug(False)

API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    api_key=API_KEY,
    model="gpt-4o-mini",
    temperature=0.5,
)

# Função para obter dados históricos de um ativo financeiro
def get_historical_data(ticker):
    data = yf.download(ticker, period="1mo", interval="1d")
    return data

# Função para calcular indicadores técnicos
def calculate_indicators(data):
    indicators = {}

    # Exemplo de cálculo de alguns indicadores
    indicators["SMA_50"] = ta.SMA(data["Close"], timeperiod=50).tolist()
    indicators["SMA_200"] = ta.SMA(data["Close"], timeperiod=200).tolist()
    indicators["RSI"] = ta.RSI(data["Close"], timeperiod=14).tolist()
    
    # Calculando MACD e convertendo os valores para listas
    macd, macd_signal, _ = ta.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    indicators["MACD"] = macd.tolist()
    indicators["MACD_Signal"] = macd_signal.tolist()

    return indicators

# Prompt para a LLMChain que gera o JSON final com os indicadores
prompt_template = """
Dados históricos processados para {ticker}.
Indicadores calculados:
- SMA 50
- SMA 200
- RSI
- MACD

Aqui está o JSON com os indicadores calculados:
{json_output}
"""

# Função para gerar o JSON final a ser utilizado
def generate_json_output(ticker, indicators):
    json_output = json.dumps(indicators, indent=4)
    return json_output

# Função principal da chain
def trading_chain(ticker):
    # Passo 1: Obter dados históricos
    data = get_historical_data(ticker)

    # Passo 2: Calcular os indicadores técnicos
    indicators = calculate_indicators(data)

    # Passo 3: Gerar o JSON com os resultados
    json_output = generate_json_output(ticker, indicators)

    # Construção da LLMChain para integração final
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["ticker", "json_output"],
            template=prompt_template,
        ),
    )

    # Execução da chain
    output = chain.run(ticker=ticker, json_output=json_output)

    return output

# Exemplo de uso
ticker = "AAPL"  # Exemplo de ativo
result = trading_chain(ticker)
print(result)
