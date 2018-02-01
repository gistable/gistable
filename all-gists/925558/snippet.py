"""
An implementation of binary search, based on the challanges in the following blog posts:

http://googleresearch.blogspot.com/2006/06/extra-extra-read-all-about-it-nearly.html
http://reprog.wordpress.com/2010/04/19/are-you-one-of-the-10-percent/
http://www.solipsys.co.uk/new/BinarySearchReconsidered.html?tw

This was not my first attempt however, there was a broken version (of course)
that I wrote prior to running it for the first time. Sadly I didn't take a
snapshot before I fixed it but the bug was fairly major; although I'd worked
out correctly the various cases it didn't actually cut down the search space at
each step or return the correct value following each iteration.

Note that this and the original version are both robust against the integer
overflow bug described in the above blog posts.

This implementation assumes that the list doesn't contain (contiguous) duplicates.
"""

import random

# For consistency and reproducability choose a particular seed value
random.seed(1)

# Create a randomly generate list of items
# Note that these won't contain duplicates
samplesize = 100
samplelist = random.sample(range(10000),  samplesize)

# Ensure that the list is sorted before operating on it
samplelist.sort()

def chop(sourcelist, min_i, max_i, finditem):
    """ Returns either the index of the item to be found or None, indicating that
    the item could not be found in the given range.
    
    Assumes that x has been sorted prior to running the search
    """

    # For debug
    print "min: %s max: %s" % (min_i, max_i)
    
    # Determine the length of list
    y = (max_i - min_i)

    # The two cases to consider involve the length being either odd or even
    if y % 2 == 0:
        # The range length is even
        if y > 3:
            if sourcelist[min_i + (y / 2)] >= finditem:
                return chop(sourcelist, min_i, min_i + (y / 2), finditem)
            elif sourcelist[min_i + (y / 2) + 1] <= finditem:
                return chop(sourcelist, min_i + (y / 2) + 1, max_i, finditem)
        elif sourcelist[min_i] == finditem:
            return min_i
        elif sourcelist[max_i] == finditem:
            return max_i
        else:
            return None
    elif min_i == max_i:
        # The range length is exactly 1
        if sourcelist[min_i] == finditem:
            return min_i
        else:
            return None
    else:
        # The range length is odd and greater than 2
        if sourcelist[min_i + (y / 2)] >= finditem:
            return chop(samplelist, min_i, min_i + (y/2), finditem)
        elif sourcelist[ max_i - (y/2)] <= finditem:
            return chop(samplelist, max_i - (y/2), max_i, finditem)
        elif sourcelist[min_i + (y/2) + 1] == finditem:
            return min_i
        else:
            return None

# Test the binary search algorithm on random sample, with an item known to be
# in the list
print samplelist

targetval = samplelist[random.randint(1, samplesize)]
print targetval

print chop(samplelist, 0, len(samplelist) - 1, targetval)
