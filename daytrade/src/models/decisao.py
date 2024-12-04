from pydantic import BaseModel, Field

# Modelo de retorno para todos os agentes
class Decisao(BaseModel):
    decisao: str = Field(..., description="Decisão do agente (comprar, vender ou esperar)")
    motivo: str = Field(..., description="Motivo pelo qual o agente tomou a decisão")
