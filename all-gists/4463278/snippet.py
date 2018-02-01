#!/usr/bin/env python3

# This script demonstrates a custom TreeModel (known as
# GenericTreeModel in PyGtk 2).
#
# Note: This script requires python-gi (pygobject) >= 3.4.

from gi.repository import GObject, Gtk


class CustomTreeModel(GObject.GObject, Gtk.TreeModel):

    def __init__(self, data):
        self.data = data
        self._num_rows = len(self.data)
        if self.data:
            self._n_columns = len(self.data[0])
        else:
            self._n_columns = 0
        GObject.GObject.__init__(self)

    def do_get_iter(self, path):
        """Returns a new TreeIter that points at path.

        The implementation returns a 2-tuple (bool, TreeIter|None).
        """
        indices = path.get_indices()
        if indices[0] < self._num_rows:
            iter_ = Gtk.TreeIter()
            iter_.user_data = indices[0]
            return (True, iter_)
        else:
            return (False, None)

    def do_iter_next(self, iter_):
        """Returns an iter pointing to the next column or None.

        The implementation returns a 2-tuple (bool, TreeIter|None).
        """
        if iter_.user_data is None and self._num_rows != 0:
            iter_.user_data = 0
            return (True, iter_)
        elif iter_.user_data < self._num_rows - 1:
            iter_.user_data += 1
            return (True, iter_)
        else:
            return (False, None)

    def do_iter_has_child(self, iter_):
        """True if iter has children."""
        return False

    def do_iter_nth_child(self, iter_, n):
        """Return iter that is set to the nth child of iter."""
        # We've got a flat list here, so iter_ is always None and the
        # nth child is the row.
        iter_ = Gtk.TreeIter()
        iter_.user_data = n
        return (True, iter_)

    def do_get_path(self, iter_):
        """Returns tree path references by iter."""
        if iter_.user_data is not None:
            path = Gtk.TreePath((iter_.user_data,))
            return path
        else:
            return None

    def do_get_value(self, iter_, column):
        """Returns the value for iter and column."""
        return str(self.data[iter_.user_data][column])

    def do_get_n_columns(self):
        """Returns the number of columns."""
        return self._n_columns

    def do_get_column_type(self, column):
        """Returns the type of the column."""
        # Here we only have strings.
        return str

    def do_get_flags(self):
        """Returns the flags supported by this interface."""
        return Gtk.TreeModelFlags.ITERS_PERSIST


if __name__ == '__main__':
    import sys, random

    # Create dummy data (a list of 2-tuples: id, name)
    names = ['Alice', 'Bob', 'Carol', 'Dave']
    n_rows = 1000
    data = [(str(i), random.choice(names)) for i in range(n_rows)]

    # Create the custom tree model with this data
    model = CustomTreeModel(data)

    # Create a window
    win = Gtk.Window()
    win.connect('destroy', lambda *a: Gtk.main_quit())

    # Setup TreeView
    view = Gtk.TreeView()
    view.set_model(model)
    view.append_column(Gtk.TreeViewColumn('#', Gtk.CellRendererText(), text=0))
    view.append_column(Gtk.TreeViewColumn('Name', Gtk.CellRendererText(), text=1))

    # Put it in a ScrolledWindow and show it
    sw = Gtk.ScrolledWindow()
    sw.add(view)
    win.add(sw)
    win.resize(500, 500)
    win.show_all()
    Gtk.main()
  