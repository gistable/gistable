# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin

class MinimapSetting(sublime_plugin.EventListener):

    def on_activated(self, view):
        show_minimap = view.settings().get('show_minimap')
        if show_minimap:
            view.window().set_minimap_visible(True)
        elif show_minimap is not None:
            view.window().set_minimap_visible(False)
