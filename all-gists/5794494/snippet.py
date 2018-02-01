#!/usr/bin/python3
from gi.repository import Gtk, Gdk
import sys


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_name('MyWindow')
        self.set_default_size(600, 300)

        self.box = Gtk.HBox()
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.CENTER)
        self.add(self.box)

        self.button1 = Gtk.Button(label="Hello")
        self.button1.connect("clicked", self.on_button1_clicked)
        self.box.pack_start(self.button1, True, True, 0)

        self.button2 = Gtk.Button(label="Goodbye")
        self.button2.connect("clicked", self.on_button2_clicked)
        self.box.pack_start(self.button2, True, True, 0)

    def on_button1_clicked(self, widget):
        print("Hello")

    def on_button2_clicked(self, widget):
        print("Goodbye")


def main(argv):

    def gtk_style():
        css = b"""
* {
    transition-property: color, background-color, border-color, background-image, padding, border-width;
    transition-duration: 1s;

    font: Cantarell 20px;
}

GtkWindow {
    background: linear-gradient(153deg, #151515, #151515 5px, transparent 5px) 0 0,
                linear-gradient(333deg, #151515, #151515 5px, transparent 5px) 10px 5px,
                linear-gradient(153deg, #222, #222 5px, transparent 5px) 0 5px,
                linear-gradient(333deg, #222, #222 5px, transparent 5px) 10px 10px,
                linear-gradient(90deg, #1b1b1b, #1b1b1b 10px, transparent 10px),
                linear-gradient(#1d1d1d, #1d1d1d 25%, #1a1a1a 25%, #1a1a1a 50%, transparent 50%, transparent 75%, #242424 75%, #242424);
    background-color: #131313;
    background-size: 20px 20px;
}

.button {
    color: black;
    background-color: #bbb;
    border-style: solid;
    border-width: 2px 0 2px 2px;
    border-color: #333;

    padding: 12px 4px;
}

.button:first-child {
    border-radius: 5px 0 0 5px;
}

.button:last-child {
    border-radius: 0 5px 5px 0;
    border-width: 2px;
}

.button:hover {
    padding: 12px 48px;
    background-color: #4870bc;
}

.button *:hover {
    color: white;
}

.button:hover:active,
.button:active {
    background-color: #993401;
}
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    gtk_style()
    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main(sys.argv)
