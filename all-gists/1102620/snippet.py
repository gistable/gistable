#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example of `abstract factory' design pattern
# Copyright (C) 2011 Radek Pazdera

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


class Window:
    __toolkit = ""
    __purpose = ""

    def __init__(self, toolkit, purpose):
        self.__toolkit = toolkit
        self.__purpose = purpose

    def getToolkit(self):
        return self.__toolkit

    def getType(self):
        return self.__purpose

class GtkToolboxWindow(Window):
    def __init__(self):
        Window.__init__(self, "Gtk", "ToolboxWindow")

class GtkLayersWindow(Window):
    def __init__(self):
        Window.__init__(self, "Gtk", "LayersWindow")

class GtkMainWindow(Window):
    def __init__(self):
        Window.__init__(self, "Gtk", "MainWindow")


class QtToolboxWindow(Window):
    def __init__(self):
        Window.__init__(self, "Qt", "ToolboxWindow")

class QtLayersWindow(Window):
    def __init__(self):
        Window.__init__(self, "Qt", "LayersWindow")

class QtMainWindow(Window):
    def __init__(self):
        Window.__init__(self, "Qt", "MainWindow")

# Abstract factory class
class UIFactory:
    def getToolboxWindow(self): pass
    def getLayersWindow(self): pass
    def getMainWindow(self): pass

class GtkUIFactory(UIFactory):
    def getToolboxWindow(self):
        return GtkToolboxWindow()

    def getLayersWindow(self):
        return GtkLayersWindow()

    def getMainWindow(self):
        return GtkMainWindow()

class QtUIFactory(UIFactory):
    def getToolboxWindow(self):
        return QtToolboxWindow()

    def getLayersWindow(self):
        return QtLayersWindow()

    def getMainWindow(self):
        return QtMainWindow()

if __name__ == "__main__":
    gnome = True
    kde   = not gnome

    # What environment is available?
    if gnome:
        ui = GtkUIFactory()
    elif kde:
        ui = QtUIFactory()

    # Build the UI
    toolbox = ui.getToolboxWindow()
    layers  = ui.getLayersWindow()
    main    = ui.getMainWindow()

    # Let's see what have we recieved
    print "%s:%s" % (toolbox.getToolkit(), toolbox.getType())
    print "%s:%s" % (layers.getToolkit(), layers.getType())
    print "%s:%s" % (main.getToolkit(), main.getType())

