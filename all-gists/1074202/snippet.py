#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import os
import sys
import re

import subprocess
import functools

from os.path import normpath

from urlparse import urlparse, parse_qsl
from urllib   import unquote,  urlencode, quote, pathname2url as p2u


from xml.etree.ElementTree import Element, tostring
from json import dumps as dumpsj, loads as loadsj

# Sublime Libs
import sublime
import sublime_plugin

################################### BINDINGS ###################################
# Adjust to taste and place in `Default ($PLATFORM).sublime-keymap files

KEYS =  [ { "command": "create_protocol_link",
               "args": {"protocol": "sblm"},
               "keys": ["ctrl+alt+shift+l"] },

          { "command": "create_protocol_link",
               "args": {"protocol": "txmt"},
               "keys": ["ctrl+shift+alt+m"] } ]

################################### CONSTANTS ##################################

DEBUG         = 0
ON_LOAD       = sublime_plugin.all_callbacks['on_load']
PROTOCOLS     = ('txmt', 'sblm') # ://

################### TXMT & SBLM:// AUTO REGISTRY FOR WINDOWS ###################

WINDOWS = sublime.platform() == 'windows'

if WINDOWS:
    from _winreg import (OpenKey, QueryValueEx, CreateKey, SetValueEx, SetValue,
                          KEY_ALL_ACCESS, HKEY_CLASSES_ROOT, REG_SZ)

    for protocol_name in PROTOCOLS:
        try:
            with OpenKey( HKEY_CLASSES_ROOT,
                         r'%s\shell\open\command' % protocol_name) as key:
                val, _ = QueryValueEx(key, None)

                # What if you have a portable sublime? and you move it
                # somewhere?
                if DEBUG or sys.executable not in val:
                    raise WindowsError

        except WindowsError:
            with CreateKey(HKEY_CLASSES_ROOT, protocol_name) as key:
                def setvalue(value='', subkey=None, value_name=None):
                    if value_name:
                        with OpenKey(key, None, 0, KEY_ALL_ACCESS) as h:
                            SetValueEx(h, value_name, 0, REG_SZ, value)
                    else:
                        SetValue(key, subkey, REG_SZ, value)

                setvalue('URL:%s Protocol Handler' % protocol_name)
                setvalue(value_name='URL Protocol', value='')

                # Can't use string formatting:             {           %s  }
                #                                          v           v
                setvalue (
                    (r'"$EXE" --command "open_protocol_url {\"url\": \"%1\"}"'
                    .replace('$EXE', sys.executable)), r'shell\open\command')

                print ('Added %r SublimeProtocol to windows'
                       ' registry' % protocol_name )

################################ GENERIC HELPERS ###############################

if not WINDOWS:
    def quote_arg(arg):
        for char in ['\\', '"', '$', '`']: arg = arg.replace(char, '\\' + char)
        return '"%s"' % arg

    def args_2_string(args):
        return ' '.join(quote_arg(a) for a in args)
else:
    args_2_string = subprocess.list2cmdline

class one_shot(object):
    def __init__(self):
        self.callbacks.append(self)
        self.remove = lambda: self.callbacks.remove(self)

def on_load(f=None, window=None, encoded_row_col=True):
    window = window or sublime.active_window()

    def wrapper(cb):
        if not f: return cb(window.active_view())
        view = window.open_file(f, encoded_row_col)

        if view.is_loading():
            class set_on_load(one_shot):
                callbacks = ON_LOAD

                def on_load(self, view):
                    try:     cb(view)
                    finally: self.remove()

            set_on_load()
        else: cb(view)

    return wrapper

def open_file_path(fn):
    """
    Formats a path as /C/some/path/on/windows/no/colon.txt that is suitable to
    be passed as the `file` arg to the `open_file` command.
    """
    fn = normpath(fn)
    fn = re.sub('^([a-zA-Z]):', '/\\1', fn)
    fn = re.sub(r'\\', '/', fn)
    return fn

def encode_for_command_line(command=None, args=None, **kw):
    """
    Formats a command as expected by --command. Does NOT escape. This is the
    same format that sublime.log_commands(True) will output to the console.

    eg.
        `command: show_panel {"panel": "console"}`

        This command will format the `show_panel {"panel": "console"}` part.

    May be used to create the command to register the Protocol Handler with.

    eg.

        >>> repr(subprocess.list2cmdline ([
        ... sys.executable, '--command',
        ... encode_for_command_line('open_protocol_url', url="%1")] )))
        '"C:\\Program Files\\Sublime Text 2\\sublime_text.exe" --command "open_protocol_url {\\"url\\": \\"%1\\"}"'
    """
    if isinstance(command, dict):
        args    = command['args']
        command = command['command']

    if kw:
        if args: args.update(kw)
        else: args = kw

    return '%s %s' % (command, dumpsj(args))

