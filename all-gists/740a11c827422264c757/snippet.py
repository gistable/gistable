#!/usr/bin/env python
 
"""Basic Python Cheat Sheet by Filip Kral on 2015/02/16"""
 
"""
Python is a cross-platform, interpreted, object-oriented programming language.
That means you can run it on Linux, Windows, Mac, and other platforms,
you don't need to compile your code to execute it because it is compiled on
the fly, and you can use classes and objects.

This cheat sheet summarizes the very basics of Python programming syntax.
It is by no means exhaustive! For more comprehensive yet still compact reference
I recommend Python Pocket Reference by Mark Lutz published by O'Reilly.
And of course use standard help: http://docs.python.org/

As you can see on this string, triple double-quotes indicate multi-line string.
Triple double quotes are also used for documentation strings at the beginning 
of functions, classes, and modules.
"""
 
# Anything after a hash character on the same row is a comment
# (unless the hash is in a string)
 
# The very top row of #!/usr/bin/env python is not relevant for Windows users.
# On unix/linux however, it indicates which program to use to run the script.
 

 ## Data types
 
# You do not have to declare variables, data type is inferred.
#http://docs.python.org/tutorial/introduction.html#strings
#http://docs.python.org/tutorial/introduction.html#numbers
#http://docs.python.org/tutorial/stdlib.html#dates-and-times
# Here we overwrite variable x on every line with a new value:
 
x = 1 # integer number
x = int(1) # integer number, function int() returns integer part of the argument
# Do not confuse int() and round()! int(1.8) => 1, round(1.8) => 2.0
 
x = False # boolean, can be True or False
 
x = 1.0 # floating point number
# Notice the decimal point, that makes it floating point and not integer!
x = float(1.0) # floating point explicitly, same as float(1) or float('1')
 
# Other numeric data types are Decimal and Fraction (see help for details)
 
x = 'A string' # string, single quotes preferred but double-quotes work too
x = r'Another string' # string, the r at the beginning indicates a raw string 
#                     # so special characters are read as they are without
#                     # the need to escape them. For example:
#                     # 'c:\\data' and r'c:\data' are the same
x = r'One type of "quotes" can include the other type'
x = r"That's helpful when dealing with apostrophes."
# There are some other prefixes than r, see Python help for details.
x = str(123456) # Function str() converts its argument to string

# Slicing
# Extracting parts of a variable is called slicing or subsetting.
# Slicing works on most objects that have multiple elements, for example 
# strings (have multiple characters), lists, tuples, dictionaries. For example:
x = str(123456) # x is now '123456'
x[0] # '1'
x[-1] # '6'
x[1:3] # '23'
x[3:] # '456'
x[:2] # '12'
x[0:6:2] # '135', generic pattern is x[from:to:step]
x[::-1] # '654321'

# Why objects? What are objects all about?
# More details are further down, for now just know that anything in Python is
# an object. Objects can have properties (data) and methods (functions). 
# For example strings have many methods. Here is how you call some of them:
x = 'A,b,C-'
x.upper() # returns 'A,B,C-'
x.strip('-') # reutrns 'A,b,C'
x.split(',') # returns a list ['A', 'b', 'C-']
 
x = [1, 2, 3] # list
x = list([1, 2]) # explicit declaration of a list
x = [] # this is an empty list, same as calling list()
x = ['Lists', "can", ['mix', 'types'], 123, 4.56] # lists can be nested
# Refer to individual items by zero-based offset (e.g. x[2][0] returns 'mix')
# Lists are mutable so you can change values of items (e.g. x[0] = 4)
 
x = (1, 2, 3) # tuple
x = tuple((1, 3)) # explicit declaration of a tuple
x = () # this is an empty tuple, same as calling tuple()
x = ('nested', ('and', 'mixed'), 'tuple', 1, 2, 3, 4) # tuples can be nested
# Refer to individual items by zero-based offset, e.g. x[0] returns 'nested'
# Tuples are immutable so you cannot change items, x[0] = 4 raises exception!
 
