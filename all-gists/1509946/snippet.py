# encoding: utf-8

import sublime, sublime_plugin

class DetectSpecialCharacters(sublime_plugin.EventListener):
    def on_load(self, view):
        sublime.status_message("detect_special_characters is active")
    def on_modified(self, view):
            # find no-break space
            special_characters = view.find_all(u"\u00A0")
            if len(special_characters) > 0:
                sublime.error_message("ohhh noose! detected a NO-BREAK SPACE (U+00A0)")
