#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import walk, rename, unlink, mkdir, remove
from os.path import isdir, exists
from sys import argv, exit, getfilesystemencoding
from shutil import copyfile
import shutil

conversion = {
	u'А': u'A',
        u'Б': u'B',
        u'В': u'V',
        u'Г': u'G',
        u'Д': u'D',
        u'Е': u'E',
        u'Ё': u'E',
        u'Ж': u'Zh',
        u'З': u'Z',
        u'И': u'I',
        u'Й': u'Y',
        u'К': u'K',
        u'Л': u'L',
        u'М': u'M',
        u'Н': u'N',
        u'О': u'O',
        u'П': u'P',
        u'Р': u'R',
        u'С': u'S',
        u'Т': u'T',
        u'У': u'U',
        u'Ф': u'F',
        u'Х': u'H',
        u'Ц': u'Ts',
        u'Ч': u'Ch',
        u'Ш': u'Sh',
        u'Щ': u'Sch',
        u'Ъ': u'',
        u'Ы': u'Y',
        u'Ь': u'',
        u'Э': u'E',
	u' ' : '_',
        }
def cyr2lat(s):
    retval = ""
    for c in s:
	if ord(c) > 128: 
		try: 
			c = conversion[c.upper()].lower() 
		except KeyError: 
			c=''
	elif c == ' ':
		c = '_'
        retval += c
    return retval
    
if len(argv) == 1:
    print "Usage: %s <dirs>" % argv[0]
    exit(-1)

processed = []

def recursive_walk(dir):
    # See http://docs.activestate.com/activepython/2.5/whatsnew/2.3/node6.html
    found = []
    dir = unicode(dir)
    for finfo in walk(dir, True):
        dirnames = finfo[1]
        fnames = finfo[2]
        for subdir in dirnames:
            subdir = "%s/%s" % (dir, subdir)
            if subdir in processed:
                continue
            for yield_val in recursive_walk(subdir):
                yield yield_val
        for fname in fnames:
            yield '%s/%s' % (dir, fname)
    raise StopIteration

if __name__ == "__main__":
    fs_enc = getfilesystemencoding()
    for dir in argv[1:]:
        for fpath in recursive_walk(dir):
            new_fpath = cyr2lat(fpath).lower()
	    print 'new path %s' % new_fpath
            print fpath.encode('utf-8')
            # First make dirs
            path_elts = new_fpath.split('/')
            for idx in range(len(path_elts))[1:]:
                subpath = '/'.join(path_elts[:idx])
                while True:
                    i = 0
                    if exists(subpath):
                        if not isdir(subpath):
                            print '%s exists but is not a directory, will try again' % subpath
                            subpath += str(i)
                            continue
                        else:
                            path_elts[idx - 1] = subpath.split('/')[-1]
                            break
                    else:
                        print 'Creating directory: %s' % subpath
                        mkdir(subpath)
                        break
            print 'Copying %s to %s' % (fpath, new_fpath)
            shutil.copyfile(fpath, new_fpath)
	    remove(fpath)