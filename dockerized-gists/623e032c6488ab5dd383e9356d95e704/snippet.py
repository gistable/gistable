# for the love of bacon!
# by Ian Mariano @ianmariano https://twitter.com/ianmariano https://github.com/ianmariano
#
# Free and provided AS-IS with no warranty. No license required.
#

import os
import mimetypes
import re
import sys
import urllib

if len(sys.argv) < 2:
    print "You must specify the start directory!"
    sys.exit(1)

# regex to detect .dir in path
igregex = re.compile(r'\/\.[^\/]*', re.IGNORECASE)

# simple URL match regex
urlregex = re.compile(r'((http[s]?:)?\/\/([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,})', re.IGNORECASE)

# explicit extensions to ignore

igexts = set([
    '.a',
    '.asmx',
    '.bz2',
    '.cer',
    '.class',
    '.config',
    '.csproj',
    '.csr',
    '.dbp',
    '.disco',
    '.dll',
    '.exe',
    '.gz',
    '.idb',
    '.idl',
    '.indd',
    '.key',
    '.log',
    '.map',
    '.mdb',
    '.mo',
    '.nib',
    '.o',
    '.obj',
    '.out',
    '.p12',
    '.pbxproj',
    '.pdb',
    '.pch',
    '.pem',
    '.pfx',
    '.plist',
    '.po',
    '.pot',
    '.rar',
    '.rc',
    '.rc2',
    '.sbr',
    '.sketch',
    '.sln',
    '.storyboard',
    '.strings',
    '.suo',
    '.tar',
    '.vap',
    '.vbproj',
    '.vcxitems'
    '.vcxproj',
    '.vdproj',
    '.xcappdata',
    '.xcarchive',
    '.xcbkptlist',
    '.xccheckout',
    '.xccolortheme',
    '.xcconfig',
    '.xccrashpoint',
    '.xcdatamodel',
    '.xcode',
    '.xcodeplugin',
    '.xcodeplugindata'
    '.xcproject',
    '.xcscheme',
    '.xcuserstate',
    '.xcworkspace',
    '.xib',
    '.xliff',
    '.xsd',
    '.zip'
])

# explicit mime types to ignore
igmimes = set([
    'application/vnd.ms-fontobject',
    'application/font-woff',
    'application/json',
    'application/octet-stream',
    'application/pdf',
    'application/x-font-ttf',
    'application/x-xliff+xml'
])

def should_ignore(r, f):
    igs = igregex.findall(r)

    if len(igs) > 0:
        return True

    if f.startswith('.'):
        return True

    if os.path.splitext(f)[1].lower() in igexts:
        return True

    m = mimetypes.guess_type(f)[0]

    if m:
        m = m.lower()

        if (m.startswith('image/')
            or m.startswith('application/vnd.')
            or m.startswith('audio/')
            or m.startswith('video/')):
            return True

        # simple case
        if m in igmimes:
            return True


    print "{}: {}".format(f, m)

    return False

start = sys.argv[1]
files = []

for root, dirs, filenames in os.walk(start):
    for f in filenames:
        if should_ignore(root, f):
            continue

        files.append(os.path.join(root, f))

print "Scanning {} files...".format(len(files))

cache = [] # for already scanned

for file in files:
    print file

    with open(file, 'r') as f:
        i = 1

        for line in f:
            urls = urlregex.findall(line)

            if len(urls) > 0:
                for u in urls:
                    url = u[0]

                    if url in cache:
                        print "    {}: {} (cached)".format(i, url)
                    else:
                        cache.append(url)

                        if url.startswith('//'):
                            url = 'http:' + url

                        try:
                            code = urllib.urlopen(url).getcode()
                            print "    {}: {} {}".format(i, url, code)
                        except IOError as e:
                            print "    {}: {} ERROR {}".format(i, url, e.strerror)

            i += 1
