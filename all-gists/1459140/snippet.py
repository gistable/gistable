#!/usr/bin/env python

#http://faq.pygtk.org/index.py?req=show&file=faq23.039.htp


try :
	import gtk.gdk
except ImportError :
	print 'You need to install pygtk'
	exit(1)

# Calculate the size of the whole screen
screenw = gtk.gdk.screen_width()
screenh = gtk.gdk.screen_height()

# Get the root and active window
root = gtk.gdk.screen_get_default()

if root.supports_net_wm_hint("_NET_ACTIVE_WINDOW") and root.supports_net_wm_hint("_NET_WM_WINDOW_TYPE"):
	active = root.get_active_window()
	# You definately do not want to take a screenshot of the whole desktop, see entry 23.36 for that
	# Returns something like ('ATOM', 32, ['_NET_WM_WINDOW_TYPE_DESKTOP'])
	if active.property_get("_NET_WM_WINDOW_TYPE")[-1][0] == '_NET_WM_WINDOW_TYPE_DESKTOP' :
		print False

	# Calculate the size of the wm decorations
	relativex, relativey, winw, winh, d = active.get_geometry() 
	w = winw + (relativex*2)
	h = winh + (relativey+relativex)

	# Calculate the position of where the wm decorations start (not the window itself)
	screenposx, screenposy = active.get_root_origin()
else:
	print False

screenshot = gtk.gdk.Pixbuf.get_from_drawable(gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
	gtk.gdk.get_default_root_window(),
	gtk.gdk.colormap_get_system(),
	screenposx, screenposy, 0, 0, w, h)

# Either "png" or "jpeg" (case matters)
format = "png"

# Pixbuf's have a save method 
# Note that png doesnt support the quality argument. 
screenshot.save("screenshot." + format, format)
