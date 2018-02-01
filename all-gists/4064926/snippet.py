import os
import re
import sys

# Crazy URL regexp from Gruber
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
r = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))')

# grep -r
for parent, dnames, fnames in os.walk(sys.argv[1]):
    for fname in fnames:
        filename = os.path.join(parent, fname)
        if os.path.isfile(filename):
            with open(filename) as f:
                c = 0
                for line in f:
                    c = c + 1
                    match = r.search(line)
                    if match:
                        # <file>:<line>:<match>
                        print '%s:%s:%s' % (filename, c, match.string[match.start():match.end()])
                        # <match>
                        #print match.string[match.start():match.end()]
