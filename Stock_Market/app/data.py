import yfinance as yf
import streamlit as st
from datetime import date

@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str, period: str = None, start_date: date = None, end_date: date = None):
    interval = "1d"
    if period:
        if period in ["1d", "5d"]:
            interval = "15m"
    if period:
        data = yf.download(ticker, period=period, interval=interval)
    elif start_date and end_date:
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval=interval)
    else:
        st.error("Please provide either a timeframe (period) or a custom date range.")
        return None

    if data.empty:
        return None

    data.columns = data.columns.get_level_values(0)
    if data.index.tz is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Asia/Kolkata')

    return data