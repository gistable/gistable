import sublime, sublime_plugin
import os.path, string

VALID_FILENAME_CHARS = "-_.() %s%s%s" % (string.ascii_letters, string.digits, "/:\\")

# { "keys": ["alt+o"], "command": "open_filename_under_cursor" }
# https://gist.github.com/1186126
class OpenFilenameUnderCursor(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            # Collect the texts that may possibly be filenames
            quoted_text = self.get_quoted_selection(region)
            selected_text = self.get_selection(region)
            whole_line = self.get_line(region)
            clipboard = sublime.get_clipboard().strip()
            default_new_filename = self.create_filename(selected_text)

            # Search for a valid filename from the possible sources: quoted_text, selected_text, whole_line, clipboard
            # If none of these sources match a valid filename the a new filename will be created from the selected_text
            filename = default_new_filename
            for text in (quoted_text, selected_text, whole_line, clipboard):
                potential_filename = self.get_filename(text)
                if os.path.isfile(potential_filename):
                    filename = potential_filename
                    break

            # If a filename was discovered from one of the sources, then open it
            if filename:
                print "Opening file '%s'" % (filename)
                self.view.window().open_file(filename)
            else:
                 print "No filename discovered in the quoted_text, selected_text, whole_line or clipboard"

    def get_selection(self, region):
        return self.view.substr(region).strip()

    def get_line(self, region):
        return self.view.substr(self.view.line(region)).strip()

    def get_quoted_selection(self, region):
        text = self.view.substr(self.view.line(region))
        position = self.view.rowcol(region.begin())[1]
        quoted_text = self.expand_within_quotes(text, position, '"')
        if not quoted_text:
            quoted_text = self.expand_within_quotes(text, position, '\'')
        return quoted_text

    def expand_within_quotes(self, text, position, quote_character):
        open_quote = text.rfind(quote_character, 0, position)
        close_quote = text.find(quote_character, position)
        return text[open_quote+1:close_quote] if (open_quote > 0 and close_quote > 0) else ''

    def get_filename(self, text):
        return text if os.path.isfile(text.strip()) else ''

    def create_filename(self, text):
        return ''.join(c for c in text if c in VALID_FILENAME_CHARS)
