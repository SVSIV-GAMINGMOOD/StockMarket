import plotly.graph_objects as go
import streamlit as st

def plot_chart_with_bollinger(data, ticker, timeframe_label, chart_type="Candlestick", sentiment=None, predicted_price=None):
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['Upper'] = data['SMA50'] + 2 * data['Close'].rolling(window=50).std()
    data['Lower'] = data['SMA50'] - 2 * data['Close'].rolling(window=50).std()

    fig = go.Figure()

    if predicted_price:
        fig.add_hline(
            y=predicted_price,
            line=dict(color="orange", dash="dash"),
            annotation_text=f"Predicted: {predicted_price:.2f}",
            annotation_position="top left")

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Price"))
    elif chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            name="Close Price",
            line=dict(color="cyan")))
    elif chart_type == "Mountain":
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            name="Mountain",
            fill="tozeroy",
            line=dict(color="skyblue")))
    elif chart_type == "Bar":
        fig.add_trace(go.Ohlc(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="OHLC Bar"))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA50'],
        name="SMA 50",
        line=dict(color="yellow", width=1.5)))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Upper'],
        name="Upper Band",
        line=dict(color="red", width=1, dash="dot")))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Lower'],
        name="Lower Band",
        line=dict(color="green", width=1, dash="dot")))

    fig.update_layout(
        title=f"{ticker} {chart_type} Chart ({timeframe_label})",
        yaxis_title="Price",
        xaxis_title="Date",
        xaxis_rangeslider_visible=(chart_type == "Candlestick"),
        template="plotly_dark",
        height=600,
        showlegend=True)

    fig.update_yaxes(
        autorange=True,
        fixedrange=False)

    return fig

def chart_type_selector():
    if "chart_type" not in st.session_state:
        st.session_state.chart_type = "Candlestick"

    chart_type = st.selectbox(
        "Select Chart Type",
        ["Candlestick", "Line", "Mountain", "Bar"],
        index=["Candlestick", "Line", "Mountain", "Bar"].index(st.session_state.chart_type),
        key="chart_type_selector")

    st.session_state.chart_type = chart_type
    return chart_type