#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen
import shlex
import sys
import os

SPHINXOPTS = ""
SPHINXBUILD = "sphinx-build"
PAPER = ""
BUILDDIR = "build"
SOURCE = "source"

if PAPER == "a4":
    PAPEROPT = "-D latex_paper_size=a4"
elif PAPER == "letter":
    PAPEROPT = "-D latex_paper_size=letter"
else:
    PAPEROPT = ""

# Internal variables.
ALLSPHINXOPTS = "%(paperopt)s %(sphinxopts)s %(source)s" % {
    'builddir': BUILDDIR,
    'paperopt': PAPEROPT,
    'sphinxopts': SPHINXOPTS,
    'source': SOURCE
    }

sphinxcmd = "%(sphinx)s -b %(builder)s %(options)s %(targetdir)s"


def html(opt):
    '''  html       to make standalone HTML files'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("Build finished. The HTML pages are in %s/html." % BUILDDIR)


def dirhtml():
    '''  dirhtml    to make HTML files named index.html in directories'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("Build finished. The HTML pages are in %s/dirhtml." % BUILDDIR)

def singlehtml():
    '''  singlehtml to make a single large HTML file'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("Build finished. The HTML page is in %s/singlehtml." % BUILDDIR)


def pickle():
    '''  pickle     to make pickle files'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("Build finished. now you can process the pickle files.")


def json():
    '''  json       to make JSON files'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("Build finished; now you can process the JSON files.")


def htmlhelp():
    '''  htmlhelp   to make HTML files and a HTML help project'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)
    print("""Build finished; now you can run HTML Help Workshop with
the .hhp project file in %s/htmlhelp."""  % BUILDDIR)


def qthelp():
    '''  qthelp     to make HTML files and a qthelp project'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, opt['builder'])
    p = _exec(sphinxcmd % opt)

def gettext():
    '''  gettext    to make PO message catalogs'''
    opt['builder'] = sys._getframe().f_code.co_name
    opt['targetdir'] = os.path.join(BUILDDIR, 'locale')
    p = _exec(sphinxcmd % opt)
    print("Build finished. The message catalogs are in %s/locale." % BUILDDIR)


def help():
    '''  help       to show this help'''
    import types

    print("Please use 'python make.py <target>' where <target> is one of")

    for k, f in globals().items():
        if k.startswith("_"):  # private function
            continue
        if isinstance(f, types.FunctionType):
            print(f.__doc__)
    
    exit(0)

def clean(opt):
    '''  clean      to clean up build dir'''
    print("Cleaning build dir")
    cmd = "/bin/rm -rf %s/*" % (BUILDDIR)
    _exec(cmd)


def _exec(cmd):
    '''helper function'''
    cwd = os.path.dirname(os.path.abspath(__file__))
    p = Popen(shlex.split(cmd), cwd=cwd)
    p.wait()

    if p.returncode < 0:
        exit(p.returncode)
    return p

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help()

    opt = {
        'sphinx': SPHINXBUILD,
        'options': ALLSPHINXOPTS
        }
    for builder in sys.argv[1:]:
        try:
            locals()[builder](opt)
        except KeyError:
            help()