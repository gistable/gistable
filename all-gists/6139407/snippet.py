# To call script from Drafts, use the follwing URL as URL Action:
# <pythonista://sort?action=run&argv=[[draft]]>

import sys
import urllib
import webbrowser

a = sys.argv[1].split("\n")
a.sort(key=str.lower)
a = "\n".join(a)

webbrowser.open("drafts://x-callback-url/create?text=" + urllib.quote(a))
