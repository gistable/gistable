import plistlib
from StringIO import StringIO

def plist_from_mobileprovision(provision_path):
    f = open(provision_path)
    f.seek(62)
    string = ""
    lookfor = "</plist>"
    found = False
    while True:
        bytes = f.read(1024)
        pos = bytes.find(lookfor)
        if pos == -1:
            string += bytes
            continue
        string += bytes[0:pos+len(lookfor)]
        found = True
        break
    f.close()
    if not found:
        return None
    s = StringIO(string)
    result = plistlib.readPlist(s)
    if not result:
        return None
    return result