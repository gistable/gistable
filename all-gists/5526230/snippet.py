
'''
prefix_code.py
Copyright 2012-2013 Josiah Carlson
Released under the GNU LGPL v 2.1 license

This module offers the ability to encode/decode a sequence of integers into
strings that can then be used to compare sequences of integers (or paths on
trees) quickly. This module was originally intended to be used in a case-
preserving index in a relational database (where 'Z' comes before 'a', as is
the case with binary coallation).


Methods *very similar* to this were used to handle paginated tree-structured
comments for the YouTube Groups forums (which was used from August 2009 to
December 2010). My impotice to write this code came as a result of reading the
following blog post, an realizing that I'd solved the same problem a couple
years before:

http://justcramer.com/2012/04/08/using-arrays-as-materialized-paths-in-postgres/


I don't have a name for this type of coding, though it shares some concepts
of golomb codes (specifying the length of the sub-code, while at the same time
encoding information about how many bytes are used to encode the number.

There are a few other similar ideas that could (for example) use 1 bit of
every X grouped bits to offer magnitude scaling (which would be 1 bit of every
6 bits below), but those methods do not offer the same sort of comparison
consistency that this method offers.
'''

from itertools import chain
import string

# The choice and order of these values is such that each character is sorted
# with respect to other characters, and the relative order of integers is the
# same before and after conversion to a string.
to_char = '!.' + string.digits + string.uppercase + string.lowercase
to_int = dict((k,v) for v,k in enumerate(to_char))
cutoff = len(to_char) - 11

# 0 ... cutoff-1 -> single char
# with X digits, x > 1 you can represent values:
# cutoff + len(to_char)**(X-2) - 1 to cutoff + len(to_char)**(X-1) - 1

# So with a a cutoff of 64 - 11, you can represent 0 to 2**66 + cutoff - 1


def to_chars(value):
    '''
    Converts an integer to its text-encoded form.
    '''
    if value < cutoff:
        return to_char[value]
    value -= cutoff
    out = []
    while value:
        value, rem = divmod(value, len(to_char))
        out.append(to_char[rem])
    # handle when value == cutoff
    if not out:
        out.append(to_char[value])
    out.append(to_char[cutoff + len(out) - 1])
    out.reverse()
    return ''.join(out)

def to_val(chars):
    '''
    Converts characters from the provided string back into their integer
    representation, and returns both the desired integer as well as the number
    of bytes consumed from the character string (this function can accept a
    string that is the result of a concatenation of results from to_chars() ).
    '''
    first = to_int[chars[0]]
    if first < cutoff:
        return first, 1
    first -= cutoff - 1
    dec = []
    for ch in chars[1:1+first]:
        dec.append(to_int[ch])
    value = dec.pop() + cutoff
    m = len(to_char)
    while dec:
        value += m * dec.pop()
        m *= len(to_char)
    return value, first + 1

def from_sequence(lst):
    '''
    Converts a sequence of integers into a string that represents those
    integers.
    '''
    return ''.join(map(to_chars, lst))

def from_string(str):
    '''
    Converts a string that represents a sequence of integers back into a list
    of integers.
    '''
    out = []
    i = 0
    while i < len(str):
        this, used = to_val(str[i:])
        out.append(this)
        i += used
    return out

def from_sequence_delta(lst):
    '''
    The same as from_sequence(), except that each subsequent integer has the
    previous integer subtracted from it. This can reduce data storage
    somewhat, depending on your data.

    This method requires that all subsequent values in the sequence are at
    least as large as those proceeding it. Which is to say the following are
    good sequences:
    [1, 2, 3]
    [1, 1, 1, 2, 2, 2]

    But the following are bad sequences:
    [1, 2, 3, 2]
    [1, 0]
    '''
    return from_sequence(this - prev for prev, this in zip(chain([0], lst), lst))

def from_string_delta(str):
    '''
    The reverse of from_sequence_delta().
    '''
    d = from_string(str)
    for i in xrange(1, len(d)):
        d[i] += d[i-1]
    return d

def test():
    import random
    
    for i in xrange(0, 1024, 100):
        x = [i]
        y = from_sequence(x)
        z = from_string(y)
        assert x == z, (x, y, z)
        print (x, y, z)

    x = [2**random.randrange(10) + random.randrange(128) for i in xrange(10)]
    y = from_sequence(x)
    z = from_string(y)
    assert x == z, (x, y, z)
    print (x, y, z)
    x.sort()
    y = from_sequence_s(x)
    z = from_string_s(y)
    assert x == z, (x, y, z)
    print (x, y, z)
    
    x = [2**66 + cutoff - 1]
    y = from_sequence(x)
    z = from_string(y)
    assert x == z, (x, y, z)
    print (x, y, z)

    for i in xrange(1000):
        x = [[random.randrange(10000)] for i in xrange(100)]
        y = map(from_sequence, x)
        x.sort()
        y.sort()
        z = map(from_string, y)
        assert x == z, (x, y, z)
    
    print hex(from_string('zzzzzzzzzzzz')[0] - cutoff).count('f')

if __name__ == '__main__':
    test()
