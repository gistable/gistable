#!/usr/bin/env python
"""
Ever had a mysqldump of utf8 data stored in latin1 tables, dumped in utf8 and 
munged with windows cp1252? 

If so this is your friend. Just pipe it through this little baby and spare 
yourself hours of unicode hell- it'll take your dirt and spit out clean utf8.

You can also import it and use it in your python code.

Big shouts to stack overflow for a few clues and our beautiful soup buddy at 
effbot for the cp1252 map.

Keywords mysql unicode double encode decode

Simon Litchfield
simon@s29.com.au
"""
import sys

def doubledecode(s, as_unicode=True):
    s = s.decode('utf8')
    # remove the windows gremlins O^1
    for src, dest in cp1252.items():
        s = s.replace(src, dest)
    s = s.encode('raw_unicode_escape')
    if as_unicode:
        # return as unicode string
        s = s.decode('utf8', 'ignore')
    return s
    
cp1252 = {
    # from http://www.microsoft.com/typography/unicode/1252.htm
    u"\u20AC": u"\x80", # EURO SIGN
    u"\u201A": u"\x82", # SINGLE LOW-9 QUOTATION MARK
    u"\u0192": u"\x83", # LATIN SMALL LETTER F WITH HOOK
    u"\u201E": u"\x84", # DOUBLE LOW-9 QUOTATION MARK
    u"\u2026": u"\x85", # HORIZONTAL ELLIPSIS
    u"\u2020": u"\x86", # DAGGER
    u"\u2021": u"\x87", # DOUBLE DAGGER
    u"\u02C6": u"\x88", # MODIFIER LETTER CIRCUMFLEX ACCENT
    u"\u2030": u"\x89", # PER MILLE SIGN
    u"\u0160": u"\x8A", # LATIN CAPITAL LETTER S WITH CARON
    u"\u2039": u"\x8B", # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u"\u0152": u"\x8C", # LATIN CAPITAL LIGATURE OE
    u"\u017D": u"\x8E", # LATIN CAPITAL LETTER Z WITH CARON
    u"\u2018": u"\x91", # LEFT SINGLE QUOTATION MARK
    u"\u2019": u"\x92", # RIGHT SINGLE QUOTATION MARK
    u"\u201C": u"\x93", # LEFT DOUBLE QUOTATION MARK
    u"\u201D": u"\x94", # RIGHT DOUBLE QUOTATION MARK
    u"\u2022": u"\x95", # BULLET
    u"\u2013": u"\x96", # EN DASH
    u"\u2014": u"\x97", # EM DASH
    u"\u02DC": u"\x98", # SMALL TILDE
    u"\u2122": u"\x99", # TRADE MARK SIGN
    u"\u0161": u"\x9A", # LATIN SMALL LETTER S WITH CARON
    u"\u203A": u"\x9B", # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u"\u0153": u"\x9C", # LATIN SMALL LIGATURE OE
    u"\u017E": u"\x9E", # LATIN SMALL LETTER Z WITH CARON
    u"\u0178": u"\x9F", # LATIN CAPITAL LETTER Y WITH DIAERESIS
}

if __name__ == '__main__':
    for line in sys.stdin:
        # we want to pipe it out as a utf8-encoded string, not a python unicode string
        s = doubledecode(line, False)
        print s