#/usr/bin/env python

from pandas import np
from pandas.io.data import DataReader


def historical_volatility(sym, days):
    "Return the annualized stddev of daily log returns of `sym`."
    try:
        quotes = DataReader(sym, 'yahoo')['Close'][-days:]
    except Exception, e:
        print "Error getting data for symbol '{}'.\n".format(sym), e
        return None, None
    logreturns = np.log(quotes / quotes.shift(1))
    return np.sqrt(252*logreturns.var())

if __name__ == "__main__":
    print historical_volatility('GOOG', 30)