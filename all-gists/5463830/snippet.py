#!/usr/bin/env python
# coding=utf-8
import argparse
import freetype
import os
import re
import struct
import sys
import itertools
from math import ceil

# Font
#   FontInfo
#       (uint8_t)  version
#       (uint8_t)  max_height
#       (uint16_t) number_of_glyphs
#   (uint32_t) offset_table[]
#       this table contains offsets into the glyph_table for characters 0x20 to 0xff
#       each offset is counted in 32-bit blocks from the start of the glyph
#       table. 16-bit offsets are keyed by 16-bit codepoints.
#       packed:     (uint_16) codepoint
#                   (uint_16) offset
#
#   (uint32_t) glyph_table[]
#       [0]: the 32-bit block for offset 0 is used to indicate that a glyph is not supported
#       then for each glyph:
#       [offset + 0]  packed:   (int_8) offset_top
#                               (int_8) offset_left,
#                              (uint_8) bitmap_height,
#                              (uint_8) bitmap_width (LSB)
#
#       [offset + 1]           (int_8) horizontal_advance
#                              (24 bits) zero padding
#         [offset + 2] bitmap data (unaligned rows of bits), padded with 0's at
#         the end to make the bitmap data as a whole use multiples of 32-bit
#         blocks

# Set a codepoint that the font doesn't know how to render
# The watch will use this glyph as the wildcard character
WILDCARD_CODEPOINT = 0x3f
ELLIPSIS_CODEPOINT = 0x2026
# ASCII codepoints: 0x20-0x7e      95
# Latin-1 Supplement: 0x80-0xff   128
# Latin-1 Extend A: 0x100-0x17f   128
# Latin-1 Extend A: 0x180-0x24f   208
# Spacing Modifier: 0x2b0-0x2ff    80
# diacritical marks 0x300-0x36f   112
# Greek and Copic : 0x370-0x3ff   144
# Cyrillic        : 0x400-0x4ff   256
# Russian:          410-44f, 401+451, 72
# General Punctuation: 0x2000-0x206f 

## generate codepoints 

# Basic ASCII
codepoints = list(range(0x20, 0x7f))
# Russian
codepoints.extend(list(range(0x410, 0x450))) 
# Ё ё
codepoints.append(0x401)
codepoints.append(0x451)
codepoints.append(ELLIPSIS_CODEPOINT)

codepoints.sort()

MIN_CODEPOINT = 0x20
MAX_CODEPOINT = 0xffff


def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

