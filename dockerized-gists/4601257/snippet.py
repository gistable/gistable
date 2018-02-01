from rtree import index
from random import random
from datetime import datetime

timer = datetime.now()

# Create 10,000,000 random numbers between 0 and 1
rands = [random() for i in range(10000000)] 

# Function required to bulk load the random points into the index
# Looping over and calling insert is orders of magnitude slower than this method
def generator_function():
    for i, coord in enumerate(rands):
        yield (i, (coord, coord+1, coord, coord+1), coord)

# Add points
tree = index.Index(generator_function())

print (datetime.now()-timer).seconds # How long did it take to add the points
print list(tree.nearest((rands[50], rands[50], rands[50], rands[50]), 3))
print (datetime.now()-timer).seconds # How long did it take to query for the nearest 3 points