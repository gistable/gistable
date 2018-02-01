import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)

GObject.threads_init()
Gst.init(None)
