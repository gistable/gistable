
"""
DCPU Font converter.
Written by Daniel Keep <daniel.keep@gmail.com>.

Released under the MIT license.

"""

from PIL import Image

font_b = Image.open("font.png").convert("1")

glyphs = []

for i in range(128):
    x = i % 32
    y = i // 32

    cols = [0, 0, 0, 0]

    px = x * 4
    py = y * 8

    for col in range(4):
        colv = 0
        for row in range(8):
            pv = font_b.getpixel((px+col,py+row)) & 1
            colv = colv | (pv << row)

        cols[col] = colv

    print "%r:\t%r" % (chr(i),
                          ["%08s" % bin(w)[2:] for w in cols])

    glyph = (cols[1] | (cols[0] << 8), cols[3] | (cols[2] << 8))
    glyphs.append(glyph)

#
# Output
#

with open("font.dasm", "wt") as f:
    for line in __doc__.splitlines():
        f.write("; %s\n" % line)

    for i,glyph in enumerate(glyphs):
        f.write("dat 0x%04x, 0x%04x ; '%r'\n" % (glyph[0], glyph[1], chr(i)))

with open("font.bin", "wb") as f:
    for i,glyph in enumerate(glyphs):
        for word in glyph:
            f.write(chr(word & 0xFF))
            f.write(chr(word >> 8))
