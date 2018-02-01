#!/usr/bin/env python
# $ python sitemap.py ~/sbp.so | pbcopy

import sys
import os

def help():
    print "Usage: sitemap.py [ docroot ]"

def main():
    docroot = '.'
    if len(sys.argv) == 2:
        docroot = sys.argv[1]
    elif len(sys.argv) != 1:
        return help()

    os.chdir(docroot)

    paths = []
    for root, dirs, files in os.walk('.'):
        for name in files:
            path = os.path.join(root, name)
            paths.append(path.lstrip('./'))

    prefix = None
    for path in sorted(paths, key=str.lower):
        suffix = path.rsplit('.', 1).pop()
        if suffix in set(["ttf", "ico", "png", "jpg", "gif", "svg", "xml", "woff"]):
            continue

        content = False
        if path.endswith(".html") or path.endswith(".txt"):
            path = path.rsplit(".", 1)[0]
            content = True

        first = path[0].lower() if path[0].isalpha() else '%'
        if first != prefix:
            if prefix: print '<!-- ] --><br>'
            prefix = first
            print '<strong>%s</strong>' % prefix.upper()
            print '<!-- [ -->'
        cls = '' if content else ' class="anciliary"'
        print ' &middot; <a href="/%s"%s>%s</a>' % (path, cls, path)
    print '<!-- ] --><br>'

if __name__ == "__main__":
    main()
