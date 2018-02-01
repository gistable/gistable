print "Hello welcome to Austin's calculator. Would you like to use (b)asic functions or more (c)omplex functions?"
dec = (raw_input())

if dec == "b":
  print """(m)ultiply, (d)ivide, (a)dd, or (s)ubtract?. Don't forget, 
this can only be integers or whole numbers."""

answer = (raw_input())

if answer == "m":                                          #Multiplication
  print "Type your first number."                          
  m1 = int(raw_input())

print "Now, type the second number."
m2 = int(raw_input())

print m1 * m2                                            #Multiplication

print "Thank your for using Austin's calculator."

import sys
sys.exit()

if answer == "d":                                           #Division
  print "Type your first number."                          
  m1 = int(raw_input())

print "Now, type the second number."
m2 = int(raw_input())

print m1 / m2                                            #Division

print "Thank your for using Austin's calculator."

import sys
sys.exit()

if answer == "a":                                           #Addition
  print "Type your first number."                          
  a1 = int(raw_input())

print "Now, type the second number."
a2 = int(raw_input())

print a1 + a2                                            #Addition

print "Thank your for using Austin's calculator."

import sys
sys.exit()

if answer == "s":                                          #Subtraction
  print "Type your first number."                          
  s1 = int(raw_input())

print "Now, type the second number."
s2 = int(raw_input())

print s1 - s2                                            #Subtraction

print "Thank your for using Austin's calculator."

import sys
sys.exit()

if dec == "c":   #complex functions
  print "(e)xponents? Don't forget this can only be integers or whole numbers."
answer2 = (raw_input())

if answer2 == "e":
  print " what is the base number?"
  e1 = int(raw_input())
  
print "what is the exponent? Up to 10"
e2 = int(raw_input())

if e2 == "1":
  print e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "2":
  print e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "3":
  print e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "4":
  print e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "5":
  print e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "6":
  print e1 * e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "7":
  print e1 * e1 * e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "8":
  print e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "9":
  print e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."

import sys
sys.exit()

if e2 == "10":
  print e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1 * e1
print "Thank your for using Austin's calculator."


import sys
sys.exit()