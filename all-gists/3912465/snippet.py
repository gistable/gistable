import re
import terminatorlib.plugin as plugin
import subprocess

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['FileURLHandler']

class FileURLHandler(plugin.URLHandler):
    capabilities = ['url_handler']
    handler_name = 'file_path'

    # Match any non-space string starting with an alnum or a slash and ending with a line number
    match = r'[a-zA-Z0-9\/][^ ]+:[[:digit:]]+|[a-zA-Z0-9\/][^ ]+\([[:digit:]]+\)'

    def callback(self, url):
        p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        p.communicate(input=url)
        p.wait()
        subprocess.call(["subl", "--command", "open_clipboard_path"])
        return "some_random_string_just_so_that_opening_the_resulting_url_will_fail"
