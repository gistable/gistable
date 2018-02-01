#!/usr/bin/env python
import gtk
import pango
def on_text_view_expose_event(text_view, event):
    text_buffer = text_view.get_buffer()
    bounds = text_buffer.get_bounds()
    text = text_buffer.get_text(*bounds)
    nlines = text.count("\n") + 1
    layout = pango.Layout(text_view.get_pango_context())
    layout.set_markup("\n".join([str(x + 1) for x in range(nlines)]))
    layout.set_alignment(pango.ALIGN_RIGHT)
    width = layout.get_pixel_size()[0]
    text_view.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, width + 4)
    y = -text_view.window_to_buffer_coords(gtk.TEXT_WINDOW_RIGHT, 2, 0)[1]
    window = text_view.get_window(gtk.TEXT_WINDOW_RIGHT)
    window.clear()
    text_view.style.paint_layout(window=window,
                                 state_type=gtk.STATE_NORMAL,
                                 use_text=True,
                                 area=None,
                                 widget=text_view,
                                 detail=None,
                                 x=2,
                                 y=y,
                                 layout=layout)

text_view = gtk.TextView()
text_buffer = text_view.get_buffer()
text_buffer.insert_at_cursor("ABC\nabc")
text_view.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 24)
text_view.connect("expose-event", on_text_view_expose_event)
scroller = gtk.ScrolledWindow()
scroller.set_shadow_type(gtk.SHADOW_IN)
scroller.add(text_view)
window = gtk.Window()
window.connect("delete-event", gtk.main_quit)
window.set_position(gtk.WIN_POS_CENTER)
window.set_default_size(300, 100)
window.set_border_width(12)
window.add(scroller)
window.show_all()
gtk.main()
