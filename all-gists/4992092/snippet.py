#!/usr/bin/env python2
from gi.repository import Gtk

class Grid(Gtk.Window):
	widget_list = []
	WIDGET_SIZE = 140
	COLS = 1
	NUM = 100

	def calcule_columns(self, scroll, grid):
		cols = scroll.get_allocated_width() / (self.WIDGET_SIZE + grid.get_column_spacing())
		if (cols > len(self.widget_list)): cols = len(self.widget_list)
		return cols
		
	def on_resize(self, arg1, arg2, scroll, grid):
		new_cols = self.calcule_columns(scroll, grid)
		if  new_cols == self.COLS or new_cols == 0 or new_cols > len(self.widget_list): return
		self.COLS = new_cols
		self.remove_widgets(grid)
		self.load_widgets(grid)
		
	def remove_widgets(self, grid):
		if self.widget_list == 0: return
		for wid in grid.get_children():
			grid.remove(wid)

	def create_grid(self):
		grid = Gtk.Grid()
		grid.set_column_spacing(10)
		grid.set_row_spacing(10)
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(False)
		grid.set_border_width(0)
		return grid
		
	def load_widgets(self, grid):
		i,j = 0,0
		COLS = self.COLS

		if len(self.widget_list) == 0: return
		
		for wid in self.widget_list:
			grid.attach(wid, i, j, 1, 1)
			i+=1
			if i == COLS:
				i=0
				j+=1

	def __init__(self):
		def callback(widget):
			this = widget.get_label()
			dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
				message_type=Gtk.MessageType.QUESTION,
				buttons=Gtk.ButtonsType.OK)
			dialog.set_title("Window title %s" % this.split(" ")[1])
			dialog.set_markup("You chose <b>%s</b>, try it again!" % this)
			dialog.run()
			dialog.destroy()

		Gtk.Window.__init__(self, title="Grid")
		
		self.resize(self.WIDGET_SIZE*6, self.WIDGET_SIZE*2)
		self.set_position(Gtk.WindowPosition.CENTER)

		grid_main = self.create_grid()
		viewport = Gtk.Viewport(None, None);
		viewport.add(grid_main)
		viewport.set_shadow_type (Gtk.ShadowType.NONE)
		scroll = Gtk.ScrolledWindow()
		scroll.set_border_width(0)
		scroll.add(viewport)
		scroll.connect("size-allocate", self.on_resize, scroll, grid_main)
		scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.add(scroll)

		z = 1
		while z is not self.NUM+1:
			button = Gtk.Button()
			button.set_label("Button %s" % z)
			button.connect("clicked", callback)
			self.widget_list.append(button)
			z+=1

		self.load_widgets(grid_main)


win = Grid()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()