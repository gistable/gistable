#! /usr/bin/python2
import gtk.gdk
w = gtk.gdk.window_foreign_new( gtk.gdk.get_default_root_window().property_get("_NET_ACTIVE_WINDOW")[2][0] )
w.set_decorations( (w.get_decorations()+1)%2 ) # toggle between 0 and 1
gtk.gdk.window_process_all_updates()
gtk.gdk.flush()

# now bind this to super-r or something 