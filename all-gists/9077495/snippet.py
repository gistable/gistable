import sublime, sublime_plugin

BUILD_COLOR_SCHEME = "Packages/Color Scheme - Default/Twilight.tmTheme"

def in_build_dir(view):
    if not view or not view.file_name():
        return False
    return "/build/" in view.file_name()


class GTFO(sublime_plugin.EventListener):

    def on_modified(self, view=None):
        if in_build_dir(view):
            sublime.error_message("GTFO")

    def on_activated(self, view=None):
        if in_build_dir(view):
            view.settings().set("color_scheme", BUILD_COLOR_SCHEME)
