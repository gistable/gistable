#!/usr/bin/env python3
from os import system
from sys import argv

# Example:
#     youtube-terminal.py foo bar baz
# calls youtube-dl 'ytsearch:foo bar baz' --max-downloads 1 -o - | cvlc - --no-video

call_str = 'youtube-dl "ytsearch:{}" --max-downloads 1 -o -'
call_str += ' | cvlc - --no-video --play-and-exit'
system(call_str.format(' '.join(argv[1:])))
