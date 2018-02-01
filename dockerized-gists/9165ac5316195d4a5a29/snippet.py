def plain_to_dot(asn):  # -> str
    '''Take ASPLAIN and return ASDOT notation

    asn: int
    '''
    barray = struct.pack('>I', asn)
    return '%d.%d' % struct.unpack('>HH', barray)


def dot_to_plain(asn):  # -> int
    '''Take ASDOT and return ASPLAIN notation

    asn: string - two nums separated by period (.)
    '''
    a1, a2 = asn.split('.')
    barray = struct.pack('>HH', int(a1), int(a2))
    return struct.unpack('>I', barray)[0]


def bytesize(i):  # -> int
    '''Return bytesize'''
    return (i.bit_length() + 7) // 8
