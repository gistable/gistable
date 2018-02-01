#!/usr/bin/env python
"""
auto scan resources file and create Qt resource(qrc) file for PySide/PyQt project

Usage:
    python auto_create_qrc.py your_pictures_path > bar.qrc

    pyside-rcc -no-compress bar.qrc -o bar.py # if you use PySide

    pyrcc4-2.7 -no-compress bar.qrc -o bar.py # if you use PyQt

Author: Shuge Lee <shuge.lee@gmail.com>
License: MIT License
"""
import os
import re
import sys

PWD = os.path.dirname(os.path.realpath(__file__))


# the function strips copy from web.utils.strips

iters = [list, tuple]
import __builtin__
if hasattr(__builtin__, 'set'):
    iters.append(set)
if hasattr(__builtin__, 'frozenset'):
    iters.append(set)
if sys.version_info < (2,6): # sets module deprecated in 2.6
    try:
        from sets import Set
        iters.append(Set)
    except ImportError:
        pass

class _hack(tuple): pass
iters = _hack(iters)
iters.__doc__ = """
A list of iterable items (like lists, but not strings). Includes whichever
of lists, tuples, sets, and Sets are available in this version of Python.
"""


def _strips(direction, text, remove):
    if isinstance(remove, iters):
        for subr in remove:
            text = _strips(direction, text, subr)
        return text

    if direction == 'l':
        if text.startswith(remove):
            return text[len(remove):]
    elif direction == 'r':
        if text.endswith(remove):
            return text[:-len(remove)]
    else:
        raise ValueError, "Direction needs to be r or l."
    return text

def rstrips(text, remove):
    """
    removes the string `remove` from the right of `text`

        >>> rstrips("foobar", "bar")
        'foo'

    """
    return _strips('r', text, remove)

def lstrips(text, remove):
    """
    removes the string `remove` from the left of `text`

        >>> lstrips("foobar", "foo")
        'bar'
        >>> lstrips('http://foo.org/', ['http://', 'https://'])
        'foo.org/'
        >>> lstrips('FOOBARBAZ', ['FOO', 'BAR'])
        'BAZ'
        >>> lstrips('FOOBARBAZ', ['BAR', 'FOO'])
        'BARBAZ'

    """
    return _strips('l', text, remove)

def strips(text, remove):
    """
    removes the string `remove` from the both sides of `text`

        >>> strips("foobarfoo", "foo")
        'bar'
    """
    return rstrips(lstrips(text, remove), remove)



def tree(top = '.',
         filters = None,
         output_prefix = None,
         max_level = 4,
         followlinks = False,
         top_info = False,
         report = True):
    # The Element of filters should be a callable object or
    # is a byte array object of regular expression pattern.
    topdown = True
    total_directories = 0
    total_files = 0

    top_fullpath = os.path.realpath(top)
    top_par_fullpath_prefix = os.path.dirname(top_fullpath)

    if top_info:
        lines = top_fullpath
    else:
        lines = ""

    if filters is None:
        _default_filter = lambda x : not x.startswith(".")
        filters = [_default_filter]

    for root, dirs, files in os.walk(top = top_fullpath, topdown = topdown, followlinks = followlinks):
        assert root != dirs

        if max_level is not None:
            cur_dir = strips(root, top_fullpath)
            path_levels = strips(cur_dir, "/").count("/")
            if path_levels > max_level:
                continue

        total_directories += len(dirs)
        total_files += len(files)

        for filename in files:
            for _filter in filters:
                if callable(_filter):
                    if not _filter(filename):
                        total_files -= 1
                        continue
                elif not re.search(_filter, filename, re.UNICODE):
                    total_files -= 1
                    continue

                if output_prefix is None:
                    cur_file_fullpath = os.path.join(top_par_fullpath_prefix, root, filename)
                else:
                    buf = strips(os.path.join(root, filename), top_fullpath)
                    if output_prefix != "''":
                        cur_file_fullpath = os.path.join(output_prefix, buf.strip('/'))
                    else:
                        cur_file_fullpath = buf

                lines = "%s%s%s" % (lines, os.linesep, cur_file_fullpath)

    lines = lines.lstrip(os.linesep)

    if report:
        report = "%d directories, %d files" % (total_directories, total_files)
        lines = "%s%s%s" % (lines, os.linesep * 2, report)

    return lines



def scan_files(src_path = ".", output_prefix = "./"):
    filters = ['.(png|jpg|gif)$']
    report = False
    lines = tree(src_path, filters = filters, output_prefix = output_prefix, report = report)

    lines = lines.split('\n')
    if "" in lines:
        lines.remove("")

    return lines


QRC_TPL = """<!DOCTYPE RCC><RCC version="1.0">
<qresource>
%s
</qresource>
</RCC>"""

def create_qrc_body(lines):
    buf = ["<file>%s</file>" % i for i in lines]
    buf = "\n".join(buf)
    buf = QRC_TPL % buf

    return buf

def get_realpath(path):
    if os.path.islink(path) and not os.path.isabs(path):
        PWD = os.path.realpath(os.curdir)
        path = os.path.join(PWD, path)
    else:
        path = os.path.realpath(path)
    return path

def create_qrc(src_path, output_prefix, dst_file = None):
    src_path = get_realpath(src_path)

    lines = scan_files(src_path, output_prefix)
    buf = create_qrc_body(lines)

    if dst_file:
        parent = os.path.dirname(dst_file)
        if not os.path.exists(parent):
            os.makedirs(parent)

        f = file(dst_file, "w")
        f.write(buf)
        f.close()
    else:
        sys.stdout.write(buf)

        
if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) not in (1, 2):
        msg = "Usage: " + '\n'
        msg += "python auto_create_qrc.py <src_path>" + '\n'
        msg += "python auto_create_qrc.py <src_path> <output_prefix>"
        sys.stdout.write('\n' + msg + '\n')
        sys.exit(-1)

    src_path = args[0]
    if len(args) == 1:
        output_prefix = "./"
    else:
        output_prefix = args[1]

    create_qrc(src_path, output_prefix)
