#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### Relay Integration ###
# Version 20160710-4 by Scott Garrett
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Requires:
#    Weechat >= 0.3.2 or XChat >= 2.8 or HexChat >= 2.9

__module_name__ = 'relay_integration'
__module_version__ = '20160710-4'
__module_description__ = 'Make relayed messages from relays look like regular channel messages.'

WEECHAT = False
XCHAT = False



import re

# Are we running under Weechat?
try:
    import weechat
    WEECHAT = True
except ImportError:
    pass

# Hexchat?
try:
    import hexchat as xchat
    XCHAT = True
except ImportError:
    pass

# Xchat?
try:
    import xchat
    XCHAT = True
except ImportError:
    pass



DEFAULT_OPTIONS = {
    'relay_bots': (
        'Nicks to parse relay messages from',
        ['demonbot', 'zeta_discord', 'discord'],
        str.lower
    ),
    'relay_vhost': (
        'VHost to give users speaking over a relay',
        'relay.localhost'
    )
}
OPTIONS = {}

ACTIONS = {
    'JOIN': 'joined',
    'PART': 'left',
    'QUIT': 'signed off',
    'MODE': 'set mode flag(s)'
}

# Strip formatting and color
FMT_REGEX = re.compile(r'[\x01\x02\x04-\x08\x0f\x14-\x1f]|\x03(?:\d{,2},?\d{,2}?)?')


def set_option(option, value):
    """Sets the value of a global option (and applies its callback)."""
    global OPTIONS
    if option in DEFAULT_OPTIONS and len(DEFAULT_OPTIONS[option]) > 2:
        if isinstance(value, str):
            value = DEFAULT_OPTIONS[option][2](value)
        else:
            value = list(map(DEFAULT_OPTIONS[option][2], value))
    OPTIONS[option] = value


def oxford_serialize(iterable):
    """Formats an iterable as a string following English grammar conventions.

    (Somewhere, in the distance:  <darkf> ugh)

    Arguments:
        iterable: an iterable/sequence

    Returns:
        'item'
        'item and item'
        'items, ..., and item'
    """
    l = len(iterable)
    if l == 1:
        return iterable[0]
    elif l == 2:
        return ' and '.join(iterable)
    return '{}, and {}'.format(', '.join(iterable[:-1]), iterable[-1])


def split_mask(mask):
    """Splits an IRC hostmask into its parts.

    Arguments:
        mask: the hostmask of a user

    Returns:
        (nick, user, host)
    """
    nick, host = mask.lstrip(':').rsplit('!', 1)
    user, host = host.rsplit('@', 1)
    return nick, user, host


def join_mask(nick, user, host):
    """Joins a nick, user, and host into an IRC hostmask.

    Arguments:
        nick: user's nick
        user: user's username
        host: user's FQDN or cloak/VHOST

    Returns:
        'nick!user@host'
    """
    return '{}!{}@{}'.format(nick, user, host)


def join_message(prefix, command, args, trailing=None):
    """Join parts of an IRC message.

    Arguments:
        prefix: the origin hostmask of the message
        command: the IRC command
        args: command parameters
        trailing: data parameter

    Returns:
        ':prefix command arguments[ :trailing]'
    """
    if not isinstance(args, str):
        args = ' '.join(args)
    if trailing is None:
        return ':{} {} {}'.format(prefix, command, args)
    return ':{} {} {} :{}'.format(prefix, command, args, trailing)


def parse_relay_msg(mask, message):
    """Parses a message from a relay bot.

    Arguments:
        mask: the IRC hostmask of the relay bot
        message: the message from the relay bot

    Returns:
        (type, new_mask, new_message)
        type: -1 -- unchanged
               0 -- message
               1 -- action
               2 -- channel event
        new_mask: the IRC hostmask of the relayed sender
        new_message: the message of the relayed sender
    """
    nick, user, host = split_mask(mask)
    relay_vhost = OPTIONS.get('relay_vhost', DEFAULT_OPTIONS['relay_vhost'])
    message = FMT_REGEX.sub('', message)

    # Is it a relayed message?
    if message.startswith('<'):
        m = re.match(r'<([^>]+)> (.*)', message)
        if m:
            mnick = re.sub(r'\s', '_', m.group(1).strip())
            mask = join_mask(mnick, nick, relay_vhost)
            msg = m.group(2).strip()

            # Is it formatted like an action?
            if len(msg) > 1 and (msg.startswith('_') and msg.endswith('_')) \
               or (msg.startswith('*') and msg.endswith('*')):
                return 1, mask, msg[1:-1]

            return 0, mask, msg
    # Is it an action or event?
    elif message.startswith('*'):
        # Is it formatted like a WvmRelay event?
        m = re.match(r'\*([^ /]+)/(\S+)', message)
        if m:
            relay_server = m.group(1)
            relay_channel = m.group(2)
            messages = []
            # Extract the list of events.
            message = message.split(' ', 1)[1].strip('*')
            for text in message.split('; '):
                # If it looks like a target and events, format appropriately.
                m = re.match(r'(\S+)s: (.*)', text)
                if m:
                    names = oxford_serialize(m.group(2).split()) if \
                            ' ' in m.group(2) else m.group(2)
                    text = '{} WvmRelay: {} {} {} on {}.'.format(
                        nick,
                        names,
                        ACTIONS.get(m.group(1), m.group(1)),
                        relay_channel,
                        relay_server
                    )
                else:
                    text = '{} relay: {}'.format(nick, text)
                messages.append(text)
            return 2, mask, messages
        # Is it formatted like an WvmRelay action?
        else:
            m = re.match(r'\*(\S+) (.*)\*$', message)
            if m:
                mnick = re.sub(r'\s', '_', m.group(1).strip())
                mask = join_mask(mnick, nick, relay_vhost)
                return 1, mask, m.group(2)
    return -1, mask, message


