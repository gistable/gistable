import sublime_plugin

class FileNameOnStatusBar(sublime_plugin.EventListener):
    def on_activated(self, view):
        path = view.file_name()
        if path:
            for folder in view.window().folders():
                path = path.replace(folder + '/', '', 1)
            view.set_status('file_name', path)
        else:
            view.set_status('file_name', 'untitled')