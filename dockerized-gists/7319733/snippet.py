#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pdfcrop
=======

Based on pdfcrop.pl_. Uses the BoundingBox [#]_

Dependencies:
  - PyPDF2_
  - ghostscript_


.. [#] http://commons.wikimedia.org/wiki/File:PDF_BOX_01.svg

.. _PyPDF2: https://github.com/mstamy2/PyPDF2/
.. _ghostscript: http://www.ghostscript.com/
.. _pdfcrop.pl: ftp://ftp.tex.ac.uk/tex-archive/support/pdfcrop/pdfcrop.pl
"""

import os
import shlex
import logging
import subprocess

from PyPDF2 import PdfFileReader, PdfFileWriter

logger = logging.getLogger('pdfcrop')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


devnull = open(os.devnull, 'w')


def _bbox(value):
    """
    >>> _bbox('%%BoundingBox: 217 208 566 357')
    [217, 208, 566, 357]
    """
    _, bbox = value.split(':')
    return map(int, bbox.split())


def _hiresbb(value):
    """
    >>> _hiresbb('%%HiResBoundingBox: 98.765997 63.935998 694.025979 497.591774')
    [98.765997, 63.935998, 694.025979, 497.591774]
    """
    _, bbox = value.split(':')
    return map(float, bbox.split())


def get_boundingbox(pdfpath, hiresbb=False):
    """
    Given a pdf file path, return its bounding box.

    :hiresbb:
        Return hiresBoundingbox, instead of Boudingbox.

    >>> get_boundingbox('/path/to/mypdf.pdf')   # doctest: +SKIP
    [[23, 34, 300, 555], [0, 0, 300, 555]]
    """
    command = shlex.split('gs -dSAFER -sDEVICE=bbox -dNOPAUSE -dBATCH')
    command.append(pdfpath)
    process = subprocess.Popen(command, stdout=devnull, stderr=subprocess.PIPE)
    out, err = process.communicate()  # gs sends output to stderr
    if hiresbb:
        return [_hiresbb(line) for line in err.split('\n') if line.startswith('%%HiResBoundingBox')]
    return [_bbox(line) for line in err.split('\n') if line.startswith('%%BoundingBox')]


def crop_pdf(inputfile, outputfile=None):
    bboxes = get_boundingbox(inputfile)
    if outputfile is None:
        outputfile = 'cropped.{0}{1}'.format(*os.path.splitext(inputfile))
    logger.info('Writing pdf output to %s', outputfile)
    with open(inputfile, 'rb') as fin:
        with open(outputfile, 'wb') as fout:
            pdf_in = PdfFileReader(fin)
            pdf_out = PdfFileWriter()
            for i, bbox in enumerate(bboxes):
                left, bottom, right, top = bbox
                page = pdf_in.getPage(i)
                logger.debug('Original mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
                logger.debug('Original boundingbox: %s, %s', (left, bottom), (right, top))
                page.mediaBox.lowerLeft = (left, bottom)
                page.mediaBox.upperRight = (right, top)
                logger.debug('modified mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
                pdf_out.addPage(page)
            pdf_out.write(fout)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Crop pdf files')
    parser.add_argument('pdf', metavar='pdf', type=str, help='input pdf')
    parser.add_argument('-o', '--output', dest='output', type=str, help='output file')
    parser.add_argument('-l', '--loglevel', dest='loglevel', default='info', type=str, help='Logging level')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), logging.INFO)
    logger.setLevel(loglevel)

    crop_pdf(args.pdf, args.output)
