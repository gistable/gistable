import os
import sys

from distutils.core import setup
from distutils.dir_util import copy_tree
from py2exe.build_exe import py2exe

import glob
import zlib
import shutil
import time
import pyface
import enable
import tvtk
import mayavi
import vtk
import compileall

distDir = "building-temp"

# Remove the build folder
shutil.rmtree("build", ignore_errors=True)

class Target(object):
    """ A simple class that holds information on our executable file. """
    def __init__(self, **kw):
        """ Default class constructor. Update as you need. """
        self.__dict__.update(kw)
        

def copyPackage (pkg, name, dist) :
    p = os.path.join (dist, name)
    copy_tree (pkg.__path__[0], p)

copyPackage (tvtk, "tvtk", distDir)
copyPackage (mayavi, "mayavi", distDir)
copyPackage (pyface, "pyface", distDir)
copyPackage (enable, "enable", distDir)
copyPackage (vtk, "vtk", distDir)


includes = ['sip', 'PyQt4.QtSvg', 'PyQt4.QtNetwork', 
            'PyQt4.Qt', 'uuid', 'shelve', 'tvtk', "mayavi", 'PyQt4.QtOpenGL',
            'vtk', 'email', 'email.iterators', 'ntlm',
             'subprocess',  'hardwareid', 'multiprocessing']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 
            'Tkconstants', 'Tkinter']
            
packages = ['tvtk', "mayavi", 'vtk']

dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']

data_files = []
icon_resources = [(1, "main.ico")]
bitmap_resources = []
other_resources = []


GUI2Exe_Target_1 = Target(
    # what to build
    script = "run.py",
    icon_resources = icon_resources,
    bitmap_resources = bitmap_resources,
    other_resources = other_resources,
    dest_base = "xxx",    
    version = "1.0",
    company_name = "xxx",
    copyright = "xxx",
    name = "xxx",
    )

                    
setup(

    data_files = data_files,

    options = {"py2exe": {"compressed": 0, 
                          "optimize": 0,
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "dist_dir": distDir,
                          "xref": False,
                          "skip_archive": True,
                          "ascii": False,
                          "custom_boot_script": '',
                         }
              },

    zipfile = r'library.zip',
    console = [],
    windows = [GUI2Exe_Target_1],
    service = [],
    com_server = [],
    ctypes_com_server = []
    )
