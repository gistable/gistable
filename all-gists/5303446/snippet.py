#!/usr/bin/env python
# coding: utf8

import imp
import sys, os

module_name = sys.argv[1]
bits = module_name.split('.')
name = imp.find_module(bits[0])[1]
if len(bits) > 1:
    subname = os.path.join(*bits[1:])
    dir_path = os.path.join(name, subname)
else:
    dir_path = name
if os.path.exists(dir_path):
    final_path = dir_path
else:
    py_path = dir_path + '.py'
    if os.path.exists(py_path):
        final_path = py_path
    else:
        print u'Module not found:\n%s\n%s\n' % (dir_path, py_path)
        final_path = None
if final_path:
    cmd = "subl %s" % final_path
    os.system(cmd)
