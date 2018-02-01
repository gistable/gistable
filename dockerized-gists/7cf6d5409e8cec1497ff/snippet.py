"""
Convert between various representations of an IPv4 address.

`ip` refers to a dotted string, like: `'127.0.0.1'`.
`octets` are indexables, like `(127, 0, 0, 1)`.
`int` is the integer representation, like `2130706433`.

Written for Python 2.7.
"""

import itertools


def ip_to_octets(ip):
    return map(int, ip.split('.'))


def octets_to_ip(octets):
    return '.'.join(map(str, octets))


def octets_to_int(octets):
    return (
        (octets[0] << 24) ^
        (octets[1] << 16) ^
        (octets[2] <<  8) ^
        (octets[3] <<  0)
    )


def int_to_octets(int_):
    return (
        (int_ >> 24) & 0xff,
        (int_ >> 16) & 0xff,
        (int_ >>  8) & 0xff,
        (int_ >>  0) & 0xff,
    )


def int_to_ip(int_):
    return octets_to_ip(int_to_octets(int_))


def ip_to_int(ip):
    """
    Return the integer representation of a dotted IPV4 address.

    Useful for comparisons and as a sort key. For example, the expression:

        sorted(['0.0.0.100', '0.0.0.20', '0.0.0.3'], key=ip_to_int)

    puts '0.0.0.20' in the middle instead of at the end, which a naive sort
    would do.
    """
    return octets_to_int(ip_to_octets(ip))


def ip_range(start_ip, end_ip):
    """
    Return an iterator of the IP addresses between `start_ip` and `end_ip`,
    inclusive.
    """
    start_int = ip_to_int(start_ip)
    end_int = ip_to_int(end_ip)

    # CPython's `xrange` is implemented with unsigned longs and overflows when
    # used with IP addresses greater than 127.255.255.255.
    int_range = itertools.islice(
        itertools.count(start_int),
        end_int - start_int + 1
    )

    ip_range = itertools.imap(int_to_ip, int_range)
    return ip_range