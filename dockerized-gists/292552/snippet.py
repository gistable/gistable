#!/usr/bin/python -u

"""
Python port of PHP serialize() and unserialize()
by Samuel Cochran <sj26@sj26.com>

I couldn't find a nice, fairly efficient implementation of serialize/unserialize for Python... so I wrote one. I didn't use str().partition because I wanted Python <2.5 compatibility.

TODO: Performance review. There's an awful lot of string copying. >.>

TODO: Something about PHP classes? Allow provision of class mappings for instantiation perhaps? Serialize via inspection of __dict__, unserialize using object.__new__(Class). Respect __slots__?

    >>> import time
    >>> class PythonClass(object):
    ...   def __init__(self, name):
    ...     self.name = name
    ...     self.created = time.time()
    ...   def __repr__(self):
    ...     return '%s(%r)' % (self.__class__.__name__, self.name)
    ... 
    >>> unserialize('O:9:"PHP_Class":{s:4:"name";s:2:"me";s:7:"created";d:1265106362.149045;};', classes={'PHP_Class': PythonClass})
    PythonClass('me')
    >>> _.created
    1265106362.149045
    >>> serialize(PythonClass('them'), classes={PythonClass: 'PHP_Class'})
    'O:9:"PHP_Class":{s:4:"name";s:4:"them";s:7:"created";d:1265106400.630085;};'

TODO: More helpful messages about PHP resources? Ability to ignore them?
"""

__all__ = ('serialize', 'unserialize')

# Do we have a decimal type?
_floats = (long, float)
if 'decimal' in dir(__builtins__):
    _floats += (decimal,)

def serialize(v):
    ''' Serialize Python data into a PHP serialized string.
    
    Acccepted types: None, str, unicode, int, float, long, decimal (if available), list, typle, dict.
    '''
    if v is None:
        return 'N;'
    elif isinstance(v, basestring):
        # TODO: utf8 casting and encoding
        return 's:%d:"%s";' % (len(v), v)
    elif isinstance(v, bool):
        return 'b:%d;' % (int(v),)
    elif isinstance(v, int):
        return 'i:%s;' % (v,)
    elif isinstance(v, _floats):
        return 'd:%s;' % (v,)
    elif isinstance(v, (dict, list, tuple)):
        return 'a:%d:{%s};' % (len(v), ''.join(serialize(k) + serialize(v) for (k, v) in (isinstance(v, dict) and v.iteritems() or enumerate(iter(v)))))
    # TODO: Objects?
    else:
        raise TypeError('Cannot serialize type %r.' % (type(v),))

def unserialize(s, array=list, hasharray=dict):
    ''' Unserializes a PHP serialized string into Python data.
    
    array=tuple: turn 0-indexed PHP arrays into tuples instead of lists.
    array=False: Return a list of (key, value) tuples for all PHP arrays.
    
    You can also emulate PHP's array which is actually an ordered map. 
    For instance, using the one supplied in Python 2.7+:
    hasharray=collections.OrderedDict
    '''
    if not isinstance(s, basestring):
        raise TypeError('Serialized value should be str or unicode, not %r.' % (type(s),))
    v, s = _unserialize(s, array, hasharray)
    if s:
        raise ValueError('Extra data after serialized value: %r' % (s,))
    return v
    
def _unserialize(s, array=list, hasharray=dict):
    ''' Unserialize a single value from the head of a serialized string.
    
    array=tuple: turn 0-indexed PHP arrays into tuples instead of lists.
    array=False: Return a list of (key, value) tuples for all PHP arrays.
    
    Returns (value, tail)
    '''
    if s.startswith('N;'):
        return None, s[2:]
    elif s.startswith('b:'):
        v, s = s[2:].split(';', 1)
        return bool(int(v)), s
    elif s.startswith('i:'):
        v, s = s[2:].split(';', 1)
        return int(v), s
    elif s.startswith('d:'):
        v, s = s[2:].split(';', 1)
        return float(v), s
    elif s.startswith('s:'):
        s = s[2:]
        l, s = s.split(':', 1)
        l = int(l)
        if l > len(s) - 3:
            raise ValueError('String length %d is too long for serialized data, length %d.' % (l, len(s)))
        elif s[0] != '"':
            raise ValueError('Missing opening quote after string, found %r.' % (s[0],))
        elif s[l+1:l+3] != '";':
            raise ValueError('Missing closing quote and semi-colon after string, found %r.' % (s[l+1:l+3],))
        return s[1:l+1], s[l+3:]
    elif s.startswith('a:'):
        s = s[2:]
        l, s = s.split(':', 1)
        l = int(l)
        if s[0] != '{':
            raise ValueError('Missing opening curly brace before array contents, found %r.' % (s[i+2],))
        s = s[1:]
        a, d = list(), False
        for i in xrange(0, l):
            k, s = _unserialize(s, array, hasharray)
            if array and not d and k != i:
                a, d = dict(enumerate(iter(a))), True
            v, s = _unserialize(s, array, hasharray)
            if not array:
                a.append((k, v))
            elif d:
                a[k] = v
            else:
                a.append(v)
        if array is tuple and not d:
            a = array(a)
        if s[0:2] != '};':
            raise ValueError('Missing closing curly brace and semicolon after array contents, found %r.' % (s[0:2],))
        return a, s[2:]
    else:
        raise ValueError('Cannot unserialize %r.' % (s,))

if __name__ == '__main__':
    import sys, traceback
    
    tests = [
        (None, 'None'),
        (True, 'True'),
        (False, 'False'),
        ('', 'Empty string'),
        ('test', 'Non-empty string'),
        (0, 'Zero Integer'),
        (10, 'Positive integer'),
        (-10, 'Negative integer'),
        (0.0, 'Zero float'),
        (10.01, 'Positive float'),
        (-10.01, 'Negative float'),
        ]
    if 'decimal' in locals():
        tests += [
            (decimal('0.0'), 'Zero decimal'),
            (decimal('10.01'), 'Positive decimal'),
            (decimal('-10.01'), 'Negative decimal'),
            ]
    tests += [
        (object(), 'Object (should fail)', ),
        (object, 'Class (should fail)', ),
        ((), 'Empty tuple'),
        ((0,), 'Single-valued tuple'),
        ((0, 1, 2, 3), 'Multi-valued tuple'),
        ([], 'Empty list'),
        ([0], 'Single-valued list'),
        ([0, 1, 2, 3], 'Multi-valued list'),
        (dict(), 'Empty dict'),
        (dict(one=1), 'Single-valued dict'),
        (dict(one=1, two=2, three=3), 'Multi-valued dict'),
        ]
        
    for (test, description) in tests:
        try:
            print description + ':', repr(test),
            s = serialize(test)
            print repr(s),
            u = unserialize(s)
            print repr(u), test == u and 'ok.' or 'failed.'
        except:
            print 'failed:'
            print '  ' + '\n  '.join(traceback.format_exc().splitlines())
