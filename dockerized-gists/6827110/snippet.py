from collections import Counter
from bitarray import bitarray

HISTOGRAM_RANGE = 16
CHAR_RANGE = 3

def string_to_charc_codes(s):
    return map(ord, list(s))

def char_codes_to_modulo(chars_codes):
    return map(lambda x : x % HISTOGRAM_RANGE, chars_codes)

def int_to_bitarray(n):
    return bitarray([n >> i & 1 for i in range(CHAR_RANGE, -1, -1)])

def bitarray_to_int(a):
    result = 0
    for bit in a:
        result = (result << 1) | bit
    return result

'''
returns a character distribution histogram for for a  string s:
you take a 64-bit long, split it up into 16 sets of 4 bits, and then compute the number of characters
that are X modulo 16 for X = 0...15. For example, in the string "hello", the ASCII values of characters are
104, 101, 108, 108, 111, which are 8, 5, 12, 12, 15 modulo 16. In a 64-bit long, "hello" would thus correspond
to a 0001 in the 9th, 6th, and 16th sets of 4 bits, a 0010 in the 13th set, and a 0000 in every other set of 4 bits

source:
http://www.quora.com/Algorithms/Which-is-the-best-programming-algorithm-that-you-have-ever-created/answer/Leo-Polovets
'''
def histogram(s):
    cnt = Counter(char_codes_to_modulo(string_to_charc_codes(s)))
    return reduce(lambda x, y: x+y, [int_to_bitarray(cnt[i]) for i in range(HISTOGRAM_RANGE)])


'''
returns lower bound to Levensthein distance for two strings s1, s2;
a and b are calculated from s1, s2 with the histogram(s) function;
a and ab are not calculated here, because they should be precalculated.
Algo:
    1/2 * Sum(absolute value(a[i]-b[i])) for i = 0...15
    + 1/2 * (absolute value of L1 - L2)

The intuitive explanation is that let's say you have 4 'a's in one string and 0 'a's in another string.
You would have to delete/replace 4 characters to get the 'a' disparity to go away
(e.g. you could delete the 4 'a's in the first string, or you could replace 4 characters in the second string with 'a',
or you could insert 4 'a's into the second string.)
This is a lower bound on the distance, but you also have to divide it by two because you're double counting
(e.g. if you have AAAA vs BBBB, and you decide to replace the 4 'A's with 'B's, that fixes the 'A' disparity
AND the 'B' disparity with just 4 changes).

Finally, if one string is longer than another, you have to compensate for that. For example, AA vs AAAA has a disparity
of 2 'A's and a disparity of 2 in the length, so the minimum distance is (2 + 2)/2 = 2.
(Here, adding 2 'A's fixes the 'A' disparity AND the length disparity.)

credits:
http://www.quora.com/Leo-Polovets

source:
http://www.quora.com/Algorithms/Which-is-the-best-programming-algorithm-that-you-have-ever-created/answer/Leo-Polovets/comment/2798400?srid=XTj&share=1
'''
def lower_bound(s1, s2, a, b):
    return 0.5 * sum([abs(bitarray_to_int(a[i:i+4]) - bitarray_to_int(b[i:i+4])) \
                      for i in range(0, HISTOGRAM_RANGE*4, 4)]) \
        + 0.5 * abs(len(s1) - len(s2))


'''
used for testing, source:
https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
'''
def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:])+(a[0] != b[0]), lev(a[1:], b)+1, lev(a, b[1:])+1)

test_cases = [('AABB', 'BBAA'), ('asdfg', 'aswfg'), ('aaaaa', 'bbbbb'), ('abbba', 'abbaa'), ('aaaa', 'bbb'), ('aaa', 'aaab'), ('aaaa', 'aaab'), ('abbba', 'abbca')]


for case in test_cases:
    print case[0], case[1], lev(case[0], case[1]), lower_bound(case[0], case[1], histogram(case[0]), histogram(case[1]))
