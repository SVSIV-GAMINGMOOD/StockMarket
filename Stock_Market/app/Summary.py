import streamlit as st
import pandas as pd
from data import fetch_stock_data
from plots import plot_chart_with_bollinger, chart_type_selector
from predictions import StockPredictor
from news import fetch_news_and_sentiment
from metrics import fetch_stock_metrics, company_name
from streamlit_autorefresh import st_autorefresh
from streamlit.web.server import Server
from datetime import datetime, date, timedelta

if 'app_started' not in st.session_state:
    st.session_state.app_started = False

if not st.session_state.app_started:
    st.set_page_config(page_title="Stock Analyzer Dashboard", layout="centered", initial_sidebar_state="collapsed")
    st.title("Welcome to the Stock Analyzer Dashboard! 📈")
    st.markdown("Enter a stock ticker below to begin your analysis.")
    st.markdown("""<style>[data-testid="collapsedControl"]{display: none !important;}</style>""", unsafe_allow_html=True)
    initial_ticker_input = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, GOOGL, MSFT)", "").strip().upper()
    if st.button("Start Analysis"):
        if initial_ticker_input:
            st.session_state.app_started = True
            st.session_state.selected_ticker = initial_ticker_input
            st.rerun()
        else:
            st.warning("Please enter a ticker symbol to start.")
