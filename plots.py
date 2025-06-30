import plotly.graph_objects as go

def plot_candlestick_with_bollinger(data, ticker, timeframe_label, sentiment=None, predicted_price=None):
    # Calculate Bollinger Bands
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['Upper'] = data['SMA50'] + 2 * data['Close'].rolling(window=50).std()
    data['Lower'] = data['SMA50'] - 2 * data['Close'].rolling(window=50).std()

    fig = go.Figure()

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    ))

    # SMA20
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['SMA50'],
        name="SMA 50",
        line=dict(color="yellow", width=1.5)
    ))

    # Upper Bollinger
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Upper'],
        name="Upper Band",
        line=dict(color="red", width=1, dash="dot")
    ))

    # Lower Bollinger
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Lower'],
        name="Lower Band",
        line=dict(color="green", width=1, dash="dot")
    ))

    # layout
    fig.update_layout(
        title=f"{ticker} Candlestick Chart ({timeframe_label})",
        yaxis_title="Price",
        xaxis_title="Date",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=600,
        showlegend=True
    )

    # Conditional rangebreaks
    if len(data.index) >= 2:
        interval_minutes = (data.index[1] - data.index[0]).total_seconds() / 60
        if interval_minutes <= 60:  # intraday
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),       # skip weekends
                    dict(bounds=[15.5, 9.25], pattern="hour")  # skip non-market hours
                ]
            )
        else:  # daily candles
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"])
                ]
            )

    return fig
