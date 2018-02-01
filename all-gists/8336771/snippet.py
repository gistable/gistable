import sublime, sublime_plugin

BLOCKLEN = 4

class TypeFileOutCommand(sublime_plugin.TextCommand):
    def nextchar(self):
        if self.body:
            totype = []
            while 1:
                try:
                    ch = self.body.pop(0)
                except IndexError:
                    totype.append(ch)
                    break
                totype.append(ch)
                if ch in ["\n", " "] or len(totype) > BLOCKLEN:
                    break
            self.view.insert(self.edit, self.view.sel()[0].begin(), "".join(totype))
            timeout = 10
            if "\n" in totype:
                timeout = 250
            elif " " in totype:
                timeout = 80
            sublime.set_timeout(self.nextchar, timeout)

    def run(self, edit):
        self.edit = edit
        # First, read everything in this view
        reverything = sublime.Region(0, self.view.size())
        self.body = list(self.view.substr(reverything))

        self.view.erase(edit, reverything)

        sublime.set_timeout(self.nextchar, 2000)
