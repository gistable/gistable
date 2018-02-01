# -*- coding: utf-8 -*-

# Studying this script might be helpful in understanding why UnicodeDecode errors
# sometimes happen when trying to capture utf-8 output to files with Python 2 even
# though the output prints to your (utf-8 capable) terminal.

# Note that the first line of this file is called the Byte Order Marker (BOM), which 
# is a directive to tell Python that it should treat this file as utf-8 (i.e. comments and 
# string values may be utf-8)

import sys
import codecs

cant = u'can\u2019t' # can’t is a utf-8 <unicode> object

# Using "print", you can print to a terminal that can display utf-8 fine, but can't be 
# redirected to file in a termainal/script through the > operator because when 
# redirecting output to a file, sys.stdout.encoding is used. With Python 2, it  
# defaults to None, which means that ascii is used for the encoding.

print 'I %s believe it is so complicated.' % (cant,)

# What happens when you try to use "print" to redirect output a file, including sys.stdout?
# It also displays to a utf-8 terminal but can't be redirected. 
# This is effectively the same as "print 'I %s believe it is so complicated.' % (cant,)"

print >> sys.stdout, 'I %s believe it is so complicated.' % (cant,)

# However, just explicitly writing to sys.stdout doesn't print to a utf-8 terminal and can't 
# be redirected to file because it relies on the value of sys.stdout.encoding, 
# which defaults to ascii

sys.stdout.write('I %s believe it is so complicated.' % (cant,))

# You also can't write utf-8 directly to a file because encoding defaults to ascii

f = open("/tmp/cant", "w")
print >> f, 'I %s believe it is so complicated.' % (cant,)
f.close()

# However, explicitly setting the encoding on the file to be written as utf-8 works fine

f = codecs.open("/tmp/cant", "w", "utf-8")
f.write(cant)
f.close()

# The best solution (?!?)
# Prints to screen and can be redirected to file without
# any further thought by the user of a script emitting utf-8 output
# if you change the stdout writer codec at the top of your script before
# any output is emitted. Would have been really convenient if the BOM would
# have triggered the Python interpreter to do this automatically

sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
sys.stdout.write('I %s believe it is so complicated.' % (cant,))