#!/usr/bin/env python

import sys
import appscript

def main():
    iterm_transparency = appscript.app('iTerm').current_terminal.current_session.transparency
    iterm_transparency.set("0.9" if sys.argv[1] == '-' else "0.1")

if __name__ == '__main__':
    main()

# vim: fileencoding=utf-8