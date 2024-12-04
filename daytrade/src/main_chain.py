import yfinance as yf
import talib as ta
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain.globals import set_debug

import os
from dotenv import load_dotenv

# Retorno padrão para todos os agentes
class Decisao(BaseModel):
    decisao: str = Field(..., description="Decisão do agente (comprar, vender ou esperar)")
    motivo: str = Field(..., description="Motivo pelo qual o agente tomou a decisão")

# Carregar as variáveis de ambiente
load_dotenv()
set_debug(True)

API_KEY = os.getenv("OPENAI_API_KEY")

# Definindo a LLM que será usada por cada agente
llm = ChatOpenAI(
    api_key=API_KEY,
    model="gpt-4o",
    temperature=0.5,
)


# Função para obter dados históricos de um ativo financeiro
def get_historical_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    return data


# Função para calcular indicadores técnicos
def calculate_technical_analysis(data):
    indicators = {}

    # Exemplo de cálculo de alguns indicadores
    indicators["SMA_50"] = ta.SMA(data["Close"], timeperiod=50).tolist()
    indicators["SMA_200"] = ta.SMA(data["Close"], timeperiod=200).tolist()
    indicators["RSI"] = ta.RSI(data["Close"], timeperiod=14).tolist()
    macd, macd_signal, _ = ta.MACD(
        data["Close"], fastperiod=12, slowperiod=26, signalperiod=9
    )
    indicators["MACD"] = macd.tolist()
    indicators["MACD_Signal"] = macd_signal.tolist()

    return indicators


# Função de agente para análise técnica
def technical_agent(ticker, data):
    indicators = calculate_technical_analysis(data)
    
    # Prompt especializado para análise técnica
    prompt_template = """
    Você é um especialista em análise técnica de ativos financeiros.
    Para o ativo {ticker}, os indicadores técnicos mais recentes são:
    - SMA 50 (Média Móvel Simples de 50 dias): {sma_50}
    - SMA 200 (Média Móvel Simples de 200 dias): {sma_200}
    - RSI (Índice de Força Relativa): {rsi}
    - MACD: {macd}
    - Sinal MACD: {macd_signal}

    Analise esses indicadores e recomende **comprar**, **vender** ou **esperar**. 
    Justifique sua resposta.
    """
    
    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["ticker", "sma_50", "sma_200", "rsi", "macd", "macd_signal"],
            template=prompt_template,
        )
    )
    
    resposta = chain.run(
        ticker=ticker,
        sma_50=indicators["SMA_50"][-1],
        sma_200=indicators["SMA_200"][-1],
        rsi=indicators["RSI"][-1],
        macd=indicators["MACD"][-1],
        macd_signal=indicators["MACD_Signal"][-1]
    )
    
    # Retorna a decisão usando a classe Decisao
    return Decisao(decisao=resposta.split("\n")[0], motivo=resposta.split("\n")[1])



# Função de agente para análise fundamentalista (simplificado para este exemplo)
def fundamental_agent(ticker):
    # Prompt especializado para análise fundamentalista
    prompt_template = """
    Você é um especialista em análise fundamentalista e economia global, focado em criptomoedas como o ({ticker}).
    
    Considere os seguintes fatores para sua análise fundamentalista:
    - Adoção institucional de {ticker} e políticas monetárias globais.
    - Mudanças nas regulamentações governamentais, especialmente nos EUA e na União Europeia.
    - Taxa de juros nos EUA e impactos no mercado de criptomoedas.
    - Análise do impacto de eventos macroeconômicos, como inflação, crescimento do PIB e tensões geopolíticas (ex: guerras, sanções).
    - Sentimento do mercado em relação à inflação de ativos digitais e uso do {ticker} como reserva de valor.

    Com base nesses fatores, você recomendaria **comprar**, **vender** ou **esperar** {ticker} neste momento? Justifique brevemente sua resposta com base nos fundamentos.

    Responda apenas com uma das opções: "comprar", "vender" ou "esperar".
    """

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["ticker"],
            template=prompt_template,
        ),
    )

    decision = chain.run(ticker=ticker)

    return {"Agente_Fundamentalista": decision.strip()}


# Função de agente para fluxo de ordens (simplificado)
def order_flow_agent(ticker):
    # Prompt especializado para análise de fluxo de ordens
    prompt_template = """
    Você é um especialista em análise de fluxo de ordens, com foco em grandes players e movimentos de volume.

    Para o ativo {ticker}, considere os seguintes fatores:
    - Níveis de suporte e resistência atuais baseados no volume de ordens (order book).
    - Padrões de volume: houve um aumento significativo de volume em um curto período, indicando entrada de grandes players?
    - Delta de volume: diferenças entre volume de compra e volume de venda, e como isso pode indicar desequilíbrios de oferta e demanda.
    - Ordens iceberg (grandes ordens divididas em pequenos lotes) e sua influência no mercado.

    Com base no fluxo de ordens, você recomendaria **comprar**, **vender** ou **esperar**? Justifique sua decisão com base nos dados de volume e comportamento de grandes players.

    Responda apenas com uma das opções: "comprar", "vender" ou "esperar".
    """

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["ticker"],
            template=prompt_template,
        ),
    )

    decision = chain.run(ticker=ticker)

    return {"Agente_Fluxo_Ordens": decision.strip()}


def sentiment_agent(ticker):
    # Prompt especializado para análise de sentimento de mercado
    prompt_template = """
    Você é um especialista em análise de sentimento de mercado para criptomoedas como o ({ticker}).
    
    Considere os seguintes fatores para sua análise de sentimento:
    - Sentimento predominante nas redes sociais (Twitter, Reddit) em relação ao {ticker}.
    - Notícias recentes sobre regulamentações, adoção ou eventos negativos como hacks em exchanges.
    - Relatórios de grandes players institucionais e sua visão sobre o futuro do {ticker}.
    - Medidores de medo e ganância (Fear and Greed Index) para o mercado de criptomoedas.

    Com base no sentimento geral do mercado, você recomendaria **comprar**, **vender** ou **esperar** {ticker} neste momento? Justifique sua resposta com base no sentimento.

    Responda apenas com uma das opções: "comprar", "vender" ou "esperar".
    """

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["ticker"],
            template=prompt_template,
        ),
    )

    decision = chain.run(ticker=ticker)

    return {"Agente_Sentimento": decision.strip()}


# Função principal para executar todos os agentes
def trading_chain(ticker):
    # Obter dados históricos
    data = get_historical_data(ticker)

    print(f"Dados históricos para {ticker}:")
    print(data.tail())

    # Executar agentes
    technical_decision = technical_agent(ticker, data)
    fundamental_decision = fundamental_agent(ticker)
    order_flow_decision = order_flow_agent(ticker)
    sentiment_decision = sentiment_agent(ticker)

    # Combinar as decisões em um dicionário
    decisions = {
        "Ticker": ticker,
        **technical_decision,
        **fundamental_decision,
        **order_flow_decision,
        **sentiment_decision,
    }

    # Salvar o resultado em um arquivo JSON
    with open(f"{ticker}_decisions.json", "w") as f:
        json.dump(decisions, f, indent=4)

    return decisions


# Exemplo de uso
ticker = "ETH-USD"  # Pode mudar para minidólar (WDO)
result = trading_chain(ticker)
print(result)
