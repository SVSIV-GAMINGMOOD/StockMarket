import yfinance as yf

def fetch_stock_metrics(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    metrics = {
        # valuation
        "Market Cap": info.get("marketCap", "N/A"),
        "Enterprise Value": info.get("enterpriseValue", "N/A"),
        "Trailing P/E": info.get("trailingPE", "N/A"),
        "Forward P/E": info.get("forwardPE", "N/A"),
        "PEG Ratio (5yr expected)": info.get("pegRatio", "N/A"),
        "Price/Sales (ttm)": info.get("priceToSalesTrailing12Months", "N/A"),
        "Price/Book (mrq)": info.get("priceToBook", "N/A"),
        "Enterprise Value/Revenue": info.get("enterpriseToRevenue", "N/A"),
        "Enterprise Value/EBITDA": info.get("enterpriseToEbitda", "N/A"),
        
        # price/volume
        "52W High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52W Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Volume": info.get("volume", "N/A"),
        "Previous Close": info.get("previousClose", "N/A"),
        "Open": info.get("open", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        
        # profitability
        "Profit Margin": info.get("profitMargins", "N/A"),
        "Return on Assets (ttm)": info.get("returnOnAssets", "N/A"),
        "Return on Equity (ttm)": info.get("returnOnEquity", "N/A"),
        "Revenue (ttm)": info.get("totalRevenue", "N/A"),
        "Net Income (ttm)": info.get("netIncomeToCommon", "N/A"),
        "Diluted EPS (ttm)": info.get("trailingEps", "N/A"),
        
        # balance sheet
        "Total Cash (mrq)": info.get("totalCash", "N/A"),
        "Total Debt/Equity (mrq)": info.get("debtToEquity", "N/A"),
        "Levered Free Cash Flow (ttm)": info.get("leveredFreeCashflow", "N/A"),
    }
    return metrics
