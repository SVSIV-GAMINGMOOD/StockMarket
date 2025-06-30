import yfinance as yf

def fetch_stock_data(ticker, timeframe):
    if timeframe in ["1d", "5d"]:
        interval = "15m"
    else:
        interval = "1d"
    data = yf.download(ticker, period=timeframe, interval=interval)
    data.columns = data.columns.get_level_values(0)  # flatten multi-index
    if data.index.tz is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Asia/Kolkata')
    
    return data