x = {'a': 'dictionaries', 'b': 'are great', 'c': 123} # dictionary
x = {1: 'keys can be mixed', 'b': 'and items too', 2: 123, 'c': 4.56}
x = dict({1: 'explicit', 3: 'dictionary', 'b': 'declaration'})
x = dict([[1, 'many ways to'], [3, 'create'], ['b', 'dicts']])
# Refer to values in dictionaries by their keys, e.g. x['b'] returns 'dicts'
# Assign new value to a key x['c'] = 'new value'
 
x = None # x is now a reference to the empty object, i.e. to nothing
 
## Operators and operations
 
# Binary operators take one argument on the left, one argument on the right,
# and return a value. Convention suggests spaces around a binary operators.
# One operator can have different effect depending on the types of arguments.
1 + 1 # addition; returns 2; similarily – (subtraction)
2 * 2 # multiplication; returns 4
2 ** 3 # power; returns 8
2.0 / 3.0 # division; returns 0.6666...
# Note that 2 / 3 returns 0, correct division an operand to be float:
#  float(2) / 3 or 2 / 3.0
2.0 // 3.0 # floor division (result is rounded down); returns 0.0
4 % 3 # modulo; returns 1
'a' + 'b' # string concatenation, returns 'ab'
'a' * 3 # repetition; returns 'aaa'
['a'] + ['b'] # returns ['a', 'b'], see also list.append and list.extend methods
[1] * 3 # repetition; returns [1,1,1]
 
# Boolean and comparison operators
1 == 2 # equal to; returns False
1 != 3 # not equal to; returns True
x or y # if x is False then y, else x
x and y # if x is False then x, else y
not x # if x is False then True, else False
# Other boolean operators are >, <, >=, =<, is, is not.
# Preferably use brackets to separate individual conditions to prevent
# unexpected operator preference effects:
(1 < 0) or (3 > 1 and 0 < 1)
# which is: False or (True and True) => False or True => the result is True
 
# Operations are executed using methods, different types have different methods.
# There are plenty of methods. Just a few more examples then:
'A-string-with-dashes'.replace('-', '_') # replace dashes with underscores
a_list = [1, 2] # define a new list, and now call its methods:
a_list.append(3) # a_list is now [1, 2, 3]
a_list.extend([4, 5]) # a_list is now [1, 2, 3, 4, 5]
a_list.append([6, 7]) # a_list is now [1, 2, 3, 4, 5, [6, 7]]
a_dict = {1: 'a', 2: 'dictionary'} # define a new dictionary
a_dict.keys() # returns [1, 2]
a_dict.items() # returns ['a', 'dictionary']
a_dict.update({3: 'new item'}) # a_dict is now {1: 'a', 2: 'dictionary', 3: 'new item'}
a_dict.get(1, 2) # returns 'a', would return 2 if 1 was an invalid key
 

## Program flow - code structure and code blocks

# In many languages, blocks of code are surrounded by brackets,
# usually by curly brackets {}, but Python is different.
# In Python, blocks of code are defined by indentation!
# By convention, four spaces define an indentation of a block.
# It is important to be consistent!
# Python interpreter is very sensitive to inappropriate indentation.
 
## Branching (executing blocks of codes depending on a condition)
 
# Examples below use print function to print things to the console.
 
# full branching example
x = 1
if x < 0:
    print('This block will execute if x is lower than zero.')
elif x == 0:
    print('This block will execute if x is exactly zero.')
else:
    print('This will execute if any of the above is true.')
 
# basic branching example
if x is None:
    print('This will execute if x is an empty reference')
else:
    print('And... this will print to console in other cases.')
 
# simple branching example
if x > 0:
    print('The simplest if block.')
 
 
## Looping (iterations)
 
# while loops are the basics
i = 0
while i < 10:
    print('Looping is great' + str(i))
    i = i + 1 # don't forget to increment the counter to avoid infinite loop
 
# for loops are often more convenient than while loops
for i in [1,2,3,4]:
    print('Variable i goes from 1 to 4, now it is ' + str(i))
    print('You can iterate over various iterable variables, not just lists')
 
# couple of tricks for looping
x = 0
while 1: # condition is always true (infinite loop)
    if x < 9:
        pass # pass statement does nothing but is needed to define a block
    elif x < 14:
        continue # continue statement moves onto another iteration
    else:
        break # break statement stops the closest loop
    x += 1 # increment variable x by one, equivalent to x = x + 1


