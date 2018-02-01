#!/usr/bin/env python

import os
import subprocess as sp

def build_cmake_bin(srcdir, installdir):
    """
    This function builds a 'build' directory under srcdir for out of source build.
    The compiled binaries will be automatically installed to installdir.
    
    Inputs:
    - srcdir: directory containing 'CMakeLists.txt'
    - installdir: directory to install compiled binaries
    """

    origpath = os.getcwd()
    os.chdir(srcdir)

    if not os.path.isfile("CMakeLists.txt"):
        print "-- ERROR: can't find CMakeLists.txt in " + os.getcwd()
        exit(-1)

    if os.path.isdir( "build" ):
        r = raw_input( "-- Previous build exists, delete?[y/n]")
        if r == "y":
            sp.call( "rm -rf build/*", shell=True )
    else:
        os.makedirs( "build" )

    os.chdir( "build" )
    sp.call( ["cmake", "-DCMAKE_INSTALL_PREFIX=" + installdir, ".."] )
    sp.call( ["make"] )
    sp.call( ["make", "install"] )

    os.chdir(origpath)