# Importação das Bibliotecas:
from utils.backtest import backtest_par, plot_saldo

# Parâmetros da estratégia
MME_PERIOD = 21
RISCO_RETORNO = 2  # Relação risco/retorno de 1:2
TAMANHO_POSICAO = 1  # Tamanho inicial da posição
RISK_PERCENTAGE = 0.1  # 10% de risco por operação

# Execução do Backtest para os Pares de Moedas Desejados:
pares = ["EURUSD=X"]
# pares = ['EURUSD=X', 'NZDUSD=X', 'AUDUSD=X', 'USDCAD=X']

for par in pares:
    backtest_par(par, MME_PERIOD, RISCO_RETORNO, TAMANHO_POSICAO, RISK_PERCENTAGE)
