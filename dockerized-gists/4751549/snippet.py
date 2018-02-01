"""
Pythonist script to expand any URL surrounded by **'s

"""
import clipboard
import requests
import webbrowser
import urlparse
from urllib import quote, urlencode

blacklist_query_params = ['utm_campaign', 'utm_source', 'utm_medium']
text = clipboard.get()
if text == '':
    print 'No text in clipboard'

if '**' in text:
    start, url, end = text.split('**')
    resp = requests.get(url)
    if resp.ok:
        url = resp.url

    parts = urlparse.urlsplit(url)
    query = urlparse.parse_qs(parts.query)
    for bkey in blacklist_query_params:
        try:
            del query[bkey]
        except KeyError:
            pass
    parts = list(parts)
    parts[3] = urlencode(query)
    url = urlparse.urlunsplit(parts)

    text = ''.join([start, url, end])

q = quote(text)
webbrowser.open('felix://compose/post?text=' + q)