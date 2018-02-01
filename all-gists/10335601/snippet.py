import sublime, sublime_plugin

def open_url(url):
    sublime.active_window().run_command("open_url", { "url": url })

class PromptQuickDocCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Documentation Search:", "", self.on_done, None, None)
        pass

    def on_done(self, text):
        try:
            if self.window.active_view():
                self.window.active_view().run_command("quick_doc", {"text": text} )
        except ValueError:
            pass

class QuickDocCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        open_url("http://en.cppreference.com/mwiki/index.php?title=Special:Search&search=%s" % text)
