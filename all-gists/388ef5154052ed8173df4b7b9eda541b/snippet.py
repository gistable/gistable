# ----------------------------------------------
# hashcash.py: Hashcash implementation
# ----------------------------------------------

"""
    Hashcash is a "proof of work."

    Example:
        >>> import sha
        >>> sha.new('denmark2890CF').hexdigest() '000000cf89643370c24e413ec0886ab92bd7f6e8'

    Here we have a 24-bit (6 Bytes) partial SHA collision against the zero string.

    This proves to us that someone took the prefix 'denmark', and tried about 2**24 different suffixes. Thus we know that someone has burnt around 2**24 CPU cycles on the prefix string 'denmark'. Usually, 'denmark' will be a unique challenge string, so old hashcash cannot be recycled.

    For speed, this library takes the hash of the string 'denmark' before doing the collision with the zero string. Otherwise, it is identical to the above example.

    Library examples:
        >>> import hashcash
        >>> hashcash.make_token('Denmark', 22)
        '59538D'
        >>> hashcash.verify_token('Denmark', '59538D')
        22 
        >>> t = hashcash.make_cluster('Denmark', 18)
        >>> t 'BC48-D5A1-F8C2-27F0-9CC0-DD31-2F04-2052-835-FFF1-E319-0E91-A9D0-D359-E996-70BA'
        >>> hashcash.verify_cluster('Denmark', t)
        18

    Note that make_token() takes wildly varying amounts of CPU time.
    The make_cluster() function concatenates 16 hashcash tokens to even out the amount of CPU time spent.
    
    Code originally released as Public domain at <https://bytes.com/topic/python/answers/34361-simple-hashcash-implementation> by barnesc with the disclaimer: `This document is in public domain (as are all of my past Usenet postings)`.
"""

import sha, math, itertools

def trailing_zeros(n):
    """Number of trailing 0s in binary representation of integer n."""
    if n <= 0: return 0
    for i in itertools.count(0):
        if n & (1<<i): return i

def irange(n):
    """Implementation of xrange(n) that does not overflow."""
    i = 0
    while i < n:
        yield i; i += 1

def all_strings(charset='0123456789ABCDEF'):
    """Yields all strings in given character set, sorted by length."""
    m = len(charset)
    for n in itertools.count(0):
        for i in irange(m**n):
            yield ''.join([charset[(i//(m**j))%m] for j in xrange(n)])

def hash(s):
    """Hash function used by hashcash. Returns an integer."""
    return int(sha.new(s).hexdigest(), 16)

def make_token(s, n, charset='0123456789ABCDEF'):
    """Makes hashcash token of value 'n' against basestring 's'."""
    h = sha.new(s).digest()
    for token in all_strings(charset):
        if trailing_zeros(hash(h + token)) >= n: return token

def verify_token(s, token):
    """Returns hashcash value of given token against basestring 's'."""
    return trailing_zeros(hash(sha.new(s).digest() + token))

def make_cluster(s, n, charset='0123456789ABCDEF'):
    """Makes hashcash cluster of value 'n' against basestring 's'."""
    return '-'.join([make_token(s+str(i),n-4,charset) for i in range(16)])

def verify_cluster(s, token):
    """Hashcash value of the given cluster against basestring 's'."""
    T = token.split('-')
    return min([verify_token(s+str(i), T[i]) for i in range(len(T))])+\
    int(math.log(len(T)) / math.log(2.0))

   