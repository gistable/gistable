#!/usr/bin/env python2

import appindicator
import gtk
import urllib2


class IPIndicator(appindicator.Indicator):
    """
    An indicator displaying public IP address.
    """
    
    def __init__(self):
        super(IPIndicator, self).__init__(
            "ip-indicator",
            "applications-internet",
            appindicator.CATEGORY_APPLICATION_STATUS
        )
        # Create the quit menu item
        menu, quit = gtk.Menu(), gtk.MenuItem('Quit')
        quit.connect('activate', gtk.main_quit)
        quit.show()
        menu.append(quit)
        self.set_menu(menu)
        self.set_status(appindicator.STATUS_ACTIVE)
    
    def run(self):
        self._refresh()
        gtk.timeout_add(600, self._refresh)
        gtk.main()
    
    def _refresh(self):
        self.set_label("[Refreshing...]")
        try:
            ip = '[%s]' % urllib2.urlopen('http://icanhazip.com').read().strip()
        except:
            ip = '[Error]'
        self.set_label(ip)


if __name__ == '__main__':
    IPIndicator().run()