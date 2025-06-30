import numpy as np
from sklearn.linear_model import LinearRegression

class StockPredictor:
    def __init__(self):
        self.model = LinearRegression()
    
    def train(self, data):
        data = data.dropna()
        X = data[['Close_lag1', 'Sentiment']].values
        y = data['Close'].values
        self.model.fit(X, y)
    
    def predict_next(self, last_close, avg_sentiment):
        X_pred = np.array([[last_close, avg_sentiment]])
        return float(self.model.predict(X_pred)[0])
