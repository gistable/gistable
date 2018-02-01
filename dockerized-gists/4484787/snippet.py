#!/usr/bin/env python3

from collections import namedtuple

IRC_Source = namedtuple('IRC_Source', 'nick ident host')
IRC_Message = namedtuple('IRC_Message', 'source command args')

def message_source_parse(spec):
    spec, _, host = spec.partition('@')
    nick, _, ident = spec.partition('!')
    if '.' in nick:
        nick, ident, host = '', '', nick
    return IRC_Source(nick, ident, host)

def message_parse(spec):
    cmd, _, spec = spec.partition(' ')
    if len(cmd) < 1:
        return None
    source = IRC_Source('','','')
    if cmd[0]  == ':':
        source = message_source_parse(cmd[1:])
        cmd, _, spec = spec.partition(' ')
    if len(cmd) < 1:
        return None
    command = cmd.upper()
    args = []
    while len(spec) > 0:
        if spec[0] == ':':
            args.append(spec[1:])
            break
        s, _, spec = spec.partition(' ')
        args.append(s)
    return IRC_Message(source, command, args)