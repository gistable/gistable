# Clickable Files by nofxx
"""files.py - Clickable Files URIs open in Emacs"""
import re
import terminatorlib.plugin as plugin
import subprocess

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['FileURLHandler']

class FileURLHandler(plugin.URLHandler):
    capabilities = ['url_handler']
    handler_name = 'file_path'

    # Match any non-space string starting with an alphanumericm or a slash
    # and ending with a colon followed by a number
    match = r'[a-zA-Z0-9\.\/][^ ]+:[[:digit:]]+|[a-zA-Z0-9\/][^ ]+\([[:digit:]]+\)'

    def callback(self, url):
        # Change file(N) to file:N
        url = re.sub('[\)]', '', re.sub('[\(]', ':', url))
        # Change file#N to file:N
        url = re.sub('[#]', ':', url)
        # Split result match file:line:col
        params = url.split(':')
        if len(params) == 3:
          fname, line, col = params
          opts = "+" + line + ":" + col
        else:
          fname, line = params
          opts = "+" + line
        print "Opening..." + fname + "#" + opts
        subprocess.call(["emacsclient", "-n", opts, fname])
        return "some_nice_shining_string"