class Font:
    def __init__(self, ttf_path, height):
        self.version = 1
        self.ttf_path = ttf_path
        self.max_height = int(height)
        self.face = freetype.Face(self.ttf_path)
        self.face.set_pixel_sizes(0, self.max_height)
        self.name = self.face.family_name + "_" + self.face.style_name
        self.wildcard_codepoint = WILDCARD_CODEPOINT
        self.number_of_glyphs = 0
        self.tracking_adjust = 0
        self.regex = None
        return

    def set_tracking_adjust(self, adjust):
        self.tracking_adjust = adjust
    def set_regex_filter(self, regex_string):
        if regex_string != ".*":
            try:
                self.regex = re.compile(regex_string)
            except Exception, e:
                raise Exception("Supplied filter argument was not a valid regular expression.")
        else:
            self.regex = None
    def is_supported_glyph(self, codepoint):
        return (self.face.get_char_index(codepoint) > 0 or (codepoint == unichr(self.wildcard_codepoint)))

    def glyph_bits(self, codepoint):
        self.face.load_char(codepoint)
        if not self.is_supported_glyph(codepoint):
            return None

        # Font metrics
        bitmap = self.face.glyph.bitmap
        advance = self.face.glyph.advance.x / 64     # Convert 26.6 fixed float format to px
        advance += self.tracking_adjust
        width = bitmap.width
        height = bitmap.rows
        left = self.face.glyph.bitmap_left
        bottom = self.max_height - self.face.glyph.bitmap_top

        glyph_structure = ''.join((
            '<',  #little_endian
            'B',  #bitmap_width
            'B',  #bitmap_height
            'b',  #offset_left
            'b',  #offset_top
            '3B', #zero_padding
            'b'   #horizontal_advance
            ))
        glyph_header = struct.pack(glyph_structure, width, height, left, bottom, 0, 0, 0, advance)

        # Iterate through the glyph's bitmap:
        glyph_bitmap = []
        for word in grouper(32, bitmap.buffer, 0):
            w = 0
            for index, px in enumerate(word):
                value = 1 if (px > 127) else 0
                w |= value << (index)
            glyph_bitmap.append(struct.pack('<I', w))

        return glyph_header + ''.join(glyph_bitmap)

    def fontinfo_bits(self):
        return struct.pack('<BBHH',
                           self.version,
                           self.max_height,
                           self.number_of_glyphs,
                           self.wildcard_codepoint)

    def bitstring(self):
        offset_table = []
        glyph_table = []
        self.number_of_glyphs = 0

        # MJZ: The 0th offset of the glyph table is 32-bits of
        # padding, no idea why.
        offset = 1
        glyph_table.append(struct.pack('<I', 0))

        # for codepoint in xrange(MIN_CODEPOINT, MAX_CODEPOINT + 1):
        for codepoint in codepoints:
            # Hard limit on the number of glyphs in a font
            if (self.number_of_glyphs > 255):
                break

            character = unichr(codepoint)
            if (codepoint not in (WILDCARD_CODEPOINT, ELLIPSIS_CODEPOINT)):
                if self.regex != None:
                    if self.regex.match(character) == None:
                        continue

            glyph_bits = self.glyph_bits(character)
            if glyph_bits == None:
                # unsupported glyph, store no data
                continue

            self.number_of_glyphs += 1
            glyph_table.append(glyph_bits)
            offset_table.append(struct.pack('<HH', codepoint, offset))
            offset += len(glyph_bits) / 4

        return self.fontinfo_bits() + ''.join(offset_table) + ''.join(glyph_table)

    def convert_to_h(self):
        to_file = os.path.splitext(self.ttf_path)[0] + '.h'
        f = open(to_file, 'wb')
        f.write("// TODO: Load font from flash...\n\n")
        f.write("static const uint8_t {0}[] = {{\n\t".format(self.name))
        bytes = self.bitstring().bytes
        for byte, index in zip(bytes, xrange(0, len(bytes))):
            if index != 0 and index % 16 == 0:
                f.write("/* bytes {0} - {1} */\n\t".format(index-16, index))
            f.write("0x%02x, " % ord(byte))
        f.write("\n};\n")
        f.close()
        return to_file

    def convert_to_pfo(self, pfo_path=None):
        to_file = pfo_path if pfo_path else (os.path.splitext(self.ttf_path)[0] + '.pfo')
        with open(to_file, 'wb') as f:
            f.write(self.bitstring())
        return to_file

def cmd_pfo(args):
    f = Font(args.input_ttf, args.height)
    if (args.tracking):
        f.set_tracking_adjust(args.tracking)
    if (args.filter):
        f.set_regex_filter(args.filter)
    f.convert_to_pfo(args.output_pfo)

def process_all_fonts():
    font_directory = "ttf"
    font_paths = []
    for _, _, filenames in os.walk(font_directory):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.ttf':
                font_paths.append(os.path.join(font_directory, filename))

    header_paths = []
    for font_path in font_paths:
        f = Font(font_path)
        print "Rendering {0}...".format(f.name)
        f.convert_to_pfo()
        to_file = f.convert_to_h()
        header_paths.append(os.path.basename(to_file))

    f = open(os.path.join(font_directory, 'fonts.h'), 'w')
    print>>f, '#pragma once'
    for h in header_paths:
        print>>f, "#include \"{0}\"".format(h)
    f.close()

def process_cmd_line_args():
    parser = argparse.ArgumentParser(description="Generate pebble-usable fonts from ttf files")
    subparsers = parser.add_subparsers(help="commands", dest='which')

    pbi_parser = subparsers.add_parser('pfo', help="make a .pfo (pebble font) file")
    pbi_parser.add_argument('height', metavar='HEIGHT', help="Height at which to render the font")
    pbi_parser.add_argument('--tracking', type=int, help="Optional tracking adjustment of the font's horizontal advance")
    pbi_parser.add_argument('--filter', help="Regex to match the characters that should be included in the output")
    pbi_parser.add_argument('input_ttf', metavar='INPUT_TTF', help="The ttf to process")
    pbi_parser.add_argument('output_pfo', metavar='OUTPUT_PFO', help="The pfo output file")
    pbi_parser.set_defaults(func=cmd_pfo)

    args = parser.parse_args()
    args.func(args)

def main():
    if len(sys.argv) < 2:
        # process all the fonts in the ttf folder
        process_all_fonts()
    else:
        # process an individual file
        process_cmd_line_args()


if __name__ == "__main__":
    main()
