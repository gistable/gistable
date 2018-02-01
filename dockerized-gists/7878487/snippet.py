#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import math

import pylab

import random

from matplotlib import mlab

xmin = 0
xmax = 10
dx = 0.01
value = 0


TPR = 0
TNR = 0

def func (x):
    return x

def rand():
	ran = random.random() * 10
   	return ran

def count_parameters(i):
	TP = 0
	TN = 0
	FN = 0
	FP = 0
	real_n = 0
	real_p = 0
	for el in x_list:
		value = 3 * x_list[i] + 4*y_list[i]	
		flag = 0
		if x_list[i] > 5:
			flag = 1
	
		if y_list[i] > 5:
			flag = 1

		if flag ==0:
			if value < 30:
				TN = TN +1
				real_n = real_n+1
			if value > 30:
				FN = FN +1
				real_p = real_p+1
		if flag ==1:
			if value < 30:
				FP = FP +1
				real_n = real_n+1
			if value > 30:
				TP = TP +1
				real_p = real_p+1
		i = i+1
		if i > 1000:
			result = [TP, FP, TN, FN, real_p, real_n]
			return result

flag = 0

x_list = mlab.frange(xmin, xmax, dx)

y_list = [rand() for i in x_list]

N = 1000
index = range(N)

first_tp = count_parameters(0)

for element in index:
	res = count_parameters(element)
	TPR = res[0]*100/first_tp[0]
	FPR = (N - element - res[0])*100/(N - first_tp[0])
	x_list2[element] = FPR
	y_list2[element] = TPR
	#print(TPR,FPR)

pylab.ylabel('Sensitivity')
pylab.xlabel('Specificity')
pylab.axis([0,100,0,100])
pylab.plot(x_list2,y_list2,'bs')
pylab.show()
