#
# Stock Market Prediction
# with Linear Regression
#
# The Python Quants GmbH
#
import numpy as np
import pandas as pd
from pandas_datareader import data as web
import seaborn as sns
sns.set()


class RegPred(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.get_data()

    def get_data(self):
        self.data = pd.DataFrame(web.DataReader(
            self.symbol, data_source='yahoo')['Adj Close'])
        self.data.columns = ['prices']
        self.data['returns'] = np.log(self.data / self.data.shift(1))
        self.data.dropna(inplace=True)

    def generate_matrix(self, lags):
        self.matrix = np.zeros((lags + 1, len(self.data) - lags))
        for i in range(lags + 1):
            if i == lags:
                self.matrix[i] = self.data.returns.values[i:]
            else:
                self.matrix[i] = self.data.returns.values[i: i - lags]

    def predict_returns(self, lags):
        self.lags = lags
        self.generate_matrix(lags)
        reg = np.linalg.lstsq(
            self.matrix[:lags].T, np.sign(self.matrix[lags]))[0]
        self.pred = np.dot(self.matrix[:lags].T, reg)

    def get_performance(self):
        self.perf = self.data.ix[self.lags:].copy()
        self.perf['positions'] = np.sign(self.pred)
        self.perf['strategy'] = self.perf.positions * self.perf.returns
        self.perf[['returns', 'strategy']].cumsum().apply(np.exp).plot()