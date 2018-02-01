import sublime, sublime_plugin
import os, stat

class MakeExecutable(sublime_plugin.EventListener):

    def on_post_save(self, view):

        filename = view.file_name()
        ext = os.path.splitext(filename)[1]

        if not ext:
            shebang = view.substr(sublime.Region(0, 2))

            if shebang == '#!':
                mode = os.stat(filename)[stat.ST_MODE]
                mode = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                os.chmod(filename, mode)

                self.name = os.path.split(filename)[1]
                sublime.set_timeout(
                    lambda: sublime.status_message(
                        "'{0}' is now executable.".format(self.name)
                    ),
                    4000)
