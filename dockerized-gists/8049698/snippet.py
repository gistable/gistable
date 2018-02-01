import sys
import webbrowser
import urllib

unstruck = sys.argv[1]
struck = []
for c in unstruck:
  struck.append(c)
  if c not in ' \t\n':
    struck.append(u'\u0338')
struck = ''.join(struck)

# To call script from Drafts, use the following URL as URL Action:
# <pythonista://Strikeout?action=run&argv=[[draft]]>

webbrowser.open("drafts://x-callback-url/create?text=" + urllib.quote(struck.encode('utf-8')))