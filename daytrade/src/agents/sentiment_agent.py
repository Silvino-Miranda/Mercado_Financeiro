from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.decisao import Decisao


class SentimentAgent:
    def __init__(self, llm):
        self.llm = llm
        # self.get_sentiment_data = get_sentiment_data

    def analyze(self, ticker):
        indicators = self.get_sentiment_data(ticker)
        parseador = JsonOutputParser(pydantic_object=Decisao)

        prompt_template = PromptTemplate(
            template="""Você é um especialista em análise de sentimento de mercado para o ativo {ticker}.
            Os indicadores de sentimento mais recentes são:
            - Índice de Medo e Ganância: {fear_greed_index}
            - Volume de Notícias Positivas: {positive_news_volume}
            - Volume de Notícias Negativas: {negative_news_volume}
            - Sentimento nas Redes Sociais: {social_sentiment}

            Com base nesses indicadores, recomende **comprar**, **vender** ou **esperar**. Justifique sua resposta. {resposta}""",
            input_variables={"ticker"},
            partial_variables={"resposta": parseador.get_format_instructions()},
        )

        chain = prompt_template | self.llm | parseador

        resposta = chain.invoke(
            {
                "ticker": ticker,
                "fear_greed_index": indicators["fear_greed_index"],
                "positive_news_volume": indicators["positive_news_volume"],
                "negative_news_volume": indicators["negative_news_volume"],
                "social_sentiment": indicators["social_sentiment"],
            }
        )

        return resposta

    def get_sentiment_data(self, ticker):
        # Exemplo de dados de sentimento - substituir por dados reais ou API
        return {
            "fear_greed_index": "N/A",  # 45 Exemplo de índice de medo e ganância (0 a 100)
            "positive_news_volume": "N/A",  # 120 Número de notícias positivas
            "negative_news_volume": "N/A",  # 60 Número de notícias negativas
            "social_sentiment": "N/A",  # "Positivo" Sentimento geral nas redes sociais
        }
