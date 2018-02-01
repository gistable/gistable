#!/usr/bin/env python
# Unity indicator for evolution-less clock and date display
# author: phil ayres
# 24 Oct 2011

import gobject
import gtk
import appindicator
import os, sys
import time
from time import gmtime, strftime

if __name__ == "__main__":

    #def on_left_click(widget,data=None):
        # Placeholder for later
      
    def on_timer(args=None):
      ind.set_label(strftime("%H:%M",time.localtime()))    
      item.set_label(strftime("%a, %d %b %Y - %H:%M",time.localtime()))
      return True
              
    ind = appindicator.Indicator ("simple-clock-client", "clock", appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_status (appindicator.STATUS_ACTIVE)
    ind.set_label(strftime("%H:%M",time.localtime()));    
    menu = gtk.Menu()
    item = gtk.MenuItem(strftime("%a, %d %b %Y",time.localtime()))    
    #item.connect("activate", on_left_click)
    item.show()
    menu.append(item)
    ind.set_menu(menu)
    gtk.timeout_add(1000, on_timer)    
    gtk.main()
