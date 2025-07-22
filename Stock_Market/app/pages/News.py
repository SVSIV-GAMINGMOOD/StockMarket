# app/pages/news.py
import streamlit as st
from metrics import company_name
from news import fetch_news_and_sentiment

st.set_page_config(page_title="Stock Analyzer - News", layout="wide")
st.title("📰 Latest News & Sentiment")

ticker = st.session_state.selected_ticker
newsapi_key = st.secrets.get("NEWS_API_KEY")

if not newsapi_key:
    st.error("NEWS_API_KEY not found in Streamlit secrets. Please add it to .streamlit/secrets.toml")
    st.stop()

st.write(company_name(ticker))

with st.spinner(f"Fetching news and sentiment for {ticker}"):
    avg_sentiment, articles = fetch_news_and_sentiment(ticker, company_name(ticker), st.secrets["NEWS_API_KEY"])

st.subheader(f"Recent News Articles for {company_name(ticker)}")

if articles:
    for i, article in enumerate(articles):
        with st.expander(f"**{article.get('title', 'No Title')}**"):
            if article.get('source') and article['source'].get('name'):
                st.write(f"**Source:** {article['source']['name']}")
            if article.get('author'):
                st.write(f"**Author:** {article['author']}")
            if article.get('publishedAt'):
                st.write(f"**Published:** {article['publishedAt']}")
            if article.get('description'):
                st.write(article['description'])
            if article.get('url'):
                st.markdown(f"[Read full article]({article['url']})")
            if article.get('urlToImage'):
                st.image(article['urlToImage'], caption="Article Image", use_container_width=True)
else:
    st.info(f"No recent news articles found for {company_name(ticker)}.")