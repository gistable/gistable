import sys
import math
from random import random
from PIL import Image, ImageOps, ImageEnhance

def dot(bits):
    bits = bits & 7 | (bits & 112) >> 1 | (bits & 8) << 3 | bits & 128
    return unichr(0x2800 + bits)

class Grayscale24:
    GRAY_START = 232
    ADJUST_FACTOR = 1.6

    def prepare(self, image):
        image = ImageOps.grayscale(image)
        return ImageEnhance.Brightness(image).enhance(1 / self.ADJUST_FACTOR)

    def extract_colors(self, octet):
        c1 = self.encode(min(octet))
        c2 = self.encode(max(octet), ceil=True)

        if c1 == c2:
            c2 = max(self.GRAY_START, min(255, c2 + 1))
            if c1 == c2:
                c1 = max(self.GRAY_START, min(255, c1 - 1))

        return c1, c2

    def dist(self, v1, v2):
        return abs(v1 - v2)

    def encode(self, value, ceil=False):
        value /= 11.086
        if ceil:
            return self.GRAY_START + int(math.ceil(value))
        else:
            return self.GRAY_START + int(math.floor(value))

    def decode(self, value):
        return int((value - self.GRAY_START) * 11.086)

    def color(self, value, c1, c2):
        c1 = self.decode(c1)
        c2 = self.decode(c2)

        if self.dist(c1, c2) == 0:
            return True

        d = float(self.dist(value, c1)) / self.dist(c1, c2)
        d = 1.0 / (1 + math.exp(-5.0 * self.dist(c1, c2) / 16 * (d - 0.5)))

        return random() < d

    def calc(self, octet):
        c1, c2 = self.extract_colors(octet)

        c3 = int(c1 + (c2 - c1) * self.ADJUST_FACTOR) - self.GRAY_START
        c3 = max(0, min(23, c3))
        c3 += self.GRAY_START

        r = reduce(lambda r, i: r | self.color(octet[i], c1, c2) << i, range(8), 0)
        r = dot(r).encode('utf8')

        return c1, c3, r

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = '/usr/local/Cellar/macvim/7.3-66/MacVim.app/Contents/Resources/MacVim.icns'

if len(sys.argv) > 2:
    maxsize = int(sys.argv[2])
else:
    maxsize = 128

i = Image.open(filename)
w, h = i.size

if w > maxsize:
    w, h = maxsize, h * maxsize / w

if h > maxsize:
    w, h = w * maxsize / h, maxsize

i = ImageOps.fit(i, (w, h), Image.BICUBIC, 0, (0, 0))

g = Grayscale24()
i = g.prepare(i)

pix = i.load()

print filename
print "{0} x {1}".format(w, h)


for y in range(h/4):
    pc1, pc2 = None, None
    for x in range(w/2):
        octet = [pix[x * 2 + ((i & 4) >> 2), y * 4 + (i & 3)] for i in range(8)]

        c1, c2, r = g.calc(octet)

        if pc1 != c1:
            sys.stdout.write('\033[48;5;{0}m'.format(c1))

        if pc2 != c2:
            sys.stdout.write('\033[38;5;{0}m'.format(c2))

        sys.stdout.write(r)

        pc1, pc2 = c1, c2

    print "\033[0m"
print