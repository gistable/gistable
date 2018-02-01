#-*- coding:utf-8 -*-
# Author: @chuangbo
# For: @likexian

import socket
import struct

class CIDR:
    '''Check if ip in cidr

    >>> '8.8.8.8' in CIDR('8.8.8.8', 8)
    True
    >>> '8.8.7.8' in CIDR('8.8.8.8', 8)
    False
    '''
    
    # bin(_MASK) = 0b11111111111111111111111111111111，32位1
    _MASK = (1 << 32) - 1

    def __init__(self, ip, mask):
        ip = self.ip2int(ip)
        mask = self._MASK << mask
        self.cidr = ip & mask

    @staticmethod
    def ip2int(str):
        return struct.unpack("!I",socket.inet_aton(str))[0]

    def __contains__(self, ip):
        return self.ip2int(ip) & self.cidr == self.cidr


if __name__ == '__main__':
    import doctest
    doctest.testmod()