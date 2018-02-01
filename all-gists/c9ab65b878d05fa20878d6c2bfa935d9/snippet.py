#!/usr/bin/env python

import os
import sys
import os.path
import site

try:
    import binaryninja
    print "Binary Ninja API Installed"
    sys.exit(0)
except ImportError:
    pass

if sys.platform == "linux":
    binaryninja_api_path = "/opt/binaryninja/python"
elif sys.platform == "darwin":
    binaryninja_api_path = "/Applications/Binary Ninja.app/Contents/Resources/python"
else:
    # Windows
    binaryninja_api_path = "r'C:\Program Files\Vector35\BinaryNinja\python'"

def validate_path(path):
    try:
        os.stat(path)
    except OSError:
        return False

    old_path = sys.path
    sys.path.append(path)

    try:
        import binaryninja
    except ImportError:
        sys.path = old_path
        return False

    return True

while not validate_path(binaryninja_api_path):
    print "Binary Ninja not found. Please provide the path to Binary Ninja's install directory"
    sys.stdout.write("[{}] ".format(binaryninja_api_path))

    new_path = sys.stdin.readline().strip()
    if len(new_path) == 0:
        print "Invalid Path"
        continue

    if not new_path.endswith('python'):
        new_path = os.path.join(new_path, 'python')

    binaryninja_api_path = new_path

import binaryninja
print "Found Binary Ninja core version: {}".format(binaryninja.core_version)

install_path = site.getsitepackages()[0]
binaryninja_pth_path = os.path.join(install_path, 'binaryninja.pth')
open(binaryninja_pth_path, 'wb').write(binaryninja_api_path)

print "Binary Ninja API installed"
