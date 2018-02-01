#!/usr/bin/env python

import os
import sys

from markdown2 import markdown
from xhtml2pdf import pisa

"""
## Inspired by 

https://github.com/walle/gimli
https://gist.github.com/SpotlightKid/0efb4d07f28af1c8fc1b

## Documentation of underlying tools
http://xhtml2pdf.appspot.com/static/pisa-en.html

Required packages: markdown2, xhtml2pdf, html5lib
"""

DEFAULT_EXTRAS = [
    'fenced-code-blocks',
    'footnotes',
    'metadata',
    'pyshell',
    'smarty-pants',
    'tag-friendly',
    'wiki-tables'
]

def main(md_file, css_file):
    # read css file
    from xhtml2pdf.default import DEFAULT_CSS
    if css_file is not None:
        with open(css_file) as f:
            DEFAULT_CSS += f.read()
    
    # read markdown
    with open(md_file) as f:
        md = f.read()

    # to html
    html = markdown(md, extras=DEFAULT_EXTRAS)

    base_with_path = os.path.splitext(sys.argv[1])[0]
    basename = os.path.basename(base_with_path)

    with open('%s.pdf'%basename, "wb") as fp:
        # convert HTML to PDF
        pisa.CreatePDF(html, dest=fp, default_css=DEFAULT_CSS)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: md2pdf input.md style.css')
        print('       You can also set a CSS file as env var.')
        print('       E.g. export MD2PDF_CSS=style.css')
        sys.exit()
    if len(sys.argv) == 2:
        css = os.getenv('MD2PDF_CSS')
    if len(sys.argv) == 3:
        css = sys.argv[2]

    main(sys.argv[1], css)
