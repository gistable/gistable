import sublime
import sublime_plugin

class NumberCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            try:
                value = int(self.view.substr(region))
                self.view.replace(edit, region, str(self.op(value)))
            except ValueError:
                pass

    def is_enabled(self):
        return len(self.view.sel()) > 0

class IncrementCommand(NumberCommand):
    def op(self, value):
          return value + 1

class DecrementCommand(NumberCommand):
    def op(self, value):
          return value - 1
