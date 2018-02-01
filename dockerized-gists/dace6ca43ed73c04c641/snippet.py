#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as op
import base64
import argparse
import logging
from lxml import etree


FONT_TYPES = {'ttf': 'truetype',
              'otf': 'opentype'}


def create_argparser():
    parser = argparse.ArgumentParser(description='Embed base64 font to SVG file')
    parser.add_argument('-i', '--input', action='store', dest='svg_filepath',
                        default='',
                        help='The SVG file path. If you dont give input file, '
                             ' will output to the file or stdout')
    parser.add_argument('-f', '--font', action='append', dest='fonts', 
                        default=[],
                        help='Font file. You can add as many as you want.')
    parser.add_argument('-o', '--output', action='store', dest='out_path',
                        default='',
                        help='The resulting SVG file path. Overwritten if exist.')
    return parser


def get_base64_encoding(bin_filepath):
    """Return the base64 encoding of the given binary file"""

    if not op.exists(bin_filepath):
        msg = 'Could not find file {}.'.format(bin_filepath)
        log.error(msg)
        raise IOError(msg)

    return base64.b64encode(open(bin_filepath, 'r').read())


def remove_ext(filepath):
    """Return the basename of filepath without extension."""
    return op.basename(filepath).split('.')[0]


def get_ext(filepath):
    """Return file extension"""
    return op.basename(filepath).split('.')[-1]


class FontFace(object):
    """CSS font-face object"""

    def __init__(self, filepath, fonttype=None, name=None):
        self.filepath = filepath
        self.ftype = fonttype
        self.given_name = name

    @classmethod
    def from_file(cls, filepath):
        return cls(filepath)

    @property
    def name(self):
        if self.given_name is None:
            return remove_ext(self.filepath)
        else:
            return self.given_name

    @property
    def base64(self):
        return get_base64_encoding(self.filepath)

    @property
    def fonttype(self):
        if self.ftype is None:
            return FONT_TYPES[get_ext(self.filepath)]
        else:
            return self.ftype

    @property
    def ext(self):
        return get_ext(self.filepath)

    @property
    def css_text(self):
        css_text  = u"@font-face{\n"
        css_text += u"font-family: " + self.name + ";\n"
        css_text += u"src: url(data:font/" + self.ext + ";"
        css_text += u"base64," + self.base64 + ") "
        css_text += u"format('" + self.fonttype + "');\n}\n"
        return css_text


class FontFaceGroup(object):
    """Group of FontFaces"""

    def __init__(self):
        self.fontfaces = []

    @property
    def css_text(self):
        css_text  = u'<style type="text/css">'
        for ff in self.fontfaces:
            css_text += ff.css_text
        css_text += u'</style>'
        return css_text

    @property
    def xml_elem(self):
        return etree.fromstring(self.css_text)

    def append(self, font_face):
        self.fontfaces.append(font_face)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__file__)

    parser = create_argparser()
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as exc:
        log.exception('Error parsing arguments.')
        parser.error(str(exc.message))
        exit(-1)

    svg_filepath = args.svg_filepath
    fonts = args.fonts
    out_path = args.out_path

    #check where to write the stuff
    stdout = False
    raw_write = False
    if not svg_filepath:
        raw_write = True
    elif not op.exists(svg_filepath):
        log.error('Could not find file: {}'.format(ipynbf))
        exit(-1)

    if not out_path:
        raw_write = True
        stdout = True

    #check if user gave any font
    if not fonts:
        log.error('No fonts given.')
        exit(-1)

    #build the stuff to write
    fontfaces = FontFaceGroup()
    for font_path in fonts:
        fontfaces.append(FontFace(font_path))

    #write the stuff
    if raw_write and stdout:
        print(fontfaces.css_text)
        exit(0)

    elif raw_write:
        xtree = etree.ElementTree(fontfaces.xml_elem)
        xtree.write(out_path)
        exit(0)

    else:
        with open(svg_filepath, 'r') as svgf:
            tree = etree.parse(svgf)

        for element in tree.iter():
            if element.tag.split("}")[1] == 'svg':
                break
        element.insert(0, fontfaces.xml_elem)
        tree.write(out_path, encoding='utf-8', pretty_print=True)
        exit(0)