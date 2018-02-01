#!/usr/bin/env python

"""
Convert camel-case to snake-case in python.

e.g.: CamelCase -> snake_case

Relevant StackOverflow question: http://stackoverflow.com/a/1176023/293064
"""

__author__ = 'Jay Taylor [@jtaylor]'


import re


_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')

def camelToSnake(s):
    """ 
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()

if __name__ == '__main__':
    assert camelToSnake('snakesOnAPlane') == 'snakes_on_a_plane'
    assert camelToSnake('SnakesOnAPlane') == 'snakes_on_a_plane'
    assert camelToSnake('snakes_on_a_plane') == 'snakes_on_a_plane'
    assert camelToSnake('IPhoneHysteria') == 'i_phone_hysteria'
    assert camelToSnake('iPhoneHysteria') == 'i_phone_hysteria'
    print 'All tests passed.'