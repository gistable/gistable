#!/usr/bin/env python
from random import randint
from fileinput import input
from argparse import ArgumentParser
from sys import stdout

# "data set of leet unicode chars" stolen from
# Tchouky's Zalgo Generator on eeemo.net


class Zalgo(object):
    zalgo_table = {
        "up": {
            "chars": [
                0x30d, 0x30e, 0x304, 0x305, 0x33f, 0x311, 0x306, 0x310,
                0x352, 0x357, 0x351, 0x307, 0x308, 0x30a, 0x342, 0x343,
                0x344, 0x34a, 0x34b, 0x34c, 0x303, 0x302, 0x30c, 0x350,
                0x300, 0x301, 0x30b, 0x30f, 0x312, 0x313, 0x314, 0x33d,
                0x309, 0x363, 0x364, 0x365, 0x366, 0x367, 0x368, 0x369,
                0x36a, 0x36b, 0x36c, 0x36d, 0x36e, 0x36f, 0x33e, 0x35b,
                0x346, 0x31a
            ],
            "min": -5,
            "max": 1
        },
        "down": {
            "chars": [
                0x316, 0x317, 0x318, 0x319, 0x31c, 0x31d, 0x31e, 0x31f,
                0x320, 0x324, 0x325, 0x326, 0x329, 0x32a, 0x32b, 0x32c,
                0x32d, 0x32e, 0x32f, 0x330, 0x331, 0x332, 0x333, 0x339,
                0x33a, 0x33b, 0x33c, 0x345, 0x347, 0x348, 0x349, 0x34d,
                0x34e, 0x353, 0x354, 0x355, 0x356, 0x359, 0x35a, 0x323
            ],
            "min": -2,
            "max": 4
        },
        "mid": {
            "chars": [
                0x315, 0x31b, 0x340, 0x341, 0x358, 0x321, 0x322, 0x327,
                0x328, 0x334, 0x335, 0x336, 0x34f, 0x35c, 0x35d, 0x35e,
                0x35f, 0x360, 0x362, 0x338, 0x337, 0x361, 0x489
            ],
            "min": -2,
            "max": 2
        }
    }
    encoding = 'utf-8'

    def Zalgo(self, **kwargs):
        pass

    def zalgoify(self, text):
        out = u''
        for i in xrange(len(text)):
            c = text[i]
            if ' \n\t'.find(c) > -1:
                out += c
            else:
                out += self.zalgo_char(c)
        return out.encode(self.encoding)

    def zalgo_char(self, char):
        out = unicode(char, self.encoding)
        for type in self.zalgo_table:
            t = self.zalgo_table[type]
            cc = randint(t['min'], t['max'])
            if cc > 0:
                for n in xrange(cc):
                    out += unichr(t['chars'][randint(0, len(t['chars']) - 1)])
        return out


if __name__ == "__main__":
    parser = ArgumentParser(description='He comes.')
    parser.add_argument('files', nargs='?', default=[], help='Files to zalgo, or stdin')
    args = parser.parse_args()

    z = Zalgo()
    for line in input(files=args.files):
        stdout.write(z.zalgoify(line))
