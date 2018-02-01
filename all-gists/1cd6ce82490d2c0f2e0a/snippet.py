import sublime, sublime_plugin

class MinifyOnSave(sublime_plugin.EventListener):
	def on_post_save(self, view):
		file_types_to_minify = ['js', 'css']
		filenameParts = view.file_name().split('.')
		if filenameParts[len(filenameParts) - 1] in file_types_to_minify:
			view.run_command('minify')