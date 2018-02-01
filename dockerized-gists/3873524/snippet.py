"""
Simple Linear Probabilistic Counters

Credit for idea goes to:
http://highscalability.com/blog/2012/4/5/big-data-counting-how-to-count-a-billion-distinct-objects-us.html
http://highlyscalable.wordpress.com/2012/05/01/probabilistic-structures-web-analytics-data-mining/

Installation:
    pip install smhasher
    pip install bitarray
"""
import smhasher
import math
import itertools
from bitarray import bitarray


class LPCounter(object):
    """
    Real Time Linear Probabilistic Counter of Unique Items
    """

    def __init__(self, max_space):
        """
        Initializes the counter, max_space is the maximum amount of memory
        (in KB) you want to use to maintain your counter, more memory=more
        accurate
        """
        self.bit_map = bitarray(8 * 1024 * max_space)
        self.bit_map.setall(False)

    def current_count(self):
        """
        Gets the current value of the bitmap, to do that we follow the formula:
        -size * ln(unset_bits/size)
        """
        ratio = float(self.bit_map.count(False)) / float(self.bit_map.length())
        if ratio == 0.0:
            return self.bit_map.length()
        else:
            return -self.bit_map.length() * math.log(ratio)

    def increment(self, item):
        """
        Counts an item
        """
        mm_hash = smhasher.murmur3_x64_128(str(item))
        offset = mm_hash % self.bit_map.length()
        self.bit_map[offset] = True

if __name__ == '__main__':
    def run_counts(tries, size):
        """Run some counts"""
        lpc = LPCounter(size)
        print "%d Kilobyte Bitmap" % size
        print "  Incrementing %d items" % tries
        for i in itertools.count(0):
            if i > tries:
                break

            lpc.increment(i)
        count = lpc.current_count()
        print "  Count:  %d" % count
        print "  Actual: %d" % tries
        print "  Error:  %f%%" % abs((1 - (float(count) / float(tries))) * 100)

    run_counts(1000000000, 16384)
