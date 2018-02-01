import sys


def to_octets(ip):
    return [int(i) for i in ip.split('.')]


def dotless_decimal(ip):
    octets = to_octets(ip)
    result = octets[0] * 16777216 + octets[1] * \
        65536 + octets[2] * 256 + octets[3]
    return result


def dotted_hex(ip):
    octets = to_octets(ip)
    hex_octets = [hex(i) for i in octets]
    result = '.'.join([str(i) for i in hex_octets])
    return result


def dotless_hex(ip):
    ip = dotless_decimal(ip)
    result = hex(int(ip))
    return result


def dotted_octal(ip):
    octets = to_octets(ip)
    result = '.'.join([str(oct(i)).replace('o', '') for i in octets])
    return result


def print_dotted_hex(ip):
    d_x = dotted_hex(ip)
    print('dotted hex: %s' % d_x)
    if '.0x0.0x0.' in d_x:  # check if the two middle octets == 0
        octets = d_x.split('.')
        s = octets[0] + '.' + octets[-1]
        print('dotted hex without zero octets: %s' % s)


def print_dotted_octal(ip):
    d_o = dotted_octal(ip)
    print('dotted octal:    %s' % d_o)
    if '.00.00.' in d_o:
        octets = d_o.split('.')
        s = octets[0] + '.' + octets[-1]
        print('dotted octal without zero octets: %s' % s)


def usage():
    print('Usage: python3 ip_encoder.py ip <encoding>\nencodings:\
        \n\tdl-d\n\thex\n\tdl-hex\n\toct\n\tall')
    sys.exit()


def main():
    if len(sys.argv) < 3:
        usage()
    ip = sys.argv[1]
    encoding = sys.argv[2]
    if encoding == 'dl-d':
        print('dotless decimal: %s' % dotless_decimal(ip))
    elif encoding == 'hex':
        print_dotted_hex(ip)
    elif encoding == 'dl-hex':
        print('dotless hex: %s' % dotless_hex(ip))
    elif encoding == 'oct':
        print_dotted_octal(ip)
    elif encoding == 'all':
        print('dotless decimal: %s' % dotless_decimal(ip))
        print_dotted_hex(ip)
        print('dotless hex: %s' % dotless_hex(ip))
        print_dotted_octal(ip)
    else:
        usage()


if __name__ == '__main__':
    main()
