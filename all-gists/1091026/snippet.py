import sublime_plugin

class StripTrailingWhitespaceCommand(sublime_plugin.TextCommand):
    """
    Strip whitespace from the end of each line in the file.
    """
    def run(self, edit):
        trailing_white_space = self.view.find_all("[\t ]+$")
        trailing_white_space.reverse()
        for r in trailing_white_space:
            self.view.erase(edit, r)
