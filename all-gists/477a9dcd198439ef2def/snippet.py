#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
USAGE

    python2 web2pdf.py <URL>

DESCRIPTION

    Extract main content from a web page and convert it to PDF.

DEPENDENCIES

    python-readability <https://github.com/buriy/python-readability>
    pandoc <http://johnmacfarlane.net/pandoc/>
"""

import urllib2
import subprocess
import sys
from readability.readability import Document

MAIN_FONT = "DejaVu Sans"
MONO_FONT = "Inconsolatazi4"

if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
    print __doc__
    exit(1)

print "Fetching web page…"
html = urllib2.urlopen(sys.argv[1]).read()

document = Document(html)
article = document.summary().encode("utf-8")
title = document.short_title().encode("utf-8")

file_name = title.replace(" ", "_").replace("/", "_")
input_file = "/tmp/{}.html".format(file_name)
output_file = "{}.pdf".format(file_name)

with open(input_file, "w") as input_f:
    input_f.write(article.replace(
        "<html>", "<html><head><title>{}</title></head>".format(title), 1))

print "Converting web page…"
pandoc = subprocess.Popen(["pandoc", "--highlight-style=haddock",
                           "--latex-engine=xelatex", "--variable",
                           "mainfont={}".format(MAIN_FONT), "--variable",
                           "monofont={}".format(MONO_FONT),
                           input_file, "--output={}".format(output_file)])
pandoc.wait()