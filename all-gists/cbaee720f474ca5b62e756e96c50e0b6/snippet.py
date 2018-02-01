#http://bit.ly/28VdHva

##########
#VARIABLES
##########

#numbers
a = 3 #float, int, and long
#strings
b = 'ha '

#multiply them
a * b + '!' #returns 'ha ha ha !'

#booleans: notice the capitals
t = True
f = False

n = None

#NoneType
type(n)

######
#LISTS
######

#lists can be created with elements
l = [1,'a',t]

l

#here we manually delete our list
del l

#this calls the variable that we just deleted. We're expecting an error
l


#lists can also be created empty
l = []


#let's append 3 separate elements to our list
l.append(1)
l.append('a')
l.append(True)

l.pop()

#adding lists is easy
l + [4.5,6]

#we can also add lists to a list
l.append([7,8,9])

#let's access the last element in the list
l[-1]

#######
#TUPLES
#######
#Tuples are immutable (unchangeable) lists
#Pulling data from a database usually yields tuples
t = (1,2,3)

t


###################
#CONTROL STATEMENTS
###################
#if, for, while

#There are no "end"s in Python. It is indentation strict.
#We also need a colon.   :

#True is true
if(True):
    print(True)

#1 is true
if(1):
    print(True)

#None is false
if(None):
    print(True)

#0 is false
if(0):
    print('Hello')


#else if is elif
if(False):
    print(1)
elif(0):
    print(2)
else:
    print(3)


#For statments only exist as ForEach statments
for x in range(0,5):
    print(x)

#we can also iterate through strings because they are lists of characters
a = 'Hello, world!'
for c in a:
    print(c)

#While loops are as you would expect: very easy
c = 0
while c < len(a):
    print(a[c])
    #there no ++ incremetor in Python
    c += 1

t=(1,2,3)
#converting from a tuple to a list is easy
t = [elem for elem in t]

#let's create a 3 by 3 matrix
x = ('id',1,2,3)
x = (x,x,x)

x

#suppose we got x back from a database and we want to eliminate the 'id' values
l = [row for row in x] #this takes us partway
l
l = [[elem for elem in row] for row in x] #we are still only partway there
l

#this is a single row
l[0]
#this is what we want, the first row from 1 onwards, skipping the 0th element
l[0][1:]

#now let's get rid of the 'id' values
just_values = [row[1:] for row in l]

#we now have only the data
just_values

##########
#Libraries
##########
#importing a library
import math #built-in but need to import
math.log(10) #natural log - base ~2.718 (e)

#you can specify the base
math.log(100,10)


a=[2,4,6,8]
[x**2 for x in a if x > 4] #conditional list comprehension

import random

#############
#Dictionaries
#############


d = {}
d['key'] = 'value'
d

#let's destroy it
del d


x = [['id_variable','value'],[1,2]]

#to create a dictionary from a N b 2 list
{key: value for key, value in x}




##########
#FUNCTIONS
##########

#functions require parentheses and colons. ():
def function_name():
    pass

#functions are first class, which means you can pass them as arguments before calling them
function_name

#this is how you call a function
function_name()

def function_name2(n):
    print(n)
    return(2*n)

x = function_name2(3)
x #should be 6

# the second_input has a default
def function_name3(input_name, second_input=5):
    return input_name*second_input


function_name3(4) #calls the function


########
#CLASSES
########


#Classes are templates for new object types
#This is the Hello World Class
class HW(object):
    """docstring for Class"""
    def __init__(self, x):
        self.x = x
        pass
    def callMe():
        print('This was called')

hw = HW #create a HW object
hw #the object
hw.callMe()
