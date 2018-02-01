#!/usr/bin/env python

#####################################################
#Fuzzy logic implementation of simple tipping system
#Author: 	Samuel Jackson (slj11@aber.ac.uk)
#Date: 		10/2/13
#####################################################

#################################
# Functions for calculating		#
# food quality/service 			#
#################################

#Quality of service/food is good
def f_good(x):
	if x <= 4:
		return 0
	elif x > 4:
		return 1 - (10 - float(x))/6

#Quality of service/food is bad
def f_bad(x):
	if x >= 6:
		return 0
	elif x < 6:
		return 1 - (abs(0 - float(x)))/6

#Quality of service/food is average
def f_average(x):
	if x <= 2.5 or x >= 7.5:
		return 0
	elif 2.5 < x and x < 7.5:
		return 1 - (float(abs(5-x))/2.5)

#################################
# Functions for calculating tip #
# Used in defuzzification		#
#################################

#Tip is low
def t_low(x):
	if x >= 10:
		return 0
	elif x < 10:
		return 1 - (float(x)/10)

#Tip is high
def t_high(x):
	if x <= 10:
		return 0
	elif x > 10:
		return (float(x)/10) -1

#Tip is average
def t_average(x):
	if x <= 5 or x >= 15:
		return 0
	elif 5 < x < 15:
		return 1 - (float(abs(10-x))/5.0)


if __name__ == "__main__":
	qf = float(raw_input("Enter value for quality of food:"))
	qs = float(raw_input("Enter value for quality of service:"))

	#IF 	quality of service is good
	#AND 	quality of food is good
	#THEN	tip is high
	high_score = min(f_good(qf), f_good(qs))

	#IF 	quality of service is bad
	#OR 	quality of food is bad
	#THEN	tip is low
	low_score = max(f_bad(qf), f_bad(qs))

	#IF 	quality of service is OK
	#THEN 	tip is average
	average_score = f_average(qs)

	print "High: %.2f, Average: %.2f, Low: %.2f" % (high_score, average_score, low_score)

	#Defuzzification
	n = 0
	d = 0
	for x in xrange(0,21, 1):
		
		#quick fix for not being able to get
		#0 or 20% tips
		if (high_score == 1):
			n += 20 * high_score
			d += high_score
		elif (low_score == 1):
			n += 0 * low_score
			d += low_score
		#Sample the given point on the line
		else:
			degree =  max(min(t_low(x), low_score), min(t_average(x), average_score), min(t_high(x), high_score))
			n += x * degree
			d += degree

	output = float(n)/float(d)
	print "Crisp output is: %.2f percent" % output