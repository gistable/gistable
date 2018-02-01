# -*- coding:utf-8 -*-

import numpy
import pylab
#import statsmodels.api

from sklearn import linear_model

n = 200
#データの生成
score_x = numpy.random.normal(171.77, 5.54, n)
score_y = numpy.random.normal(62.49, 7.89, n)

score_x.sort()
score_x = numpy.around(score_x + numpy.random.normal(scale=3.0, size=n), 2)
score_y.sort()
score_y = numpy.around(score_y + numpy.random.normal(size=n), 2)
#1列にしないとだめ
score_X = score_x.reshape(n, 1)

# 散布図を描く
pylab.scatter(score_x, score_y, marker='.', linewidths=0)
pylab.grid(True)
pylab.xlabel('X')
pylab.ylabel('Y')

#print '--------------------------statsmodels-----------------------------'
#statsmodelsで回帰分析してみる（うまく動かず)

#results = statsmodels.api.OLS(score_y, score_X).fit()
#print results.summary()

#回帰直線を描く
#pylab.plot(score_x, results.predict(), 'r', linewidth=2)

print '-----------------------------sklearn------------------------------'
#sklearnで回帰分析してみる
lm = linear_model.LinearRegression()


lm.fit(score_X, score_y)

print 'Coefficients :' + str(lm.coef_)
print 'Intercept :' + str(lm.intercept_)
print 'R2 :' + str(lm.score(score_X, score_y))

#回帰直線用のデータ生成
predict_x = numpy.arange(140, 200, 1)
predict_y = lm.predict(predict_x.reshape(60, 1))

#回帰直線を描く
pylab.plot(predict_x, predict_y, 'r', linewidth=2)


pylab.show()
