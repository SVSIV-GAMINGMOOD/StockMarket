from newsapi import NewsApiClient
from textblob import TextBlob

def fetch_sentiment(ticker, newsapi_key):
    newsapi = NewsApiClient(api_key=newsapi_key)
    articles = newsapi.get_everything(q=ticker, language='en', page_size=5)
    
    sentiments = []
    for article in articles['articles']:
        sentiment_score = TextBlob(article['title']).sentiment.polarity
        sentiments.append(sentiment_score)
    
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment
