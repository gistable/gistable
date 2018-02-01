# a bit of a hack
# by Cormac Relf - cormacrelf.com - @cormacrelf

# Opens the url on the clipboard in Safari
# by opening Google Chrome with an x-callback-url
# that takes you to the same url in Safari.

# I guess you could just open it in googlechrome://

import webbrowser
import clipboard
import console
import urllib
import re

url = clipboard.get()

url = urllib.quote_plus(url)

callback = "googlechrome-x-callback://x-callback-url/open/?url=YOURL&x-source=Safari&x-success=YOURL"

callback = re.sub("YOURL", url, callback)

#console.clear()
#print(callback)

webbrowser.open(callback)