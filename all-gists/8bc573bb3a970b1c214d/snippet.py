# NewFileAtCurrentFolder

import sublime_plugin
import os.path

class NewFileListener(sublime_plugin.EventListener):
    def on_new_async(self, view):
        if not view.window().active_view():
            print("NF: no view")
            return

        newView = view.window().active_view()
        index = view.window().views().index(newView)
        lastView = view.window().views()[index - 1]
        if not lastView:
            print("NF: no lastView")
            return

        fileName = lastView.file_name()
        if not fileName:
            print("NF: no fileName")
            return

        basePath = os.path.dirname(fileName)
        if not basePath:
            print("NF: no basePath")
            return
        print("NF: "+basePath)
        newView.settings().set('default_dir', basePath)
