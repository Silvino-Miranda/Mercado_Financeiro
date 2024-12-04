from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz

from constants import USER, PASS, SERVER

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

pd.set_option("display.max_columns", 500)  # number of columns to be displayed
pd.set_option("display.width", 1500)  # max table width to display
# import pytz module for working with time zone

# establish connection to MetaTrader 5 terminal
if not mt5.initialize(
    login=USER,
    password=PASS,
    server=SERVER,
):
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# get data on MetaTrader 5 version
# Defina o nome do ativo e o intervalo de tempo (por exemplo, BTCUSD)
symbol = "PETR4"
timeframe = (
    mt5.TIMEFRAME_H1
)  # Escolha o timeframe desejado (H1 para 1 hora, D1 para diário, etc.)
start_date = datetime(2000, 1, 1)
end_date = datetime.now()

# Solicite os dados do ativo
rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

# Finalize a conexão com o MT5
mt5.shutdown()

# Converta para DataFrame
data = pd.DataFrame(rates)
if data.empty:
    print("Nenhum dado encontrado")
    quit()
    
data["time"] = pd.to_datetime(data["time"], unit="s")

# Exiba os dados ou salve em CSV
print(data)
data.to_csv(f"{symbol}_data-H1.csv", index=False, sep=";")
