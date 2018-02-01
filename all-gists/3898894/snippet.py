# Sublime's HTML reindenting is currently pretty bad.  And Tidy and xmllint
# change my code in ways I don't really like or need. I just need the thing
# reindented sanely.  Emacs did that pretty well.
#
# One thing led to another.  A few drinks later and now I'm using Emacs to
# reindent HTML from within Sublime.
#
# Save the contents of this file as ohmygodemacs.py in your User directory.
# Then save the contents of the following docstring as ohmygodemacs.elsip in your
# User directory
#
# Then bind this command to a keystroke, e.g. "ctrl-alt-x" by adding
# this to your user keymap:
#
#  { "keys": ["ctrl+alt+x"], "command": "emacs_reindent" },
#
# Or execute it from the console:
#
# view.run_command('emacs_reindent')
#

"""
;; ohmygodemacs.elisp
;; ex: emacs --no-site-file -batch contents.html -l ohmygodemacs.elisp -f emacs-format-function

(defun emacs-format-function ()
   "Format the whole buffer."
   (indent-region (point-min) (point-max) nil)
   (untabify (point-min) (point-max))
   (princ (buffer-string))
)
"""

import subprocess
import tempfile
import os
import sublime
import sublime_plugin

class EmacsReindentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.sel()[0].size() > 0:
            self.cursor = None
            for region in self.view.sel():
                self.format(edit, region)
        else:
            self.cursor = self.view.sel()[0]
            region = sublime.Region(0, self.view.size())
            self.format(edit, region)
      
    def clear(self):
        self.view.erase_status('emacs_reindent')

    def format(self, edit, region):
        fd, tmpnam = tempfile.mkstemp()
        try:
            self._reindent(edit, region, fd, tmpnam)
        finally:
            try:
                os.unlink(tmpnam)
            except:
                pass

    def _reindent(self, edit, region, fd, tmpnam):
        fp = os.fdopen(fd, 'wb+')
        content = self.view.substr(region).encode('utf-8')
        fp.write(content)
        fp.flush()
        htmlname = tmpnam+'.html'
        os.rename(tmpnam, htmlname)
        packages_path = sublime.packages_path()
        ohmygodpath = os.path.join(packages_path, 'User', 'ohmygodemacs.elisp')
        command = ('emacs --no-site-file -batch %s -l %s -f '
                   'emacs-format-function' % (htmlname, ohmygodpath))
        p = subprocess.Popen(
            command, bufsize=-1, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True
            )
        result, err = p.communicate()
        if err != "":
            self.view.set_status('emacs_reindent', "emacs_reindent: "+err)
            sublime.set_timeout(self.clear,10000)
        else:
            self.view.replace(
                edit, self.view.line(region), 
                result.decode('utf-8').replace('\r\n', '\n')
                )
            sublime.set_timeout(self.clear,0)
            # minor delay necessary, not sure why (cargo culted from tidyxml)
            sublime.set_timeout(self.move_cursor,1) 

    def move_cursor(self):
        if self.cursor != None:
            self.view.sel().clear()
            self.view.sel().add(self.cursor)
            self.view.show(self.cursor)
