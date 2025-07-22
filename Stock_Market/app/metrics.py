import yfinance as yf
import streamlit as st
import pandas as pd

@st.cache_data(ttl=86400)
def company_name(ticker):
    companyname = yf.Ticker(ticker).info.get("shortName")
    return companyname

def fetch_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info

def fetch_stock_metrics(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    metrics = {
        "Market Cap": info.get("marketCap", "N/A"),
        "Enterprise Value": info.get("enterpriseValue", "N/A"),
        "Trailing P/E": info.get("trailingPE", "N/A"),
        "Forward P/E": info.get("forwardPE", "N/A"),
        "PEG Ratio (5yr expected)": info.get("pegRatio", "N/A"),
        "Price/Sales (ttm)": info.get("priceToSalesTrailing12Months", "N/A"),
        "Price/Book (mrq)": info.get("priceToBook", "N/A"),
        "Enterprise Value/Revenue": info.get("enterpriseToRevenue", "N/A"),
        "Enterprise Value/EBITDA": info.get("enterpriseToEbitda", "N/A"),
        "52W High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52W Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Volume": info.get("volume", "N/A"),
        "Previous Close": info.get("previousClose", "N/A"),
        "Open": info.get("open", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "Profit Margin": info.get("profitMargins", "N/A"),
        "Return on Assets (ttm)": info.get("returnOnAssets", "N/A"),
        "Return on Equity (ttm)": info.get("returnOnEquity", "N/A"),
        "Revenue (ttm)": info.get("totalRevenue", "N/A"),
        "Net Income (ttm)": info.get("netIncomeToCommon", "N/A"),
        "Diluted EPS (ttm)": info.get("trailingEps", "N/A"),
        "Total Cash (mrq)": info.get("totalCash", "N/A"),
        "Total Debt/Equity (mrq)": info.get("debtToEquity", "N/A"),
        "Levered Free Cash Flow (ttm)": info.get("leveredFreeCashflow", "N/A"),
        "Business Summary": info.get("BusinessSummary", "No summary available."),
        "Current Price": info.get("currentPrice", "N/A"),}
    return metrics

def fetch_quarterly_financials(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_financials
    balance_sheet = stock.quarterly_balance_sheet

    key_metrics = [
        "Total Revenue", "Gross Profit",
        "Operating Income", "EBITDA",
        "EBIT", "Net Income",
        "Diluted EPS", "Total Debt",
        "Cash And Cash Equivalents",
        "Share Issued", "Tangible Book Value"]

    combined_data = pd.concat([financials, balance_sheet])
    quarterly_summary = combined_data[combined_data.index.isin(key_metrics)]
    cleaned_summary = quarterly_summary.dropna(axis=1, how='all')
    return quarterly_summary.iloc[:, :6]
