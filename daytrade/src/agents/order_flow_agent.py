from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.decisao import Decisao


class OrderFlowAgent:
    def __init__(self, llm):
        self.llm = llm
        # self.get_order_flow_data = get_order_flow_data

    def analyze(self, ticker):
        indicators = self.get_order_flow_data(ticker)
        parseador = JsonOutputParser(pydantic_object=Decisao)

        prompt_template = PromptTemplate(
            template="""Você é um especialista em análise de fluxo de ordens para o ativo {ticker}.
            Os dados de fluxo de ordens mais recentes são:
            - Volume Total: {volume}
            - Nível de Suporte: {support_level}
            - Nível de Resistência: {resistance_level}
            - Delta de Volume (compra - venda): {volume_delta}

            Com base nesses dados, recomende **comprar**, **vender** ou **esperar**. Justifique sua resposta. {resposta}""",
            input_variables={"ticker"},
            partial_variables={"resposta": parseador.get_format_instructions()},
        )

        chain = prompt_template | self.llm | parseador

        resposta = chain.invoke(
            {
                "ticker": ticker,
                "volume": indicators["volume"],
                "support_level": indicators["support_level"],
                "resistance_level": indicators["resistance_level"],
                "volume_delta": indicators["volume_delta"],
            }
        )

        return resposta

    def get_order_flow_data(self, ticker):
        # Exemplo de dados de fluxo de ordens - substituir por dados reais ou API
        return {
            "volume": "N/A",  # 1500000 Volume total de negociações
            "support_level": "N/A",  # 30000 Nível de suporte (exemplo)
            "resistance_level": "N/A",  # 35000 Nível de resistência (exemplo)
            "volume_delta": "N/A",  # 100000 Delta entre volume de compra e volume de venda
        }
