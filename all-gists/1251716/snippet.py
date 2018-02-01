# saved from: http://pastie.org/private/bclbdgxzbkb1gs2jfqzehg

import sublime
import sublimeplugin
import subprocess

class RunExternalCommand(sublimeplugin.TextCommand):
    """
    Runs an external command with the selected text,
    which will then be replaced by the command output.
    """

    def run(self, view, args):
        if view.sel()[0].empty():
            # nothing selected: process the entire file
            region = sublime.Region(0L, view.size())
        else:
            # process only selected region
            region = view.line(view.sel()[0])

        p = subprocess.Popen(
            args,
            shell=True,
            bufsize=-1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)

        output, error = p.communicate(view.substr(region).encode('utf-8'))

        if error:
            sublime.errorMessage(error.decode('utf-8'))
        else:
            view.replace(region, output.decode('utf-8'))
