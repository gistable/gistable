#!/usr/bin/env python

import string
import re
import sys

def get_gbk(value):
    result = ''
    for i in value:
        result = result + chr(ord(i))
    return result.decode('gbk').encode('utf8')

def decode(line):
    result = ''
    i = 0
    while i < len(line):
        if line[i] in string.printable:
            result += line[i]
            i = i + 1
            continue
        gbk_value = line[i:i+4].decode('utf8')
        gbk_char = get_gbk(gbk_value)
        result += gbk_char
        i += 4
    return result


if __name__ == '__main__':
    line = sys.argv[1]
    match_str = "[^%s]+" % string.printable
    target_re = re.compile(match_str)

    newline = line
    for m in re.finditer(target_re, line):
        newline = re.sub(m.group(0), decode(m.group(0)), newline)
    print newline
