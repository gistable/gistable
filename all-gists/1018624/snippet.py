# encoding: utf-8
import difflib
from itertools import izip
import sys
import re

SINGLE_LETTER_ESCAPES = {
    7: 'a',
    8: 'b',
    9: 't',
    10: 'n',
    11: 'v',
    12: 'f',
    13: 'r',
    92: '\\'
}

class DiffWriter(object):
    def __init__(self, out, defaultenc="utf-8"):
        self.out = out
        self.defaultenc = defaultenc
        self.cattrs = []

    def pushcattrs(self, attr):
        self.cattrs.append(attr)
        self.write("\x1b[%sm" % attr)

    def popcattrs(self):
        self.cattrs.pop()
        self.write("\x1b[0;%sm" % ";".join(self.cattrs))

    def diff(self, a, b):
        if type(a) == type(b):
            if isinstance(a, str) and isinstance(b, str):
                self.write('"')
                self.diff_string(a, b)
                self.write('"')
            elif isinstance(a, unicode) and isinstance(b, unicode):
                self.write('u"')
                self.diff_string(a, b)
                self.write('"')
            elif isinstance(a, dict) and isinstance(b, dict):
                self.write("{")
                self.diff_dict(a, b)
                self.write("}")
            elif isinstance(a, list) and isinstance(b, list):
                self.write("[")
                self.diff_seq(a, b)
                self.write("]")
            elif isinstance(a, tuple) and isinstance(b, tuple):
                self.write("(")
                self.diff_seq(a, b)
                self.write(")")
            else:
                self.pushcattrs("31")
                self.write("<unsupported comparision: %s and %s>" % (repr(a), repr(b)))
                self.popcattrs()
        else:
            self.pushcattrs("34")
            self.write(a)
            self.popcattrs()
            self.pushcattrs("33")
            self.write(a)
            self.popcattrs()

    def diff_string(self, a, b):
        d = difflib.SequenceMatcher(a=a, b=b)
        for op, a_rs, a_re, b_rs, b_re in d.get_opcodes():
            if op == 'equal':
                self.writestr(a[a_rs:a_re])
            elif op == 'replace':
                self.pushcattrs("34")
                self.writestr(a[a_rs:a_re])
                self.popcattrs()
                self.pushcattrs("4")
                self.writestr(b[b_rs:b_re])
                self.popcattrs()
            elif op == 'delete':
                self.pushcattrs("34")
                self.writestr(a[a_rs:a_re])
                self.popcattrs()
            elif op == 'insert':
                self.pushcattrs("4")
                self.writestr(b[b_rs:b_re])
                self.popcattrs()

    def diff_seq(self, a, b):
        d = difflib.SequenceMatcher(a=a, b=b)
        first = True
        for op, a_rs, a_re, b_rs, b_re in d.get_opcodes():
            if op == 'equal':
                for _a, _b in zip(a[a_rs:a_re], b[b_rs:b_re]):
                    if not first:
                        self.write(", ")
                    self.diff(_a, _b)
            elif op == 'replace':
                if len(a[a_rs:a_re]) == len(b[b_rs:b_re]) and any(type(_a) == type(_b) for _a, _b in izip(a[a_rs:a_re], b[b_rs:b_re])):
                    for _a, _b in izip(a[a_rs:a_re], b[b_rs:b_re]):
                        if not first:
                            self.write(", ")
                        self.diff(_a, _b)
                else:
                    self.pushcattrs("34")
                    for _a in a[a_rs:a_re]:
                        if not first:
                            self.write(", ")
                        self.diff(_a, _a)
                    self.popcattrs()
                    self.pushcattrs("33")
                    for _b in b[b_rs:b_re]:
                        if not first:
                            self.write(", ")
                        self.diff(_b, _b)
                    self.popcattrs()
            elif op == 'delete':
                self.pushcattrs("34")
                for _a in a[a_rs:a_re]:
                    if not first:
                        self.write(", ")
                    self.diff(_a, _a)
                self.popcattrs()
            elif op == 'insert':
                self.pushcattrs("33")
                for _b in b[b_rs:b_re]:
                    if not first:
                        self.write(", ")
                    self.diff(_b, _b)
                self.popcattrs()
            first = False

    def diff_dict(self, a, b):
        ak = sorted(a.keys())
        bk = sorted(b.keys())
        d = difflib.SequenceMatcher(a=ak, b=bk)
        first = True
        for op, a_rs, a_re, b_rs, b_re in d.get_opcodes():
            if op == 'equal':
                for k in ak[a_rs:a_re]:
                    if not first:
                        self.write(", ")
                    self.write(k)
                    self.write(": ")
                    self.diff(a[k], b[k])
            elif op == 'replace':
                self.pushcattrs("34")
                for k in ak[a_rs:a_re]:
                    if not first:
                        self.write(", ")
                    self.write(k)
                    self.write(": ")
                    self.diff(a[k], a[k])
                self.popcattrs()
                self.pushcattrs("33")
                for k in bk[b_rs:b_re]:
                    if not first:
                        self.write(", ")
                    self.write(k)
                    self.write(": ")
                    self.diff(b[k], b[k])
                self.popcattrs()
            elif op == 'delete':
                self.pushcattrs("34")
                for k in ak[a_rs:a_re]:
                    if not first:
                        self.write(", ")
                    self.write(k)
                    self.write(": ")
                    self.diff(a[k], a[k])
                self.popcattrs()
            elif op == 'insert':
                self.pushcattrs("33")
                for k in bk[b_rs:b_re]:
                    if not first:
                        self.write(", ")
                    self.write(k)
                    self.write(": ")
                    self.diff(b[k], b[k])
                self.popcattrs()
            first = False

    def writestr(self, s):
        for c in s:
            cc = ord(c)
            ec = SINGLE_LETTER_ESCAPES.get(cc, None)
            if ec:
                self.pushcattrs("1;30")
                self.write("\\")
                self.popcattrs()
                self.write(ec)
            elif c < 0x20 or c == 0x7f:
                self.pushcattrs("1;30")
                self.write("\\")
                self.popcattrs()
                self.write("x%02x" % cc)
            else:
                self.write(c)

    def write(self, s):
        return self.out.write(s.encode(getattr(self.out, 'encoding', self.defaultenc)) if isinstance(s, unicode) else s)

def dprint(a, b):
    d = DiffWriter(sys.stdout)
    d.diff(a, b)
    d.write("\n")
    sys.stdout.flush()

if __name__ == '__main__':
    dprint([u"abc", u"def"], [u"日本語", u"def", u"ghi"])
    dprint({"abc":"def", "def":"ghi"}, {"abc": "deg\\"})
