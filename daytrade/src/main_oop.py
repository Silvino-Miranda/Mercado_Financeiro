from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.order_flow_agent import OrderFlowAgent
from agents.sentiment_agent import SentimentAgent
from utils.data_fetcher import get_historical_data
from utils.indicators import calculate_technical_analysis
from utils.file_saver import save_decisions_as_md
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

# Configuração da LLM
llmGPT = ChatOpenAI(api_key=API_KEY, model="gpt-4o-mini", temperature=0.5)


def genereateDecisions(ticker):
    # Carrega os dados históricos do ativo
    data = get_historical_data(ticker)

    # Instancia os agentes
    technical_agent = TechnicalAgent(llmGPT, calculate_technical_analysis)
    fundamental_agent = FundamentalAgent(llmGPT)
    order_flow_agent = OrderFlowAgent(llmGPT)
    sentiment_agent = SentimentAgent(llmGPT)

    # Executa os agentes
    technical_decision = technical_agent.analyze(ticker, data)
    fundamental_decision = fundamental_agent.analyze(ticker)
    order_flow_decision = order_flow_agent.analyze(ticker)
    sentiment_decision = sentiment_agent.analyze(ticker)

    # Consolida as decisões
    decisions = {
        "Ticker": ticker,
        "Agente_Tecnico": technical_decision,
        "Agente_Fundamentalista": fundamental_decision,
        "Agente_Fluxo_Ordens": order_flow_decision,
        "Agente_Sentimento": sentiment_decision,
    }

    # Chama a função para salvar as decisões em um arquivo Markdown
    save_decisions_as_md(ticker, decisions)


def main():
    # Ativos a serem analisados
    tickers = [
        # "BTC-USD",
        # "PENDLE-USD",
        # "RUNE-USD",
        "DISB34.SA",
        # "IMX-USD",
        # "UNI-USD",
        # "STX-USD",
        # "SOL-USD",
        # "LINK-USD",
        # "ETH-USD",
        # "MKR-USD",
    ]

    for ticker in tickers:
        genereateDecisions(ticker)


if __name__ == "__main__":
    main()
