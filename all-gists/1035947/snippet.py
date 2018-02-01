#!/usr/bin/env python
#
# Copyright (C) 2011 by Ben Noordhuis <info@bnoordhuis.nl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

TMIN = 1
TMAX = 26
BASE = 36
SKEW = 38
DAMP = 700 # initial bias adaptation
INITIAL_N = 128
INITIAL_BIAS = 72

assert 0 <= TMIN <= TMAX <= (BASE - 1)
assert 1 <= SKEW
assert 2 <= DAMP
assert (INITIAL_BIAS % BASE) <= (BASE - TMIN) # always true if TMIN=1

class Error(Exception):
    pass

def basic(c):
    return c < 128

def encode_digit(d):
    return d + (97 if d < 26 else 22)

def decode_digit(d):
    if d >= 48 and d <= 57:
        return d - 22 # 0..9
    if d >= 65 and d <= 90:
        return d - 65 # A..Z
    if d >= 97 and d <= 122:
        return d - 97 # a..z
    raise Error('Illegal digit #%d' % d)

def next_smallest_codepoint(non_basic, n):
    m = 0x110000 # Unicode's upper bound + 1
    for c in non_basic:
        if c >= n and c < m:
            m = c
    assert m < 0x110000
    return m

def adapt_bias(delta, n_points, is_first):
    # scale back, then increase delta
    delta //= DAMP if is_first else 2
    delta += delta // n_points

    s = (BASE - TMIN)
    t = (s * TMAX) // 2 # threshold=455
    k = 0

    while delta > t:
        delta //= s
        k += BASE

    a = (BASE - TMIN + 1) * delta
    b = (delta + SKEW)

    return k + (a // b)

def threshold(k, bias):
    """Calculate the new threshold."""
    if k <= bias + TMIN:
        return TMIN
    if k >= bias + TMAX:
        return TMAX
    return k - bias

def encode_int(bias, delta):
    """Encode bias and delta to a generalized variable-length integer."""
    result = []

    k = BASE
    q = delta

    while True:
        t = threshold(k, bias)
        if q < t:
            result.append(encode_digit(q))
            break
        else:
            c = t + ((q - t) % (BASE - t))
            q = (q - t) // (BASE - t)
            k += BASE
            result.append(encode_digit(c))

    return result


def encode(input):
    """Encode Unicode string to Punycode. Returns an ASCII string.

    >>> encode('\xc3\xbc'.decode('utf-8'))
    'tda'
    >>> encode('Goethe'.decode('utf-8'))
    'Goethe-'
    >>> encode('B\xc3\xbccher'.decode('utf-8'))
    'Bcher-kva'
    >>> encode('Willst du die Bl\xc3\xbcthe des fr\xc3\xbchen, die Fr\xc3\xbcchte des sp\xc3\xa4teren Jahres'.decode('utf-8'))
    'Willst du die Blthe des frhen, die Frchte des spteren Jahres-x9e96lkal'

    """

    input = [ord(c) for c in input]
    output = [c for c in input if basic(c)]
    non_basic = [c for c in input if not basic(c)]

    # remember how many basic code points there are 
    b = h = len(output)

    if output:
        output.append(ord('-'))

    n = INITIAL_N
    bias = INITIAL_BIAS
    delta = 0

    while h < len(input):
        m = next_smallest_codepoint(non_basic, n)
        delta += (m - n) * (h + 1)
        n = m

        for c in input:
            if c < n:
                delta += 1
                assert delta > 0
            elif c == n:
                output.extend(encode_int(bias, delta))
                bias = adapt_bias(delta, h + 1, b == h)
                delta = 0
                h += 1

        delta += 1
        n += 1

    return ''.join(chr(c) for c in output)

def decode(input):
    '''code Punycode string to Unicode. Returns a Unicode string.

    >>> decode('tda')
    u'\\xfc'
    >>> decode('Goethe-')
    u'Goethe'
    >>> decode('Bcher-kva')
    u'B\\xfccher'
    >>> decode('Willst du die Blthe des frhen, die Frchte des spteren Jahres-x9e96lkal')
    u'Willst du die Bl\\xfcthe des fr\\xfchen, die Fr\\xfcchte des sp\\xe4teren Jahres'

    '''

    try:
        b = 1 + input.rindex('-')
    except ValueError:
        b = 0

    input = [ord(c) for c in input]
    output = input[:b - 1] if b else []

    i = 0
    n = INITIAL_N
    bias = INITIAL_BIAS

    while b < len(input):
        org_i = i
        k = BASE
        w = 1

        while True:
            d = decode_digit(input[b])
            b += 1

            # TODO overflow check
            i += d * w

            t = threshold(k, bias)
            if d < t:
                break

            # TODO overflow check
            w *= BASE - t
            k += BASE

        x = 1 + len(output)
        bias = adapt_bias(i - org_i, x, org_i == 0)
        # TODO overflow check
        n += i // x
        i %= x
        output.insert(i, n)
        i += 1

    return ''.join(unichr(c) for c in output)

if __name__ == '__main__':
    import doctest
    doctest.testmod()