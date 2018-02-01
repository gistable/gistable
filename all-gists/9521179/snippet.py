# let's say you have four sequences you want to print columnwise, like so:

19       59       97       44   
92       57       63       68   
66       21       69       90   
75       66       12       19   

# mock some data
import random as RND
gen_row = lambda: [ RND.randint(10, 99) for c in range(3) ]
# 'data' is a nested list comprised of five rows and three columns
data = [gen_row() for c in range(5)]

# create some column headers
col_headers = ["col{}".format(i) for i in range(1, 4)]

# print the column headers first
print("{:^8} {:^8} {:^8}".format(*col_headers)

# now print the rows
for row in 
  aligned_row = "{:^8} {:^8} {:^8}".format(*row)
  print(aligned_row)
  
  
# i have not used placeholders in my print statement, eg, {0}, {1}, as of python 3.3 i believe, 
# you can omit them and the sequence is implicit because i have four sets of curly braces and four arguments
# passed to 'format'

'''
{:^8} says (seems more intuitive if i read it backwards:

  {}  => create one field
  8   => it will have a width of 8
  ^   => center the data within this field (use '<' for left align and '>' for right align)
  
  every token inside the curly braces is either 
    (i)  an index to the sequence passed to 'format', or
    (ii)  a format specifier, 
    depending on whether it is to the left or right of the colon, 
    {index, format specifier}
    
'''
  
# more format specifiers:

# to control number formatting (eg, number of places to the right of the decimal to print for floats) eg,
# the statement below says to print the value for that field with two decimal places
"{:^8.2f}".format(v1)

# but how do you know what order to place these format specifiers? 
# ie, why not
"{:.2f^8}"   # wrong
# the python docs publish a 'general form for a standard format specifier:
# http://docs.python.org/2.6/library/string.html#formatstrings

