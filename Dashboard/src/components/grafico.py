import streamlit as st
import plotly.graph_objects as go

def Grafico(ticker, data, stock_names):
    st.write(f"### {stock_names[ticker]} ({ticker})")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            name="Preço de Fechamento",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA_200"],
            name="Média Móvel 200",
            line=dict(color="orange"),
        )
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Preço em USD",
        legend_title="Legenda",
        height=500,
        width=1000,
    )
    st.plotly_chart(fig)
