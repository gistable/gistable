#!/usr/bin/env python2

from gi.repository import Gtk, GObject, GLib
import os
import os.path

class File(object):

    def __init__(self, file_name, place_holder=False, directory=True, root=False, empty=False):
        self.file_name = file_name
        self.place_holder = place_holder
        self.directory = directory
        self.root = root
        self.empty = empty

    def __str__(self):
        return 'File: name: {}, dir: {}, empty: {}'.\
                format(self.file_name, self.directory, self.empty)

PLACE_HOLDER = File('<should never be visible>', place_holder=True)
EMPTY_DIR = File('<empty>', empty=True)

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='File Viewer')
        self.set_default_size(500, 300)

        vbox = Gtk.Box(False, orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        self.treemodel = Gtk.TreeStore(object)

        scrolled_tree = Gtk.ScrolledWindow()
        vbox.pack_start(scrolled_tree, True, True, 0)

        tree = Gtk.TreeView(self.treemodel)
        tree.set_headers_visible(False)
        tree.connect('row-expanded', self.on_row_expanded)
        scrolled_tree.add(tree)

        file_name_renderer = Gtk.CellRendererText()
        file_type_renderer = Gtk.CellRendererPixbuf()

        file_name_column = Gtk.TreeViewColumn('file')
        file_name_column.pack_start(file_type_renderer, False)
        file_name_column.pack_start(file_name_renderer, False)
        file_name_column.set_cell_data_func(file_name_renderer, self.render_file_name)
        file_name_column.set_cell_data_func(file_type_renderer, self.render_file_type_pix)
        tree.append_column(file_name_column)

        add_button = Gtk.Button('add')
        add_button.connect('clicked', self.prompt_dir_select)
        vbox.pack_start(add_button, False, True, 0)

    def render_file_type_pix(self, col, renderer, model, tree_iter, user_data):
        _file = model[tree_iter][0]
        if _file.empty:
            renderer.set_property('stock_id', None)
        elif _file.directory:
            renderer.set_property('stock-id', Gtk.STOCK_OPEN)
        else:
            renderer.set_property('stock-id', Gtk.STOCK_FILE)

    def render_file_name(self, col, renderer, model, tree_iter, user_data):
        _file = model[tree_iter][0]
        if _file.root:
            label = _file.file_name
        else:
            label = os.path.basename(_file.file_name)
        hidden = os.path.basename(_file.file_name)[0] == '.'
        label = GLib.markup_escape_text(label)
        if hidden:
            label = '<i>' + label + '</i>'
        renderer.set_property('markup', label)

    def prompt_dir_select(self, widget):
        dialog = Gtk.FileChooserDialog(
                action=Gtk.FileChooserAction.SELECT_FOLDER,
                parent=self,
                buttons=(
                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK))
        rv = dialog.run()

        if rv == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            dialog.destroy()
            GObject.idle_add(self.add_dir, filename)
        else:
            dialog.destroy()

    def on_row_expanded(self, widget, tree_iter, path):
        current_dir = self.treemodel[tree_iter][0]

        place_holder_iter = self.treemodel.iter_children(tree_iter)
        if not self.treemodel[place_holder_iter][0].place_holder:
            return

        paths = os.listdir(current_dir.file_name)
        paths.sort()
        if len(paths) > 0:
            for child_path in paths:
                self.add_dir(os.path.join(current_dir.file_name, child_path), tree_iter)
        else:
            self.treemodel.append(tree_iter, [EMPTY_DIR])

        self.treemodel.remove(place_holder_iter)

    def add_dir(self, dir_name, root=None):
        is_root = root == None
        if os.path.isdir(dir_name):
            tree_iter = self.treemodel.append(root, [File(dir_name, root=is_root)])
            self.treemodel.append(tree_iter, [PLACE_HOLDER])
        else:
            self.treemodel.append(root, [File(dir_name, root=is_root, directory=False)])

if __name__ == '__main__':
    win = MainWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    win.add_dir(os.path.expanduser('~'))
    Gtk.main()
