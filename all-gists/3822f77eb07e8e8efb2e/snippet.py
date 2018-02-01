#!/usr/bin/env python

import pygtk
import gtk
import webkit
import sys

class Browser:

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        #self.window.set_default_size(600,400)
        #self.window.set_resizable(True)
        self.web_view = webkit.WebView()
        self.web_view.open(str(sys.argv[1]))
        scroll_window = gtk.ScrolledWindow(None, None)
        scroll_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scroll_window.set_placement(gtk.CORNER_TOP_LEFT)
        scroll_window.add(self.web_view)
        box = gtk.VBox(False, 0)
        box.add(scroll_window)
        self.window.add(box)
        self.window.show_all()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    browser = Browser()
    browser.main()