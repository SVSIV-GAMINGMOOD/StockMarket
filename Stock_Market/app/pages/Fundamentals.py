# pages/📈_Full_Fundamentals.py

import streamlit as st
from metrics import fetch_stock, fetch_quarterly_financials
from datetime import datetime

st.set_page_config(page_title="Full Fundamentals", layout="wide")
st.title("📊 Detailed Financial Fundamentals")

if 'selected_ticker' in st.session_state and st.session_state.selected_ticker:
    ticker = st.session_state.selected_ticker
else:
    st.info("Please select a stock ticker from the main Dashboard page first.")
    st.stop()

def format_metric(value, key):
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        if key in [
            'marketCap', 'enterpriseValue', 'totalRevenue', 'grossProfits', 'ebitda',
            'netIncomeToCommon', 'totalCash', 'totalDebt', 'operatingCashflow',
            'freeCashflow', 'sharesOutstanding', 'floatShares', 'sharesShort']:
            if abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            else:
                return f"{value:,.0f}"
        elif key in [
            'profitMargins', 'operatingMargins', 'returnOnAssets', 'returnOnEquity',
            'revenueGrowth', 'earningsGrowth', 'payoutRatio', 'dividendYield',
            'trailingAnnualDividendYield', 'heldPercentInsiders', 'heldPercentInstitutions',
            'shortPercentOfFloat', 'sharesPercentSharesOut', '52WeekChange', 'SandP52WeekChange']:
            return f"{value:.2%}"
        elif 'Date' in key:
            return datetime.fromtimestamp(value).strftime('%Y-%m-%d')
        else:
            return f"{value:,.2f}"
    return str(value)

st.header("Quarterly Financials")

try:
    quarterly_df = fetch_quarterly_financials(ticker)
    quarterly_df_formatted = quarterly_df.applymap(
        lambda x: f"${x/1e6:,.0f}M" if isinstance(x, (int, float)) and x != 0 else ('$0M' if x == 0 else 'N/A')
    )
    st.dataframe(quarterly_df_formatted, use_container_width=True)
except Exception as e:
    st.warning("Could not retrieve quarterly financial data.")

st.divider()

st.header("Key Statistics & Ratios")

with st.spinner(f"Fetching key statistics for {ticker}..."):
    metrics = fetch_stock(ticker)

    metric_groups = {
        "General / Fiscal Info": ['fiscalYearEnd', 'mostRecentQuarter'],
        "Profitability": ['profitMargins', 'operatingMargins'],
        "Management Effectiveness": ['returnOnAssets', 'returnOnEquity'],
        "Income Statement": [
            'totalRevenue', 'revenuePerShare', 'revenueGrowth', 'grossProfits', 'ebitda',
            'netIncomeToCommon', 'trailingEps', 'earningsGrowth'],
        "Balance Sheet": [
            'totalCash', 'totalCashPerShare', 'totalDebt', 'debtToEquity',
            'currentRatio', 'bookValue'],
        "Cash Flow Statement": ['operatingCashflow', 'freeCashflow'],
        "Trading / Stock Price History": [
            'beta', '52WeekChange', 'SandP52WeekChange', 'fiftyTwoWeekHigh',
            'fiftyTwoWeekLow', 'fiftyDayAverage', 'twoHundredDayAverage'],
        "Share Statistics": [
            'averageVolume', 'averageDailyVolume10Day', 'sharesOutstanding',
            'impliedSharesOutstanding', 'floatShares', 'heldPercentInsiders',
            'heldPercentInstitutions', 'sharesShort', 'shortRatio',
            'shortPercentOfFloat', 'sharesPercentSharesOut', 'sharesShortPriorMonth'],
        "Dividends & Splits": [
            'dividendRate', 'dividendYield', 'trailingAnnualDividendRate',
            'trailingAnnualDividendYield', 'payoutRatio', 'dividendDate',
            'exDividendDate', 'lastSplitFactor', 'lastSplitDate']
    }

    def display_metric_group(title, keys):
        st.markdown(f"**{title}**")
        for key in keys:
            if key in metrics:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.text(key)
                with col2:
                    st.text(format_metric(metrics[key], key))
        st.markdown("---")


    left_col, right_col = st.columns(2)

    groups_in_left = [
        "General / Fiscal Info", "Profitability", "Management Effectiveness",
        "Income Statement", "Balance Sheet", "Cash Flow Statement"]

    groups_in_right = [
        "Trading / Stock Price History", "Share Statistics", "Dividends & Splits"]

    with left_col:
        for group in groups_in_left:
            if group in metric_groups:
                display_metric_group(group, metric_groups[group])

    with right_col:
        for group in groups_in_right:
            if group in metric_groups:
                display_metric_group(group, metric_groups[group])