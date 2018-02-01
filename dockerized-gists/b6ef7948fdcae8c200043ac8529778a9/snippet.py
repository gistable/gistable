"""
Usage: python3 regional.py list of words
Prints a representation of the words as Regional Identifiers, and copies the output directly to keyboard for you
This is because some terminals think that zero width spaces are silly.

Currently supports: A-Z
Requires: Python 3

Now less complex, thanks @bmispelon!
"""


import sys
import xerox
import unicodedata

def regional_indicator(letter):
    # Try and see if there's a REGIONAL INDICATOR SYMBOL for our letter.
    try:
        return unicodedata.lookup('REGIONAL INDICATOR SYMBOL LETTER %s' % letter.upper());
    except KeyError:
        return letter
        
output = "\u200B".join([regional_indicator(x) for x in " ".join(sys.argv[1:]).upper()])

xerox.copy(output)

print("Copied to Clipboard: %s" % output)