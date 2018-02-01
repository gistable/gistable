#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

using_unicode = True
using_color = True

_bar = '│' if using_unicode else '|'
_middle = '├' if using_unicode else '|'
_extend = '─' if using_unicode else '-'
_bottom = '└' if using_unicode else '\''
_tree_width = 3
_space = ' '*_tree_width
_extension = _extend*_tree_width

MIDDLE_EXTENSION = _middle + _extension
BOTTOM_EXTENSION = _bottom + _extension
BAR_SPACE = _bar + _space
EMPTY_SPACE = ' ' + _space

def colorize(fullpath):
    path = os.path.split(fullpath)[-1]
    if not using_color:
        return path
    if os.path.isdir(fullpath):
        color = '34'
    elif os.path.isfile(fullpath) and os.access(fullpath, os.X_OK):
        color = '32'
    else:
        return path
    return '\33[%sm%s\33[0m'%(color,path)

def draw_dir(fullpath, roots, branch, curr_root):
    sys.stdout.write(roots+branch+colorize(fullpath)+'\n')
    if os.path.isdir(fullpath):
        roots += curr_root
        paths = os.listdir(fullpath)
        if len(paths) > 0:
            for child in paths[:-1]:
                draw_dir(os.path.join(fullpath,child),roots,MIDDLE_EXTENSION,BAR_SPACE)
            draw_dir(os.path.join(fullpath,paths[-1]),roots,BOTTOM_EXTENSION,EMPTY_SPACE)

if __name__=='__main__':
    path = '.'
    for arg in sys.argv[1:]:
        if arg == '-m':
            using_color = False
        elif arg == '-a':
            using_unicode = False
        elif arg == '-h' or arg == '--help':
            sys.stdout.write("tree usage : \n    -a  use ascii instead of unicode\n    -m  use monotone instead of color\n    -h  print the help text\n")
            sys.exit(0)
        else:
            path = arg

    if not os.path.exists(path):
        sys.stdout.write('not a file %s\n'%path)
        sys.exit(1)
    draw_dir(path,'','','')