# pages/Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import fetch_stock_data
from metrics import fetch_quarterly_financials

st.set_page_config(page_title="Analysis", layout="wide")
st.title("🔬 Advanced Analysis")

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, slow=26, fast=12, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

if 'selected_ticker' not in st.session_state or not st.session_state.selected_ticker:
    st.warning("Please select a stock ticker from the 'Summary' page first.")
    st.stop()

ticker = st.session_state.selected_ticker

with st.spinner("Fetching data for analysis..."):
    hist_data = fetch_stock_data(ticker, period="2y")
    quarterly_data = fetch_quarterly_financials(ticker)

if hist_data is None or hist_data.empty:
    st.error("Could not fetch historical data for analysis.")
    st.stop()

tab1, tab2 = st.tabs(["📈 Technical Indicators", "📊 Fundamental Trends"])

with tab1:
    st.header("Technical Indicators")
    st.subheader("Moving Averages (20, 50, 200-day)")
    hist_data['SMA20'] = hist_data['Close'].rolling(window=20).mean()
    hist_data['SMA50'] = hist_data['Close'].rolling(window=50).mean()
    hist_data['SMA200'] = hist_data['Close'].rolling(window=200).mean()

    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], mode='lines', name='Close Price'))
    fig_ma.add_trace(go.Scatter(x=hist_data.index, y=hist_data['SMA20'], mode='lines', name='20-Day SMA'))
    fig_ma.add_trace(go.Scatter(x=hist_data.index, y=hist_data['SMA50'], mode='lines', name='50-Day SMA'))
    fig_ma.add_trace(go.Scatter(x=hist_data.index, y=hist_data['SMA200'], mode='lines', name='200-Day SMA'))
    fig_ma.update_layout(template="plotly_dark", yaxis_title="Price")
    st.plotly_chart(fig_ma, use_container_width=True)

    st.subheader("Relative Strength Index (RSI)")
    hist_data['RSI'] = calculate_rsi(hist_data)

    fig_rsi = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig_rsi.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], name='Close Price'), row=1, col=1)
    fig_rsi.add_trace(go.Scatter(x=hist_data.index, y=hist_data['RSI'], name='RSI'), row=2, col=1)
    fig_rsi.add_hline(y=70, line_dash="dot", row=2, col=1, line_color="red", annotation_text="Overbought (70)")
    fig_rsi.add_hline(y=30, line_dash="dot", row=2, col=1, line_color="green", annotation_text="Oversold (30)")
    fig_rsi.update_layout(template="plotly_dark", showlegend=False)
    fig_rsi.update_yaxes(title_text="Price", row=1, col=1)
    fig_rsi.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    st.plotly_chart(fig_rsi, use_container_width=True)

    st.subheader("MACD")
    macd, signal_line, histogram = calculate_macd(hist_data)

    fig_macd = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig_macd.add_trace(go.Scatter(x=hist_data.index, y=hist_data['Close'], name='Close Price'), row=1, col=1)
    fig_macd.add_trace(go.Scatter(x=hist_data.index, y=macd, name='MACD'), row=2, col=1)
    fig_macd.add_trace(go.Scatter(x=hist_data.index, y=signal_line, name='Signal Line'), row=2, col=1)
    fig_macd.add_trace(go.Bar(x=hist_data.index, y=histogram, name='Histogram'), row=2, col=1)
    fig_macd.update_layout(template="plotly_dark")
    fig_macd.update_yaxes(title_text="Price", row=1, col=1)
    fig_macd.update_yaxes(title_text="MACD", row=2, col=1)
    st.plotly_chart(fig_macd, use_container_width=True)

with tab2:
    st.header("Fundamental Trends")
    if quarterly_data.empty:
        st.warning("Quarterly fundamental data not available for this stock.")
    else:
        plot_data = quarterly_data.transpose()
        plot_data.index = plot_data.index.strftime('%Y-%m-%d')

        st.subheader("Quarterly Total Revenue")
        if "Total Revenue" in plot_data.columns:
            fig_rev = go.Figure(data=[go.Bar(x=plot_data.index, y=plot_data["Total Revenue"])])
            fig_rev.update_layout(template="plotly_dark", yaxis_title="Revenue", xaxis_title="Quarter End Date")
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.info("Total Revenue data not available.")

        st.subheader("Quarterly Net Income")
        if "Net Income" in plot_data.columns:
            fig_income = go.Figure(data=[go.Bar(x=plot_data.index, y=plot_data["Net Income"])])
            fig_income.update_layout(template="plotly_dark", yaxis_title="Net Income", xaxis_title="Quarter End Date")
            st.plotly_chart(fig_income, use_container_width=True)
        else:
            st.info("Net Income data not available.")

        st.subheader("Quarterly Debt vs. Equity")
        if "Total Debt" in plot_data.columns and "Total Stockholder Equity" in plot_data.columns:
            fig_debt = go.Figure()
            fig_debt.add_trace(go.Bar(
                x=plot_data.index,
                y=plot_data["Total Debt"],
                name='Total Debt'
            ))
            fig_debt.add_trace(go.Bar(
                x=plot_data.index,
                y=plot_data["Total Stockholder Equity"],
                name='Stockholder Equity'
            ))
            fig_debt.update_layout(
                barmode='group',
                template="plotly_dark",
                yaxis_title="Amount",
                xaxis_title="Quarter End Date"
            )
            st.plotly_chart(fig_debt, use_container_width=True)
        else:
            st.info("Debt or Equity data not available.")