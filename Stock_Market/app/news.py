# app/news.py
import streamlit as st
from newsapi import NewsApiClient
from textblob import TextBlob
import datetime

@st.cache_data(ttl=3600)
def fetch_news_and_sentiment(ticker, company_name, newsapi_key):
    newsapi = NewsApiClient(api_key=newsapi_key)
    query = f'("{company_name}" OR {ticker}) AND ("earnings" OR "revenue" OR "profit" OR "guidance" OR "acquisition" OR "merger" OR "takeover" OR "new product" OR "launch" OR "CEO" OR "CFO" OR "lawsuit" OR "settlement" OR "rating" OR "upgrade" OR "downgrade" OR "fda approval")'
    try:
        articles_response = newsapi.get_everything(
            q=query,
            language='en',
            from_param=(datetime.datetime.now() - datetime.timedelta(days=28)).strftime('%Y-%m-%d'),
            to=datetime.datetime.now().strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=50)
        articles = articles_response.get('articles', [])
        sentiments = []
        for article in articles:
            content_to_analyze = (article.get('title', '') or '') + " " + (article.get('description', '') or '')
            if content_to_analyze.strip():
                sentiments.append(TextBlob(content_to_analyze).sentiment.polarity)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        return avg_sentiment, articles
    except Exception as e:
        st.error(f"Error fetching news or calculating sentiment: {e}")
        return 0, []