
import httplib
import urllib
import re
import os.path

def gist_write(name, content, ext=None, login=None, token=None):
    if ext is None:
        ext = os.path.splitext(name)[1]

    params = {
        "file_ext[gistfile1]": ext,
        "file_name[gistfile1]": name,
        "file_contents[gistfile1]": content
        }
    if not (login is None or token is None):
        params['login'] = login
        params['token'] = token

    conn = httplib.HTTPConnection("gist.github.com")
    conn.request("POST", "/gists", urllib.urlencode(params))
    response = conn.getresponse()

    ret = None
    if response.status == 302:
        data = response.read()
        ret = re.search("(http://gist.github.com/\d+)", data).group(1)

    conn.close()
    return ret

def gist_embed(url):
    return '<script src="%s.js"></script>' % url
