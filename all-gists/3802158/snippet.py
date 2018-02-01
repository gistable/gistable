#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# This is how I used it:
# $ cat ~/.bash_history | bash-history-to-zsh-history >> ~/.zsh_history

import sys


def main():
    timestamp = None
    for line in sys.stdin.readlines():
        line = line.rstrip('\n')
        if line.startswith('#') and timestamp is None:
            t = line[1:]
            if t.isdigit():
                timestamp = t
                continue
        elif timestamp:
            sys.stdout.write(': %s:0;%s\n' % (timestamp, line))
            timestamp = None


if __name__ == '__main__':
    main()