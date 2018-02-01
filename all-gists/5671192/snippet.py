"""
$ pip install opml
$ python opml_to_markdown.py some_outline.opml
-> some_outline.md
"""

import codecs
import opml
import sys

INPUT = sys.argv[1]
OUTPUT = '.'.join(INPUT.split('.')[:-1] + ['md'])

with codecs.open(INPUT, 'r', 'utf-8') as f:
    outline = opml.from_string(f.read())

blocks = []

def _extractBlocks(node):
    for child in node:
        blocks.append(child.text)
        if len(child) > 0:
            _extractBlocks(child)

_extractBlocks(outline)

output_content = '\n\n'.join(blocks)
with codecs.open(OUTPUT, 'w', 'utf-8') as f:
    f.write(output_content)

print '->', OUTPUT