## Functions and statements by example (an extremely reduced selection)
 
# Built-in functions
x = range(5) # x is now list of [0, 1, 2, 3, 4]
len(x) # returns length of x, 5 in this case
type(x) # returns type of an object, <type 'list'> in this case
min(x), max(x) # returns minimum and maximum
map(len, ['applies', 'function', 'to', 'items']) # this returns [7, 8, 2, 5]
zip("a" * 3, ['b', 'c', 'd']) # returns ['ab', 'ac', 'ad']
dir(x) # returns list of names of properties and methods of object x
dir() # returns list of names of variables
del x # delete the first reachable variable x from memory
 
## Defining your own functions
 
# declare function like this
def myFunction(x):
    """Functions are declared using the def statement.
    Get used to writing documentation strings like this one.
    This function just simply returns the input unchanged."""
    return x
 
# and then call a function like this
y = myFunction([1, 2, 3]) # y is now [1, 2, 3]
 
# couple of notes about arguments
def secondFunction(a_list, y='my default', *args, **kwargs):
    """This function demonstrates different ways of passing arguments."""
 
    # a_list must be always supplied and here we assume it is a list
    # so we can append y, which always exists thanks to its default value
    a_list.append(y)
 
    # variable globList was not specified in the argument list, however...
    # ... Python will search in the global scope from the function call.
    # See help for details about scope, this is just a dirty demo.
    # We assume globList is a list somewhere in the scope.
    # Relying on global variables should be avoided in most cases.
    # We also assume a_list argument is a list so we can do:
    globList.extend(a_list)
 
    # Extra unnamed arguments are collected as a list
    print('There are ' + str(len(args)) + ' extra arguments without a name.')
    # Extra named arguments are collected as a dictionary
    print('Keys ' + str(kwargs.keys()) + '; items ' + str(kwargs.items()))
 
    # Functions may not return any value.
    # Technically, in Python, functions always return at least None.
    # Global variables altered within a function will remain altered.
    return
 
# You can call the above function in many ways:
 
globList = [1, 2, 3] # let's define a list outside a function first
 
secondFunction([4, 5])
# >> There are 0 extra arguments passed without a name.
# >> Keys []; items []
# globList is now [1, 2, 3, 4, 5, 'my default']
 
secondFunction([6, 7], y = 'not default')
# >> There are 0 extra arguments passed without a name.
# >> Keys []; items []
# globList is now [1, 2, 3, 4, 5, 'my default', 6, 7, 'not default']
 
secondFunction([8, 9], 'a', 'b', c = 10, d = 11)
# >> There are 1 extra arguments passed without a name.
# >> Keys ['c', 'd']; items [('c', 10), ('d', 11)]
# globList is now [1, 2, 3, 4, 5, 'my default', 6, 7, 'not default', 8, 9, 'a']
 
## Reading and writing files
 
# An example reads lines from one file and writes them to another file.
# This is an old way of handling files.
readthis = r'C:\toread.txt'
writethis = r'C:\towrite.txt'
fread = open(readthis, 'r') # fread is now a file object ready to be read
fwrite = open(writethis, 'w') # fwrite is now a file object ready to be written in
# Other useful modes are 'a' for append, 'rb' for binary reading, etc.
line = fread.readline() # read one line
fwrite.write(line) # write line
# Remember to add characters for new line like fwrite.write('abc' + '\n')
# let's finish the rest quickly
for line in fread:
    fwrite.write(line)
# and close the files when done; see Exception handling for another example
fread.close()
fwrite.close()

# The above is an old way of handling files. Below is the modern version.
# Use the with statement to close files automatically even if something fails. 
readthis = r'C:\toread.txt'
writethis = r'C:\towrite.txt'
with open(readthis, 'r') as fread:
    with open(writethis, 'w') as fwrite:
        for line in fread:
            fwrite.write(line)

            
## Exception handling
 
readthis = r"C:\toread.txt"
try:
    # code for some risky operation like reading or writing files
    fread = open(fread, 'r')
    for line in fread:
        print('Just doing something with a line ' + str(line))
