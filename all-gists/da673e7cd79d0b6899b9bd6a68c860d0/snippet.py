import sublime
import sublime_plugin

class ShowZeroWidthCharacters(sublime_plugin.EventListener):
    """
        Tries to detect and mark zero-width joiners, non-joiners, and other invisible characters.
        Most of the characters were detected by manually testing code points from C++ specs.
        http://en.cppreference.com/w/cpp/language/identifiers
    """

    sublime3 = sublime.version() > '3000'
    zero_width_characters = u'|'.join([
        '\u200b',   # zero-width space
        '\u200c',   # zero-width non-joiner
        '\u200d',   # zero-width joiner
        '\u2060',   # word joiner
        '\u2061',   # function application
        '\u2062',   # invisible times
        '\u2063',   # invisible separator
        '\u2064',   # invisible plus
        '\u2065',   # invalid, still present in the C++ spec
        '\u2066',   # left-to-right isolate
        '\u2067',   # right-to-left isolate
        '\u2068',   # first strong isolate
        '\u2069',   # pop directional isolate
        '\u206a',   # inhibit symmetric swapping
        '\u206b',   # activate symmetric swapping
        '\u206c',   # inhibit arabic form shaping
        '\u206d',   # activate arabic form shaping
        '\u206e',   # national digit shapes
        '\u206f',   # nominal digit shapes
        '\ufeff',   # zero-width no-break space
    ])

    def show_zero_width_characters(self, view):
        view.erase_regions('zero-width')
        regions = view.find_all(self.zero_width_characters)
        if regions:
            view.add_regions('zero-width', regions, 'invalid')

    if sublime3:
        def on_load_async(self, view):
            self.show_zero_width_characters(view)

        def on_post_save_async(self, view):
            self.show_zero_width_characters(view)
    else:
        def on_load(self, view):
            self.show_zero_width_characters(view)

        def on_post_save(self, view):
            self.show_zero_width_characters(view)
