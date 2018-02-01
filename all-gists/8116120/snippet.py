#!/usr/bin/env python
# -*- coding: utf-8 -*-

# For conky's configuration file ($HOME/.conkyrc):
#   ${if_running cmus}
#     ${execi 03 (conky-cmus.py)}
#   ${endif}

from subprocess import check_output
from re import match, compile

cmus_remote = check_output(['cmus-remote', '-Q'])
status = cmus_remote.split('\n')[0].split()[1]

if status == 'playing':
    l = []
    p = compile('tag (artist|album|title|date|genre|tracknumber) ')
    for e in cmus_remote.split('\n'):
        if p.match(e):
            l.append(p.sub('', e).title())
    # l[0] is the "Artist", l[1] is the "Album" and l[2] is the "Title"
    print "Playing: {0} ({1}) - {2}".format(l[0], l[1], l[2])
else:
    print "Stopped"
