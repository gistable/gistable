#!/usr/bin/env python
#encoding: utf-8
import urllib2
from base64 import b64decode


LIST_URL   = 'https://autoproxy-gfwlist.googlecode.com/svn/trunk/gfwlist.txt'
BLACK_FILE = 'gfw.url_regex.lst'
WHITE_FILE = 'cn.url_regex.lst'

def convert_line(line):
    if line[0] == '/' and line[-1] == '/':
        return line[1:-1]
        
    line = line.replace('*', '.+')
    line = line.replace('(', r'\(').replace(')', r'\)')
    if line.startswith('||'):
        return '^https?:\/\/%s.*' % line[2:]  
    elif line.startswith('|'):
        return '^%s.*' % line[1:]
    elif line[-1] == '|':
        return '.*%s$' % line
    else:
        return '.*%s.*' % line

        
def convert(gfwlist):
    black = open(BLACK_FILE, 'w')
    white = open(WHITE_FILE, 'w')
    
    for l in gfwlist.split('\n'):
        l = l[:-1]
        if not l or l[0] == '!' or l[0] == '[':
            continue
            
        if l.startswith('@@'):
            white.write(convert_line(l[2:]) + '\n')
        else:
            black.write(convert_line(l) + '\n')

            
def main():
    src = urllib2.urlopen(LIST_URL).read()
    src = b64decode(src)
    convert(src)
             
if __name__ == '__main__':
    main()