def init_options():
    """Initialize global options dict from client."""
    global OPTIONS
    for opt, attr in DEFAULT_OPTIONS.items():
        xchat_opt = '_'.join((__module_name__, opt))
        if isinstance(attr[1], str):
            value = attr[1]
        else:
            value = ' '.join(attr[1])

        desc = '{} (default: "{}")'.format(attr[0], value)
        if WEECHAT:
            weechat.config_set_desc_plugin(opt, desc)
            plugin_pref = weechat.config_is_set_plugin(opt)
        else:
            cmd_name = ''.join(('WVM', opt.upper()))
            xchat.hook_command(
                cmd_name,
                xchat_update_option_cb,
                userdata=opt,
                help='/{} -- {}'.format(cmd_name, desc)
            )
            plugin_pref = xchat.get_pluginpref(xchat_opt)

        if plugin_pref:
            value = weechat.config_get_plugin(opt) if WEECHAT else \
                    xchat.get_pluginpref(xchat_opt)
            if not isinstance(DEFAULT_OPTIONS[opt][1], str):
                value = list(map(str.strip, value.split()))
            set_option(opt, value)
        else:
            if WEECHAT:
                weechat.config_set_plugin(opt, value)
            else:
                xchat.set_pluginpref(xchat_opt, value)
            set_option(opt, attr[1])



###############
### Weechat ###
###############

def weechat_update_option_cb(pointer, name, value):
    """Update global options dict when changed from Weechat."""
    global OPTIONS
    set_option(name.rsplit('.', 1)[1], value)
    return weechat.WEECHAT_RC_OK


def weechat_privmsg_cb(data, modifier, modifier_data, string):
    """Mangle PRIVMSGs in Weechat."""
    message = weechat.info_get_hashtable('irc_message_parse',
                                         {'message': string})
    if message['nick'].lower() in set(OPTIONS["relay_bots"]):
        text = message['arguments'].split(' :', 1)[1]
        mtype, mask, text = parse_relay_msg(message['host'], text)
        if mtype == -1:
            return string
        elif mtype == 2:
            channel_buffer = weechat.info_get(
                'irc_buffer',
                ','.join((modifier_data, message['channel']))
            )
            for string in text:
                weechat.prnt(channel_buffer, '***  {}'.format(string))
            return ''
        if mtype == 1:
            text = '\x01ACTION {}\x01'.format(text)
        return join_message(mask, 'PRIVMSG', message['channel'], text)
    return string



#####################
### HexChat/XChat ###
#####################

def xchat_chanmsg_cb(word, word_eol, userdata):
    nick = FMT_REGEX.sub('', word[0])
    if nick.lower() not in set(OPTIONS['relay_bots']):
         return xchat.EAT_NONE
    mtype, mask, text = parse_relay_msg('{}!.@.'.format(nick), word[1])
    if mtype == -1:
        return xchat.EAT_NONE
    elif mtype == 2:
        for string in text:
            xchat.emit_print('Channel Action', '***', string)
        return xchat.EAT_ALL
    nick = mask.split('!', 1)[0]
    if userdata and xchat.nickcmp(word[0], xchat.get_info('nick')) != 0:
        event = 'Action Hilight' if mtype == 1 else 'Msg Hilight'
    else:
        event = 'Action' if mtype == 1 else 'Message'
    event = ' '.join(('Channel', event))
    xchat.emit_print(event, nick, text, '*')
    return xchat.EAT_ALL


def xchat_chanmsg_hi_cb(word, word_eol, userdata):
    return xchat_chanmsg_cb(word, word_eol, True)


def xchat_update_option_cb(word, word_eol, userdata):
    """Update global options dict when changed from Xchat/Hexchat."""
    global OPTIONS
    if len(word) < 2:
        print('Must supply at least one argument.')
    else:
        set_option(userdata, *word[1:])
    return xchat.EAT_ALL


############
### Main ###
############

if __name__ == '__main__':
    if WEECHAT:
        weechat.register(
            __module_name__,
            'Scott Garrett',
            __module_version__,
            'GPL3',
            __module_description__,
            '',
            ''
        )
        weechat_version = int(weechat.info_get("version_number", "")) or 0
        if weechat_version < 0x00030200:
            weechat.prnt('', '{}{} {}'.format(
                weechat.prefix("error"),
                __module_name__,
                ': Requires at least Weechat 0.3.2.'
            ))
            weechat.command(
                '', '/wait 10ms /python unload {}'.format(__module_name__)
            )
        else:
            init_options()
            weechat.hook_config('plugins.var.python.{}.*'.format(__module_name__),
                                'weechat_update_option_cb', '')
            weechat.hook_modifier('irc_in_privmsg', 'weechat_privmsg_cb', '')
    elif XCHAT:
        init_options()
        xchat.hook_print("Channel Message", xchat_chanmsg_cb)
        xchat.hook_print("Channel Msg Hilight", xchat_chanmsg_hi_cb)
        xchat.prnt('Relay Integration loaded.')
    else:
        print('This script must be used with Weechat, xchat, or XChat.')
        exit(1)