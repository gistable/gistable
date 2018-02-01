import re
from collections import namedtuple


ASCII_BYTE = " !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"


String = namedtuple("String", ["s", "offset"])


def ascii_strings(buf, n=4):
    reg = "([%s]{%d,})" % (ASCII_BYTE, n)
    ascii_re = re.compile(reg)
    for match in ascii_re.finditer(buf):
        yield String(match.group().decode("ascii"), match.start())

def unicode_strings(buf, n=4):
    reg = b"((?:[%s]\x00){%d,})" % (ASCII_BYTE, n)
    uni_re = re.compile(reg)
    for match in uni_re.finditer(buf):
        try:
            yield String(match.group().decode("utf-16"), match.start())
        except UnicodeDecodeError:
            pass


def main():
    import sys

    with open(sys.argv[1], 'rb') as f:
        b = f.read()

    for s in ascii_strings(b, n=4):
        print('0x{:x}: {:s}'.format(s.offset, s.s))

    for s in unicode_strings(b):
        print('0x{:x}: {:s}'.format(s.offset, s.s))


if __name__ == '__main__':
    main()
