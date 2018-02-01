# encoding: utf8
import sys

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Granite

class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
            flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.license_type = Gtk.License.GPL_3_0

    def do_activate(self):
        self.window = Granite.WidgetsLightWindow.new("Tareas")
        self.window.set_resizable(False)
        self.window.set_keep_above(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_size_request(350, 430)

        welcome = Granite.WidgetsWelcome.new('No hay tareas', 'Excelente!')
        self.window.add(welcome)

        self.add_window(self.window)
        self.window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_quit(self, widget, data):
        self.quit()


if __name__ == '__main__':
    application = Application()
    application.run(None)