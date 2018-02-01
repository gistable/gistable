import sys
from gi.repository import Gtk, Gdk, WebKit

class WebKitWindow(Gtk.Window):
	scrolls = None
	webView = None

	def __init__(self, url, transparent=False):
		Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL, title='')
		self.scrolls = Gtk.ScrolledWindow()
		self.webView = WebKit.WebView()
		
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.resize(1024, 600)

		self.installTransparency(self.scrolls)
		self.scrolls.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

		self.webView.set_transparent(True)
		self.webView.connect('title-changed', self.titleChanged)
		self.webView.load_uri(url)

		self.scrolls.add(self.webView)
		self.add(self.scrolls)
		
		if ( transparent ):
			self.set_decorated(False)
			self.installTransparency(self)
			self.installTransparency(self.webView)

	def installTransparency(self, component):
		component.set_visual(component.get_screen().get_rgba_visual())

		component.override_background_color(Gtk.StateFlags.ACTIVE, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.BACKDROP, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.DIR_LTR, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.DIR_RTL, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.FOCUSED, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.INCONSISTENT, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.INSENSITIVE, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.PRELIGHT, Gdk.RGBA(0, 0, 0, 0))
		component.override_background_color(Gtk.StateFlags.SELECTED, Gdk.RGBA(0, 0, 0, 0))

		transparentWindowStyleProvider = Gtk.CssProvider()
		transparentWindowStyleProvider.load_from_data("""
			GtkWindow {
				background-color: rgba(0, 0, 0, 0);
				background-image: none;
			}
		""")

		component.get_style_context().add_provider(transparentWindowStyleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

	def titleChanged(self, webView, frame, title):
		self.set_title(title)

if ( __name__ == "__main__" ):
	Gtk.init(sys.argv)

	mainWindow = WebKitWindow('http://www.google.com.br/', transparent=True)
	mainWindow.connect('delete-event', Gtk.main_quit)
	mainWindow.show_all()

	Gtk.main()