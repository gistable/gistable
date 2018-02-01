#!/usr/bin/env python

"""
Usage: index-sentences.py FILE

print an index of the parsed sentences in FILE
"""

import re
import sys

assert(len(sys.argv) == 2)

filename = sys.argv[1]


tokenre = re.compile(r'\(|\)|[^()\s]+')

def tokenize(file):
    for line in file:
        line = line.strip()
        while line:
            m = tokenre.match(line)
            if m:
                tok = m.group()
                line = line[m.end():].lstrip()
                yield tok

def balance_parens(tokens):
    elts = []
    pars = 0
    for tok in tokens:
        if tok == '(':
            elts.append('(')
            pars += 1
        elif tok == ')':
            assert(pars > 0)

            elts.append(')')
            pars -= 1

            if pars == 0:
                yield elts
                elts = []
        else:
            if pars == 0:
                yield tok
            else:
                elts.append(tok)

def sexps(tokens):
    for els in balance_parens(tokens):
        if isinstance(els, str):
            yield els
        elif len(els) == 1:
            yield els[0]
        else:
            assert(els[0] == '(' and els[-1] == ')')
            yield list(sexps(els[1:-1]))
            
def stringify(sexp):
    if isinstance(sexp, list):
        return '({})'.format(' '.join(stringify(s) for s in sexp))
    else:
        return sexp

def terminals(sexp, include_nulls=False):
    assert(isinstance(sexp, list))
    if len(sexp) == 2 and isinstance(sexp[0], str) and isinstance(sexp[1], str):
        if sexp[0] != '-NONE-' or include_nulls:
            yield(sexp)
    else:
        for s in sexp:
            if isinstance(s, list):
                for t in terminals(s, include_nulls):
                    yield t

# for testing
def print_tokens(filename, include_nulls=False):
    for sexp in sexps(tokenize(open(filename))):
        print("----")
        for t,w in terminals(sexp, include_nulls):
            print('{}/{}'.format(w,t))
        print("----")


def index_sentences(filename):
    for i,sexp in enumerate(sexps(tokenize(open(filename)))):
        print('{file}|{sent}|{len}|{sexp}'.format(
            file=filename,
            sent=i,
            len=len(list(terminals(sexp))),
            sexp=stringify(sexp)))


index_sentences(filename)
#print_tokens(filename)
#print_tokens(filename, include_nulls=True)