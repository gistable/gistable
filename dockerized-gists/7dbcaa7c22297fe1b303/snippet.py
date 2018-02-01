#!/usr/bin/env python

"""
Pandoc filter to parse CriticMarkup into Spans for
Insertion and Deletion. The Docx writer will convert
these into Tracked Changes.

A comment immediately after a change will be parsed
for "author: The Author" and "date: 12-21-12", which
will be inserted into the Span as appropriate.
"""


from pandocfilters import Span, Str, RawInline, walk, attributes, stringify
import re
import sys
import json

regexes = {
    'all':      re.compile(r"([-+=~]{2}\}\{>>|\{[-+~>=]{2}|[-+=~<]{2}\}|~>)"),
 #   'all':      re.compile(r"(\{[-+~>=]{2}|[-+=~<]{2}\}|~>)"),
}


def parseMarks (key, value, format, meta):
    if key == 'Str':
        if regexes['all'].search(value):
            items = regexes['all'].split(value, 1)
            result = [
                Str(items[0]),
                RawInline('critic', items[1])]
            result.extend(walk([Str(items[2])], parseMarks, format, meta))
            return result

spanstart = {
    '{++' : 'insertion',
    '{--' : 'deletion',
    '{==' : 'hilite',
    '{>>' : 'comment',
    '{~~' : 'subdelete'
}

spanend = {
    'insertion' : '++}',
    'deletion' : '--}',
    'hilite' : '==}',
#    'comment' : '<<}',
}

spancomment = {
    'insertion' : '++}{>>',
    'deletion' : '--}{>>',
    'hilite' : '==}{>>',
    'subadd' : '~~}{>>',
}

def makeSpan (contents, classes = "", author = "", date = ""):
    attrs = {'classes' : classes.split(), 'author' : author, 'date' : date}
    return Span (attributes(attrs), contents)

def findAuthor (comment):
    author = re.search(r"(author:|@)\s*([\w\s]+)", comment)
    if author:
        return author.group(2)
    else:
        return ""

def findDate (comment):
    date = re.search(r"date:\s*(\S+)", comment)
    if date:
        return date.group(1)
    else:
        return ""

inspan = False
spantype = None
lasttype = None
spancontents = []
priorspan = []

def spanify (key, value, format, meta):
    global inspan
    global spantype
    global lasttype
    global spancontents
    global priorspan

    if inspan:
#        pass
        if key == 'RawInline' and value[0] == 'critic':
            if value[1] == spanend.get(spantype, ""):
                newspan = makeSpan(spancontents, spantype)
                inspan = False
                spantype = None
                spancontents = []
                return walk([newspan], spanify, format, meta)
            elif spantype == 'subdelete' and value[1] == '~>':
                priorspan.append({'type': 'deletion', 'contents': spancontents})
                spancontents = []
                spantype = 'subadd'
                return []
            elif spantype == 'subadd' and value[1] == '~~}':
                delspan = makeSpan(priorspan[0]['contents'], 'deletion')
                addspan = makeSpan(spancontents, 'insertion')
                inspan = False
                spantype = None
                priorspan = []
                spancontents = []
                return walk([delspan, addspan], spanify, format, meta)
            elif value[1] == spancomment.get(spantype, ""):
                thistype = spantype
                if thistype == 'subadd': thistype = 'insertion'
                priorspan.append({'type': thistype, 'contents': spancontents})
                spancontents = []
                spantype = 'comment'
                return []
            elif value[1] == '<<}' and spantype == 'comment':
                commentstring = stringify(spancontents)
                result = []
#                if len(priorspan) > 0:
                author = findAuthor(commentstring)
                date = findDate(commentstring)
                for item in priorspan:
                    result.append(makeSpan(item['contents'], item['type'], author, date))
                comment = "<!-- %s -->" % commentstring
                result.append(RawInline('html', comment))
                priorspan = []
                spancontents = []
                spantype = None
                inspan = False
                return walk(result, spanify, format, meta)
            else:
                spancontents.append({'t': key, 'c': value})
                return []
        else:
            spancontents.append({'t': key, 'c': value})
            return []
    else:
        if key == 'RawInline' and value[0] == 'critic':
            thetype = spanstart.get(value[1], "")
            if thetype:
                spantype = thetype
                inspan = True
                spancontents = []
                return []
            else:
                #this is a user error, do not parse
                pass
        else:
            pass

if __name__ == "__main__":
    doc = json.loads(sys.stdin.read())
    if len(sys.argv) > 1:
        format = sys.argv[1]
    else:
        format = ""
    meta = doc[0]['unMeta']
    parsed = walk(doc, parseMarks, format, meta)
    altered = walk(parsed, spanify, format, meta)
    json.dump(altered, sys.stdout)
