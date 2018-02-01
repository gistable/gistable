#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import locale
import subprocess

locale.setlocale(locale.LC_ALL, '')

from libqtile import bar, hook, layout, widget
from libqtile.command import lazy
from libqtile.manager import Drag, Click, Group, Key, Screen

class Commands(object):
    menu = 'dmenu_run -i -b -p "»" -fn "-*-14-*-" -nb "#000" -nf "#fff" -sb "#15181a" -sf "#fff"'
    browser = 'firefox'
    terminal = 'sakura'
    lock = 'xscreensaver-command -lock'
    vbox = 'virtualbox'
    skype = 'skype'
    files = 'nautilus'
    
    autostart = [browser, terminal, skype, files]

class Theme(object):
    bar = {
        'size': 26,
        'background': '15181A',
    }
    widget = {
        'font': 'Ubuntu',
        'fontsize': 13,
        'background': bar['background'],
        'foreground': 'EEEEEE'
    }
    graph = {
        'background': bar['background'],
        'border_width': 0,
        'line_width': 2,
        'margin_x': 5,
        'margin_y': 5,
        'width': 50
    }
    groupbox = dict(widget)
    groupbox.update({
        'padding': 2,
        'borderwidth': 3,
        'inactive': '999999'
    })
    sep = {
        'background': bar['background'],
        'foreground': '444444',
        'height_percent': 75
    }
    systray = dict(widget)
    systray.update({
        'icon_size': 16,
        'padding': 3
    })

ALT = 'mod1'
MOD = 'mod4'
SHIFT = 'shift'

keys = [
    # Applications
    Key([MOD], 'b', lazy.spawn(Commands.browser)),
    Key([MOD], 'm', lazy.spawn(Commands.menu)),
    Key([MOD], 'l', lazy.spawn(Commands.lock)),
    Key([MOD], 'Return', lazy.spawn(Commands.terminal)),
    
    # Simple Window Management
    Key([MOD], 'Tab', lazy.layout.up()),
    Key([MOD, SHIFT], 'Tab', lazy.layout.shuffle_up()),
    Key([MOD], 'c', lazy.window.kill()),
    
    # Advanced Window Management
    Key([MOD, ALT], 'Right', lazy.layout.up()),
    Key([MOD, ALT], 'Left', lazy.layout.down()),
    Key([MOD, ALT], 'Up', lazy.layout.shuffle_up()),
    Key([MOD, ALT], 'Down', lazy.layout.shuffle_down()),
    Key([MOD, SHIFT], 'Up', lazy.layout.grow()),
    Key([MOD, SHIFT], 'Down', lazy.layout.shrink()),
    Key([MOD, SHIFT], 'n', lazy.layout.normalize()),
    
    # Multimedia
    Key([], 'XF86AudioRaiseVolume', lazy.spawn('amixer -q set Master 5%+')),
    Key([], 'XF86AudioLowerVolume', lazy.spawn('amixer -q set Master 5%-')),
    Key([], 'XF86AudioMute', lazy.spawn('amixer -q set Master toggle'))
]

layouts = (
    # Basic Tiling
    layout.MonadTall(name='xmonad'),
    # Fullscreen Window
    layout.Max(name='full'),
    # Special Skype Layout
    layout.MonadTall(0.2, name='skype')
)

group_setup = (
    # Shell
    ('shell', {
        'apps': {'wm_class': ('Sakura',)}
    }),
    # File Management
    ('files', {
        'apps': {'wm_class': ('Nautilus',)}
    }),
    # Web
    ('web', {
        'apps': {'wm_class': ('Firefox',)},
        'layout': 'full'
    }),
    # Multimedia
    ('media', {
        'apps': {'wm_class': ('Totem', 'Banshee')},
        'layout': 'full'        
    }),
    # Development
    ('dev', {
        'apps': {'wm_class': ('Gedit', 'Eclipse')}
    }),
    # VirtualBox
    ('vbox', {
        'apps': {'wm_class': ()}
    }),
    # Skype
    ('skype', {
        'apps': {'wm_class': ('Skype',)},
        'layout': 'skype'        
    }),
)

groups = []
for index, (name, config) in enumerate(group_setup, 1):
    groups.append(Group(name, layout=config.get('layout', 'xmonad')))
    keys.extend([
        Key([MOD], str(index), lazy.group[name].toscreen()),
        Key([MOD, SHIFT], str(index), lazy.window.togroup(name))
    ])

mouse = [
    Drag([MOD], 'Button1', lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([MOD], 'Button3', lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([MOD], 'Button2', lazy.window.bring_to_front())
]

screens = [
    Screen(
        top=bar.Bar(widgets=[
            widget.TextBox('', 'screen 1', **Theme.widget),

            widget.GroupBox(**Theme.groupbox),
            widget.WindowName(**Theme.widget),

            widget.TextBox('', 'cpu', **Theme.widget),
            widget.CPUGraph(graph_color='18BAEB', fill_color='1667EB.3', **Theme.graph),
            widget.TextBox('', 'mem', **Theme.widget),
            widget.MemoryGraph(graph_color='00FE81', fill_color='00B25B.3', **Theme.graph),
            widget.TextBox('', 'swap', **Theme.widget),
            widget.SwapGraph(graph_color='5E0101', fill_color='FF5656', **Theme.graph),
            widget.TextBox('', 'eth0', **Theme.widget),
            widget.NetGraph(graph_color='ffff00', fill_color='4d4d00', interface='eth0',  **Theme.graph),

            widget.Sep(**Theme.sep),

            widget.CurrentLayout(**Theme.widget),

            widget.Sep(**Theme.sep),

            widget.Systray(**Theme.systray),
            widget.Clock(fmt='%a %d %b %H:%M:%S', **Theme.widget)
            ], **Theme.bar)
    ),
    Screen(
        top=bar.Bar(widgets=[
            widget.TextBox('', 'screen 2', **Theme.widget),

            widget.GroupBox(**Theme.groupbox),
            widget.WindowName(**Theme.widget),

            widget.CurrentLayout(**Theme.widget)
        ], **Theme.bar)
    )
]

floating_layout = layout.floating.Floating(
    float_rules=[{'wmclass': wmclass} for wmclass in (
        'Download',
        'Conky'
    )],
    auto_float_types=[
        'notification',
        'toolbar',
        'splash',
        'dialog'
    ]
)

@hook.subscribe.startup
def autostart():
    for command in Commands.autostart:
        subprocess.Popen([command], shell=True)

@hook.subscribe.client_new
def dialogs(window):
    if(window.window.get_wm_type() == 'dialog' or window.window.get_wm_transient_for()):
        window.floating = True
    print window.window.get_wm_class()

def main(qtile):
    from grouper import AppGrouper, Match

    AppGrouper(qtile, [{
        'group': name,
        'match': Match(**config['apps']),
    } for name, config in group_setup if 'apps' in config])