def find_and_open_file(f):
    """
    Looks in open windows for `f` and focuses the related view.
    Opens file if not found. Returns associated view in both cases.
    """
    for w in sublime.windows():
        for v in w.views():
            if normpath(f) == v.file_name():
                w.focus_view(v)
                return v

    return sublime.active_window().open_file(f)

#################################### HELPERS ###################################

def create_sublime_url(fn=None, row=1, col=1, commands=[]):
    """
    Creates a sblm:// url with the `file`:`row`:`col` urlencoded as the `path`.
    It urlencodes JSON encoded commands into the query string.

    `commands` must be a sequence of length 2 sequences.

        [(cmd_type"", json_array[]), ...]

    `cmd_type` is a key for the type of command:

        {'cmd': TextCommand,  'wcmd': WindowCommand }

    `json_array` expects a sequence, which will be encoded as a JSON array, the
    first item representing a command name and the next a JSON object for the
    command arguments.

        [command_name"", command_args{}]

    >>> create_sublime_url('C:\\example.txt', 25, 10, [('wcmd', ['show_panel', {'panel': 'replace'}])])
    'sblm:///C/example.txt%3A26%3A11?wcmd=%5B%22show_panel%22%2C+%7B%22panel%22%3A+%22replace%22%7D%5D'
    """
    sblm     = 'sblm://%s?%s'
    if DEBUG:
        commands = [('wcmd', ['show_panel', {'panel': 'replace'}])]

    if fn:
        # In a format window.open_file(f, sublime.ENCODED_POSITION) understands
        path = quote('%s:%s:%s' % (open_file_path(fn), row, col))
    else:
        # Just send commands to run on the currently active view
        path = ''

    return sblm % (path, urlencode([(k, dumpsj(v)) for (k,v) in  commands]))

def create_textmate_url(fn, row, col):
    """
    http://blog.macromates.com/2007/the-textmate-url-scheme/

    `txmt://open?url=%(url)s&line=%(line)s&column=%(column)s`

    `url`

        The actual file to open (i.e. a file://… URL), if you leave out this
        argument, the frontmost document is implied.

    `line`

        Line number to go to (one based).

    `column`

        Column number to go to (one based).
    """
    txmt  = 'txmt://open?%s'

    return txmt % (urlencode( [ ('url',   'file://' + p2u(open_file_path(fn))),
                                ('line',   row) ,
                                ('column', col) ]))

URL_CREATORS = {'sblm': create_sublime_url, 'txmt': create_textmate_url}

################################### COMMANDS ###################################

class ClipboardOpenProtocolUrlCommandline(sublime_plugin.WindowCommand):
    def run(self, url_ph="%1", as_repr=False):
        """
        >>> window.run_command('clipboard_open_protocol_url_commandline')
        >>> view.run_command('paste')
        "C:\Program Files\Sublime Text 2\sublime_text.exe" --command "open_protocol_url {\"url\": \"%1\"}"
        """

        sublime.set_clipboard((repr if as_repr else lambda x: x) (
                args_2_string ([sys.executable, '--command',
                encode_for_command_line('open_protocol_url', url=url_ph)]) ))

class CreateProtocolLink(sublime_plugin.TextCommand):
    def is_enabled(self, **args):
        return self.view.file_name() and self.view.sel()

    def run(self, edit, paste_into=None, protocol='sblm'):
        """
        If `paste_into` specified then that file will be opened for pasting the
        link into. A convenience.
        """
        view        = self.view
        fn          = view.file_name()
        row, col    = view.rowcol(view.sel()[0].begin())
        url_creator = URL_CREATORS.get(protocol)

        a = Element('a', {'href':  url_creator(fn, row+1, col+1)})
        a.text = '${1:%s}' % view.substr(view.word(view.sel()[0]))

        sublime.set_clipboard ( tostring(a) )
        if DEBUG: paste_into = r"C:\Users\nick\AppData\Roaming\Sublime Text 2\Packages\SublimeProtocol\test.html"
        if paste_into: find_and_open_file(paste_into)

class OpenProtocolUrl(sublime_plugin.WindowCommand):
    def run(self, url=None):

        window = self.window
        txmt   = url.startswith('txmt')
        p      = urlparse('http' + url[4:])
        cmds   = parse_qsl(p.query)

        if txmt:
            txmt = dict(cmds)
            url  = txmt.get('url')

            if url: f = unquote(urlparse(url).path)
            else:   f = window.active_view().file_name()

            f += ':%(line)s:%(column)s' % txmt
        else:
            f =  unquote(p.path)

        @on_load(f)
        def do(view):
            if txmt: return
            runners = {'cmd': view,  'wcmd': window}

            for cmd_type, cmd in cmds:
                cmd, args = loadsj(cmd)
                runner    = runners.get(cmd_type)

                if runner:
                    if DEBUG:
                        # Formatted like sublime.log_commands(True)
                        print 'command: %s' % encode_for_command_line(cmd, args)

                    # Bug: command can't be unicode
                    runner.run_command(cmd.encode('utf8'), args)

################################################################################