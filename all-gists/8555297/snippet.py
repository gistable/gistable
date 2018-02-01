# this plugin creates a command `open_from_clipboard` that opens the path that's currently in the clipboard
# save this file at Packages/User/openclipboard.py
# then add the follow key binding if you like via the menu Preferences > Key Bindings - User
# 	{ "keys": ["ctrl+shift+o"], "command": "open_from_clipboard" }

import sublime
import sublime_plugin

class OpenFromClipboardCommand(sublime_plugin.WindowCommand):
	def run(self):
		fn = sublime.get_clipboard()
		if fn:
			sublime.active_window().open_file(fn)
		else:
			sublime.status_message("Nothing to open. The clipboard is empty.")
