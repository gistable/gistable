# http://stackoverflow.com/a/10031877

import numpy
import cairo
import math

from gi.repository import Gtk,Gdk

data = numpy.zeros((200, 200, 4), dtype=numpy.uint8)
surface = cairo.ImageSurface.create_for_data(
    data, cairo.FORMAT_ARGB32, 200, 200)
cr = cairo.Context(surface)

# fill with solid white
cr.set_source_rgb(1.0, 1.0, 1.0)
cr.paint()

# draw red circle
cr.arc(100, 100, 80, 0, 2*math.pi)
cr.set_line_width(3)
cr.set_source_rgb(1.0, 0.0, 0.0)
cr.stroke()

#draw directly to the shared buffer
data[10:30,10:30,2] = 128

# write output
print data[38:48, 38:48, 0]
surface.write_to_png("circle.png")

pb = Gdk.pixbuf_get_from_surface(surface,0,0,200,200)
im = Gtk.Image.new_from_pixbuf(pb)
w = Gtk.Window()
w.connect("delete-event", Gtk.main_quit)
w.add(im)
w.show_all()
Gtk.main()