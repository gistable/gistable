#!/usr/bin/python
# -*- coding: utf-8 -*-

# [SNIPPET_NAME: Systray icon]
# [SNIPPET_CATEGORIES: PyGTK]
# [SNIPPET_DESCRIPTION: Shows a system tray icon with a menu  ]
# [SNIPPET_AUTHOR: João Pinto <joao.pinto@getdeb.net>]
# [SNIPPET_LICENSE: GPL]
# 
# adapted from: http://eurion.net/python-snippets/snippet/Systray%20icon.html
# TODO: add slider (current version has only scroll on icon)


import gtk, gobject
from subprocess import Popen

VOL_UP = 'amixer set Master 5%+' # command to set up
VOL_DOWN = 'amixer set Master 5%-' # command to set down


class SystrayIconApp:
	def __init__(self):
		self.tray = gtk.status_icon_new_from_icon_name('audio-volume-medium')
		self.tray.connect('scroll-event', self.on_scroll)
		self.tray.set_tooltip(('Volume tray app'))
		
	def on_scroll(self, icon, event):
		if event.direction == gtk.gdk.SCROLL_UP:
			Popen(VOL_UP.split(' '))
		else:
			Popen(VOL_DOWN.split(' '))	


if __name__ == "__main__":
	SystrayIconApp()
	gtk.main()
