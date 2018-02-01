#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Alexey Kutepov a.k.a. rexim

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import codecs
import locale
import sys
import json

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

def export_bookmarks(bookmarks, fp):
    # The inner recursive function which does the main work
    def export_bookmarks_impl(bookmarks, level):
        # Output the node according to its type and the current level
        if bookmarks['type'] == 'text/x-moz-place-container':
            fp.write('%s %s\n' % ('*' * level, bookmarks['title']))
        elif bookmarks['type'] == 'text/x-moz-place':
            fp.write('%s - [[%s][%s]]\n' % (' ' * (level - 1),
                                            bookmarks['uri'],
                                            bookmarks['title']))

        if bookmarks.has_key('children'):
            # Due to the nature of org-mode format, it is important to
            # export not folder nodes first. So they are guaranteed to
            # be children of the current node.
            for child in bookmarks['children']:
                if child['type'] == 'text/x-moz-place':
                    export_bookmarks_impl(child, level + 1)

            for child in bookmarks['children']:
                if child['type'] == 'text/x-moz-place-container':
                    export_bookmarks_impl(child, level + 1)

    # Starting the traversal from level 1
    export_bookmarks_impl(bookmarks, 1)

if __name__ == '__main__':
    # Reading JSON from stdin
    bookmarks = json.load(sys.stdin)

    # Writing org-mode to stdout
    export_bookmarks(bookmarks, sys.stdout)
