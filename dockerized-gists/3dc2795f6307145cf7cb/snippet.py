#!/usr/bin/env python

"""
Pandoc filter to convert Tracked Changes in docx
input to CriticMarkup in the output.
"""

from pandocfilters import toJSONFilter, Str, RawInline

def findValue (which, items):
    for item in items:
        if item[0] == which:
            return item[1]
    return 'Unknown'

def makeCriticPart (kind, attr, contents):
    if kind == 'insertion':
        start = Str('{++')
        end = Str('++}')
    else:
        start = Str('{--')
        end = Str('--}')
    author = findValue('author', attr)
    date = findValue('date', attr)
    comment = RawInline('html',"{>>author: %s, date: %s<<}" % (author, date))
    result = [start]
    result.extend(contents)
    result.append(end)
    result.append(comment)
    return result

def convertCritic (key, value, format, meta):
    if key == 'Span':
        classes = value[0][1]
        if 'insertion' in classes:
            return makeCriticPart('insertion', value[0][2], value[1])
        elif 'deletion' in classes:
            return makeCriticPart('deletion', value[0][2], value[1])
        else:
            return None

if __name__ == "__main__":
    toJSONFilter(convertCritic)
