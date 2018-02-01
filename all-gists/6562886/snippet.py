# Copyright (c) 2013, Niklas Rosenstein
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Changelog:
#
# 2013-09-14: Initial version
#
# This script demonstrates how to find the hierarchy-path from one object
# to another using recursion.

import c4d

def find_path(src, dst, down=True, up=True, next=True, pred=True):
    if not src or not dst:
        return None
    if src == dst:
        return ''
    
    curr = src.GetDown()
    if curr and down:
        path = find_path(curr, dst, down, False, next, pred)
        if path is not None:
            return 'D' + path

    curr = src.GetPred()
    if curr and pred:
        path = find_path(curr, dst, True, up, False, pred)
        if path is not None:
            return 'P' + path

    curr = src.GetNext()
    if curr and next:
        path = find_path(curr, dst, True, up, next, False)
        if path is not None:
            return 'N' + path

    curr = src.GetUp()
    if curr and up:
        path = find_path(curr, dst, False, up, next, pred)
        if path is not None:
            return 'U' + path
        
    return None

def execute_path(src, path):
    path = str(path).upper()
    for c in path:
        if not src: break
        if c == 'D':
            src = src.GetDown()
        elif c == 'U':
            src = src.GetUp()
        elif c == 'N':
            src = src.GetNext()
        elif c == 'P':
            src = src.GetPred()
    return src

def main():
    a = doc.SearchObject('From')
    b = doc.SearchObject('To')

    # Find the path from object A to object B.
    p = find_path(a, b)
    if p is None:
        print "Path could not be found!"
        return

    # Execute the path starting from object A.
    new_b = execute_path(a, p)
    
    namet = a.GetName(), b.GetName(), p
    if new_b == b:
        print "The path from object %r to %r is %r" % namet
    else:
        print "The generated path from object %r to %r is invalid: %s" % namet

main()