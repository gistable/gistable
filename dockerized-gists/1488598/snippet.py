#!/usr/bin/env python
# coding: utf-8

# scanf.py - written by odiak
# 
# example.
# i, f = scanf('%d%d')
# s = scanf('%s')

import sys
import re

_d = lambda s: int(float(s))
_f = lambda s: float(s)
_s = lambda s: str(s)
_c = lambda s: str(s)[0]

def _escape (s):
    chars = r'\.^$*+?{}[]()|#'
    for c in chars:
        s = s.replace(c, '¥¥' + c)
    return s

def _parse_format (f):
    patterns = []
    pattern  = ''
    fgroup   = r'(%s)'
    fngroup  = r'(?:%s)'
    rnum     = r'[-+]?¥d+(?:¥.¥d+(?:[eE][-+]?¥d+))?'
    rchar    = r'¥S'
    rstr     = r'¥S+'
    funcs    = []
    tmp      = ''
    iswhsp   = re.compile(r'^¥s+$')
    
    for c in f:
        if tmp == '' and c == '%':
            tmp = '%'
            
        elif tmp == '%' and c == '%':
            pattern += '%'
            tmp = ''
            
        elif tmp == '%' and c == '*':
            tmp = '%*'
            
        elif tmp == '%' and c in 'dfcs':
            if len(pattern) > 0:
                patterns.append(pattern)
                pattern = ''
            
            if c == 'd':
                patterns.append(fgroup % rnum)
                funcs.append(_d)
            elif c == 'f':
                patterns.append(fgroup % rnum)
                funcs.append(_f)
            elif c == 'c':
                patterns.append(fgroup % rchar)
                funcs.append(_c)
            elif c == 's':
                patterns.append(fgroup % rstr)
                funcs.append(_s)
            tmp = ''
                
        elif tmp == '%*' and c in 'dfcs':
            if len(pattern) > 0:
                patterns.append(pattern)
                pattern = ''
            
            if c == 'd':
                patterns.append(fngroup % rnum)
            elif c == 'f':
                patterns.append(fngroup % rnum)
            elif c == 'c':
                patterns.append(fngroup % rchar)
            elif c == 's':
                patterns.append(fngroup % rstr)
            tmp = ''
                
        else:
            if iswhsp.match(c):
                if len(pattern) > 0:
                    patterns.append(pattern + _escape(tmp))
                    pattern = ''
            else:
                pattern += _escape(tmp + c)
            tmp = ''
    
    if len(pattern + tmp) > 0:
        patterns.append(pattern + _escape(tmp))
                      
    return patterns, funcs

def scanf (f):
    iswhsp  = re.compile('^¥s+$')
    matches = []
    regs, funcs = _parse_format(f)
    i = 0
    buf = ''
    
    for r in regs:
        p = re.compile('^%s$' % r)
        s = ''
        while True:
            if len(buf) > 0:
                c = buf[0]
                buf = buf[1:]
            else:
                c = sys.stdin.read(1)
            if not c:
                break
            if iswhsp.match(c):
                if len(s) > 0:
                    break
            else:
                s += c
        while True:
            if len(s) == 0:
                return ()
            m = p.match(s)
            if m:
                g = m.groups()
                if len(g) > 0:
                    matches.append(g[0])
                break
            buf = s[-1] + buf
            s = s[:-1]
        for i in range(len(matches)):
            matches[i] = funcs[i](matches[i])
    return matches