except Exception as e:
    # Older versions of Python (<2.6) use syntax: "except Exception, e:".
    # Here you would put anything you want to do to when an error occurs.
    # You can have more except branches addressing different types of exceptions
    print('Sorry, there was an error: ' + str(e)) # notify the user via console
finally:
    # Finally branch is for cleanup code, here we want to close the file.
    # First, check if variable fread exists, 
    # if it has property "closed" and if closed is not True
    if 'fread' in dir() and 'closed' in dir(fread) and not fread.closed:
        # At this point we can close the file.
        # If we don't check the above, we may introduce another exception!
        fread.close()
    # The finally branch is optional,
    # you can leave it out altogether if you have nothing to clean up.
    # Use the with statement to avoid try:except:finally when handling files,
    # however, try:except:finally blocks are necessary many other scenarios.
 
 
## Classes and object oriented programming
 
# Programming is about data as variables of certain data types,
# mechanisms for branching and looping, and functions.
# Classes (and instances of classes, i.e. objects)
# encapsulate data and functions into self-contained bundles.
 
# An example of a simple class
class Point2D:
    """A 2D point"""
    def __init__(self, x, y):
        """Constructors are by convention called __init__.
        Constructor is invoked when the class is instantiated.
        Constructor is a type of method, all methods must
        receive a reference to the current object as first parameter,
        by convention called self, not used when methods are called.
        Constructors are not always necessary.
        """
        self.X = float(x) # defines a data member of the class
        self.Y = float(y) # defines another data member of the class
        # there is much more to data members (see help for details)
 
    def shift(self, dx, dy):
        """A method to shift the point by vector (dx, dy)"""
        self.X = self.X + float(dx)
        self.Y = self.Y + float(dy)
 
# Instantiate an object of class Point and use its method
pt = Point2D(1, 5)
pt.shift(2,-1) # pt.X is now 3, pt.Y is now 4
 
# Every object is an instance of a class. Including exceptions. Most exceptions
# are derived from Exception class. Let's define a custom exception class.
class MyException(Exception):
    """This class inherits from class Exception.
    Exception is a baseclass (or superclass) of class (or subclass) MyException.
    A class can inherit from multiple baseclasses (separated by comma).
    """
    def __init__(self, extradata):
        """The __init__ function runs when an object of this class is created.
        This is also an example of method overriding: the baseclass has its own
        Exception.__init__ function, but it has been overridden by this method.
        """
        # There are no real private members (properties or methods) in Python,
        # all members can be accessed directly. However there are conventions.
        self.extra = extradata # defining a data member of the class
        # One underscore indicates this should be treated as private member,
        # i.e. accessed only within the class where it is defined.'
        self._secret = 'Not intended for use outside of this class'
    
    def notifyUser(self):
        print(str(self.args)) # self.args is inherited from baseclass Exception
        print(str(self.message)) # also inherited from Exception
        print(str(len(self.extra)) + ' data items: ' + str(self.extra))
 
# We can raise our custom exception intentionally (somewhat artificial example)
try: raise MyException([1, 2, 3])
except MyException as m: m.notifyUser()
# prints out "() \n3 data items: [1, 2, 3]"


## Modules
 
# Modules are collections of functions you can load using the import statement
# The import statement has several forms.
 
# import module for interaction with operating system
import os
a_path = r'C:\my\file.txt'
filename = os.path.basename(a_path) # 'file.txt'
foldername = os.path.dirname(a_path) # 'C:\my'
os.path.join(foldername, filename) # 'C:\my\file.txt'
os.listdir(foldername) # returns list of files in folder foldername
 
# use the datetime module to retrieve date-time stamp
import datetime
t = datetime.datetime.now() # returns current computer time
t.strftime('%Y%m%d%H%M%S') # formats time into a string as specified
 
# Other useful modules are sys, shutil, math, and many others. You can create
# your own modules too ( http://docs.python.org/2/tutorial/modules.html ).
 
## Message to R users
# If you are familiar with R, Python may seem somewhat clumsy.
# R is more flexible when it comes to vector operations, stats, and plotting.
# Check out Python modules numpy, scipy, matplotlib, and pandas.