#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2,json
from urllib import quote_plus,unquote_plus
from gtk import *
from sys import exit

class GUI:

	def destroy(self, widget, data=None):
		exit()


	def __init__(self):
		self.window = Window(WINDOW_TOPLEVEL)
		self.window.set_position(WIN_POS_CENTER)
		self.window.set_size_request(400, 250)
		self.window.set_title("Google Dork Scan V0.1")
		self.window.set_resizable(False)
		color = gdk.color_parse('#000000')
		self.window.modify_bg(STATE_NORMAL, color)

		fix = Fixed()

		self.lb1 = Label("<span color='green'>Search:</span>")
		self.lb2 = Label("<span color='green'>Autor: MMxM</span>")
		self.lb3 = Label("<a href=''><span color='green'>Clear</span></a>")

		self.lb3.connect("activate-link", self.clear)

		self.lb1.set_use_markup(True)	
		self.lb2.set_use_markup(True)
		self.lb3.set_use_markup(True)

		self.bt1 = Button("Start")
		self.bt1.connect("clicked",self.busca)

		self.edit1 = Entry()
		self.edit1.set_size_request(250, 25)

		self.view = TextView(buffer = None)
		self.view.set_size_request(360, 150)
		sw = ScrolledWindow()
		sw.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
		sw.add(self.view)

		self.view.set_editable(False)
		self.view.set_cursor_visible(False)

		fix.put(self.lb1, 10, 22)
		fix.put(self.lb2, 10, 215)
		fix.put(self.lb3, 340, 215)
		fix.put(self.bt1, 340, 17)
		fix.put(self.edit1, 68, 17)
		fix.put(sw, 15, 55)
	
		self.window.add(fix)
		self.window.show_all()
		self.window.connect("destroy",self.destroy)

	def busca(self,widget):
		if self.edit1.get_text() == '': return

		try:
			search = quote_plus(self.edit1.get_text())
			n = 0
			while True:
				url = 'http://ajax.googleapis.com/ajax/services/search/web?v=2.0&q=%s&start=%s' %(search,n)
				req = urllib2.Request(url)
				response = urllib2.urlopen(req).read()
				data = json.loads(response)
				for extract in (data['responseData']['results']):
					self.view.get_buffer().insert_at_cursor('%s\n'%unquote_plus(extract['url']))
					while events_pending():
						main_iteration()

				n += 4
		except:
			self.view.get_buffer().insert_at_cursor('\n100% Complete !!!\n')

	def clear(self, a, b):
		self.view.get_buffer().set_text('')
		return True

	def main(self):
		main()


if __name__ == "__main__":
	start = GUI()
	start.main()