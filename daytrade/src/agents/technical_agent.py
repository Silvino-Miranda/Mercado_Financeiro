from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.decisao import Decisao


class TechnicalAgent:
    def __init__(self, llm, calculate_technical_analysis):
        self.llm = llm
        self.calculate_technical_analysis = calculate_technical_analysis

    def analyze(self, ticker, data):
        indicators = self.calculate_technical_analysis(data)
        parseador = JsonOutputParser(pydantic_object=Decisao)

        prompt_template = PromptTemplate(
            template="""
                Você é um especialista em análise técnica de ativos financeiros.
                Para o ativo {ticker}, os indicadores técnicos mais recentes são:
                - SMA 50: {sma_50}
                - SMA 200: {sma_200}
                - RSI: {rsi}
                - MACD: {macd}
                - MACD Signal: {macd_signal}

                Com base nesses indicadores, recomende **comprar**, **vender** ou **esperar**. Justifique sua resposta. {resposta}""",
            input_variables={"ticker"},
            partial_variables={"resposta": parseador.get_format_instructions()},
        )

        chain = prompt_template | self.llm | parseador

        resposta = chain.invoke(
            {
                "ticker": ticker,
                "sma_50": indicators["SMA_50"][-1],
                "sma_200": indicators["SMA_200"][-1],
                "rsi": indicators["RSI"][-1],
                "macd": indicators["MACD"][-1],
                "macd_signal": indicators["MACD_Signal"][-1],
            }
        )

        # print(resposta)

        return resposta
