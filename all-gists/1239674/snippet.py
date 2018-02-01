# encoding: utf-8

import sublime
import sublime_plugin


class UnicodeTransformer(sublime_plugin.EventListener):
    """The transfrormer was tested with CoffeeScript code."""
    _just_io = False  # Determines if the file was just loaded / saved.
    _is_saving = False
    substitutions = {
        u"<-": u"←",
        u"->": u"→",
        u"=>": u"⇒",
        u">=": u"≳",
        u"<=": u"≲",
        u"==": u"≡",
        u"!=": u"≠",
        u" for ": u" ∀ ",
        u" or ": u" ∨ ",
        u" and ": u" ∧ ",
        u" in ": u" ∈ ",
        u" not in ": u" ∉ ",
        u" not ": u" ¬ ",
    }

    def _replace(self, view, edit, replace_from, replace_to):
        def get_region():
            return view.find(replace_from, 0)
        region = get_region()
        while region:
            view.replace(edit, region, replace_to)
            region = get_region()

    def _replace_all(self, view, reversed):
        edit = view.begin_edit()
        for text, subst in self.substitutions.items():
            if reversed:
                replace_from, replace_to = subst, text
            else:
                replace_from, replace_to = text, subst
            self._replace(view, edit, replace_from, replace_to)
        view.end_edit(edit)

    def plain_to_unicode(self, view):
        self._replace_all(view, False)

    def unicode_to_plain(self, view):
        self._replace_all(view, True)

    def on_modified(self, view):
        if self._is_saving or view.is_loading():
            return
        if self._just_io:
            self._just_io = False
            return
        if view.is_scratch():
            view.set_scratch(False)
        self.plain_to_unicode(view)

    def on_load(self, view):
        view.set_scratch(True)
        self.plain_to_unicode(view)
        self._just_io = True

    def on_pre_save(self, view):
        self._is_saving = True
        self.unicode_to_plain(view)

    def on_post_save(self, view):
        view.set_scratch(True)
        self.plain_to_unicode(view)
        self._just_io = True
        self._is_saving = False