else:
    st.set_page_config(page_title="Stock Analyzer", layout="wide", initial_sidebar_state="expanded")
    st.title("📈 Stock Analyzer Dashboard")

    st.sidebar.header("Configuration")
    ticker = st.sidebar.text_input("Stock Ticker", st.session_state.selected_ticker).strip().upper()
    if ticker != st.session_state.selected_ticker:
        st.session_state.selected_ticker = ticker
        st.rerun()

    timeframe_option = st.sidebar.radio("Select Timeframe", ["Predefined", "Custom Date Range"])

    if timeframe_option == "Predefined":
        timeframes = {
            "1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo",
            "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "Max": "max"}
        selected_tf = st.sidebar.selectbox("Timeframe", list(timeframes.keys()), index=8)
        selected_period = timeframes[selected_tf]
        start_date = None
        end_date = None
    else:
        today = date.today()
        default_start = today - timedelta(days=365)
        start_date = st.sidebar.date_input("Start Date", default_start)
        end_date = st.sidebar.date_input("End Date", today)
        selected_period = None
        selected_tf = f"{start_date} to {end_date}"

    refresh_interval = st.sidebar.slider("Auto Refresh Interval (seconds)", 10, 600, 60)
    refresh_now = st.sidebar.button("Refresh Now")

    if refresh_now:
        st.rerun()
    else:
        st_autorefresh(interval=refresh_interval * 1000, key="refresh_key")

    with st.spinner("Fetching data and running prediction..."):
        data = fetch_stock_data(
            ticker=ticker,
            period=selected_period,
            start_date=start_date,
            end_date=end_date)

        if data is None or data.empty:
            st.error("No data available for the selected timeframe or custom date range.")
            st.stop()

        metrics = fetch_stock_metrics(ticker)

        current_price = metrics.get("Current Price")
        prev_close = metrics.get("Previous Close")
        if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)):
            price_change = current_price - prev_close
            percent_change = (price_change / prev_close) * 100
            st.metric(
                label=company_name(ticker),
                value=f"{current_price:.2f}",
                delta=f"{price_change:.2f} ({percent_change:.2f}%)")
        else:
            st.metric(label=company_name(ticker), value="Price data not available")

        st.markdown("---")

        def format_metric(value, key):
            if isinstance(value, (int, float)):
                if "Cap" in key or "Value" in key or "Revenue" in key or "Cash" in key or "Income" in key:
                    if abs(value) >= 1e9:
                        return f"${value/1e9:.2f}B"
                    elif abs(value) >= 1e6:
                        return f"${value/1e6:.2f}M"
                    else:
                        return f"${value:,.2f}"
                elif "Yield" in key or "Margin" in key or "Return" in key:
                    return f"{value:.2%}" if value is not None else "N/A"
                elif "Ratio" in key or "P/E" in key:
                    return f"{value:.2f}" if value is not None else "N/A"
                else:
                    return f"${value:,.2f}"
            return str(value) if value is not None else "N/A"

        st.subheader(f"Financial Metrics for {company_name(ticker)}")

        prev_close = format_metric(metrics.get("Previous Close"), "Previous Close")
        market_cap = format_metric(metrics.get("Market Cap"), "Market Cap")
        volume = format_metric(metrics.get("Volume"), "Volume")
        open_price = format_metric(metrics.get("Open"), "Open")
        trailing_pe = format_metric(metrics.get("Trailing P/E"), "Trailing P/E")
        forward_pe = format_metric(metrics.get("Forward P/E"), "Forward P/E")

        day_low = data['Low'].iloc[-1] if 'Low' in data.columns and not data.empty else "N/A"
        day_high = data['High'].iloc[-1] if 'High' in data.columns and not data.empty else "N/A"
        days_range = f"{day_low:.2f} - {day_high:.2f}" if isinstance(day_low, (int, float)) and isinstance(day_high, (int, float)) else "N/A"

        fifty_two_w_high = format_metric(metrics.get("52W High"), "52W High")
        fifty_two_w_low = format_metric(metrics.get("52W Low"), "52W Low")
        fifty_two_w_range = f"{fifty_two_w_low} - {fifty_two_w_high}" if fifty_two_w_low != "N/A" and fifty_two_w_high != "N/A" else "N/A"

        col1, col2, col3, col4, summary_col = st.columns([0.1, 0.15, 0.1, 0.1, 0.55])
        with col1: st.markdown(f"**Previous Close**<br>{prev_close}", unsafe_allow_html=True)
        with col2: st.markdown(f"**Market Cap**<br>{market_cap}", unsafe_allow_html=True)
        with col3: st.markdown(f"**Volume**<br>{volume}", unsafe_allow_html=True)
        with col4: st.markdown(f"**Open**<br>{open_price}", unsafe_allow_html=True)
        with summary_col:
            summary = metrics.get("Business Summary", "No summary available.")
            st.markdown(f"**About {ticker}**")
            if len(summary) > 400:
                st.markdown(summary[:400] + "...")
                with st.expander("Read More"):
                    st.markdown(summary)
            else:
                st.markdown(summary)

        col9, col10, col11, col12, _ = st.columns([0.1, 0.15, 0.1, 0.1, 0.55])
        with col9: st.markdown(f"**Day's Range**<br>{days_range}", unsafe_allow_html=True)
        with col10: st.markdown(f"**52 Week Range**<br>{fifty_two_w_range}", unsafe_allow_html=True)
        with col11: st.markdown(f"**Trailing P/E**<br>{trailing_pe}", unsafe_allow_html=True)
        with col12: st.markdown(f"**Forward P/E**<br>{forward_pe}", unsafe_allow_html=True)

        if st.button("View All Financial Fundamentals"):
            st.switch_page(r"pages\Fundamentals.py")

        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown("---")
        st.caption(f"Last updated: {last_update}")

        avg_sentiment, articles = fetch_news_and_sentiment(ticker, company_name(ticker), st.secrets["NEWS_API_KEY"])
        data['Sentiment'] = avg_sentiment
        data['Close_lag1'] = data['Close'].shift(1)

        predictor = StockPredictor()
        predictor.train(data)
        last_close = float(data['Close'].iloc[-1])
        predicted_price = predictor.predict_next(last_close, avg_sentiment)

        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {overflow-x: hidden;}
        [data-testid="stAppViewContainer"] img,[data-testid="stAppViewContainer"] video,[data-testid="stAppViewContainer"] iframe {max-width: 100%;display: block;}
        [data-testid="stPlotlyChart"] {overflow-x: auto !important;}
        </style>""", unsafe_allow_html=True)

        chart_selector_col, _ = st.columns([0.15, 0.85])
        with chart_selector_col:
            chart_type = chart_type_selector()
        _, fig = st.columns([0.001, 1])
        with fig:
            fig = plot_chart_with_bollinger(data, ticker, selected_tf, chart_type=chart_type, predicted_price=predicted_price)
            st.plotly_chart(fig, use_container_width=True)