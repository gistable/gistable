#!/usr/bin/env python
# vim: set filetype=python :

"""

Synopsis
================================

*objcfmt* is the code formatter for Objective-C source programs.


How formatting method signature works
---------------------------------------

    - (void)doSomething:(NSString*)str with:(int)value {
        ...
    }

to:

    - (void) doSomething: (NSString *) str
                    with: (int) value
    {
        ...
    }


Author
================================

Takanori Ishikawa <takanori.ishikawa@gmail.com>


"""

import sys
import re


# ---- Simple Rules
RULES = [
    (r'\b(if|while|for)\s*\(', r'\1 ('),
    (r'\){', r') {'),
]


# ---- Method Signatures
TYPE_RE = re.compile(r'([\w_]+)\s*(\**)', re.MULTILINE)

METHOD_SIGNATURE_RE = re.compile(r'''
    (?P<head>[-\+])\s*
    \((?P<returnType>[^\)]+)\)\s*
    (?P<name>[\w_:]+)
    (?P<remain>[^;{]*)
    (?P<terminator>[;{])
    ''', re.VERBOSE | re.MULTILINE)

METHOD_PARAM_RE = re.compile(r'''
    (?P<name>[\w_:]+)\s*
    \((?P<type>[^\)]+)\)\s*
    (?P<param>[\w_]+)
    ''', re.VERBOSE | re.MULTILINE)

def format_type(type):
    m = TYPE_RE.match(type.strip())
    if not m.group(2):
        return m.group(1)
    else:
        return m.expand(r'\1 \2')

def repl_method_signature(m):
    heading = '%s (%s) ' % (m.group(1), format_type(m.group(2)))
    name    = m.group('name')
    remain  = m.group('remain').strip()
    term    = m.group('terminator')

    src = heading
    if not remain:
        src += name
    else:
        remain = name + remain
        params = [ list(groups) for groups in METHOD_PARAM_RE.findall(remain)]

        # Type
        for p in params:
            p[1] = format_type(p[1])

        # Vertical Alignment
        max = len(src) + len(params[0][0])
        for p in params:
            if max < len(p[0]):
                max = len(p[0])
        for i, p in enumerate(params):
            l = max - len(p[0])
            if i == 0:
                l -= len(src)
            if l:
                p[0] = (' ' * l) + p[0]

        params = [ '%s (%s) %s' % tuple(v) for v in params ]
        if len(params) > 1 and term == '{':
            term = "\n{"

        remain = "\n".join(params)
        src += remain

    if term == '{':
        src += ' '

    src += term
    return src


def main(src):
    for rule in RULES:
        p = re.compile(rule[0], re.MULTILINE)
        src = p.sub(rule[1], src)

    src = METHOD_SIGNATURE_RE.sub(repl_method_signature, src)
    return src


print main(sys.stdin.read()),

