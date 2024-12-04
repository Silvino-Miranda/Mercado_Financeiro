import streamlit as st
import pandas as pd




def Tabela(crypto_data, signals, stock_names):
    # Cria uma lista para armazenar os DataFrames individuais
    df_list = []
    for ticker, data in crypto_data.items():
        # Seleciona a última linha (mais recente) dos dados
        last_data = data.iloc[[-1]].copy()
        # Adiciona o nome, o ticker e o sinal da criptomoeda
        last_data["Ticker"] = ticker
        last_data["Nome"] = stock_names.get(ticker, ticker)
        last_data["Sinal"] = signals.get(ticker, "Espera")
        df_list.append(last_data)

    # Concatena todos os DataFrames em um único DataFrame
    if df_list:
        indicators_df = pd.concat(df_list)
        # Define a coluna 'Nome' como índice
        indicators_df.set_index("Nome", inplace=True)
        columns_to_display = [
            "Close",
            "MA_200",
            "RSI",
            "MACD",
            "MACD_Signal",
            "%K",
            "%D",
            "Sinal",
        ]

        # Define a function to apply styles based on indicator values
        def highlight_cells(val, col_name):
            if col_name == "RSI":
                if val < 30:
                    return "background-color: green"  # Favorable to buy
                elif val > 70:
                    return "background-color: red"  # Favorable to sell
            elif col_name == "MACD":
                if val > 0:
                    return "background-color: green"  # Favorable to buy
                else:
                    return "background-color: red"  # Favorable to sell
            # Add conditions for other indicators if needed
            return ""

        # Apply the styling function to the DataFrame
        styled_df = indicators_df[columns_to_display].style

        for col_name in indicators_df[columns_to_display].columns:
            styled_df.applymap(
                lambda val: highlight_cells(val, col_name), subset=[col_name]
            )

        # Display the styled DataFrame
        st.dataframe(styled_df)
    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")
