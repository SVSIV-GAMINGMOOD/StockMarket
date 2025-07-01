import streamlit as st
from data import fetch_stock_data
from plots import plot_candlestick_with_bollinger
from prediction import StockPredictor
from news import fetch_sentiment
from streamlit_autorefresh import st_autorefresh
from metrics import fetch_stock_metrics

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title("📈Stock Analyzer")

# sidebar
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL")

timeframes = {
    "1 Day": "1d",
    "5 Days": "5d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "Max": "max"
}
selected_tf = st.sidebar.selectbox("Timeframe", list(timeframes.keys()), index=4)
selected_period = timeframes[selected_tf]

refresh_interval = st.sidebar.slider("Auto Refresh Interval (seconds)", 10, 600, 60)
st_autorefresh(interval=refresh_interval * 1000, key="refresh_key")

with st.spinner("Fetching data and running prediction..."):
    data = fetch_stock_data(ticker, selected_period)
    if data is None or data.empty:
        st.error("No data available for the selected timeframe.")
        st.stop()

    # plot
    fig = plot_candlestick_with_bollinger(data, ticker, selected_tf)
    st.plotly_chart(fig, use_container_width=True)

    # sentiment
    newsapi_key = st.secrets["NEWSAPI_KEY"]
    avg_sentiment = fetch_sentiment(ticker, newsapi_key)

    data['Sentiment'] = avg_sentiment
    data['Close_lag1'] = data['Close'].shift(1)

    predictor = StockPredictor()
    predictor.train(data)

    last_close = float(data['Close'].iloc[-1])  # safe
    predicted_price = predictor.predict_next(last_close, avg_sentiment)

    # metrics
    metrics = fetch_stock_metrics(ticker)
    # categorize them

    valuation_metrics = {
    k: metrics[k] for k in [
        "Market Cap", "Enterprise Value", "Trailing P/E", "Forward P/E", "PEG Ratio (5yr expected)",
        "Price/Sales (ttm)", "Price/Book (mrq)", "Enterprise Value/Revenue", "Enterprise Value/EBITDA"
    ]
}
    price_volume_metrics = {
    k: metrics[k] for k in [
        "52W High", "52W Low", "Volume", "Previous Close", "Open", "Dividend Yield"
    ]
}
    profitability_metrics = {
    k: metrics[k] for k in [
        "Profit Margin", "Return on Assets (ttm)", "Return on Equity (ttm)",
        "Revenue (ttm)", "Net Income (ttm)", "Diluted EPS (ttm)"
    ]
}
    balance_sheet_metrics = {
    k: metrics[k] for k in [
        "Total Cash (mrq)", "Total Debt/Equity (mrq)", "Levered Free Cash Flow (ttm)"
    ]
}

# display in 4 columns
# display in 4 columns
st.subheader(f"{ticker} Fundamentals")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        "<div style='text-align:center; font-weight:bold; font-size:16px;'>Valuation Measures</div><hr>",
        unsafe_allow_html=True
    )
    for k, v in valuation_metrics.items():
        val = f"${v/1e9:.2f}B" if isinstance(v, (int, float)) and v > 1e9 else v
        st.markdown(f"<div style='font-size:12px;text-align:center'>{k}: <b>{val}</b></div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        "<div style='text-align:center; font-weight:bold; font-size:16px;'>Price / Volume</div><hr>",
        unsafe_allow_html=True
    )
    for k, v in price_volume_metrics.items():
        st.markdown(f"<div style='font-size:12px;text-align:center'>{k}: <b>{v}</b></div>", unsafe_allow_html=True)

with col3:
    st.markdown(
        "<div style='text-align:center; font-weight:bold; font-size:16px;'>Profitability & Income</div><hr>",
        unsafe_allow_html=True
    )
    for k, v in profitability_metrics.items():
        if isinstance(v, (int, float)) and ("Margin" in k or "Return" in k):
            val = f"{v*100:.2f}%" if v < 1 else v
        else:
            val = v
        st.markdown(f"<div style='font-size:12px;text-align:center'>{k}: <b>{val}</b></div>", unsafe_allow_html=True)

with col4:
    st.markdown(
        "<div style='text-align:center; font-weight:bold; font-size:16px;'>Balance Sheet & Cash Flow</div><hr>",
        unsafe_allow_html=True
    )
    for k, v in balance_sheet_metrics.items():
        val = f"${v/1e9:.2f}B" if isinstance(v, (int, float)) and v > 1e9 else v
        st.markdown(f"<div style='font-size:12px;text-align:center'>{k}: <b>{val}</b></div>", unsafe_allow_html=True)

# footer
st.success("Analysis Complete ✅")
