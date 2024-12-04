from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.decisao import Decisao


class FundamentalAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, ticker):
        indicators = self.get_fundamental_data(ticker)
        parseador = JsonOutputParser(pydantic_object=Decisao)

        prompt_template = PromptTemplate(
            template="""Você é um especialista em análise fundamentalista focado em criptomoedas como o {ticker}.
            Os indicadores econômicos mais recentes relacionados ao ativo são:
            - Taxa de Juros Global: {interest_rate}
            - Inflação Global: {inflation_rate}
            - Expectativa de Regulamentações: {regulation_outlook}

            Com base nesses indicadores, recomende **comprar**, **vender** ou **esperar**. Justifique sua resposta. {resposta}""",
            input_variables={"ticker"},
            partial_variables={"resposta": parseador.get_format_instructions()},
        )

        chain = prompt_template | self.llm | parseador

        resposta = chain.invoke(
            {
                "ticker": ticker,
                "interest_rate": indicators["interest_rate"],
                "inflation_rate": indicators["inflation_rate"],
                "regulation_outlook": indicators["regulation_outlook"],
            }
        )

        return resposta

    # Corrigido: Adiciona o parâmetro self
    def get_fundamental_data(self, ticker):
        # Exemplo de dados fundamentais - substituir por dados reais ou API
        return {
            "interest_rate": "N/A",  # 4.5 Exemplo de taxa de juros global
            "inflation_rate": "N/A",  # 2.3 Exemplo de inflação
            "regulation_outlook": "N/A" # "Positivo, com possível flexibilização",  # Expectativa regulatória
        }
