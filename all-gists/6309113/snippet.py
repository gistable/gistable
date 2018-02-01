# -*- coding:utf-8 -*-

import numpy
from scipy import stats

n = 200
#正規分布にあてはまる乱数を生成
score_x = numpy.random.normal(171.77, 5.54, n)
score_y = numpy.random.normal(62.49, 7.89, n)

#適当にちょっとノイズ入れる
score_x.sort()
score_x = numpy.around(score_x + numpy.random.normal(scale=3.0, size=n), 2)
score_y.sort()
score_y = numpy.around(score_y + numpy.random.normal(size=n), 2)


#最大値
print "Max x: " + str(numpy.max(score_x)) + " y: " + str(numpy.max(score_y))
#最小値
print "Min x: " + str(numpy.min(score_x)) + " y: " + str(numpy.min(score_y))
#平均値
print "Avg x: " + str(numpy.mean(score_x)) + " y: " + str(numpy.mean(score_y))
#第1四分位
print "1Q x:" + str(stats.scoreatpercentile(score_x, 25)) + " y: " + str(stats.scoreatpercentile(score_y, 25))
#中央値
print "Med x: " + str(numpy.median(score_x)) + " y: " + str(numpy.median(score_y))
#第3四分位
print "3Q x:" + str(stats.scoreatpercentile(score_x, 75)) + " y: " + str(stats.scoreatpercentile(score_y, 75))
#分散
print "Var x: " + str(numpy.var(score_x)) + " y: " + str(numpy.var(score_y))
#標準偏差
print "S.D. x: " + str(numpy.std(score_x)) + " y:" + str(numpy.std(score_y))
#相関係数
cor = numpy.corrcoef(score_x, score_y)
print "Correlation Coefficient : " + str(cor[0,1])