#!/usr/bin/env python3

import optparse

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import GObject, Gtk, WebKit


GObject.threads_init()


class UI(object):
    def __init__(self, benchmark):
        self.benchmark = benchmark
        self.window = Gtk.Window()
        self.window.connect('destroy', Gtk.main_quit)
        self.window.set_default_size(960, 540)
        self.window.show_all()
        GObject.idle_add(self.on_idle)

    def on_idle(self):
        print('Now do your heavy initialization...')
        if self.benchmark:
            Gtk.main_quit()


if __name__ == '__main__':    
    parser = optparse.OptionParser()
    parser.add_option('--benchmark',
        help='benchmark app startup time',
        action='store_true',
        default=False,
    )
    (options, args) = parser.parse_args()
    ui = UI(options.benchmark)
    Gtk.main()