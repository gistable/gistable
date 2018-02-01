#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Solarized theme for pantheon-terminal

see http://ethanschoonover.com/solarized
"""
import posixpath
import sys
from gi.repository import Gio

BASE03  = '#002B36'
BASE02  = '#073642'
BASE01  = '#586E75'
BASE00  = '#657B83'
BASE0   = '#839496'
BASE1   = '#93A1A1'
BASE2   = '#EEE8D5'
BASE3   = '#FDF6E3'
YELLOW  = '#B58900'
ORANGE  = '#CB4B16'
RED     = '#DC322F'
MAGENTA = '#D33682'
VIOLET  = '#6C71C4'
BLUE    = '#268BD2'
CYAN    = '#2AA198'
GREEN   = '#859900'
# 16 colors palette
PALETTE = [BASE02, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BASE2,
           BASE03, ORANGE, BASE01, BASE00, BASE0, VIOLET, BASE1, BASE3]
           
SCHEMES = {'dark': {'background_color' : BASE03,
                    'foreground_color' : BASE0,
                    'bold_color'       : BASE1},
                    
           'light': {'background_color': BASE3,
                     'foreground_color': BASE00,
                     'bold_color'      : BASE01}}

def _solarize(scheme):       
    s = Gio.Settings.new("org.pantheon.terminal.settings")
    s.set_string("palette", ':'.join(PALETTE))
    s.set_string("foreground", SCHEMES[scheme]['foreground_color'])
    s.set_string("background", SCHEMES[scheme]['background_color'])
    s.set_string("cursor-color", SCHEMES[scheme]['foreground_color'])
    s.sync()
    print('applyed {0} scheme'.format(scheme))

def _default():
    s = Gio.Settings.new("org.pantheon.terminal.settings")
    s.reset("palette")
    s.reset("foreground")
    s.reset("background")
    s.sync()
    print('applied defaults')
    
def main():

    if len(sys.argv) > 1 and sys.argv[1] in ('dark', 'light'):
        _solarize(scheme=sys.argv[1])
    else:
        _default()

if __name__ == '__main__':
    main()
