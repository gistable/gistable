# This section just builds a sample tab delimited file to work with, don't
# worry too much about this code yet. Just have a look at the `test.txt` file
# that it creates and checkout the following sections.

x = range(10)
funcs = [lambda x: x**2, lambda x: x / 5.0, lambda x: x**3, lambda x: x + 3]
lines = 'x\tx^2\tx/5\tx^3\tx+3\n'
for row in x:
    lines += str(row)
    for col in funcs:
        lines += '\t' + str(col(row))
    if row != 9:
        lines += '\n'
with open('test.txt', 'w') as f:
    f.write(lines)

# Now we have a simple file `test.txt` that is tab delimited with a header.
# Here are three ways to load that data in starting from the basics to using
# libraries that are basically one call.

# Plain Python and then converting the data to a NumPy array (similar to Matlab
# matrix).

from numpy import array

f = open('test.txt', 'r') # open the file for reading
data = []
for row_num, line in enumerate(f):
    # Remove the new line at the end and then split the string based on
    # tabs. This creates a python list of the values.
    values = line.strip().split('\t')
    if row_num == 0: # first line is the header
         header = values
    else:
        data.append([float(v) for v in values])
basic_data = array(data)
f.close() # close the file

# Now you have a very familiar array/matrix entity to work with. Check out
# http://www.scipy.org/NumPy_for_Matlab_Users to see what you can do with this
# array.

print(basic_data)

# You can also use NumPy to do this in one command (except you don't get
# headers).

from numpy import loadtxt

np_data = loadtxt('test.txt', delimiter='\t', skiprows=1) # skips header
print(np_data)

# Finally, pandas provides a R like data frame that is good for this stuff and
# makes manipulating and plotting data pretty fun. See
# http://pandas.pydata.org/pandas-docs/stable/ for getting started with this
# package. This may be over kill, and you can just start with NumPy.

from pandas import read_csv

pandas_data = read_csv('test.txt', delimiter='\t')
print(pandas_data)

# Now say I want to plot something, you bring in the plotting libary.

import matplotlib.pyplot as plt

# plot x^2
plt.figure()
plt.plot(basic_data[:, 0], basic_data[:, 1])
plt.title('From NumPy + matplotlib')

# Or use pandas

plt.figure()
pandas_data.plot(x='x', y='x^2') # just give it the headers.
plt.title('From Pandas')

# display to the screen
plt.show()