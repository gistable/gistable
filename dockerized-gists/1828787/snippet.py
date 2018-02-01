import sys
import urllib2
from json import loads
from urllib import urlencode
import base64
print sys.argv

LOG_FILE = 'uploads.log'

DEV_KEY = 'YOUR KEY HERE' # from http://imgur.com/register/api_anon

def add_to_clipboard(str):
    from Tkinter import Tk
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(str)
    r.destroy()

def upload(local):

    img = open(local, "rb").read()

    b64 = base64.encodestring(img)
    data = urlencode({
                       "image" : b64,
                       "key" : DEV_KEY
                    })
    request = urllib2.Request("http://api.imgur.com/2/upload.json", data)
    try:
        response = urllib2.urlopen(request).read()
        json = loads(response)
        remote = json["upload"]["links"]["original"]
    except urllib2.HTTPError, e:
        print e

    return remote

def main():
    if len(sys.argv) < 2:
        print """
    Usage:
        snagurl.py <local-file>
    """
        return 1

    local = sys.argv[1]

    print "Processing %s" % local

    remote = upload(local)

    print "Uploaded to: %s" % remote
    add_to_clipboard(remote)
    f = open(LOG_FILE, 'a')
    f.write("%s -> %s\n" % (local, remote))

if __name__ == '__main__':
    main()
