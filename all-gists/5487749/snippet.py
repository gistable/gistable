#!/usr/bin/python

from random import choice, randint
import weechat

NAME = 'do'
AUTHOR = 'aji <http://ajitek.net>'
VERSION = '1.0'
LICENSE = 'MIT'
DESC = 'print commands before doing them'

CMD_NAME = 'do'
CMD_DESC = 'say what you\'ll do, then do it'
CMD_ARGS = '[command]'
CMD_ARGS_DESC = 'command to do'

def cmd_do(data, buf, args):
    if len(args) == 0:
        return weechat.WEECHAT_RC_ERROR

    while True:
        if args[0] != '/':
            args = '/' + args
        weechat.command(buf, '/say ' + args)
        x, _, y = args.partition(' ')
        if x == '/do':
            args = y
        else:
            weechat.command(buf, args)
            return weechat.WEECHAT_RC_OK

if __name__ == '__main__':
    weechat.register(NAME, AUTHOR, VERSION, LICENSE, DESC, '', '')
    weechat.hook_command(CMD_NAME, CMD_DESC, CMD_ARGS, CMD_ARGS_DESC,
                         '', 'cmd_do', '')
