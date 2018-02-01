#!/usr/bin/env python
# Knuth-Morris-Pratt demonstration
# Kyle Gorman <kgorman@ling.upenn.edu>
#
# A naive Python implementation of a function that returns the (first) index of
# a sequence in a supersequence is the following:

def subsequence(needle, haystack):
    """
    Naive subsequence indexer; None if not found

    >>> needle = 'seven years ago'.split()
    >>> haystack = 'four score and seven years ago our fathers'.split()
    >>> print subsequence(needle, haystack)
    3
    """
    for i in xrange(len(haystack) - len(needle) + 1):
        if needle == haystack[i:i + len(needle)]: return i


# The outer loop runs |haystack| - |needle| times in the worst case, and the
# (implicit) inner loop results in complexity O(|needle| * (|haystack| - 
# |needle|). Knuth, Morris, and Pratt (1977) develop a method which requires
# a fixed cost per "needle", plus O(|haystack|) worst-case search, for total
# worst-case time complexity O(2|needle| + |haystack|). The following class 
# implements this method.

class KMP(object):
    """
    Efficient subsequence indexer; returns None if not found

    >>> needle = 'seven years ago'.split()
    >>> haystack = 'four score and seven years ago our fathers'.split()
    >>> print KMP(needle).search_in(haystack)
    3
    """

    def __init__(self, needle):
        self.needle = needle
        self.table = [1] * (len(needle) + 1)
        shift = 1
        for index, obj in enumerate(needle):
            while shift <= index and obj != needle[index - shift]:
                shift += self.table[index - shift]
            self.table[index + 1] = shift

    def __repr__(self):
        return 'KMP(%r)' % needle

    def search_in(self, haystack):
        index = 0
        match = 0
        while index + match < len(haystack):
            if self.needle[match] == haystack[index + match]:
                match += 1
                if match == len(self.needle): return index
            else:
                if match == 0: index += 1
                else:
                    index += match - self.table[match]


## run tests
if __name__ == '__main__':
    import doctest
    doctest.testmod()